from typing import Any

def find_scenes_by_beat(
    beat: str
) -> list[dict[str, Any]]:
    """
    Fetch scenes from MongoDB by beat.

    Args:
        beat: story beat value
    
    Returns:
        A list of scenes.
    """
    return [{"foo": "bar"}]

def fetch_most_relevant_embeddings(
    user_query: str,
    candidate_scenes: list[str],
    top_k: int
) -> list[list[float]]:
    """
    Fetch most relevant embeddings based on user query.

    Args:
        user_query: user's query
        candidate_scenes: list of candidate scenes
        top_k: limit to the k most relevant embeddings
    
    Returns:
        Top k most relevant results from the candidate scenes.
    """
    return [[0.1]]