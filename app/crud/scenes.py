import os
import time
from dotenv import load_dotenv
from openai import OpenAI
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
    ai_client: OpenAI,
    embedding_model: str,
    mongodb_client: AsyncDatabase,
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
    embedding = ai_client.embeddings.create(
        model=embedding_model,
        input=scene_text["embedding_text"],
        encoding_format="float"
    ).data[0].embedding
    mongodb_insert_record["embedding_vector"] = embedding
    mongodb_record = await mongodb_client["scenes"].insert_one(mongodb_insert_record)
    index = pinecone_client.IndexAsyncio(host="SCENE_EMBEDDINGS")
    index.upsert(
        vectors=[
            {
                "mongodb_scene_id": mongodb_record.inserted_id,
                "values": embedding,
                "metadata": mongodb_insert_record
                
            }
        ],
        namespace="scene_embeddings"
    )


async def create_scene_from_text(
    scene_text: dict[str, str],
    screenplay_id: int,
    scene_number: int,
    total_scenes: int,
    embedding_model: str,
    session: Session
) -> Scene:
    progress_num = scene_number / total_scenes if total_scenes else 0 # lazy way to handle divide by zero
    scene_create_model = SceneCreate(
        screenplay_id=screenplay_id,
        scene_number=scene_number,
        progress_raw=f"{scene_number}/{total_scenes}",
        progress_num=progress_num,
    )
    scene_record = Scene(**scene_create_model.model_dump())
    session.add(scene_record)
    session.commit()
    session.refresh(scene_record)
    await create_mongodb_pinecone_records(
        scene_id=scene_record.id,
        scene_text=scene_text,
        embedding_model=embedding_model
    )
    # TODO: create update methods to update scenes (in this case, with mongodb_id)
    return scene_record

async def create_scenes(
    scene_texts: list[dict[str, str]],
    screenplay_id: int,
    ai_client: OpenAI,
    embedding_model: str,
    mongodb_client: AsyncDatabase,
    pinecone_client: PineconeAsyncio,
    session: Session
):
    total_scenes = len(scene_texts)
    scene_number = 1
    previous_scene_id = None
    previous_story_beat = "exposition"
    for scene_text in scene_texts:
        sql_scene_record = create_scene_from_text(
            scene_text=scene_text,
            screenplay_id=screenplay_id,
            scene_number=scene_number,
            total_scenes=total_scenes,
            embedding_model=embedding_model,
            session=session
        )
        ai_summary = generate_ai_summary(
            scene_progress=f"{scene_number} out of {total_scenes}",
            previous_story_beat=previous_story_beat,
            ai_client=ai_client
        )
        time.sleep(0.5)
        story_beat = generate_beat(
            scene_progress=f"{scene_number} out of {total_scenes}",
            previous_story_beat=previous_story_beat,
            ai_client=ai_client
        )
        create_mongodb_pinecone_records(
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
            mongodb_client=mongodb_client,
            pinecone_client=pinecone_client
        )
        previous_scene_id=sql_scene_record.id
        previous_story_beat=story_beat
        

        