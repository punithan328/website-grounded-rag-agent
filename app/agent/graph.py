# from langgraph.graph import (
#     StateGraph,
#     START,
#     END,
# )

# from app.agent.state import AgentState

# from app.agent.nodes import (
#     retrieve_node,
#     evaluate_retrieval_node,
#     generate_answer_node,
#     grounding_node,
#     no_answer_node,
#     regenerate_node,
#     finalize_node,
# )

# from app.agent.routing import (
#     route_after_retrieval,
#     route_after_grounding,
# )


# def build_graph():

#     graph = StateGraph(
#         AgentState
#     )

#     # ----------------------------------------
#     # Nodes
#     # ----------------------------------------

#     graph.add_node(
#         "retrieve",
#         retrieve_node,
#     )

#     graph.add_node(
#         "evaluate_retrieval",
#         evaluate_retrieval_node,
#     )

#     graph.add_node(
#         "generate",
#         generate_answer_node,
#     )

#     graph.add_node(
#         "grounding",
#         grounding_node,
#     )

#     graph.add_node(
#         "regenerate",
#         regenerate_node,
#     )

#     graph.add_node(
#         "no_answer",
#         no_answer_node,
#     )

#     graph.add_node(
#         "finalize",
#         finalize_node,
#     )

#     # ----------------------------------------
#     # Entry
#     # ----------------------------------------

#     graph.add_edge(
#         START,
#         "retrieve",
#     )

#     # ----------------------------------------
#     # Retrieval
#     # ----------------------------------------

#     graph.add_edge(
#         "retrieve",
#         "evaluate_retrieval",
#     )

#     graph.add_conditional_edges(
#         "evaluate_retrieval",
#         route_after_retrieval,
#         {
#             "generate": "generate",
#             "no_answer": "no_answer",
#         },
#     )

#     # ----------------------------------------
#     # Generation
#     # ----------------------------------------

#     graph.add_edge(
#         "generate",
#         "grounding",
#     )

#     # ----------------------------------------
#     # Grounding
#     # ----------------------------------------

#     graph.add_conditional_edges(
#         "grounding",
#         route_after_grounding,
#         {
#             "finalize": "finalize",
#             "regenerate": "regenerate",
#             "no_answer": "no_answer",
#         },
#     )

#     # ----------------------------------------
#     # Retry
#     # ----------------------------------------

#     graph.add_edge(
#         "regenerate",
#         "generate",
#     )

#     # ----------------------------------------
#     # End
#     # ----------------------------------------

#     graph.add_edge(
#         "finalize",
#         END,
#     )

#     graph.add_edge(
#         "no_answer",
#         END,
#     )

#     return graph.compile()

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agent.state import AgentState

from app.agent.nodes import (
    retrieve_node,
    evaluate_retrieval_node,
    generate_answer_node,
    grounding_node,
    regenerate_node,
    no_answer_node,
    finalize_node,
)

from app.agent.routing import (
    route_after_retrieval,
    route_after_grounding,
)


def build_graph():

    workflow = StateGraph(
        AgentState
    )

    workflow.add_node(
        "retrieve",
        retrieve_node,
    )

    workflow.add_node(
        "evaluate_retrieval",
        evaluate_retrieval_node,
    )

    workflow.add_node(
        "generate",
        generate_answer_node,
    )

    workflow.add_node(
        "grounding",
        grounding_node,
    )

    workflow.add_node(
        "regenerate",
        regenerate_node,
    )

    workflow.add_node(
        "no_answer",
        no_answer_node,
    )

    workflow.add_node(
        "finalize",
        finalize_node,
    )

    workflow.add_edge(
        START,
        "retrieve",
    )

    workflow.add_edge(
        "retrieve",
        "evaluate_retrieval",
    )

    workflow.add_conditional_edges(
        "evaluate_retrieval",
        route_after_retrieval,
        {
            "generate": "generate",
            "no_answer": "no_answer",
        },
    )

    workflow.add_edge(
        "generate",
        "grounding",
    )

    workflow.add_conditional_edges(
        "grounding",
        route_after_grounding,
        {
            "finalize": "finalize",
            "regenerate": "regenerate",
            "no_answer": "no_answer",
        },
    )

    workflow.add_edge(
        "regenerate",
        "generate",
    )

    workflow.add_edge(
        "finalize",
        END,
    )

    workflow.add_edge(
        "no_answer",
        END,
    )

    return workflow.compile()