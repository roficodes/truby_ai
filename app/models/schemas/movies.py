from datetime import datetime
from pydantic import BaseModel

class MovieCreate(BaseModel):
    tmdb_id: int


class MovieRead(BaseModel):
    id: int | None
    tmdb_id: int | None
    imdb_id: int | None


class MovieUpdate(BaseModel):
    imdb_id: str | None
    release_date: datetime | None 
    vote_average: float | None
    vote_count: int | None
    genre_ids: list[int] | None
