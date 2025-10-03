"""API routers for scene-related endpoints.

Provides a minimal /scenes router used during development.
"""

from typing import List
from typing import Any
import mcp
from pydantic import BaseModel
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

class QueryRequest(BaseModel):
    user_query: str

class QueryResult(BaseModel):
    contexts: List[str]

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
    body: QueryRequest,
    request: Request,
    embedding_model: str=EMBEDDING_MODEL,
    top_k: int=TOP_K_CONTEXTS,
    namespace: str=PINECONE_NAMESPACE
    ) -> dict[str, Any]:
    """Query scenes based on a user query.
    This is useful for LLM models if the user asks for how they can write specific types of scenes.

    Args:
        user_query (str): The user's search or question.

    Returns:
        dict: A payload containing the user query and placeholder scenes.
    """
    user_query = body.user_query
    result = await get_relevant_contexts(
        user_query=user_query,
        ai_client=request.app.state.openai_client,
        pinecone_client=request.app.state.pinecone_client,
        embedding_model=embedding_model,
        top_k=top_k,
        namespace=namespace
    )
    return QueryResult(contexts=result).model_dump()

@router.get("/scenes/{screenplay_id}", operation_id="get_scenes_by_screenplay")
async def get_scenes_by_screenplay(
    screenplay_id: int,
    session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Retrieve scenes associated with a given screenplay ID.

    Args:
        screenplay_id: ID of the screenplay whose scenes are to be retrieved.
        session: SQLModel/SQLAlchemy session used for DB operations.

    Returns:
        Relevant contexts from the vector database.

    Raises:
        ValueError: If no scenes are found for the given screenplay ID.
    """
    return get_scenes(screenplay_id=screenplay_id, session=session)