from datetime import date
from pydantic import BaseModel, Field

class TMDBMovieModel(BaseModel):
    id: int = Field(..., description="The Movie Database (TMDB) id")
    imdb_id: str | None = Field(default=None, description="IMDb id")
    title: str = Field(..., description="Movie's title")
    overview: str = Field(..., description="TMDB movie summary")
    release_date: date | None = Field(default=None, description="Movie's release date")
    vote_average: float | None = Field(default=None, description="User rating average")
    vote_count: int | None = Field(default=None, description="User vote count")

class MovieCreate(BaseModel):
    tmdb_id: int
    imdb_id: str
    title: str
    overview: str
    release_date: date
    vote_average: float
    vote_count: int


class MovieRead(BaseModel):
    id: int | None
    tmdb_id: int | None
    imdb_id: int | None


class MovieUpdate(BaseModel):
    imdb_id: str | None
    release_date: date | None 
    vote_average: float | None
    vote_count: int | None
    # genre_ids: list[int] | None
