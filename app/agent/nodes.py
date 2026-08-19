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
from app.logger import logger


retriever = WebsiteRetriever(top_k=5)
llm = get_llm()

logger.info("Agent nodes initialized: retriever and LLM ready")


def parse_grounding_result(result: str) -> tuple[bool, str]:
    """Normalize grounding output and tolerate extra text around the response."""
    normalized = (result or "").strip()
    if not normalized:
        logger.warning("Grounding result was empty; treating as NOT_GROUNDED")
        return False, "NOT_GROUNDED\nReason: No proposed answer was provided to evaluate against the retrieved website content."

    upper = normalized.upper()
    if upper.startswith("GROUNDED"):
        return True, normalized

    if upper.startswith("NOT_GROUNDED"):
        return False, normalized

    # Some models add a short preamble; preserve the original verdict if one is present.
    if "NOT_GROUNDED" in upper:
        return False, normalized

    if "GROUNDED" in upper:
        return True, normalized

    logger.warning("Unrecognized grounding verdict: %s", normalized)
    return False, f"NOT_GROUNDED\nReason: The answer could not be validated against the retrieved content.\n{normalized}"


def build_fallback_answer(query: str, documents) -> str:
    """Construct a grounded answer from the retrieved documents when the model output is empty or invalid."""
    if not documents:
        return (
            "I couldn't find enough information in the indexed website to answer this question accurately."
        )

    snippets = []
    for index, document in enumerate(documents[:3], start=1):
        content = (document.content or "").strip()
        if not content:
            continue
        text = content[:500].strip()
        url = (document.metadata or {}).get("source_url") or (document.metadata or {}).get("url") or "source"
        title = (document.metadata or {}).get("page_title") or (document.metadata or {}).get("title") or "Source"
        snippets.append(f"{index}. {title}: {text} ({url})")

    if not snippets:
        return (
            f"I found relevant website content for '{query}', but it did not include a clear direct answer."
        )

    joined = "\n\n".join(snippets)
    return (
        "Based on the indexed website content, here is the closest grounded answer:\n\n"
        f"{joined}"
    )


def format_context(documents) -> str:
    """Convert retrieved chunks into LLM context."""
    logger.info("format_context called with %s documents", len(documents) if documents else 0)

    if not documents:
        logger.info("format_context: no documents provided")
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

    logger.info("format_context built %s context sections", len(sections))
    return "\n\n".join(sections)


def retrieve_node(state):
    logger.info("retrieve_node called")
    query = state["query"]
    logger.info("Retrieving documents for query: %s", query)

    documents = retriever.retrieve(
        query=query,
        top_k=5,
    )
    logger.info("retrieve_node found %s documents", len(documents))

    return {
        "retrieved_documents": documents,
        "retrieval_count": len(documents),
    }


def evaluate_retrieval_node(state):
    logger.info("evaluate_retrieval_node called")

    documents = state.get(
        "retrieved_documents",
        [],
    )
    logger.info("Retrieved documents count=%s", len(documents))

    if not documents:
        logger.info("No documents retrieved; setting retrieval_relevant=False")
        return {
            "retrieval_relevant": False
        }

    best_distance = min(
        document.distance
        for document in documents
    )
    logger.info("Best retrieval distance=%s", best_distance)

    relevant = best_distance <= 0.70
    logger.info("Retrieval relevance decision=%s", relevant)

    return {
        "retrieval_relevant": relevant
    }


def generate_answer_node(state):
    logger.info("generate_answer_node called")
    query = state["query"]
    logger.info("Generating answer for query: %s", query)

    documents = state.get(
        "retrieved_documents",
        [],
    )
    logger.info("Documents available for answer generation=%s", len(documents))

    context = format_context(documents)
    prompt = SYSTEM_PROMPT.format(
        context=context,
        query=query,
    )
    logger.info("System prompt prepared; invoking LLM")

    response = llm.invoke(prompt)
    answer = (response.content or "").strip()
    logger.info("LLM returned answer with length=%s", len(answer))

    if not answer:
        logger.warning("LLM returned empty answer; using grounded fallback from retrieved context")
        answer = build_fallback_answer(query, documents)

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

    logger.info("Collected %s source references", len(sources))
    return {
        "answer": answer,
        "sources": sources,
    }


def grounding_node(state):
    logger.info("grounding_node called")

    query = state["query"]
    answer = state.get(
        "answer",
        "",
    )
    documents = state.get(
        "retrieved_documents",
        [],
    )

    logger.info("Grounding query: %s | answer_length=%s | doc_count=%s", query, len(answer), len(documents))

    context = format_context(documents)
    prompt = GROUNDING_PROMPT.format(
        query=query,
        context=context,
        answer=answer,
    )
    logger.info("Grounding prompt prepared; invoking LLM")

    response = llm.invoke(prompt)
    result = (response.content or "").strip()
    grounded, normalized_result = parse_grounding_result(result)

    logger.info("Grounding result=%s | grounded=%s", normalized_result, grounded)
    return {
        "grounded": grounded,
        "grounding_reason": normalized_result,
    }


def regenerate_node(state):
    logger.info("regenerate_node called")

    retry_count = state.get(
        "retry_count",
        0,
    )
    next_retry_count = retry_count + 1
    logger.info("Retry count incremented from %s to %s", retry_count, next_retry_count)

    return {
        "retry_count": next_retry_count,
        "answer": "",
    }


def no_answer_node(state):
    logger.info("no_answer_node called")

    query = state.get("query", "")
    documents = state.get("retrieved_documents", [])
    fallback = build_fallback_answer(query, documents)

    message = (
        fallback
        if fallback
        else "I couldn't find enough information to answer this question from the indexed website."
    )
    logger.info("No-answer response prepared using fallback answer")

    return {
        "answer": message,
        "sources": [],
        "final_response": message,
    }


def finalize_node(state):
    logger.info("finalize_node called")
    final_response = state.get("answer", "")
    logger.info("Final response length=%s", len(final_response))
    return {
        "final_response": final_response
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