from pydantic import BaseModel

class ScreenplayCreate(BaseModel):
    movie_id: int 
    storage_path: str
    text: str | None
    total_scenes: int | None

class ScreenplayRead(BaseModel):
    id: int | None
    movie_id: int | None
    tmdb_id: int | None
    imdb_id: int | None

class ScreenplayUpdate(BaseModel):
    # authors: list[str] | None
    total_scenes: int | None
