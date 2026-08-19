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

def route_after_retrieval(state):
    
    if state.get(
        "retrieval_relevant",
        False,
    ):
        return "generate"

    return "no_answer"


def route_after_grounding(state):

    if state.get(
        "grounded",
        False,
    ):
        return "finalize"

    retry_count = state.get(
        "retry_count",
        0,
    )

    if retry_count < 1:
        return "regenerate"

    return "no_answer"