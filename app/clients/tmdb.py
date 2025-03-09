import functools
import logging

import requests

from app.schemas.schemas import MovieInfo, TrendingMovie
from app.settings import settings

logger = logging.getLogger(__name__)


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.tmdb_api_key
        if not self.api_key:
            raise ValueError(
                "TMDB API Key is missing. Please set it in your environment variables."
            )

    def _make_request(self, endpoint: str, params: dict = None):
        if params is None:
            params = {}
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def search_movie(
        self, query: str, language: str = "en-US", page: int = 1
    ) -> MovieInfo:
        """
        Search for a movie by its title.
        """
        endpoint = "/search/movie"
        params = {"query": query, "language": language, "page": page}
        return MovieInfo(
            **self._make_request(endpoint, params)["results"][0]
        )  # always get the first result

    def get_trending_movies(self, language: str = "en-US", page: int = 1):
        """
        Get trending movies.
        """
        endpoint = "/trending/movie/day"
        params = {"language": language, "page": page}
        return TrendingMovie(
            trending_movies=[
                MovieInfo(**movie)
                for movie in self._make_request(endpoint, params)["results"]
            ]
        )

    @functools.lru_cache(maxsize=32)
    def get_genre_list(self, language: str = "en-US"):
        """
        Get the list of official genres for movies.

        Returns a dictionary mapping genre IDs to genre names.

        Args:
            language: Language code for the genre names (default: "en-US")

        Returns:
            dict: Dictionary with genre IDs as keys and genre names as values
        """
        endpoint = "/genre/movie/list"
        params = {"language": language}
        response = self._make_request(endpoint, params)

        # Create a mapping of genre_id to genre_name
        genre_mapping = {genre["id"]: genre["name"] for genre in response["genres"]}

        return genre_mapping

    def get_movie_genres(self, movie_info: MovieInfo) -> list[str]:
        """
        Get the genres of a movie by its name.

        Args:
            movie_info: The movie info to search for
            language: Language code for the results (default: "en-US")

        Returns:
            list[str]: List of genre names for the movie
        """
        try:
            genre_ids = movie_info.genre_ids
            genres = [
                self.get_genre_list().get(genre_id)
                for genre_id in genre_ids
                if genre_id in self.get_genre_list()
            ]

            return genres
        except Exception as e:
            logger.error(
                f"Error getting movie genres for '{movie_info.title}': {str(e)}"
            )
            return []


tmdb_client = TMDBClient()
