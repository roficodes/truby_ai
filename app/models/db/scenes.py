"""Database models for scene and embedding entities.

This module defines the Scene table for per-screenplay scene metadata and
a SceneEmbedding helper table to track embeddings stored externally.
"""

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlmodel import SQLModel, Field


class Scene(SQLModel, table=True):
    """SQLModel representing a single scene in a screenplay.

    Attributes include ordering metadata, brief analysis fields, and
    references to any external persistence (e.g. MongoDB record id).
    """

    id: int | None = Field(default=None, primary_key=True)
    screenplay_id: int = Field(..., foreign_key="screenplay.id")
    scene_number: int = Field(...)
    progress_raw: str = Field(...)
    progress_num: float = Field(...)
    beat: str | None = Field(default=None)
    ai_summary: str | None = Field(default=None)
    previous_scene_id: int | None = Field(default=None)
    next_scene_id: int | None = Field(default=None)
    mongodb_record_id: str | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )


class SceneEmbedding(SQLModel, table=True):
    """SQLModel used to track embedding metadata for a scene.

    This table stores minimal references to externally stored embeddings.
    """

    id: int | None = Field(default=None, primary_key=True)
    scene_id: int = Field(..., foreign_key="scene.id")
    mongo_id: str | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )