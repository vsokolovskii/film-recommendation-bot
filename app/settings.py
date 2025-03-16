from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings

APP_TITLE = "Movie Recommendation Assistant"


class Settings(BaseSettings):
    llm_host: AnyUrl
    llm_name: str = Field(default="llama3.2")
    llm_api_key: str = Field(default="ollama")
    tmdb_api_key: str = Field(default="")
    max_question_length: int = Field(default=512)
    embedding_model_name: str = Field(default="text-embedding-3-small")
    telegram_bot_token: str = Field(default="")


settings = Settings()
