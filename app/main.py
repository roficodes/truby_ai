"""Application entrypoint and FastAPI app configuration.

This module creates the FastAPI application, sets up the lifespan
context manager for startup/shutdown tasks (database and client
initialization/cleanup), registers routers, and provides a small
debugging helper to wrap routes so returned coroutines are awaited
and their types logged during development.

Functions:
    wrap_routes_for_debug(app): Wraps APIRoute endpoints to await coroutine
        results and print debug output.
    lifespan(app): Async context manager used by FastAPI to initialize and
        teardown shared resources (DB, HTTP client, OpenAI, Pinecone, etc.).
    get_root(): Simple root health endpoint.
"""
from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from api.routers import movies_router, screenplays_router, scenes_router
from fastapi.routing import APIRoute
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


def wrap_routes_for_debug(app: FastAPI):
    """Wrap APIRoute endpoints to await coroutine results and log them.

    This function iterates the app routes and replaces the endpoint with a
    wrapper that ensures coroutine results are awaited before being returned.

    Args:
        app (FastAPI): The FastAPI application whose routes will be wrapped.

    Returns:
        None
    """

    for route in app.routes:
        if isinstance(route, APIRoute):
            original_endpoint = route.endpoint

            async def debug_endpoint(*args, __original_endpoint=original_endpoint, **kwargs):
                """Await the original endpoint if it returns a coroutine and log its type.

                Args:
                    *args: Positional args forwarded to the original endpoint.
                    **kwargs: Keyword args forwarded to the original endpoint.

                Returns:
                    The resolved endpoint result.
                """

                result = __original_endpoint(*args, **kwargs)
                # If it's a coroutine, await it
                if asyncio.iscoroutine(result):
                    result = await result
                print(f"[DEBUG] {__original_endpoint.__module__}.{__original_endpoint.__name__} returned {type(result)}")
                return result

            route.endpoint = debug_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application startup and shutdown.

    This lifecycle manager performs initialization of resources during
    application startup (database, HTTP/OpenAI/Pinecone clients) and
    ensures they are correctly closed on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
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
mcp_app = FastApiMCP(
    fastapi=app,
    name="trubyai-mcp",
    description="Truby AI lookup tool for contexts",
    include_operations=["get_relevant_scenes"]
)
mcp_app.mount()
mcp_app.setup_server()

wrap_routes_for_debug(app)

@app.get("/")
def get_root():
    """Return a simple root-level health and summary payload.

    Returns:
        dict: A minimal JSON-friendly dictionary describing the app.
    """

    return {
        "App": "Root Page",
        "Summary": "Having trouble with your screenplay's beats? Truby AI will help you out.",
    }
