"""Database initialization and session helpers.

This module is responsible for creating the SQLAlchemy/SQLModel engine
and providing helper functions for initializing the database schema and
obtaining sessions for use by request handlers and CRUD operations.

Functions:
    init_db(): Create database tables defined by SQLModel metadata.
    get_session(): Generator that yields a SQLModel Session for dependency injection.
"""

import os
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from dotenv import load_dotenv
from models.db import Movie, Screenplay, Scene, SceneEmbedding

load_dotenv()

DATABASE_URL = f"sqlite:///{os.getenv('SQL_DB_PATH')}"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def init_db():
    """Create all tables in the database.

    Uses SQLModel.metadata to create tables for all declared models
    bound to the configured engine.

    Returns:
        None
    """

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for use with dependency injection.

    Yields:
        Session: A SQLModel Session instance.
    """

    with Session(engine) as session:
        yield session