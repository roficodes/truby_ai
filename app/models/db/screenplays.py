"""Database models for screenplay entities.

Declares the Screenplay table which stores references to a movie and the
original screenplay text along with timestamps.
"""

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field, Relationship
from models.db.movies import Movie
from models.db.scenes import Scene


class Screenplay(SQLModel, table=True):
    """SQLModel representing a screenplay record.

    Fields:
        id (int): Primary key.
        movie_id (int): Foreign key to the movies table.
        storage_path (str): Filesystem path to the screenplay file.
        text (str | None): Full screenplay text if stored in DB.
        total_scenes (int | None): Cached count of scenes.
    """

    id: int | None = Field(default=None, primary_key=True)
    # TODO: create an author table and screenplay-author junction.
    storage_path: str = Field(...)
    text: str | None = Field(default=None)
    total_scenes: int | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    scene: list["Scene"] = Relationship(
        cascade_delete=True
    )

    movie: Movie = Relationship(
        cascade_delete=True
    )