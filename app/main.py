from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routers import movies_router, screenplays_router, scenes_router
from core.config import MONGODB_DATABASE
from core.db import init_db, engine as db_engine
from core.clients import (
    init_async_client, 
    close_async_client, 
    init_openai_client, 
    close_openai_client,
    init_pinecone_client,
    close_pinecone_client,
    init_mongodb_client,
    close_mongodb_client
)

from fastapi.routing import APIRoute
# import types
import asyncio

def wrap_routes_for_debug(app):
    for route in app.routes:
        if isinstance(route, APIRoute):
            original_endpoint = route.endpoint

            async def debug_endpoint(*args, __original_endpoint=original_endpoint, **kwargs):
                result = __original_endpoint(*args, **kwargs)
                # If it’s a coroutine, await it
                if asyncio.iscoroutine(result):
                    result = await result
                print(f"[DEBUG] {__original_endpoint.__module__}.{__original_endpoint.__name__} returned {type(result)}")
                return result

            route.endpoint = debug_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    mongodb_client = init_mongodb_client()
    app.state.mongodb_client = mongodb_client
    app.state.mongodb_database = mongodb_client[MONGODB_DATABASE]
    app.state.async_client = init_async_client()
    app.state.db_engine = db_engine
    app.state.openai_client = init_openai_client()
    app.state.pinecone_client = init_pinecone_client()
    try:
        yield
    finally:
        db_engine.dispose()
        await close_async_client(app.state.async_client)
        await close_mongodb_client(app.state.mongodb_client)
        close_openai_client(app.state.openai_client)
        await close_pinecone_client(app.state.pinecone_client)
        del app.state.mongodb_database
        del app.state.openai_client


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

wrap_routes_for_debug(app)

@app.get("/")
def get_root():
    return {
        "App": "Root Page",
        "Summary": "Having trouble with your screenplay's beats? Truby AI will help you out.",
    }