from openai import OpenAI
from ai.prompts.prompt_templates import AI_SUMMARY_1, AI_SUMMARY_1_ENDING, BEAT_CREATION, return_story_beats
from core.config import LLM_MODEL

def generate_beat(
    movie_name: str,
    scene_progress: str,
    previous_story_beat: str,
    scene_text: str | None,
    ai_client: OpenAI
):
    full_prompt = BEAT_CREATION.format(
        movie_name=movie_name,
        scene_progress=scene_progress,
        story_beats=return_story_beats(),
        scene_text=scene_text or "",
        previous_story_beat=previous_story_beat
    )
    response = ai_client.responses.create(
        model=LLM_MODEL,
        input=full_prompt,
    )
    return response.output_text


def generate_ai_summary(
    movie_name: str,
    scene_number: int,
    scene_progress: str,
    previous_story_beat: str,
    scene_text: str | None,
    ai_client: OpenAI
) -> dict[str, str]:
    full_prompt = AI_SUMMARY_1.format(movie_name=movie_name, scene_progress=scene_progress, scene_text=scene_text)
    if scene_number != 1:
        full_prompt = full_prompt + AI_SUMMARY_1_ENDING.format(previous_story_beat=previous_story_beat)
    response = ai_client.responses.create(
        model=LLM_MODEL,
        input=full_prompt,
    )
    return response.output_text
