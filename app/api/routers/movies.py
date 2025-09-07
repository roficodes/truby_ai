from fastapi.routing import APIRouter

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

@router.get("/")
def get_screenplays_root():
    return {
        "App": "Movies Root Page",
        "Summary": "Root page for movies.",
    }