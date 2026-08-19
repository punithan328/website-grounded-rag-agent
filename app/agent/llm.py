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

from langchain_openai import ChatOpenAI

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_TEMPERATURE,
)
from app.logger import logger


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