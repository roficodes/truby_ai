from config import MONGODB_CONNECTION, MONGODB_DATABASE
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import OpenAI
from pinecone import PineconeAsyncio

load_dotenv()

def init_mongodb_client() -> AsyncDatabase:
    client = AsyncMongoClient(MONGODB_CONNECTION)
    return client[MONGODB_DATABASE]

def init_async_client() -> AsyncClient:
    return AsyncClient()

async def close_async_client(async_client: AsyncClient):
    await async_client.aclose()

def init_openai_client(api_key: str) -> OpenAI:
    return OpenAI(
        api_key=api_key
    )

def init_pinecone_client(api_key: str) -> PineconeAsyncio:
    return PineconeAsyncio(
        api_key=api_key
    )

async def close_pinecone_client(pinecone_client: PineconeAsyncio):
    await pinecone_client.close()