import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pinecone import PineconeAsyncio
from pymongo.asynchronous.database import AsyncDatabase
from sqlmodel import Session
from models.schemas.scenes import SceneCreate
from models.db.scenes import Scene
from ai.scenes import generate_ai_summary, generate_beat

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

async def get_story_beat(
    scene_number: int,
    movie_name: str,
    total_scenes: int,
    previous_story_beat: str,
    scene_text: dict[str, str],
    ai_client: AsyncOpenAI
) -> str:
    if scene_number == 1:
        return "exposition"
    if scene_number == total_scenes:
        return "resolution"
    story_beat = await asyncio.to_thread(
        generate_beat,
        movie_name,
        f"{scene_number} out of {total_scenes}",
        previous_story_beat,
        scene_text["raw_text"],
        ai_client
        )
    return story_beat

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
    print("Scenes being created now.")
    total_scenes = len(scene_texts)
    scene_number = 1
    previous_scene_id = None
    previous_story_beat = "exposition"
    for scene_text in scene_texts:
        # create_scene_from_text is async — await it
        sql_scene_record = await create_scene_from_text(
            # scene_text=scene_text,
            screenplay_id=screenplay_id,
            scene_number=scene_number,
            total_scenes=total_scenes,
            # embedding_model=embedding_model,
            session=session
        )
        print(f"Scene record created: {scene_number}")
        # generate_ai_summary and generate_beat synchronous wrappers around OpenAI client; run in threads
        ai_summary = await asyncio.to_thread(
            generate_ai_summary,
            movie_name,
            scene_number,
            f"{scene_number} out of {total_scenes}",
            previous_story_beat,
            scene_text["raw_text"],
            ai_client
        )
        await asyncio.sleep(0.5)
        story_beat = await get_story_beat(
            scene_number=scene_number,
            movie_name=movie_name,
            total_scenes=total_scenes,
            previous_story_beat=previous_story_beat,
            scene_text=scene_text,
            ai_client=ai_client
        )
        # create and index embeddings / mongodb records asynchronously
        await create_mongodb_pinecone_records(
            scene_id=sql_scene_record.id,
            scene_number=scene_number,
            previous_scene_id=previous_scene_id,
            next_scene_id=None,
            ai_summary=ai_summary,
            story_beat=story_beat,
            screenplay_id=screenplay_id,
            scene_text=scene_text,
            ai_client=ai_client,
            embedding_model=embedding_model,
            mongodb_database=mongodb_database,
            pinecone_client=pinecone_client
        )
        previous_scene_id=sql_scene_record.id
        previous_story_beat=story_beat
        scene_number += 1
        

        