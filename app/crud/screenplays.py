import httpx
from pathlib import Path
from sqlmodel import Session, select
from fastapi import UploadFile, File, HTTPException
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

