from fastapi.routing import APIRouter

from routers.movies import router as movies_router
from routers.screenplays import router as screenplays_router
from routers.scenes import router as scenes_router

router = APIRouter()
router.include_router(movies_router)
router.include_router(screenplays_router)
router.include_router(scenes_router)