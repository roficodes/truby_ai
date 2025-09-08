from pydantic import BaseModel

class SceneCreate(BaseModel):
    pass

class SceneRead(BaseModel):
    id: int | None
    movie_id: int | None
    tmdb_id: int | None
    imdb_id: int | None
    screenplay_id: int | None
    scene_number: int | None

class SceneUpdate(BaseModel):
    beat: str | None
    ai_summary: str | None
    previous_scene_id: int | None
    next_scene_id: int | None