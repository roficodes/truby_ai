"""
class Scene(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    screenplay_id: int = Field(..., foreign_key="screenplay.id")
    scene_number: int = Field(...)
    progress_raw: str = Field(...)
    progress_num: float = Field(...)
    beat: str | None = Field(default=None)
    ai_summary: str | None = Field(default=None)
    previous_scene_id: int | None = Field(default=None)
    next_scene_id: int | None = Field(default=None)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
"""