"""Database models for movie entities.

This module defines the SQLModel-backed Movie table used to persist
basic metadata about movies sourced from TMDB/IMDb.
"""

from datetime import datetime, date
from sqlalchemy import Column
from sqlalchemy.types import DateTime, Date
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field, UniqueConstraint


class Movie(SQLModel, table=True):
    """SQLModel representing a movie record.

    Attributes correspond to columns in the movies table. Unique
    constraints are declared to avoid duplicate TMDB/IMDb entries.
    """

    __table_args__ = (
        UniqueConstraint("tmdb_id", name="uniqueConstraint_tmdb_id"),
        UniqueConstraint("imdb_id", name="uniqueConstraint_imdb_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    tmdb_id: int = Field(...)
    imdb_id: str | None = Field(default=None)
    screenplay_id: int | None = Field(default=None, foreign_key="screenplay.id", ondelete="CASCADE")
    title: str = Field(...)
    overview: str = Field(...)
    release_date: date | None = Field(default=None, sa_column=Column(Date))
    vote_average: float | None = Field(default=None)
    vote_count: int | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
