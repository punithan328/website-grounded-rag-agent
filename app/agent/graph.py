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
from app.logger import logger


def build_graph():

    logger.info("Starting build_graph: creating StateGraph for AgentState")

    workflow = StateGraph(
        AgentState
    )

    logger.info("StateGraph created successfully")
    logger.info("Adding node: retrieve")
    workflow.add_node(
        "retrieve",
        retrieve_node,
    )
    logger.info("Node added: retrieve")

    logger.info("Adding node: evaluate_retrieval")
    workflow.add_node(
        "evaluate_retrieval",
        evaluate_retrieval_node,
    )
    logger.info("Node added: evaluate_retrieval")

    logger.info("Adding node: generate")
    workflow.add_node(
        "generate",
        generate_answer_node,
    )
    logger.info("Node added: generate")

    logger.info("Adding node: grounding")
    workflow.add_node(
        "grounding",
        grounding_node,
    )
    logger.info("Node added: grounding")

    logger.info("Adding node: regenerate")
    workflow.add_node(
        "regenerate",
        regenerate_node,
    )
    logger.info("Node added: regenerate")

    logger.info("Adding node: no_answer")
    workflow.add_node(
        "no_answer",
        no_answer_node,
    )
    logger.info("Node added: no_answer")

    logger.info("Adding node: finalize")
    workflow.add_node(
        "finalize",
        finalize_node,
    )
    logger.info("Node added: finalize")

    logger.info("Adding edge: START -> retrieve")
    workflow.add_edge(
        START,
        "retrieve",
    )
    logger.info("Edge added: START -> retrieve")

    logger.info("Adding edge: retrieve -> evaluate_retrieval")
    workflow.add_edge(
        "retrieve",
        "evaluate_retrieval",
    )
    logger.info("Edge added: retrieve -> evaluate_retrieval")

    logger.info("Adding conditional edge from evaluate_retrieval with route_after_retrieval")
    workflow.add_conditional_edges(
        "evaluate_retrieval",
        route_after_retrieval,
        {
            "generate": "generate",
            "no_answer": "no_answer",
        },
    )
    logger.info("Conditional edge added for evaluate_retrieval")

    logger.info("Adding edge: generate -> grounding")
    workflow.add_edge(
        "generate",
        "grounding",
    )
    logger.info("Edge added: generate -> grounding")

    logger.info("Adding conditional edge from grounding with route_after_grounding")
    workflow.add_conditional_edges(
        "grounding",
        route_after_grounding,
        {
            "finalize": "finalize",
            "regenerate": "regenerate",
            "no_answer": "no_answer",
        },
    )
    logger.info("Conditional edge added for grounding")

    logger.info("Adding edge: regenerate -> generate")
    workflow.add_edge(
        "regenerate",
        "generate",
    )
    logger.info("Edge added: regenerate -> generate")

    logger.info("Adding edge: finalize -> END")
    workflow.add_edge(
        "finalize",
        END,
    )
    logger.info("Edge added: finalize -> END")

    logger.info("Adding edge: no_answer -> END")
    workflow.add_edge(
        "no_answer",
        END,
    )
    logger.info("Edge added: no_answer -> END")

    logger.info("Compiling workflow graph")
    compiled = workflow.compile()
    logger.info("Workflow graph compiled successfully")

    return compiled