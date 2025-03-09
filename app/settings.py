from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings

APP_TITLE = "LLMChat Veeam"


class Settings(BaseSettings):
    llm_host: AnyUrl
    llm_name: str = Field(default="llama3.2")
    llm_api_key: str = Field(default="ollama")

    max_question_length: int = Field(default=512)


settings = Settings()
