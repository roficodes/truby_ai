"""Scene creation helpers and integrations.

This module coordinates the creation of scene records in the SQL database,
generation of AI-driven summaries/analysis, and indexing of embeddings in a
vector database (Pinecone) with a corresponding MongoDB document for each
scene.

The functions here are written to be non-blocking from the event loop; when
blocking or sync-only client methods are used they are executed in a
background thread where appropriate.

Note: Only docstrings are added in this change; no logic or behavior is
modified.
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pinecone import PineconeAsyncio
from pymongo.asynchronous.database import AsyncDatabase
from sqlmodel import Session
from models.schemas.scenes import SceneCreate
from models.db.scenes import Scene
from ai.scenes import generate_scene_analysis

load_dotenv()

# TODO: Ideally would like to have generic LLM and Vector DB configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

async def create_mongodb_pinecone_records(
    scene_id: int,
    scene_number: int,
    previous_scene_id: int | None,
    next_scene_id: int | None,
    ai_summary: str | None,
    story_beat: str | None,
    screenplay_id: int,
    scene_text: dict[str, str],
    ai_client: AsyncOpenAI,
    embedding_model: str,
    mongodb_database: AsyncDatabase,
    pinecone_client: PineconeAsyncio
) -> dict[str, str] | None:
    """Persist a scene document to MongoDB and upsert its embedding into Pinecone.

    This function constructs a MongoDB document containing the scene
    metadata and uses the provided `ai_client` to create an embedding vector.
    Because the OpenAI embedding client used here is synchronous, the call is
    executed inside a thread using `asyncio.to_thread` to avoid blocking the
    event loop. The resulting embedding vector is stored in Pinecone using the
    provided `pinecone_client`.

    Args:
        scene_id: Internal SQL scene id.
        scene_number: Sequential scene number within the screenplay.
        previous_scene_id: SQL id of the previous scene or ``None``.
        next_scene_id: SQL id of the next scene or ``None``.
        ai_summary: AI-generated summary text for the scene.
        story_beat: High-level story beat label for the scene.
        screenplay_id: Parent screenplay id.
        scene_text: Dictionary with keys ``raw_text`` and ``embedding_text``.
        ai_client: OpenAI async client used for embedding generation (calls the
            synchronous embeddings API under the hood).
        embedding_model: Name of the embedding model to use.
        mongodb_database: Async MongoDB database instance.
        pinecone_client: Async Pinecone client used to index vectors.

    Returns:
        The MongoDB document that was inserted (as a Python dict) or ``None``
        when no document was created. The function also performs the Pinecone
        upsert as a side-effect.
    """
    mongodb_insert_record = {
        "scene_id": scene_id,
        "scene_number": scene_number,
        "previous_scene_id": previous_scene_id,
        "next_scene_id": next_scene_id,
        "ai_summary": ai_summary,
        "story_beat": story_beat,
        "screenplay_id": screenplay_id,
        "scene_text": scene_text,
        "embedding_model": embedding_model
    }
    # ai_client.embeddings.create is synchronous; run in a thread to avoid blocking the event loop
    embedding_response = await asyncio.to_thread(
        ai_client.embeddings.create,
        model=embedding_model,
        input=ai_summary,
        encoding_format="float"
    )
    embedding = embedding_response.data[0].embedding
    mongodb_insert_record["embedding_vector"] = embedding
    mongodb_record = await mongodb_database["scenes"].insert_one(mongodb_insert_record)
    mongodb_insert_record["_id"] = str(mongodb_record.inserted_id)
    index = pinecone_client.IndexAsyncio(host=os.getenv("PINECONE_HOST_URL"))
    del mongodb_insert_record["embedding_vector"]
    await index.upsert(
        vectors=[
            {
                "id": str(mongodb_record.inserted_id),
                "values": embedding,
                "metadata": {
                    "scene_id": scene_id,
                    "screenplay_id": screenplay_id,
                    "scene_number": scene_number,
                    "embedding_model": embedding_model,
                    "ai_summary": ai_summary,
                    "embedding_text": scene_text["embedding_text"],
                    "raw_text": scene_text["raw_text"]
                }
            }
        ],
        namespace="scene_embeddings"
    )


async def create_scene_from_text(
    screenplay_id: int,
    scene_number: int,
    total_scenes: int,
    session: Session
) -> Scene:
    """Create a SQL scene record placeholder for a scene extracted from text.

    The created `Scene` is a lightweight SQL record used to track progress and
    association with a screenplay. At this stage the scene's AI-driven fields
    (summary, beat, mongodb id) are left empty and intended to be populated by
    subsequent processing.

    Args:
        screenplay_id: Parent screenplay id.
        scene_number: 1-based scene index within the screenplay.
        total_scenes: Total number of scenes in the screenplay. Used to
            compute a progress ratio (0-1).
        session: SQLModel/SQLAlchemy `Session` used to persist the record.

    Returns:
        The created and refreshed `Scene` SQL model instance.
    """
    progress_num = scene_number / total_scenes if total_scenes else 0 # lazy way to handle divide by zero
    scene_create_model = SceneCreate(
        screenplay_id=screenplay_id,
        scene_number=scene_number,
        progress_raw=f"{scene_number}/{total_scenes}",
        progress_num=progress_num,
        scene_text=None,
        beat=None,
        previous_scene_id=None,
        ai_summary=None,
        next_scene_id=None,
        mongodb_record_id=None
    )
    scene_record = Scene(**scene_create_model.model_dump())
    session.add(scene_record)
    session.commit()
    session.refresh(scene_record)
    # TODO: create update methods to update scenes (in this case, with mongodb_id)
    return scene_record

async def get_ai_response(
    scene_number: int,
    movie_name: str,
    total_scenes: int,
    previous_story_beat: str,
    scene_text: dict[str, str],
    ai_client: AsyncOpenAI
) -> str:
    """Return a story beat / AI summary for a scene.

    This function short-circuits first and last scenes to deterministic labels
    ("exposition" and "resolution"). For other scenes it delegates to the
    `generate_scene_analysis` helper (executed inside a thread) which returns
    a JSON string; this is parsed and returned as a Python structure.

    Args:
        scene_number: 1-based scene index.
        movie_name: Title of the movie, provided to the AI prompt.
        total_scenes: Total number of scenes in the screenplay.
        previous_story_beat: The previous scene's story beat.
        scene_text: Dict containing ``raw_text`` and ``embedding_text`` for the
            scene.
        ai_client: OpenAI async client used by the analysis helper.

    Returns:
        A parsed JSON object (typically a dict) returned by the AI analysis
        helper or a short-circuit string for first/last scenes.
    """
    if scene_number == 1:
        return "exposition"
    if scene_number == total_scenes:
        return "resolution"
    ai_response = await asyncio.to_thread(
        generate_scene_analysis,
        movie_name,
        scene_number,
        total_scenes,
        scene_text["raw_text"],
        previous_story_beat,
        ai_client
    )
    return json.loads(ai_response)

async def create_scenes(
    scene_texts: list[dict[str, str]],
    screenplay_id: int,
    movie_name: str,
    ai_client: AsyncOpenAI,
    embedding_model: str,
    mongodb_database: AsyncDatabase,
    pinecone_client: PineconeAsyncio,
    session: Session
):
    """Orchestrate creation of scenes, AI analysis, and indexing.

    Iterates over a sequence of scene text dictionaries and for each scene:
    1. Creates a SQL placeholder scene record.
    2. Requests AI analysis for the scene (run in a worker thread where the
       helper is synchronous).
    3. Persists the scene's embedding to MongoDB and Pinecone.

    Args:
        scene_texts: List of dicts with keys ``raw_text`` and ``embedding_text``.
        screenplay_id: Parent screenplay id.
        movie_name: Title of the movie.
        ai_client: OpenAI client used for analysis and embeddings.
        embedding_model: Embedding model name.
        mongodb_database: Async MongoDB database.
        pinecone_client: Async Pinecone client.
        session: SQLModel/SQLAlchemy session used to create scene records.

    Returns:
        None. The function performs side-effects (DB writes and Pinecone index
        operations) for each scene.
    """
    print("Scenes being created now.")
    total_scenes = len(scene_texts)
    scene_number = 1
    previous_scene_id = None
    previous_story_beat = "exposition"
    for scene_text in scene_texts:
        # create_scene_from_text is async — await it
        sql_scene_record = await create_scene_from_text(
            screenplay_id=screenplay_id,
            scene_number=scene_number,
            total_scenes=total_scenes,
            session=session
        )
        print(f"Scene record created: {scene_number}")
        # generate_ai_summary and generate_beat synchronous wrappers around OpenAI client; run in threads
        ai_response = await asyncio.to_thread(
            get_ai_response,
            scene_number,
            movie_name,
            total_scenes,
            previous_story_beat,
            scene_text["raw_text"],
            ai_client
        )
        await asyncio.sleep(0.5)
        # create and index embeddings / mongodb records asynchronously
        await create_mongodb_pinecone_records(
            scene_id=sql_scene_record.id,
            scene_number=scene_number,
            previous_scene_id=previous_scene_id,
            next_scene_id=None,
            ai_summary=ai_response["ai_summary"],
            story_beat=ai_response["story_beat"].lower(),
            screenplay_id=screenplay_id,
            scene_text=scene_text,
            ai_client=ai_client,
            embedding_model=embedding_model,
            mongodb_database=mongodb_database,
            pinecone_client=pinecone_client
        )
        previous_scene_id=sql_scene_record.id
        previous_story_beat=ai_response["story_beat"].lower()
        scene_number += 1
        

        