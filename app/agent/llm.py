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


def get_llm() -> ChatOpenAI:

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        max_tokens=OPENROUTER_MAX_TOKENS,
        temperature=OPENROUTER_TEMPERATURE,
    )