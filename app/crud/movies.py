import os
import httpx
from dotenv import load_dotenv
from sqlmodel import Session, select
from fastapi import HTTPException
from models.db.movies import Movie
from models.schemas.movies import MovieCreate, TMDBMovieModel

load_dotenv()

TMDB_READONLY_API_KEY = os.getenv("TMDB_READONLY_API_KEY")
TMDB_MOVIE_ENDPOINT_URL = "https://api.themoviedb.org/3"

async def fetch_tmdb_movie(tmdb_id: int, async_client: httpx.AsyncClient) -> dict:
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
    movie_record = session.exec(select(Movie).where(Movie.tmdb_id == tmdb_id)).first()
    if movie_record:
        raise HTTPException(status_code=400, detail="There is already a screenplay for this movie.")
    tmdb_response = await fetch_tmdb_movie(tmdb_id=tmdb_id, async_client=async_client)
    movie_record = tmdb_json_to_movie(tmdb_response=tmdb_response)
    session.add(movie_record)
    session.commit()
    session.refresh(movie_record)
    return movie_record