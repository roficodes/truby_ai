import pytest
from unittest.mock import MagicMock

import crud.movies as movies


@pytest.mark.asyncio
async def test_fetch_tmdb_movie_success(monkeypatch):
    # Use MagicMock so .json() and .raise_for_status() are synchronous
    fake_response = MagicMock()
    fake_response.json.return_value = {"id": 1, "title": "Test"}
    fake_response.raise_for_status = lambda: None

    class FakeClient:
        async def get(self, url, headers=None, params=None):
            return fake_response

    result = await movies.fetch_tmdb_movie(1, FakeClient())
    assert result["id"] == 1


def test_tmdb_json_to_movie():
    tmdb_data = {
        "id": 1,
        "imdb_id": "tt123",
        "title": "Title",
        "overview": "Overview",
        "release_date": "2020-01-01",
        "vote_average": 7.5,
        "vote_count": 100
    }
    movie_record = movies.tmdb_json_to_movie(tmdb_data)
    assert movie_record.title == "Title"
    assert movie_record.tmdb_id == 1
