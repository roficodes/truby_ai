from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routers import movies_router, screenplays_router, scenes_router
from core.db import init_db, engine as db_engine
from core.clients import init_async_client, close_async_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.async_client = init_async_client()
    app.state.db_engine = db_engine
    try:
        yield
    finally:
        db_engine.dispose()
        await close_async_client(app.state.async_client)


app = FastAPI(
    title="Truby AI: Your Screenwriting Assistant!",
    summary="Having trouble with your screenplay's beats? Truby AI will help you out.",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan 
)
app.include_router(movies_router)
app.include_router(screenplays_router)
app.include_router(scenes_router)

@app.get("/")
def get_root():
    return {
        "App": "Root Page",
        "Summary": "Having trouble with your screenplay's beats? Truby AI will help you out.",
    }