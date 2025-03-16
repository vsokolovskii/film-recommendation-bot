import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from app.agent.agent import agent
from app.clients.scheduled_tasks import scheduler
from app.schemas.schemas import Question, Response
from app.settings import APP_TITLE
from app.bot.bot_core import bot

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title=APP_TITLE, lifespan=lifespan)

bot.infinity_polling()


@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/docs")


@app.post(
    "/question",
    response_model=Response,
    status_code=status.HTTP_200_OK,
    description="Takes a question text and returns an AI-generated response",
)
async def question(question: Question) -> Response:
    try:
        response = agent.run(question.text, reset=False)
        agent.write_memory_to_messages()
        return Response(text=response)
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate response",
        )
