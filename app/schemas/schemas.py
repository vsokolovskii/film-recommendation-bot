from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.settings import settings


class Question(BaseModel):
    text: str = Field(
        default="What is the answer to life, the universe, and everything?",
        description="The question to ask the LLM",
        max_length=settings.max_question_length,
        min_length=1,
    )


class Response(BaseModel):
    text: str = Field(..., description="The response text")


class UserPreferences(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    genre: str | None = Field(None, description="Preferred movie genre(s)")
    favourite_movies: List[str] | None = Field(
        None, description="List of favourite mentioned movies"
    )
    year_range: str | None = Field(
        None, description="Preferred year range (e.g., '1990-2000')"
    )
    rating_min: float | None = Field(
        None, description="Minimum rating threshold (0-10)"
    )


class MovieInfo(BaseModel):
    id: int = Field(..., description="The unique identifier of the movie")
    title: str = Field(..., description="The title of the movie")
    overview: str = Field(None, description="A short description of the movie")
    release_date: str = Field(
        None, description="The release date of the movie in format YYYY-MM-DD"
    )
    vote_average: float = Field(None, description="The average rating of the movie")
    vote_count: int = Field(None, description="The number of votes for the movie")
    poster_path: str = Field(
        None, description="The relative path to the movie poster image"
    )
    popularity: float = Field(None, description="The popularity score of the movie")
    genre_ids: list[int] = Field(
        None, description="List of genre IDs associated with the movie"
    )
    genres: list[str] = Field(
        None, description="List of genres associated with the movie"
    )
    video: bool = Field(None, description="Whether the movie has a video")


class TrendingMovie(BaseModel):
    trending_movies: List[MovieInfo] = Field(
        default_factory=list, description="List of trending movies"
    )


class MovieSearchResponse(BaseModel):
    page: int = Field(0, description="Current page number")
    results: List[MovieInfo] = Field(default_factory=list, description="List of movies")
    total_pages: int = Field(0, description="Total number of pages")
    total_results: int = Field(0, description="Total number of results")


class UserQuestion(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    text: str = Field(
        default="What is the answer to life, the universe, and everything?",
        description="The question to ask the LLM",
        max_length=settings.max_question_length,
        min_length=1,
    )


class PreferenceData(BaseModel):
    genre: List[str] | None = Field(
        default_factory=list, description="Preferred movie genre(s)"
    )
    favourite_movies: List[str] | None = Field(
        default_factory=list, description="List of favourite mentioned movies"
    )
    year_range: tuple[int, int] | None = Field(
        (1900, datetime.now().year),
        description="Preferred year range as a tuple of (start_year, end_year)",
    )
    rating_min: float | None = Field(None, description="Minimum rating threshold")


class UserPreferenceSchema(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    preferences: PreferenceData = Field(
        ..., description="Object containing preference data"
    )


class MovieData(BaseModel):
    movie_id: int | None = Field(None, description="TMDB movie ID (if available)")
    title: str = Field(..., description="Movie title")
    rating: int | None = Field(None, description="User rating (1-10)")
    year: str | None = Field(None, description="Release year")
    director: str | None = Field(None, description="Movie director")
    genres: List[str] | None = Field(None, description="List of movie genres")


class LikedMovieSchema(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    movie_data: MovieData = Field(..., description="Object containing movie data")


class MovieRecommendationSchema(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    limit: int = Field(5, description="Maximum number of recommendations to return")


class MovieInfoSchema(BaseModel):
    movie_name: str = Field(
        ..., description="The name of the movie to fetch information about"
    )


class UserPreferencesSchema(BaseModel):
    user_id: str = Field("1", description="The unique identifier for the user")


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    error: str | None = Field(None)


class UserPreferencesResponse(BaseModel):
    genre: str | None = None
    favourite_movies: str | None = None
    year_range: str | None = None
    rating_min: float | None = None
    embedding: List[float] | None = None
    message: str | None = None
    error: str | None = None
