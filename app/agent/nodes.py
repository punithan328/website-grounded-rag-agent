# def format_context(documents) -> str:
    
#     if not documents:
#         return ""

#     sections = []

#     for index, document in enumerate(
#         documents,
#         start=1,
#     ):

#         metadata = document.metadata

#         url = (
#             metadata.get("source_url")
#             or metadata.get("url")
#             or ""
#         )

#         title = (
#             metadata.get("page_title")
#             or metadata.get("title")
#             or ""
#         )

#         section = (
#             metadata.get("section_path")
#             or metadata.get("section")
#             or ""
#         )

#         sections.append(
#             f"""
# SOURCE {index}

# Title: {title}
# Section: {section}
# URL: {url}

# Content:
# {document.content}
# """
#         )

#     return "\n\n".join(sections)



# from app.retrieval.retriever import WebsiteRetriever


# retriever = WebsiteRetriever(
#     top_k=5
# )


# def retrieve_node(
#     state,
# ):

#     query = state["query"]

#     documents = retriever.retrieve(
#         query=query,
#         top_k=5,
#     )

#     return {
#         "retrieved_documents": documents,
#         "retrieval_count": len(documents),
#     }
    
    
# def evaluate_retrieval_node(
#     state,
# ):

#     documents = state.get(
#         "retrieved_documents",
#         [],
#     )

#     if not documents:

#         return {
#             "retrieval_relevant": False
#         }

#     # ----------------------------------------
#     # Baseline relevance check
#     # ----------------------------------------

#     best_distance = min(
#         document.distance
#         for document in documents
#     )

#     # IMPORTANT:
#     # This threshold should eventually come
#     # from your retrieval evaluation.
#     #
#     # Start conservatively and tune based on
#     # measured distances.
#     relevant = (
#         best_distance <= 0.70
#     )

#     return {
#         "retrieval_relevant": relevant
#     }
# def no_answer_node(
#     state,
# ):

#     return {
#         "answer": (
#             "I couldn't find enough information "
#             "to answer this question from the "
#             "indexed website."
#         ),
#         "sources": [],
#         "final_response": (
#             "I couldn't find enough information "
#             "to answer this question from the "
#             "indexed website."
#         ),
#     }
    
# from langchain_core.messages import HumanMessage

# from app.agent.llm import get_llm
# from app.agent.prompts import SYSTEM_PROMPT


# llm = get_llm()


# def generate_answer_node(
#     state,
# ):

#     query = state["query"]

#     documents = state.get(
#         "retrieved_documents",
#         [],
#     )

#     context = format_context(
#         documents
#     )

#     prompt = SYSTEM_PROMPT.format(
#         context=context,
#         query=query,
#     )

#     response = llm.invoke(
#         [
#             HumanMessage(
#                 content=prompt
#             )
#         ]
#     )

#     answer = response.content

#     sources = []

#     for document in documents:

#         metadata = document.metadata

#         url = (
#             metadata.get("source_url")
#             or metadata.get("url")
#         )

#         if url and url not in [
#             source["url"]
#             for source in sources
#         ]:

#             sources.append(
#                 {
#                     "url": url,
#                     "title": (
#                         metadata.get(
#                             "page_title"
#                         )
#                         or metadata.get(
#                             "title"
#                         )
#                     ),
#                 }
#             )

#     return {
#         "answer": answer,
#         "sources": sources,
#     }
# from app.agent.prompts import (
#     GROUNDING_PROMPT,
# )


# def grounding_node(
#     state,
# ):

#     query = state["query"]

#     answer = state.get(
#         "answer",
#         "",
#     )

#     documents = state.get(
#         "retrieved_documents",
#         [],
#     )

#     context = format_context(
#         documents
#     )

#     prompt = GROUNDING_PROMPT.format(
#         query=query,
#         context=context,
#         answer=answer,
#     )

#     response = llm.invoke(
#         [
#             HumanMessage(
#                 content=prompt
#             )
#         ]
#     )

#     result = response.content.strip()

#     grounded = result.startswith(
#         "GROUNDED"
#     )

#     return {
#         "grounded": grounded,
#         "grounding_reason": result,
#     }
    
# def regenerate_node(
#     state,
# ):

#     retry_count = state.get(
#         "retry_count",
#         0,
#     )

#     return {
#         "retry_count": retry_count + 1,
#         "answer": "",
#     }
    
# def finalize_node(
#     state,
# ):

#     answer = state.get(
#         "answer",
#         "",
#     )

#     sources = state.get(
#         "sources",
#         [],
#     )

#     source_text = ""

#     if sources:

#         source_lines = []

#         for source in sources:

#             title = (
#                 source.get("title")
#                 or "Source"
#             )

#             url = source["url"]

#             source_lines.append(
#                 f"- {title}: {url}"
#             )

#         source_text = (
#             "\n\nSources:\n"
#             + "\n".join(
#                 source_lines
#             )
#         )

#     return {
#         "final_response":
#             answer + source_text
#     }
from app.agent.llm import get_llm
from app.agent.prompts import (
    SYSTEM_PROMPT,
    GROUNDING_PROMPT,
)
from app.retrieval.retriever import WebsiteRetriever


retriever = WebsiteRetriever(top_k=5)
llm = get_llm()


def format_context(documents) -> str:
    """Convert retrieved chunks into LLM context."""

    if not documents:
        return ""

    sections = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.metadata

        url = (
            metadata.get("source_url")
            or metadata.get("url")
            or ""
        )

        title = (
            metadata.get("page_title")
            or metadata.get("title")
            or ""
        )

        section = (
            metadata.get("section_path")
            or metadata.get("section")
            or ""
        )

        sections.append(
            f"""
SOURCE {index}
Title: {title}
Section: {section}
URL: {url}

Content:
{document.content}
"""
        )

    return "\n\n".join(sections)


def retrieve_node(state):

    query = state["query"]

    documents = retriever.retrieve(
        query=query,
        top_k=5,
    )

    return {
        "retrieved_documents": documents,
        "retrieval_count": len(documents),
    }


def evaluate_retrieval_node(state):

    documents = state.get(
        "retrieved_documents",
        [],
    )

    if not documents:
        return {
            "retrieval_relevant": False
        }

    best_distance = min(
        document.distance
        for document in documents
    )

    # Temporary threshold.
    # Tune this after retrieval evaluation.
    relevant = best_distance <= 0.70

    return {
        "retrieval_relevant": relevant
    }


def generate_answer_node(state):

    query = state["query"]

    documents = state.get(
        "retrieved_documents",
        [],
    )

    context = format_context(
        documents
    )

    prompt = SYSTEM_PROMPT.format(
        context=context,
        query=query,
    )

    response = llm.invoke(prompt)

    answer = response.content

    sources = []

    for document in documents:

        metadata = document.metadata

        url = (
            metadata.get("source_url")
            or metadata.get("url")
        )

        if not url:
            continue

        if any(
            source["url"] == url
            for source in sources
        ):
            continue

        sources.append(
            {
                "url": url,
                "title": (
                    metadata.get("page_title")
                    or metadata.get("title")
                    or "Source"
                ),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }


def grounding_node(state):

    query = state["query"]

    answer = state.get(
        "answer",
        "",
    )

    documents = state.get(
        "retrieved_documents",
        [],
    )

    context = format_context(
        documents
    )

    prompt = GROUNDING_PROMPT.format(
        query=query,
        context=context,
        answer=answer,
    )

    response = llm.invoke(prompt)

    result = response.content.strip()

    grounded = result.startswith(
        "GROUNDED"
    )

    return {
        "grounded": grounded,
        "grounding_reason": result,
    }


def regenerate_node(state):

    retry_count = state.get(
        "retry_count",
        0,
    )

    return {
        "retry_count": retry_count + 1,
        "answer": "",
    }


def no_answer_node(state):

    message = (
        "I couldn't find enough information "
        "to answer this question from the "
        "indexed website."
    )

    return {
        "answer": message,
        "sources": [],
        "final_response": message,
    }
def finalize_node(state):
    
    return {
        "final_response": state.get(
            "answer",
            "",
        )
    }

# def finalize_node(state):

#     answer = state.get(
#         "answer",
#         "",
#     )

#     sources = state.get(
#         "sources",
#         [],
#     )

#     if not sources:
#         return {
#             "final_response": answer
#         }

#     source_lines = []

#     for source in sources:

#         title = source.get(
#             "title",
#             "Source",
#         )

#         url = source["url"]

#         source_lines.append(
#             f"- {title}: {url}"
#         )

#     final_response = (
#         answer
#         + "\n\nSources:\n"
#         + "\n".join(source_lines)
#     )

#     return {
#         "final_response": final_response
#     }