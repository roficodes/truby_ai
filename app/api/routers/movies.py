"""API routers for movie-related endpoints.

This module defines a small router under the /movies prefix. It's a
convenience single-file router for movie endpoints used by the
application.
"""

from fastapi.routing import APIRouter

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