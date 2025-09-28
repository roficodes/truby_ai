import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

import crud.scenes as scenes


@pytest.mark.asyncio
async def test_create_scene_from_text(tmp_path):
    # mock session with basic add/commit/refresh behavior
    class FakeSession:
        def __init__(self):
            self.added = None

        def add(self, obj):
            self.added = obj

        def commit(self):
            pass

        def refresh(self, obj):
            obj.id = 123

    session = FakeSession()
    scene = await scenes.create_scene_from_text(screenplay_id=1, scene_number=1, total_scenes=3, session=session)
    assert scene.scene_number == 1
    assert scene.id == 123


@pytest.mark.asyncio
async def test_get_ai_response_edges():
    # scene 1 -> exposition
    res = await scenes.get_ai_response(1, "Movie", 5, "exposition", {"raw_text": "x"}, AsyncMock())
    assert res == "exposition"

    # last scene -> resolution
    res = await scenes.get_ai_response(5, "Movie", 5, "something", {"raw_text": "x"}, AsyncMock())
    assert res == "resolution"


@pytest.mark.asyncio
async def test_create_mongodb_pinecone_records(monkeypatch):
    # fake ai_client embedding response
    fake_embedding = MagicMock()
    fake_embedding.data = [MagicMock(embedding=[0.1, 0.2])]

    class FakeAI:
        embeddings = MagicMock()

    fake_ai = FakeAI()
    fake_ai.embeddings.create = MagicMock(return_value=fake_embedding)

    # fake mongodb
    class FakeCollection:
        async def insert_one(self, doc):
            class R:
                inserted_id = "abc123"
            return R()

    class FakeDB(dict):
        def __getitem__(self, name):
            return FakeCollection()

    fake_mongodb = FakeDB()

    # fake pinecone index
    class FakeIndex:
        async def upsert(self, vectors, namespace=None):
            return None

    class FakePinecone:
        def IndexAsyncio(self, host=None):
            return FakeIndex()

    fake_pine = FakePinecone()

    scene_text = {"raw_text": "text", "embedding_text": "text"}

    await scenes.create_mongodb_pinecone_records(
        scene_id=1,
        scene_number=1,
        previous_scene_id=None,
        next_scene_id=None,
        ai_summary="summary",
        story_beat="exposition",
        screenplay_id=1,
        scene_text=scene_text,
        ai_client=fake_ai,
        embedding_model="model",
        mongodb_database=fake_mongodb,
        pinecone_client=fake_pine
    )
