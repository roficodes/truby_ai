from httpx import AsyncClient

def init_async_client() -> AsyncClient:
    return AsyncClient()

async def close_async_client(async_client: AsyncClient):
    await async_client.aclose()
