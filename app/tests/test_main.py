import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi import FastAPI

import app.main as main_mod


def test_get_root():
    result = main_mod.get_root()
    assert isinstance(result, dict)
    assert "App" in result


@pytest.mark.asyncio
async def test_wrap_routes_for_debug_awaits_coroutine():
    app = FastAPI()

    # async endpoint
    @app.get("/async")
    async def async_endpoint():
        return "async_ok"

    # sync endpoint
    @app.get("/sync")
    def sync_endpoint():
        return "sync_ok"

    # wrap routes
    main_mod.wrap_routes_for_debug(app)

    # find routes and call them
    found_async = None
    found_sync = None
    for route in app.routes:
        if getattr(route, "path", None) == "/async":
            found_async = route
        if getattr(route, "path", None) == "/sync":
            found_sync = route

    assert found_async is not None
    assert found_sync is not None

    # debug endpoint wrappers are async functions
    async_result = await found_async.endpoint()
    assert async_result == "async_ok"

    sync_result = await found_sync.endpoint()
    assert sync_result == "sync_ok"


@pytest.mark.asyncio
async def test_lifespan_calls_initializers_and_closers():
    app = FastAPI()

    # Prepare mocks for all initializers and closers
    mock_init_db = MagicMock()
    mock_init_mongodb = MagicMock()
    mock_mongodb_client = AsyncMock()
    mock_init_mongodb.return_value = mock_mongodb_client

    mock_init_async_client = MagicMock()
    mock_async_client = AsyncMock()
    mock_init_async_client.return_value = mock_async_client

    mock_init_openai = MagicMock()
    mock_openai_client = MagicMock()
    mock_init_openai.return_value = mock_openai_client

    mock_init_pinecone = MagicMock()
    mock_pinecone_client = AsyncMock()
    mock_init_pinecone.return_value = mock_pinecone_client

    mock_close_async_client = AsyncMock()
    mock_close_mongodb_client = AsyncMock()
    mock_close_openai_client = MagicMock()
    mock_close_pinecone_client = AsyncMock()

    # patch names in main_mod where they are imported
    with patch("app.main.init_db", mock_init_db), \
        patch("app.main.init_mongodb_client", mock_init_mongodb), \
        patch("app.main.init_async_client", mock_init_async_client), \
        patch("app.main.init_openai_client", mock_init_openai), \
        patch("app.main.init_pinecone_client", mock_init_pinecone), \
        patch("app.main.close_async_client", mock_close_async_client), \
        patch("app.main.close_mongodb_client", mock_close_mongodb_client), \
        patch("app.main.close_openai_client", mock_close_openai_client), \
        patch("app.main.close_pinecone_client", mock_close_pinecone_client):

        # Use the lifespan context manager
        async with main_mod.lifespan(app):
            # inside startup (after yield)
            mock_init_db.assert_called_once()
            mock_init_mongodb.assert_called_once()
            mock_init_async_client.assert_called_once()
            mock_init_openai.assert_called_once()
            mock_init_pinecone.assert_called_once()

        # after context exits, closers should be awaited/called
        mock_close_async_client.assert_awaited
        mock_close_mongodb_client.assert_awaited
        mock_close_pinecone_client.assert_awaited
        mock_close_openai_client.assert_called
