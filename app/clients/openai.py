from openai import InternalServerError, OpenAI, RateLimitError
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import ChatCompletion
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.settings import settings

USER_ROLE = "user"
SYSTEM_ROLE = "system"
SYSTEM_PROMPT = (
    "You have to mimic the supercomputer from the famous book 'The Hitchhiker's Guide to the Galaxy'."  # noqa: E501
    "Respond to all user's questions with the same tone and style as in the book. Stay in character."  # noqa: E501
    "Answer short and concise."
)


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=f"{str(settings.llm_host)}",  # pydantic adds trailing slash
            api_key=settings.llm_api_key,  # required, but unused
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(exp_base=1.5, multiplier=1),
        retry=retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(InternalServerError),
        reraise=True,
    )
    async def generate_response(self, question: str) -> str:
        system_prompt = ChatCompletionSystemMessageParam(
            role=SYSTEM_ROLE, content=SYSTEM_PROMPT
        )
        message: ChatCompletionMessageParam = ChatCompletionUserMessageParam(
            role=USER_ROLE, content=question
        )
        response: ChatCompletion = await self.client.chat.completions.create(
            model=settings.llm_name,
            messages=[system_prompt, message],
        )
        return response.choices[0].message.content

    def get_embedding(self, text: str) -> list[float]:
        response: ChatCompletion = self.client.embeddings.create(
            model=settings.embedding_model_name, input=text
        )
        return response.data[0].embedding


openai_client = OpenAIClient()
