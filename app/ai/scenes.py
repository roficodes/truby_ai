from typing import Literal
from openai import OpenAI
from pydantic import BaseModel
from ai.prompts.prompt_templates import SYSTEM_MESSAGE, ai_summary_beats_prompt
from core.config import LLM_MODEL


class SceneAnalysis(BaseModel):
    ai_summary: str
    story_beat: Literal["exposition", "inciting_incident", "rising_action", "climax", "falling_action", "resolution"]


def generate_scene_analysis(
    movie_name: str,
    scene_number: int,
    total_scenes: int,
    scene_text: str,
    previous_story_beat: str,
    ai_client: OpenAI
) -> str:
    full_prompt = ai_summary_beats_prompt(
        movie_name=movie_name,
        scene_number=scene_number,
        total_scenes=total_scenes,
        scene_text=scene_text,
        previous_story_beat=previous_story_beat
    )
    response = ai_client.responses.parse(
        model=LLM_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": full_prompt}
        ],
        text_format=SceneAnalysis
    )
    return response.output_parsed.model_dump_json()

# def generate_beat(
#     movie_name: str,
#     scene_progress: str,
#     previous_story_beat: str,
#     scene_text: str | None,
#     ai_client: OpenAI
# ):
#     full_prompt = BEAT_CREATION.format(
#         movie_name=movie_name,
#         scene_progress=scene_progress,
#         story_beats=return_story_beats(),
#         scene_text=scene_text or "",
#         previous_story_beat=previous_story_beat
#     )
#     response = ai_client.responses.create(
#         model=LLM_MODEL,
#         input=full_prompt,
#     )
#     return response.output_text


# def generate_ai_summary(
#     movie_name: str,
#     scene_number: int,
#     scene_progress: str,
#     previous_story_beat: str,
#     scene_text: str | None,
#     ai_client: OpenAI
# ) -> dict[str, str]:
#     full_prompt = AI_SUMMARY_1.format(movie_name=movie_name, scene_progress=scene_progress, scene_text=scene_text)
#     if scene_number != 1:
#         full_prompt = full_prompt + AI_SUMMARY_1_ENDING.format(previous_story_beat=previous_story_beat)
#     response = ai_client.responses.create(
#         model=LLM_MODEL,
#         input=full_prompt,
#     )
#     return response.output_text
