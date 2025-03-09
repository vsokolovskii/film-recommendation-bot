import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.agent.agent import PreferenceData

logger = logging.getLogger(__name__)


class SQLiteClient:
    """Client for interacting with SQLite database to store user film preferences."""

    def __init__(self, db_path: str = "user_preferences.db"):
        """
        Initialize the SQLite client.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        # Flag to track if tables need to be recreated
        self.tables_dropped = False
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_db(self) -> None:
        """Initialize the database with required tables if they don't exist."""
        try:
            # Ensure the directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            conn = self._get_connection()
            cursor = conn.cursor()

            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Create preferences table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                genre TEXT,
                favourite_movies TEXT,
                preference_text TEXT,
                year_range TEXT,
                rating_min REAL,
                embedding TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            # Create watched_movies table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS watched_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                rating INTEGER,
                watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            # Create movie_embeddings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_embeddings (
                movie_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                embedding TEXT NOT NULL,
                genre_ids TEXT,
                overview TEXT,
                release_date TEXT,
                vote_average REAL,
                popularity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Add default user with user_id 1 if it doesn't exist
            cursor.execute("SELECT id FROM users WHERE user_id = '1'")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (user_id) VALUES ('1')")
                logger.info("Created default user with user_id 1")

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")

    def create_user(self, user_id: str) -> bool:
        """
        Create a new user if it doesn't exist.

        Args:
            user_id: Unique identifier for the user

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone() is None:
                # Create new user
                cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False

    def update_preferences(
        self,
        user_id: str,
        preferences: PreferenceData,
        preference_text: str,
        embedding: Optional[List[float]] = None,
    ) -> bool:
        """
        Update user preferences.

        Args:
            user_id: Unique identifier for the user
            preferences: Dictionary containing preference data
            embedding: Optional embedding vector for the preferences

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure user exists
            self.create_user(user_id)

            conn = self._get_connection()
            cursor = conn.cursor()

            # Check if preferences exist
            cursor.execute("SELECT id FROM preferences WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()

            # Convert embedding to JSON string if provided
            embedding_json = json.dumps(embedding) if embedding else None

            if existing:
                # Update existing preferences
                cursor.execute(
                    """
                    UPDATE preferences 
                    SET genre = ?, favourite_movies = ?, preference_text = ?, year_range = ?, rating_min = ?, embedding = ?, 
                        last_updated = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                    """,
                    (
                        ",".join(preferences.genre),
                        ";".join(preferences.favourite_movies)
                        if preferences.favourite_movies
                        else None,
                        preference_text,
                        f"{preferences.year_range[0]}-{preferences.year_range[1]}"
                        if preferences.year_range
                        else None,
                        preferences.rating_min,
                        embedding_json,
                        user_id,
                    ),
                )
            else:
                # Insert new preferences
                cursor.execute(
                    """
                    INSERT INTO preferences 
                    (user_id, genre, favourite_movies, preference_text, year_range, rating_min, embedding) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        ",".join(preferences.genre),
                        ";".join(preferences.favourite_movies)
                        if preferences.favourite_movies
                        else None,
                        preference_text,
                        f"{preferences.year_range[0]}-{preferences.year_range[1]}"
                        if preferences.year_range
                        else None,
                        preferences.rating_min,
                        embedding_json,
                    ),
                )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return False

    def get_preferences(
        self, user_id: str, include_embedding: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get user preferences.

        Args:
            user_id: Unique identifier for the user
            include_embedding: Whether to include the embedding in the result

        Returns:
            Optional[Dict[str, Any]]: User preferences or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if include_embedding:
                cursor.execute(
                    "SELECT genre, favourite_movies, year_range, rating_min, embedding FROM preferences WHERE user_id = ?",
                    (user_id,),
                )
            else:
                cursor.execute(
                    "SELECT genre, favourite_movies, year_range, rating_min FROM preferences WHERE user_id = ?",
                    (user_id,),
                )

            result = cursor.fetchone()
            conn.close()

            if result:
                if include_embedding:
                    preferences = {
                        "user_id": user_id,
                        "genre": result[0],
                        "favourite_movies": result[1],
                        "year_range": result[2],
                        "rating_min": result[3],
                    }

                    # Parse embedding if it exists
                    if result[4]:
                        preferences["embedding"] = json.loads(result[4])

                    return preferences
                else:
                    return {
                        "user_id": user_id,
                        "genre": result[0],
                        "favourite_movies": result[1],
                        "year_range": result[2],
                        "rating_min": result[3],
                    }

            return None
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            return None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            float: Cosine similarity (-1 to 1)
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Create a singleton instance
sqlite_client = SQLiteClient()
