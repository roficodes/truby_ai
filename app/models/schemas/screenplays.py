from pydantic import BaseModel

class ScreenplayCreate(BaseModel):
    file_path: str
    tmdb_id: int

class ScreenplayRead(BaseModel):
    id: int | None
    movie_id: int | None
    tmdb_id: int | None
    imdb_id: int | None

class ScreenplayUpdate(BaseModel):
    authors: list[str] | None
    total_scenes: int | None
