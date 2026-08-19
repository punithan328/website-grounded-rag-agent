from typing import TypedDict

from app.retrieval.models import RetrievalResult


class AgentState(TypedDict, total=False):

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