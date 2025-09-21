import re
import httpx
from pathlib import Path
from openai import AsyncOpenAI
from pymongo.asynchronous.database import AsyncDatabase
from pinecone import PineconeAsyncio
from sqlmodel import Session, select
from fastapi import UploadFile, HTTPException
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from crud.movies import create_movie
from crud.scenes import create_scenes
from core.config import EMBEDDING_MODEL
from models.db.screenplays import Screenplay
from models.db.movies import Movie
from models.schemas.screenplays import ScreenplayCreate

def clean_text_for_embedding_model(
    scene_text: str,
) -> str:
    text = re.sub(r"[\n\t]+", " ", scene_text) # remove multiple newlines and tabs
    text = re.sub(r" {2,}", " ", text) # remove extra spaces
    text = re.sub(r"([.!?]{2,})", r"\1", text)
    text = re.sub(r"[-]{2,}", "-", text)
    return text.strip()

def split_script_text(
    script_text: str,
    re_pattern: re.Pattern
) -> list[str]:
    final_list = []
    all_finds = re_pattern.findall(script_text)
    splits = re.split(pattern=re_pattern, string=script_text)
    for i, value in enumerate(splits):
        if i == 0:
            final_list.append(value.strip())
            i += 1
            continue
        new_text = all_finds[i-1] + " " + value.strip()
        final_list.append(new_text.replace("  ", " "))
    return final_list

async def create_screenplay_chunks(
    file_path: str,
    regex_pattern: str | None = r"(?m)^(?:\d+\s+)?(?:INT\.?|EXT\.?)(?:/(?:INT\.?|EXT\.?))?.*?(?=\n(?:\d+\s+)?(?:INT\.?|EXT\.?)(?:/(?:INT\.?|EXT\.?))?|$)"
) -> dict[str, str | list[dict[str, str]]]:
    loader = PyMuPDFLoader(file_path=file_path, mode="single")
    loaded_screenplay = await loader.aload()
    re_pattern = re.compile(regex_pattern)
    raw_scene_texts = split_script_text(script_text=loaded_screenplay[0].page_content, re_pattern=re_pattern)
    scene_texts = [
        {
            "raw_text": raw_scene_text,
            "embedding_text": clean_text_for_embedding_model(raw_scene_text)
        } for raw_scene_text in raw_scene_texts
    ]
    return {
        "full_text": loaded_screenplay[0].page_content,
        "scene_texts": scene_texts
    }

async def create_screenplay(
    file_path: str,
    tmdb_id: int,
    session: Session,
    async_client: httpx.AsyncClient,
    ai_client: AsyncOpenAI,
    mongodb_database: AsyncDatabase,
    pinecone_client: PineconeAsyncio
) -> Screenplay:
    movie_record = await create_movie(tmdb_id=tmdb_id, async_client=async_client, session=session)
    print(f"Movie record created: {movie_record}")
    screenplay_chunks = await create_screenplay_chunks(
        file_path=file_path
    )
    print("Chunks created!")
    screenplay_create_model = ScreenplayCreate(
        movie_id=movie_record.id,
        storage_path=file_path,
        text=screenplay_chunks["full_text"],
        total_scenes=len(screenplay_chunks["scene_texts"])
    )
    screenplay_record = Screenplay(**screenplay_create_model.model_dump())
    session.add(screenplay_record)
    session.commit()
    session.refresh(screenplay_record)
    print("Screenplay record committed. Database refreshed.")
    # TODO: here is where you now create the scene records as you should have a screenplay id
    await create_scenes(
        scene_texts=screenplay_chunks["scene_texts"],
        screenplay_id=screenplay_record.id,
        movie_name=movie_record.title,
        ai_client=ai_client,
        embedding_model=EMBEDDING_MODEL,
        mongodb_database=mongodb_database,
        pinecone_client=pinecone_client,
        session=session
    )
    return screenplay_record
