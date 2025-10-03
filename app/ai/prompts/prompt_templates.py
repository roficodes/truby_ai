"""Prompt templates and helper structures for AI scene analysis.

This module defines system messages, prompt constructions, and mappings
between story beat labels and human-readable descriptions used by the
AI prompt builders.
"""

from dataclasses import dataclass

SYSTEM_MESSAGE = """You are an expert in film analysis, screenwriting, and storytelling craft. You explain scenes with the precision of a story analyst, not just plot summary. Always focus on how the writing choices shape the story, character, and audience experience.""".strip()

# SYSTEM_MESSAGE = """
# You are an expert in film, screenwriting, and story analysis. Your task is to analyze screenplay scenes and determine the story beat and provide a concise summary. Always output a valid JSON object with no additional commentary.
# """.strip()

@dataclass(frozen=True)
class StoryBeat:
    label: str
    description: str

#TODO: Might be a good idea to use Enum here?
index_to_beat_lookup = {
    0: StoryBeat("exposition", """Beginning. The opening information that establishes the world, characters, and circumstances. In screenwriting, this should be woven naturally into action and dialogue rather than delivered through obvious information dumps. Shows the "normal world" before the story's main conflict begins."""),
    1: StoryBeat("inciting_incident", "Early in the story, after exposition. The central problem or opposing force that drives the story forward. This creates dramatic tension and gives characters obstacles to overcome. Can be internal (character vs. self), interpersonal (character vs. character), or external (character vs. environment/society/fate)."),
    2: StoryBeat("rising_action", "Middle portion, building from inciting incident. The series of escalating events and complications that build tension toward the climax. Each scene should raise the stakes and deepen the conflict. Characters face increasingly difficult challenges that test their resolve and force them to make harder choices."),
    3: StoryBeat("climax", "Peak of the story. Result of the rising action, typically in the third act. The story's most intense moment where the main conflict reaches its peak; the turning point where the protagonist faces their greatest challenge and the outcome of the central conflict is determined. Everything in the story has been building to this moment."),
    4: StoryBeat("falling_action", "End of the story. Immediately after the climax. The events that occur after the climax, showing the immediate consequences of the climactic moment. Loose ends begin to be tied up, and the story moves toward its conclusion. Often brief in screenwriting compared to other forms."),
    5: StoryBeat("resolution", "The final outcome where conflicts are resolved and the story concludes. Shows how the characters and their world have changed as a result of the story's events. Provides closure and answers the story's central dramatic question."),
}
beat_to_index_lookup = {v.label: (k, v.description) for k, v in index_to_beat_lookup.items()}

partial_prompt_template = """
You're familiar with the movie "{movie_name}" and its plot. Here is a scene from its screenplay:

<START SCENE CONTEXT>
{scene_text}
<END SCENE CONTEXT>

Do the following:

1. Summarize the scene in three to five sentences.
2. Explain how this scene moves the plot of the movie "{movie_name}" forward.
3. Analyze the craft of the scene and how this scene functions for screenwriting and storytelling.
4. Note that the story beat corresponding to this scene is "{previous_story_beat}", defined as "{previous_story_beat_description}". 

Output Instructions

Your output must be a JSON with two keys: "ai_summary" and "story_beat". Only output the JSON file, with no commentary, no disclaimers, no Markdown syntax, and so forth. Here are further instructions on each JSON field.

{{
    "ai_summary": <Your summary and analysis goes here. Keep your response brief: no more than two to three paragraphs.>,
    "story_beat": <hardcode to "{previous_story_beat}">
}}
""".strip()

full_prompt_template = """
You're familiar with the movie "{movie_name}" and its plot. Here is a scene from its screenplay:

<START SCENE CONTEXT>
{scene_text}
<END SCENE CONTEXT>

Do the following:

Part I: Create an AI summary.

1. Summarize the scene in three to five sentences.
2. Explain how this scene moves the plot of the movie "{movie_name}" forward.
3. Analyze the craft of the scene and how this scene functions for screenwriting and storytelling.

Part II: Determine the story beat.

You're analyzing scene number {scene_number} out of {total_scenes} total scenes; the previous scene was labeled "{previous_story_beat}". Based on the text from the screenplay and your analysis in Part I, do you think the scene you read continues the story beat "{previous_story_beat}" or do you think this scene moves the story into the next story beat "{next_story_beat}". Here is a definition for each story beat in case you need help:

- "{previous_story_beat}" - {previous_story_beat_description}
- "{next_story_beat}" - {next_story_beat_description}

Output Instructions

Your output must be a JSON with two keys: "ai_summary" and "story_beat". Only output the JSON file, with no commentary, no disclaimers, no Markdown syntax, and so forth. Here are further instructions on each JSON field.

{{
    "ai_summary": <your analysis from Part I should be here. Keep your response brief: no more than two to three paragraphs.>,
    "story_beat": <only include the story beat label that you think belongs here: either "{previous_story_beat}" or "{next_story_beat}">
}}
""".strip()

def ai_summary_beats_prompt(
    movie_name: str,
    scene_number: int,
    total_scenes: int,
    scene_text: str,
    previous_story_beat: str | None,
) -> str:
    if previous_story_beat is None or scene_number == 1:
        return partial_prompt_template.format(
            movie_name=movie_name,
            scene_text=scene_text,
            previous_story_beat="exposition",
            previous_story_beat_description=beat_to_index_lookup["exposition"][1]
        )
    elif previous_story_beat == "resolution" or scene_number == total_scenes:
        return partial_prompt_template.format(
            movie_name=movie_name,
            scene_text=scene_text,
            previous_story_beat="resolution",
            previous_story_beat_description=beat_to_index_lookup["resolution"][1]
        )
    else:
        previous_story_beat_index, previous_story_beat_description = beat_to_index_lookup[previous_story_beat.lower()]
        next_story_beat_index = min(previous_story_beat_index+1, 5)
        next_story_beat = index_to_beat_lookup[next_story_beat_index]
        _, next_story_beat_description = beat_to_index_lookup[next_story_beat.label]
        return full_prompt_template.format(
            movie_name=movie_name,
            scene_number=scene_number,
            total_scenes=total_scenes,
            scene_text=scene_text,
            previous_story_beat=previous_story_beat,
            previous_story_beat_description=previous_story_beat_description,
            next_story_beat=next_story_beat,
            next_story_beat_description=next_story_beat_description
        )
    