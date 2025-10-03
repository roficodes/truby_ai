"""API routers for screenplay-related endpoints.

This module provides endpoints under the /screenplays prefix to create
and inspect screenplays. Endpoints currently wire to CRUD helpers that
perform text-splitting, database persistence, and scene creation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from fastapi import Request, Depends, UploadFile
from sqlmodel import Session
from crud.screenplays import create_screenplay as crud_create_screenplay
from core.db import get_session
from models.db.screenplays import Screenplay

load_dotenv()

STORAGE_DIR = os.getenv("STORAGE_DIR")

if STORAGE_DIR is None:
    raise ValueError("STORAGE_DIR environment variable isn't set!")
storage_path = Path(STORAGE_DIR)

router = APIRouter(
    prefix="/screenplays",
    tags=["screenplays"]
)


@router.get("/")
def get_screenplays_root():
    """Return a minimal screenplays root payload.

    Returns:
        dict: Minimal metadata about the screenplays root endpoint.
    """

    return {
        "App": "Screenplays Root Page",
        "Summary": "Root page for screenplays.",
    }


@router.post("/")
async def create_screenplay(
    file: UploadFile,
    tmdb_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Create a screenplay from a PDF/text file and associated movie.

    This endpoint is a thin wrapper over the CRUD layer `create_screenplay`.
    It forwards the request-scoped clients and database session to perform
    the heavy lifting.

    Args:
        file: UploadFile object - should be a PDF file.
        file_path (str): Filesystem path to the screenplay file.
        tmdb_id (int): External TMDB movie identifier to attach the screenplay to.
        request (Request): FastAPI Request object (used to access app state clients).
        session (Session): Database session provided via dependency injection.

    Returns:
        dict: A payload containing the created screenplay ID.
    
    Raises: 
        HTTPException: 400 if file type is not PDF or file name is bad.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    safe_file_name = secure_filename(file.filename)
    if not safe_file_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    safe_file_path = storage_path / safe_file_name
    contents = await file.read()
    safe_file_path.write_bytes(contents)

    print("Creating screenplay...")
    screenplay_record = await crud_create_screenplay(
        file_path=str(safe_file_path),
        tmdb_id=tmdb_id,
        session=session,
        async_client=request.app.state.async_client,
        ai_client=request.app.state.openai_client,
        mongodb_database=request.app.state.mongodb_database,
        pinecone_client=request.app.state.pinecone_client
    )
    return {"screenplay_id": screenplay_record.id}

@router.delete("/{screenplay_id}")
async def delete_screenplay(
    screenplay_id: int,
    session: Session = Depends(get_session)
) -> dict[str, str]:
    """Delete a screenplay and its associated scenes from the database.

    This function deletes the screenplay record with the given ID, along
    with all associated scenes due to cascading delete behavior.

    Args:
        screenplay_id: ID of the screenplay to delete.
        session: SQLModel/SQLAlchemy session used for DB operations.

    Returns:
        Message indicating successful deletion.

    Raises:
        ValueError: If no screenplay is found for the given ID.
    """
    screenplay = session.get(Screenplay, screenplay_id)
    if not screenplay:
        raise ValueError(f"No screenplay found with ID {screenplay_id}")
    session.delete(screenplay)
    session.commit()
    return {"Deleted": f"Successfully deleted screenplay {screenplay_id}."}