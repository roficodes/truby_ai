SYSTEM_MESSAGE = """You are an expert in film analysis, screenwriting, and storytelling craft. You explain scenes with the precision of a story analyst, not just plot summary. Always focus on how the writing choices shape the story, character, and audience experience.""".strip()

story_beats = {
    "EXPOSITION": """Beginning. The opening information that establishes the world, characters, and circumstances. In screenwriting, this should be woven naturally into action and dialogue rather than delivered through obvious information dumps. Shows the "normal world" before the story's main conflict begins.""",
    "CONFLICT": "Early in the story, after exposition. The central problem or opposing force that drives the story forward. This creates dramatic tension and gives characters obstacles to overcome. Can be internal (character vs. self), interpersonal (character vs. character), or external (character vs. environment/society/fate).",
    "RISING_ACTION": "Middle portion, building from conflict. The series of escalating events and complications that build tension toward the climax. Each scene should raise the stakes and deepen the conflict. Characters face increasingly difficult challenges that test their resolve and force them to make harder choices.",
    "CLIMAX": "Peak of the story, typically in the third act. The story's most intense moment where the main conflict reaches its peak. This is the turning point where the protagonist faces their greatest challenge and the outcome of the central conflict is determined. Everything in the story has been building to this moment.",
    "FALLING_ACTION": "End of the story. Immediately after the climax. The events that occur after the climax, showing the immediate consequences of the climactic moment. Loose ends begin to be tied up, and the story moves toward its conclusion. Often brief in screenwriting compared to other forms.",
    "RESOLUTION": "The final outcome where conflicts are resolved and the story concludes. Shows how the characters and their world have changed as a result of the story's events. Provides closure and answers the story's central dramatic question.",
}

def return_story_beats(beats: dict = story_beats) -> str:
    beat_description = ""
    story_beats = []
    for k, v in beats.items():
        story_beats.append(k.lower())
        beat_description += k + ": " + v + "\n"
    full_string = f"""Here are the possible story beat values: {story_beats}. Here is a description of what they mean and where in the sequence the story beats may occur:\n{beat_description}
    """.strip()
    return full_string


BEAT_CREATION = """
You are analyzing an excerpt from the screenplay "{movie_name}". This is scene number {scene_progress}. 

<START OF EXCERPT>
{scene_text}
<END OF EXCERPT>

Based on this excerpt and your knowledge of the movie, which of the following story beats does this scene fall under? Here are your choices:

{story_beats}

Your output value can only be either equal to or immediately greater than this story beat. For example, if the previous beat is "Exposition", then your story beat choice for this one can't be Climax. It must either be Exposition or Conflict. If the previous beat was "Conflict", then your story beat choice for this one can only be either Conflict or the next greatest value RISING_ACTION. This should make sense to you because you won't jump from skip one story beat from one to another; that's not how storytelling and screenplays work.

Keep in mind where we are in the story as far as scene number is concerned. Only return one value from the list. Here is the value from the previous story beat: {previous_story_beat}. 

Only output the single word value of the story beat you choose. Do not include any other text or punctuation. Do not include any explanation or reasoning. Do not include any quotes. Just return the single word value. Super critical: if you're unsure, simply return the previous story beat ({previous_story_beat}) rather than making a guess.
""".strip()

AI_SUMMARY_1 = """
You are analyzing an excerpt from the screenplay "{movie_name}". This is scene number {scene_progress}. Keep your answer analytical, specific, and written for a professional screenwriter audience. Your entire response should be no more than two paragraphs. Avoid generic praise.

<START OF EXCERPT>
{scene_text}
<END OF EXCERPT>

1. Summarize the key events of the scene in 2–3 sentences.  
2. Comment on the writing craft:
    - How the scene conveys subtext or hidden meaning.
    - How atmosphere, pacing, and character choices drive the scene.  
    - Any notable use of dialogue, action lines, or structure.  
3. Reflect on what a screenwriter could *learn* from how this scene is written.  
""".strip()

AI_SUMMARY_1_ENDING = """\n
4. Identify the story beat or beats this scene fulfills (e.g., setup, inciting incident, midpoint, confrontation, reversal, climax).  
5. The previous beat of this story was {previous_story_beat}. Explain how the scene builds on or contrasts with the **previous beat** of the story.  
6. Keep in mind where we are in the story as far as scene number is concerned.""".strip()
