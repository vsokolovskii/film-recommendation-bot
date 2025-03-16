import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.clients.sqlite import sqlite_client
from app.clients.tmdb import tmdb_client

logger = logging.getLogger(__name__)


def scrape_trending_movies(pages: int = 20):
    logger.info("Scraping trending movies")
    for page in range(1, pages + 1):
        trending_movies = tmdb_client.get_trending_movies(page=page)
        for movie in trending_movies.trending_movies:
            genres = tmdb_client.get_movie_genres(movie)
            sqlite_client.insert_movie(movie, genres)


scheduler = BackgroundScheduler()
# scrape immediately when the app starts
scheduler.add_job(scrape_trending_movies, "date", run_date=None)
# then run it every 7 days
scheduler.add_job(scrape_trending_movies, "interval", days=1)
