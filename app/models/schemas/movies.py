"""Pydantic schemas for movie models used in API payloads.

Defines shape and validation for TMDB API responses and CRUD request/response
models for the Movie entity.
"""

from datetime import date
from pydantic import BaseModel, Field


class TMDBMovieModel(BaseModel):
    """Schema representing the JSON returned by TMDB for a movie.

    Attributes reflect the typical TMDB movie payload and include
    descriptive Field metadata used for validation and documentation.
    """

    id: int = Field(..., description="The Movie Database (TMDB) id")
    imdb_id: str | None = Field(default=None, description="IMDb id")
    title: str = Field(..., description="Movie's title")
    overview: str = Field(..., description="TMDB movie summary")
    release_date: date | None = Field(default=None, description="Movie's release date")
    vote_average: float | None = Field(default=None, description="User rating average")
    vote_count: int | None = Field(default=None, description="User vote count")


class MovieCreate(BaseModel):
    """Schema for creating a Movie record in the local database."""
    tmdb_id: int
    imdb_id: str
    title: str
    overview: str
    release_date: date
    vote_average: float
    vote_count: int


class MovieRead(BaseModel):
    """Minimal read schema for movie responses."""
    id: int | None
    tmdb_id: int | None
    imdb_id: int | None


class MovieUpdate(BaseModel):
    """Fields allowed when updating a Movie record."""
    screenplay_id: int | None
    imdb_id: str | None
    release_date: date | None 
    vote_average: float | None
    vote_count: int | None
