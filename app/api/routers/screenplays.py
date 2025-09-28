"""API routers for screenplay-related endpoints.

This module provides endpoints under the /screenplays prefix to create
and inspect screenplays. Endpoints currently wire to CRUD helpers that
perform text-splitting, database persistence, and scene creation.
"""

from fastapi.routing import APIRouter
from fastapi import Request, Depends
from sqlmodel import Session
from crud.screenplays import create_screenplay as crud_create_screenplay
from core.db import get_session
from models.db.movies import Movie
from models.db.screenplays import Screenplay
from models.db.scenes import Scene

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
    file_path: str,
    tmdb_id: int,
    request: Request,
    session: Session = Depends(get_session)
):
    """Create a screenplay from a PDF/text file and associated movie.

    This endpoint is a thin wrapper over the CRUD layer `create_screenplay`.
    It forwards the request-scoped clients and database session to perform
    the heavy lifting.

    Args:
        file_path (str): Filesystem path to the screenplay file.
        tmdb_id (int): External TMDB movie identifier to attach the screenplay to.
        request (Request): FastAPI Request object (used to access app state clients).
        session (Session): Database session provided via dependency injection.

    Returns:
        dict: A payload containing the created screenplay ID.
    """

    print("Creating screenplay...")
    screenplay_record = await crud_create_screenplay(
        file_path=file_path,
        tmdb_id=tmdb_id,
        session=session,
        async_client=request.app.state.async_client,
        ai_client=request.app.state.openai_client,
        mongodb_database=request.app.state.mongodb_database,
        pinecone_client=request.app.state.pinecone_client
    )
    return {"screenplay_id": screenplay_record.id}
