import pytest
from unittest.mock import AsyncMock, patch

import app.core.clients as clients


@pytest.mark.asyncio
async def test_init_and_close_async_client():
    async_client = clients.init_async_client()
    assert hasattr(async_client, "aclose")
    await clients.close_async_client(async_client)


def test_init_openai_and_close():
    ai = clients.init_openai_client(api_key="fake")
    assert hasattr(ai, "close")
    clients.close_openai_client(ai)


@pytest.mark.asyncio
async def test_init_and_close_pinecone_client():
    pine = clients.init_pinecone_client(api_key="fake")
    assert hasattr(pine, "close")
    await clients.close_pinecone_client(pine)
