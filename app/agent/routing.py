# def route_after_retrieval(
#     state,
# ):

#     if state.get(
#         "retrieval_relevant",
#         False,
#     ):
#         return "generate"

#     return "no_answer"

# def route_after_grounding(
#     state,
# ):

#     if state.get(
#         "grounded",
#         False,
#     ):
#         return "finalize"

#     retry_count = state.get(
#         "retry_count",
#         0,
#     )

#     if retry_count < 1:
#         return "regenerate"

#     return "no_answer"

from app.logger import logger


def route_after_query_relevance(state):
    logger.info("route_after_query_relevance called with state keys=%s", list(state.keys()))

    query_relevant = state.get(
        "query_relevant",
        False,
    )
    logger.info("query_relevant=%s", query_relevant)

    if query_relevant:
        logger.info("Routing decision: query relevant -> retrieve")
        return "retrieve"

    logger.info("Routing decision: query not relevant -> no_answer")
    return "no_answer"


def route_after_retrieval(state):
    logger.info("route_after_retrieval called with state keys=%s", list(state.keys()))

    retrieval_relevant = state.get(
        "retrieval_relevant",
        False,
    )
    logger.info("retrieval_relevant=%s", retrieval_relevant)

    if retrieval_relevant:
        logger.info("Routing decision: retrieval relevant -> generate")
        return "generate"

    logger.info("Routing decision: retrieval not relevant -> no_answer")
    return "no_answer"


def route_after_grounding(state):
    logger.info("route_after_grounding called with state keys=%s", list(state.keys()))

    grounded = state.get(
        "grounded",
        False,
    )
    logger.info("grounded=%s", grounded)

    if grounded:
        logger.info("Routing decision: grounded -> finalize")
        return "finalize"

    logger.info("Routing decision: not grounded -> no_answer")
    return "no_answer"