"""CRUD helpers for movie-related operations.

This module contains utilities to fetch movie data from The Movie Database
(TMDB), convert TMDB JSON responses into local `Movie` records, and create
movie records in the application's SQL database.

Environment variables
    TMDB_READONLY_API_KEY: API key used to authenticate TMDB read requests.

Note: This file intentionally only adds docstrings; no logic or behavior is
modified.
"""

import os
import httpx
from typing import Any
from dotenv import load_dotenv
from sqlmodel import Session, select
from fastapi import HTTPException
from models.db.movies import Movie
from models.schemas.movies import MovieCreate, TMDBMovieModel
from models.db.scenes import Scene

load_dotenv()

TMDB_READONLY_API_KEY = os.getenv("TMDB_READONLY_API_KEY")
TMDB_MOVIE_ENDPOINT_URL = "https://api.themoviedb.org/3/movie"

async def fetch_tmdb_movie(tmdb_id: int, async_client: httpx.AsyncClient) -> dict:
    """Fetch a movie record from TMDB by TMDB ID.

    Args:
        tmdb_id: The TMDB numeric identifier for the movie.
        async_client: An instance of `httpx.AsyncClient` used to perform the
            request.

    Returns:
        The parsed JSON response from TMDB as a Python dictionary.

    Raises:
        HTTPException: Re-raised when the TMDB API returns a non-2xx status.
    """
    try:
        movie_response = await async_client.get(
            url=f"{TMDB_MOVIE_ENDPOINT_URL}/{tmdb_id}",
            headers={"Authorization": TMDB_READONLY_API_KEY},
            params={"language": "en-US"}
        )
        movie_response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"TMDB API returned an error for movie ID {tmdb_id}"
        )
    return movie_response.json()

def tmdb_json_to_movie(tmdb_response: dict) -> Movie:
    """Convert a TMDB JSON response into a `Movie` SQL model instance.

    Args:
        tmdb_response: Raw JSON dictionary returned by the TMDB API for a
            single movie.

    Returns:
        A `Movie` instance populated from the TMDB response. The returned
        object is not persisted to the database; call site must add/commit it
        to a `Session`.
    """
    tmdb_movie_model = TMDBMovieModel(**tmdb_response)
    movie_create_model = MovieCreate(
        tmdb_id=tmdb_movie_model.id,
        imdb_id=tmdb_movie_model.imdb_id,
        title=tmdb_movie_model.title,
        overview=tmdb_movie_model.overview,
        release_date=tmdb_movie_model.release_date,
        vote_average=tmdb_movie_model.vote_average,
        vote_count=tmdb_movie_model.vote_count
    )
    movie_record = Movie(**movie_create_model.model_dump())
    return movie_record

async def create_movie(
    tmdb_id: int,
    async_client: httpx.AsyncClient,
    session: Session
) -> Movie:
    """Create and persist a new `Movie` record from TMDB data.

    This function checks whether a `Movie` with the given TMDB ID already
    exists in the provided `Session`. If not, it fetches the data from TMDB,
    converts it into a `Movie` instance and persists it.

    Args:
        tmdb_id: The TMDB identifier for the movie to create.
        async_client: An `httpx.AsyncClient` used to fetch TMDB data.
        session: A SQLModel/SQLAlchemy `Session` used to query and persist the
            `Movie` record.

    Returns:
        The newly created and refreshed `Movie` instance.

    Raises:
        HTTPException: If a movie with the same TMDB ID already exists (400),
            or if the TMDB API returns an error while fetching the movie.
    """
    movie_record = session.exec(select(Movie).where(Movie.tmdb_id == tmdb_id)).first()
    if movie_record:
        raise HTTPException(status_code=400, detail="There is already a screenplay for this movie.")
    tmdb_response = await fetch_tmdb_movie(tmdb_id=tmdb_id, async_client=async_client)
    movie_record = tmdb_json_to_movie(tmdb_response=tmdb_response)
    session.add(movie_record)
    session.commit()
    session.refresh(movie_record)
    return movie_record

def get_movie(
    screenplay_id: int,
    session: Session
) -> dict[str, Any]:
    """Retrieve movie based on the screenplay ID.
    
    Args:
        screenplay_id: ID of the screenplay to retrieve scenes for.
        session: SQLModel/SQLAlchemy session used for DB operations.
    
    Returns:
        dict: A payload containing the movie details.
    
    Raises:
        ValueError: If no movie is found for the given screenplay ID.
    """
    movie_stmt = select(Movie).where(Movie.screenplay_id == screenplay_id)
    results = session.exec(movie_stmt).first()
    if results:
        return {"movie": results}
    else:
        raise ValueError(f"No movie found for screenplay ID {screenplay_id}.")