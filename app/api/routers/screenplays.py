from fastapi.routing import APIRouter

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
def upload_screenplay(
    file_path: str,
    tmdb_id: int
) -> Screenplay:
    pass
