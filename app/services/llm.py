import asyncio

from openai import AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = "Answer the question based only on the provided context. If the context does not contain enough information, say so."


def _make_client() -> tuple[AsyncOpenAI, str]:
    if settings.LLM_PROVIDER == "google":
        return AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=settings.GOOGLE_API_KEY,
        ), settings.GOOGLE_MODEL

    if settings.LLM_PROVIDER == "ollama":
        return AsyncOpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama",
        ), settings.OLLAMA_MODEL

    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY), settings.OPENAI_MODEL


async def generate_answer(question: str, context_chunks: list[str]) -> str:
    client, model = _make_client()
    logger.info(f"Generating answer — provider={settings.LLM_PROVIDER}, model={model}, chunks={len(context_chunks)}")
    context = "\n\n".join(context_chunks)
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    for attempt in range(2):
        try:
            response = await client.chat.completions.create(model=model, messages=messages)
            return response.choices[0].message.content
        except RateLimitError as exc:
            if attempt == 0:
                logger.warning("Rate limited by LLM provider — retrying in 5s")
                await asyncio.sleep(5)
                continue
            raise exc
