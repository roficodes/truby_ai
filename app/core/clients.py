import os
from core.config import MONGODB_CONNECTION
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import OpenAI
from pinecone import PineconeAsyncio

load_dotenv()

def init_mongodb_client() -> AsyncMongoClient:
    client = AsyncMongoClient(MONGODB_CONNECTION)
    return client

async def close_mongodb_client(mongodb_client: AsyncMongoClient):
    await mongodb_client.aclose()

def init_async_client() -> AsyncClient:
    return AsyncClient()

async def close_async_client(async_client: AsyncClient):
    await async_client.aclose()

def init_openai_client(api_key: str = os.getenv("OPENAI_API_KEY")) -> OpenAI:
    return OpenAI(
        api_key=api_key
    )

def close_openai_client(ai_client: OpenAI):
    ai_client.close()

def init_pinecone_client(api_key: str = os.getenv("PINECONE_API_KEY")) -> PineconeAsyncio:
    return PineconeAsyncio(
        api_key=api_key
    )

async def close_pinecone_client(pinecone_client: PineconeAsyncio):
    await pinecone_client.close()