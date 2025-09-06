from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint

class Movie(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("tmdb_id", name="uniqueConstraint_tmdb_id"),
    )
    id: int | None = Field(default=None, primary_key=True)
    tmdb_id: int = Field(...)
    imdb_id: str | None = Field(default=None)
    title: str = Field(...)
    overview: str = Field(...)
    release_date: str | None = Field(default=None)
    vote_average: float | None = Field(default=None)
    vote_count: int | None = Field(default=None)
    genre_ids: list[int] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

class Script(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    movie_id: int = Field(..., foreign_key="movie.id")
    authors: list[str] | None = Field(default=None)
    storage_path: str = Field(...)
    total_scenes: int | None = Field(default=None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

class Scene(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    script_id: int = Field(..., foreign_key="script.id")
    progress_raw: str = Field(...)
    progress_num: float = Field(...)
    beat: str | None = Field(default=None)
    ai_summary: str | None = Field(default=None)
    previous_scene_id: int | None = Field(default=None)
    next_scene_id: int | None = Field(default=None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    embedding: list[float] | None = Field(default=None)