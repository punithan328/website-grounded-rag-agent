from typing import TypedDict

from app.retrieval.models import RetrievalResult
from app.logger import logger

logger.info("Agent state definitions loaded")


class AgentState(TypedDict, total=False):
    logger.info("Creating AgentState schema")

    # -------------------------------
    # User input
    # -------------------------------

    query: str

    # -------------------------------
    # Retrieval
    # -------------------------------

    retrieved_documents: list[RetrievalResult]

    retrieval_count: int

    retrieval_relevant: bool

    query_relevant: bool

    # -------------------------------
    # Generation
    # -------------------------------

    answer: str

    sources: list[dict]

    # -------------------------------
    # Validation
    # -------------------------------

    grounded: bool

    grounding_reason: str

    # -------------------------------
    # Control
    # -------------------------------

    retry_count: int

    final_response: str

    logger.info("AgentState schema ready")