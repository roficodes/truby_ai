from pydantic import BaseModel

class SceneCreate(BaseModel):
    screenplay_id: int 
    scene_number: int
    progress_raw: str
    progress_num: float
    beat: str | None
    ai_summary: str | None 
    previous_scene_id: int | None 
    next_scene_id: int | None
    mongodb_record_id: str | None

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
    mongodb_record_id: str | None