import os
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from dotenv import load_dotenv
from models.db import Movie, Screenplay, Scene, SceneEmbedding

load_dotenv()

DATABASE_URL = f"sqlite:///{os.getenv('SQL_DB_PATH')}"
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session