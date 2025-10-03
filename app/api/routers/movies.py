"""API routers for movie-related endpoints.

This module defines a small router under the /movies prefix. It's a
convenience single-file router for movie endpoints used by the
application.
"""

from typing import Any
from fastapi.routing import APIRouter
from crud.movies import get_movie
from fastapi import Depends
from sqlmodel import Session
from core.db import get_session

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)


@router.get("/")
def get_screenplays_root():
    """Return a small movies-root payload.

    Returns:
        dict: Minimal metadata for the movies root endpoint.
    """

    return {
        "App": "Movies Root Page",
        "Summary": "Root page for movies.",
    }

@router.get("/movie/{screenplay_id}")
async def get_movie_record(screenplay_id: int, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Retrieve movie details based on the screenplay ID.
    
    Args:
        screenplay_id: ID of the screenplay associated with the movie.
    Returns:
        dictionary payload containing the movie details.
    """
    movie = get_movie(screenplay_id=screenplay_id, session=session)
    return movie