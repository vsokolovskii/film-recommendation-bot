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
    text: str = Field(..., description="The response to the question")
