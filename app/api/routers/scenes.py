"""API routers for scene-related endpoints.

Provides a minimal /scenes router used during development.
"""

from typing import Any
from fastapi.routing import APIRouter
from fastapi import Request, Depends
from sqlmodel import Session
from crud.scenes import get_relevant_contexts, get_scenes
from core.db import get_session
from core.config import EMBEDDING_MODEL, TOP_K_CONTEXTS, PINECONE_NAMESPACE

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


@router.post("/query", operation_id="get_relevant_scenes")
async def query_scenes(
    user_query: str, 
    request: Request,
    embedding_model: str=EMBEDDING_MODEL,
    top_k: int=TOP_K_CONTEXTS,
    namespace: str=PINECONE_NAMESPACE
    ):
    """Query scenes based on a user query.

    This is a placeholder implementation. Replace with actual logic to
    fetch and return relevant scenes based on the user query.

    Args:
        user_query (str): The user's search or question.

    Returns:
        dict: A payload containing the user query and placeholder scenes.
    """
    result = await get_relevant_contexts(
        user_query=user_query,
        ai_client=request.app.state.openai_client,
        pinecone_client=request.app.state.pinecone_client,
        embedding_model=embedding_model,
        top_k=top_k,
        namespace=namespace
    )
    return result

@router.get("/scenes/{screenplay_id}", operation_id="get_scenes_by_screenplay")
async def get_scenes_by_screenplay(
        screenplay_id: int,
        session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Retrieve scenes associated with a given screenplay ID.

    Args:
        screenplay_id: ID of the screenplay whose scenes are to be retrieved.
        session: SQLModel/SQLAlchemy session used for DB operations.

    Raises:
        ValueError: If no scenes are found for the given screenplay ID.
    """
    return get_scenes(screenplay_id=screenplay_id, session=session)