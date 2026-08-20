from types import SimpleNamespace

from app.agent.routing import (
    route_after_retrieval,
    route_after_grounding,
    route_after_query_relevance,
)
from app.agent.nodes import (
    build_fallback_answer,
    parse_grounding_result,
)


def test_query_relevance_routes_to_retrieval_or_no_answer():

    assert (
        route_after_query_relevance({"query_relevant": True})
        == "retrieve"
    )

    assert (
        route_after_query_relevance({"query_relevant": False})
        == "no_answer"
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


def test_ungrounded_answer_stops_without_regeneration():

    state = {
        "grounded": False,
        "retry_count": 0,
    }

    assert (
        route_after_grounding(state)
        == "no_answer"
    )


def test_second_grounding_failure_still_refuses():

    state = {
        "grounded": False,
        "retry_count": 1,
    }

    assert (
        route_after_grounding(state)
        == "no_answer"
    )


def test_parse_grounding_result_accepts_structured_json_and_legacy_variants():
    assert parse_grounding_result('{"grounded": true, "reason": "supported by context"}') == (True, '{"grounded": true, "reason": "supported by context"}')
    assert parse_grounding_result('{"grounded": false, "reason": "answer is incomplete"}') == (False, '{"grounded": false, "reason": "answer is incomplete"}')
    assert parse_grounding_result("GROUNDED") == (True, "GROUNDED")
    assert parse_grounding_result("GROUNDED\nReason: supported by context") == (True, "GROUNDED\nReason: supported by context")
    assert parse_grounding_result("NOT_GROUNDED\nReason: answer is incomplete") == (False, "NOT_GROUNDED\nReason: answer is incomplete")


def test_build_fallback_answer_uses_plain_no_context_message():
    docs = [
        SimpleNamespace(
            content="Metadata filtering lets you restrict results by document fields like country or status.",
            metadata={"url": "https://example.com/metadata", "page_title": "Metadata Filtering"},
        )
    ]

    answer = build_fallback_answer("What is metadata filtering?", docs)

    assert answer == "I don't have enough context in the indexed website to answer this question accurately."
    assert "Metadata filtering" not in answer
    assert "https://example.com/metadata" not in answer


def test_generic_conversational_queries_are_not_retrieved():
    from app.agent.nodes import is_generic_chat_query

    assert is_generic_chat_query("hi") is True
    assert is_generic_chat_query("bye") is True
    assert is_generic_chat_query("What is metadata filtering?") is False