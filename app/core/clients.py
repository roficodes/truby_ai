from httpx import AsyncClient

async_client: AsyncClient | None = None

def init_async_client() -> AsyncClient:
    global async_client
    async_client = AsyncClient()
    return async_client

async def close_async_client():
    if async_client:
        await async_client.aclose()
