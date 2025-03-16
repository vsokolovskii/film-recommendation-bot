from typing import Any, Dict

import numpy as np
from smolagents import LiteLLMModel

from app.agent.templates import get_movie_prompt_templates
from app.schemas.schemas import (
    PreferenceData,
    UserPreferencesResponse,
)
from app.settings import settings

model = LiteLLMModel(
    model_id=settings.llm_name,
    api_key=settings.llm_api_key,
)

import logging

from smolagents import tool
from smolagents.agents import ToolCallingAgent

from app.clients.openai import openai_client
from app.clients.sqlite import sqlite_client
from app.clients.tmdb import tmdb_client

logger = logging.getLogger(__name__)


# Define tools
@tool
def store_user_preference(user_id: str, preferences: PreferenceData) -> str:
    """
    After the model has asked the user about their movie preferences, store the preferences in the database.
    Derive the names of the favourite movies from the chat with the user. Derive the genre of the movies from their names.

    Args:
        user_id: Unique identifier for the user
        preferences:
            - genre: List[str] | None = Field(None, description="Preferred movie genre(s)")
            - favourite_movies: List[str] | None = Field(
                None, description="List of favourite mentioned movies"
            )
            - year_range: tuple[int, int] | None = Field(
                (1900, datetime.now().year),
                description="Preferred year range as a tuple of (start_year, end_year)",
            )
            - rating_min: float | None = Field(None, description="Minimum rating threshold")

    Returns:
        str: Success message or error
    """

    preferences = PreferenceData(
        **preferences
    )  # smolagents doesn't support Pydantic models natively
    try:
        preference_text = ""
        for movie in preferences.favourite_movies:
            movie_details = tmdb_client.search_movie(movie)

            if preferences.genre is None:
                preferences.genre = []

            # Get movie genres and add them to preferences
            movie_genres = tmdb_client.get_movie_genres(movie_details)

            if movie_genres:
                preferences.genre.extend(movie_genres)
            if movie_details:
                preference_text += f"{movie_details.overview}.\n\n"

        # Split movie overviews and embed each independently
        if preference_text:
            # Split the text by double newlines and filter out empty strings
            movie_overviews = [
                overview
                for overview in preference_text.strip().split("\n\n")
                if overview
            ]

            if movie_overviews:
                # Get embeddings for non-empty overviews
                overview_embeddings = [
                    openai_client.get_embedding(overview)
                    for overview in movie_overviews
                ]

                if overview_embeddings:
                    # Convert to numpy arrays and calculate the average embedding
                    overview_embeddings_array = np.array(overview_embeddings)
                    embedding = np.mean(overview_embeddings_array, axis=0).tolist()

        embedding = openai_client.get_embedding(preference_text)

        success = sqlite_client.update_preferences(
            user_id, preferences, preference_text, embedding
        )

        if success:
            return f"Successfully stored preferences for user {user_id}."
        else:
            return f"Failed to store preferences for user {user_id}."
    except Exception as e:
        logger.error(f"Error storing user preference: {str(e)}")
        return f"Error storing user preference: {str(e)}"


@tool
def get_user_preferences(user_id: str = "1") -> Dict[str, Any]:
    """
    Retrieves a user's movie preferences from the database.

    Args:
        user_id: The unique identifier for the user. Defaults to "1".

    Returns:
        Dict[str, Any]: A dictionary containing the user's preferences (genre, favourite_movies, year_range, rating_min) or an empty dictionary if no preferences are found.
    """
    try:
        # Validate input with Pydantic
        preferences = sqlite_client.get_preferences(user_id, include_embedding=True)

        if preferences is None:
            # Handle the case when no preferences are found
            response = UserPreferencesResponse(
                error="No preferences found for this user"
            )
        else:
            response = UserPreferencesResponse(**preferences)

        return response.model_dump()
    except Exception as e:
        logger.error(f"Error retrieving user preferences: {str(e)}")
        response = UserPreferencesResponse(
            error=f"Failed to retrieve preferences: {str(e)}"
        )
        return response.model_dump()


@tool
def suggest_movies(
    user_id: str = "1", genres: list[str] = None, year_range: tuple = None
) -> Dict[str, Any]:
    """
    Suggest movies to the user based on their preferences. Derive the genres and year range from the user's preferences.

    Args:
        user_id: The unique identifier for the user. Defaults to "1"
        genres: List[str] | None = Field(None, description="Preferred movie genre(s)")
        year_range: tuple[int, int] | None = Field(
            (1900, datetime.now().year),
            description="Preferred year range as a tuple of (start_year, end_year)",
        )

    Returns:
        Dict[str, Any]: A dictionary containing the suggested movies.
    """
    # Get user preferences
    preferences = get_user_preferences(user_id)
    # Get trending movies
    trending_movies = sqlite_client.get_most_similar_movies(
        preferences, limit=5, genres=genres, year_range=year_range
    )

    return trending_movies


tools = [
    get_user_preferences,
    store_user_preference,
    suggest_movies,
]

# Create the agent
agent = ToolCallingAgent(
    tools=tools,
    model=model,
)


# If you want to use the ToolCallingAgent instead, uncomment the following lines as they both will work

agent = ToolCallingAgent(
    tools=tools,
    model=model,
    prompt_templates=get_movie_prompt_templates(),
)
