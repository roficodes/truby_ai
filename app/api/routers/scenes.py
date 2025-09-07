from fastapi.routing import APIRouter

router = APIRouter(
    prefix="/scenes",
    tags=["scenes"]
)

@router.get("/")
def get_scenes_root():
    return {
        "App": "Scenes Root Page",
        "Summary": "Root page for scenes.",
    }