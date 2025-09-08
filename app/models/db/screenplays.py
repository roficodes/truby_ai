from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field

class Screenplay(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    movie_id: int = Field(..., foreign_key="movie.id")
    # TODO: create an author table and screenplay-author junction.
    # authors: list[str] | None = Field(default=None)
    storage_path: str = Field(...)
    text: str | None = Field(default=None)
    total_scenes: int | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )