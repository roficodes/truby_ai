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
    