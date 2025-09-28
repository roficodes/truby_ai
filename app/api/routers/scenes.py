"""API routers for scene-related endpoints.

Provides a minimal /scenes router used during development.
"""

from fastapi.routing import APIRouter

router = APIRouter(
    prefix="/scenes",
    tags=["scenes"]
)


@router.get("/")
def get_scenes_root():
    """Return a small scenes-root payload.

    Returns:
        dict: Basic metadata for the scenes root endpoint.
    """

    return {
        "App": "Scenes Root Page",
        "Summary": "Root page for scenes.",
    }