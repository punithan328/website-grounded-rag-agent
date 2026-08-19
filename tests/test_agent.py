from app.agent.routing import (
    route_after_retrieval,
    route_after_grounding,
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