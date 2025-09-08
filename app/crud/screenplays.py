import re
import httpx
from pathlib import Path
from sqlmodel import Session, select
from fastapi import UploadFile, File, HTTPException
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from crud.movies import create_movie
from core.config import STORAGE_DIR
from models.db.screenplays import Screenplay
from models.db.movies import Movie
from models.schemas.screenplays import ScreenplayCreate, ScreenplayRead, ScreenplayUpdate

STORAGE_DIR_PATH = Path(STORAGE_DIR)

# TODO: reactor into (async?) create_screenplay() and save_to_path() methods
def upload_screenplay(
    file: UploadFile,
    user_filename: str,
    tmdb_id: int, 
    session: Session,
    async_client: httpx.AsyncClient
) -> Screenplay:
    movie_record = session.exec(select(Movie).where(Movie.tmdb_id == tmdb_id)).first()
    if movie_record:
        raise HTTPException(status_code=400, detail="There is already a screenplay for this movie.")
    movie_record = create_movie(tmdb_id=tmdb_id, async_client=async_client, session=session)
    file_extension = Path(file.filename).suffix
    safe_filename = "".join(char for char in user_filename if char.isalnum() or char in ("-", "_"))
    save_path = STORAGE_DIR / f"{safe_filename}{file_extension}"
    return save_path

def clean_text_for_embedding_model(
    scene_text: str
) -> str:
    text = re.sub(r"[\n\t]+", " ", scene_text) # remove multiple newlines and tabs
    text = re.sub(r" {2,}", " ", text) # remove extra spaces
    text = re.sub(r"([.!?]{2,})", r"\1", text)
    text = re.sub(r"[-]{2,}", "-", text)
    return text.strip()

async def create_screenplay_chunks(
    file_path: str,
    regex_pattern: str | None = r"(?m)^(?:\d+\s+)?((?:INT\.?|EXT\.?)(?:/(?:INT\.?|EXT\.?))?(?:\s.*)?)"
) -> dict[str, str | list[dict[str, str]]]:
    loader = PyMuPDFLoader(file_path=file_path, mode="single")
    loaded_screenplay = await loader.aload()
    re_pattern = re.compile(regex_pattern)
    raw_scene_texts = re.split(pattern=re_pattern, string=loaded_screenplay[0].page_content)
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

def create_screenplay(
    file_path: str,
    tmdb_id: int,
    session: Session,
    async_client: httpx.AsyncClient
) -> Screenplay:
    movie_record = create_movie(tmdb_id=tmdb_id, async_client=async_client, session=session)
    screenplay_chunks = create_screenplay_chunks(
        file_path=file_path
    )
    screenplay_create_model = ScreenplayCreate(
        movie_id=movie_record.id,
        storage_path=file_path,
        text=screenplay_chunks["full_text"],
        total_scenes=len(screenplay_chunks["scene_texts"])
    )
    screenplay_record = Screenplay(**screenplay_create_model.model_dump())
    session.add(screenplay_record)
    session.commit()
    session.refresh()
    # TODO: here is where you now create the scene records as you should have a screenplay id
    return screenplay_record