# # from langchain_openai import ChatOpenAI

# # from app.config import (
# #     OPENROUTER_API_KEY,
# #     OPENROUTER_BASE_URL,
# #     OPENROUTER_MODEL,
# # )


# # def get_llm() -> ChatOpenAI:

# #     if not OPENROUTER_API_KEY:
# #         raise RuntimeError(
# #             "OPENROUTER_API_KEY is not configured. "
# #             "Set it in the .env file."
# #         )

# #     return ChatOpenAI(
# #         model=OPENROUTER_MODEL,
# #         api_key=OPENROUTER_API_KEY,
# #         base_url=OPENROUTER_BASE_URL,
# #         temperature=0,
# #     )


# from langchain_openai import ChatOpenAI

# from app.config import (
#     OPENROUTER_API_KEY,
#     OPENROUTER_BASE_URL,
#     OPENROUTER_MODEL,
# )


# def get_llm() -> ChatOpenAI:

#     if not OPENROUTER_API_KEY:
#         raise RuntimeError(
#             "OPENROUTER_API_KEY is not configured. "
#             "Set it in the .env file."
#         )

#     return ChatOpenAI(
#         model=OPENROUTER_MODEL,
#         api_key=OPENROUTER_API_KEY,
#         base_url=OPENROUTER_BASE_URL,

#         # Important for OpenRouter credits
#         max_tokens=1000,

#         # Deterministic RAG answers
#         temperature=0,
#     )

import random
import time

from langchain_openai import ChatOpenAI

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_TEMPERATURE,
)
from app.logger import logger


def invoke_with_backoff(llm: ChatOpenAI, prompt: str, max_retries: int = 4, base_delay: float = 1.0):
    """Retry OpenRouter rate-limit failures with exponential backoff."""
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return llm.invoke(prompt)
        except Exception as exc:  # pragma: no cover - behavior depends on external API
            last_error = exc
            message = str(exc).lower()
            is_rate_limit = (
                "429" in message
                or "rate limit" in message
                or "too many requests" in message
            )
            if not is_rate_limit:
                raise

            if attempt >= max_retries:
                logger.error("OpenRouter rate limit exceeded after %s attempts: %s", max_retries + 1, exc)
                raise

            delay = min(base_delay * (2 ** attempt), 30.0) + random.uniform(0.25, 1.5)
            logger.warning(
                "OpenRouter rate-limited; retrying in %.2f seconds (attempt %s/%s)",
                delay,
                attempt + 1,
                max_retries,
            )
            time.sleep(delay)

    if last_error is not None:
        raise last_error

    raise RuntimeError("Model invocation failed without a response.")


def get_llm() -> ChatOpenAI:
    logger.info("get_llm called")
    logger.info(
        "LLM config: model=%s base_url=%s max_tokens=%s temperature=%s",
        OPENROUTER_MODEL,
        OPENROUTER_BASE_URL,
        OPENROUTER_MAX_TOKENS,
        OPENROUTER_TEMPERATURE,
    )

    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is not configured")
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    logger.info("OPENROUTER_API_KEY present; creating ChatOpenAI client")
    llm = ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        max_tokens=OPENROUTER_MAX_TOKENS,
        temperature=OPENROUTER_TEMPERATURE,
    )
    logger.info("ChatOpenAI client created successfully")
    return llm