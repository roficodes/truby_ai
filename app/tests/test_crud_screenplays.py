import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import crud.screenplays as screenplays


def test_clean_text_for_embedding_model():
    dirty = "Line1\n\nLine2\t\t  -- "
    cleaned = screenplays.clean_text_for_embedding_model(dirty)
    assert "\n" not in cleaned


def test_split_script_text():
    text = "INT. ROOM\nScene one\nINT. OTHER\nScene two"
    import re
    pattern = re.compile(r"(?m)^(?:\d+\s+)?(?:INT\.?|EXT\.?)")
    splits = screenplays.split_script_text(script_text=text, re_pattern=pattern)
    assert isinstance(splits, list)


@pytest.mark.asyncio
async def test_create_screenplay_chunks(monkeypatch):
    # mock PyMuPDFLoader.aload
    class DummyDoc:
        page_content = "INT. ROOM\nScene text"

    class Loader:
        def __init__(self, file_path=None, mode=None):
            pass

        async def aload(self):
            return [DummyDoc()]

    monkeypatch.setattr("crud.screenplays.PyMuPDFLoader", Loader)

    result = await screenplays.create_screenplay_chunks(file_path="fake.pdf")
    assert "full_text" in result
    assert "scene_texts" in result


@pytest.mark.asyncio
async def test_create_screenplay_end_to_end(monkeypatch):
    # mock create_movie
    fake_movie = MagicMock()
    fake_movie.id = 99
    fake_movie.title = "Movie"
    monkeypatch.setattr("crud.screenplays.create_movie", AsyncMock(return_value=fake_movie))

    # mock create_screenplay_chunks
    monkeypatch.setattr("crud.screenplays.create_screenplay_chunks", AsyncMock(return_value={
        "full_text": "full",
        "scene_texts": [{"raw_text": "t", "embedding_text": "t"}]
    }))

    # mock create_scenes
    monkeypatch.setattr("crud.screenplays.create_scenes", AsyncMock())

    # fake session
    class FakeSession:
        def add(self, obj):
            pass

        def commit(self):
            pass

        def refresh(self, obj):
            obj.id = 123

    session = FakeSession()

    # run create_screenplay
    fake_mongo = MagicMock()
    fake_pinecone = MagicMock()

    result = await screenplays.create_screenplay(
        file_path="/tmp/fake.pdf",
        tmdb_id=1,
        session=session,
        async_client=AsyncMock(),
        ai_client=AsyncMock(),
        mongodb_database=fake_mongo,
        pinecone_client=fake_pinecone
    )
    assert result.id == 123
