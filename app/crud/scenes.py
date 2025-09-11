import os
import sys
import httpx
from dotenv import load_dotenv
import random
import numpy as np
from sqlmodel import Session, select
from core.clients import OpenAI
from models.schemas.scenes import SceneCreate
from models.db.screenplays import Screenplay
from models.db.scenes import Scene, SceneEmbedding

load_dotenv()

# TODO: Ideally would like to have generic LLM and Vector DB configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

"""
class Scene(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    screenplay_id: int = Field(..., foreign_key="screenplay.id")
    scene_number: int = Field(...)
    progress_raw: str = Field(...)
    progress_num: float = Field(...)
    beat: str | None = Field(default=None)
    ai_summary: str | None = Field(default=None)
    previous_scene_id: int | None = Field(default=None)
    next_scene_id: int | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
"""

async def create_mongodb_scene_record(
    scene_id: int,
    scene_number: int,
    previous_scene_id: int | None,
    next_scene_id: int | None,
    screenplay_id: int,
    scene_text: dict[str, str],
    embedding_model: str,
    embedding: list[int]
) -> str:
    return {
        "scene_id": random.randint(a=0, b=sys.maxsize),
        "scene_number": 1,
        "previous_scene_id": 1,
        "next_scene_id": 1,
        "screenplay_id": 100,
        "raw_scene_text": "INT. CLUB - DAY: Things are looking good.",
        "embedding_scene_text": "INT CLUB DAY Things are looking good.",
        "embedding_model": "openai/text-embedding-3-small",
        "embedding": np.random.rand(1500,).tolist()
    }

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
    mongodb_id = await create_mongodb_scene_record(
        scene_id=scene_record.id,
        scene_text=scene_text,
        embedding_model=embedding_model
    )
    # TODO: create update methods to update scenes (in this case, with mongodb_id)
    return scene_record
    