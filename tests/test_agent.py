from types import SimpleNamespace

from app.agent.routing import (
    route_after_retrieval,
    route_after_grounding,
)
from app.agent.nodes import (
    build_fallback_answer,
    parse_grounding_result,
)


def test_relevant_retrieval_routes_to_generate():

    state = {
        "retrieval_relevant": True
    }

    assert (
        route_after_retrieval(state)
        == "generate"
    )


def test_irrelevant_retrieval_routes_to_no_answer():

    state = {
        "retrieval_relevant": False
    }

    assert (
        route_after_retrieval(state)
        == "no_answer"
    )


def test_grounded_answer_finalizes():

    state = {
        "grounded": True
    }

    assert (
        route_after_grounding(state)
        == "finalize"
    )


def test_ungrounded_answer_retries():

    state = {
        "grounded": False,
        "retry_count": 0,
    }

    assert (
        route_after_grounding(state)
        == "regenerate"
    )


def test_second_grounding_failure_refuses():

    state = {
        "grounded": False,
        "retry_count": 1,
    }

    assert (
        route_after_grounding(state)
        == "no_answer"
    )


def test_parse_grounding_result_accepts_grounded_variants():
    assert parse_grounding_result("GROUNDED") == (True, "GROUNDED")
    assert parse_grounding_result("GROUNDED\nReason: supported by context") == (True, "GROUNDED\nReason: supported by context")
    assert parse_grounding_result("NOT_GROUNDED\nReason: answer is incomplete") == (False, "NOT_GROUNDED\nReason: answer is incomplete")


def test_build_fallback_answer_uses_context():
    docs = [
        SimpleNamespace(
            content="Metadata filtering lets you restrict results by document fields like country or status.",
            metadata={"url": "https://example.com/metadata", "page_title": "Metadata Filtering"},
        )
    ]

    answer = build_fallback_answer("What is metadata filtering?", docs)

    assert "Metadata filtering" in answer
    assert "https://example.com/metadata" in answer
    assert len(answer) > 40