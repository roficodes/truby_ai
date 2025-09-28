"""Screenplay processing helpers.

This module contains helpers to clean and split screenplay text into scene
chunks, create screenplay database records, and orchestrate the creation of
associated movie and scene records.

Only Google-style docstrings are added in this change; no code logic has been
altered.
"""

import re
import httpx
from openai import AsyncOpenAI
from pymongo.asynchronous.database import AsyncDatabase
from pinecone import PineconeAsyncio
from sqlmodel import Session
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from crud.movies import create_movie
from crud.scenes import create_scenes
from core.config import EMBEDDING_MODEL
from models.db.screenplays import Screenplay
from models.schemas.screenplays import ScreenplayCreate

def clean_text_for_embedding_model(
    scene_text: str,
) -> str:
    """Normalize screenplay text for embedding input.

    This function removes excessive newlines, tabs and repeated punctuation
    and collapses multiple spaces so the resulting text is better suited for
    embedding models.

    Args:
        scene_text: Raw scene text extracted from the screenplay.

    Returns:
        A cleaned string suitable for embedding model input.
    """
    text = re.sub(r"[\n\t]+", " ", scene_text) # remove multiple newlines and tabs
    text = re.sub(r" {2,}", " ", text) # remove extra spaces
    text = re.sub(r"([.!?]{2,})", r"\1", text)
    text = re.sub(r"[-]{2,}", "-", text)
    return text.strip()

def split_script_text(
    script_text: str,
    re_pattern: re.Pattern
) -> list[str]:
    """Split a screenplay's full text into scene chunks using the provided regex.

    The function uses the `re_pattern` both to find scene headers and to split
    the script; it then recombines header finds with their corresponding text
    blocks to produce full scene strings.

    Args:
        script_text: Full screenplay text.
        re_pattern: Compiled regular expression that matches scene headers.

    Returns:
        A list of scene strings in the order they appear in the screenplay.
    """
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
    """Extract scene chunks from a screenplay file using PyMuPDF.

    The loader returns a list of document pages; this function uses the first
    page's content as the screenplay text, splits it into scenes and prepares
    a list of dicts containing both the raw text and a cleaned embedding text
    for each scene.

    Args:
        file_path: Path to the screenplay PDF file.
        regex_pattern: Regular expression used to split the screenplay into
            scenes. Defaults to a pattern that looks for INT/EXT sluglines.

    Returns:
        A dictionary with keys ``full_text`` (the full screenplay text) and
        ``scene_texts`` (a list of dicts with keys ``raw_text`` and
        ``embedding_text``).
    """
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
    """Create a screenplay record and its associated movie and scenes.

    This high-level helper performs the following steps:
    1. Creates a `Movie` record for the provided `tmdb_id` (if it doesn't
       already exist) via `create_movie`.
    2. Loads and splits the provided screenplay file into scene chunks.
    3. Persists a `Screenplay` record containing metadata and full text.
    4. Asynchronously creates and indexes scene records via `create_scenes`.

    Args:
        file_path: Path to the screenplay PDF file.
        tmdb_id: TMDB id for the movie associated with the screenplay.
        session: SQLModel/SQLAlchemy session used for DB operations.
        async_client: `httpx.AsyncClient` used to call external APIs.
        ai_client: OpenAI client used for analysis and embeddings.
        mongodb_database: Async MongoDB database instance.
        pinecone_client: Async Pinecone client instance.

    Returns:
        The created and refreshed `Screenplay` SQL model instance.
    """
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
