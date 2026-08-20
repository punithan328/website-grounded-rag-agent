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
import json

from app.agent.llm import get_llm, invoke_with_backoff
from app.agent.prompts import (
    SYSTEM_PROMPT,
    GROUNDING_PROMPT,
    SITE_RELEVANCE_PROMPT,
)
from app.retrieval.retriever import WebsiteRetriever
from app.logger import logger


retriever = WebsiteRetriever(top_k=5)
llm = get_llm()

logger.info("Agent nodes initialized: retriever and LLM ready")


def parse_grounding_result(result: str) -> tuple[bool, str]:
    """Normalize grounding output and tolerate both JSON and legacy text responses."""
    normalized = (result or "").strip()
    if not normalized:
        logger.warning("Grounding result was empty; treating as NOT_GROUNDED")
        return False, "NOT_GROUNDED\nReason: No proposed answer was provided to evaluate against the retrieved website content."

    try:
        payload = json.loads(normalized)
        if isinstance(payload, dict):
            grounded = bool(payload.get("grounded", False))
            reason = payload.get("reason") or ("supported by the retrieved website content" if grounded else "the answer could not be validated against the retrieved content")
            return grounded, json.dumps({"grounded": grounded, "reason": reason}, ensure_ascii=False)
        if isinstance(payload, str):
            lowered = payload.strip().lower()
            if lowered in {"grounded", "true"}:
                return True, json.dumps({"grounded": True, "reason": "supported by the retrieved website content"}, ensure_ascii=False)
            if lowered in {"not_grounded", "false"}:
                return False, json.dumps({"grounded": False, "reason": "the answer could not be validated against the retrieved content"}, ensure_ascii=False)
    except (TypeError, ValueError, json.JSONDecodeError):
        pass

    upper = normalized.upper()
    if upper.startswith("GROUNDED"):
        return True, normalized

    if upper.startswith("NOT_GROUNDED"):
        return False, normalized

    if "NOT_GROUNDED" in upper:
        return False, normalized

    if "GROUNDED" in upper:
        return True, normalized

    logger.warning("Unrecognized grounding verdict: %s", normalized)
    return False, f"NOT_GROUNDED\nReason: The answer could not be validated against the retrieved content.\n{normalized}"


NO_CONTEXT_MESSAGE = "I don't have enough context in the indexed website to answer this question accurately."


def build_fallback_answer(query: str, documents) -> str:
    """Return a strict refusal without exposing raw retrieved snippets when context is weak or irrelevant."""
    return NO_CONTEXT_MESSAGE


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


GENERIC_PHRASES = {
    "hi",
    "hello",
    "hey",
    "bye",
    "goodbye",
    "thanks",
    "thank you",
    "how are you",
    "who are you",
    "what is your name",
    "good morning",
    "good evening",
    "good night",
}


def is_generic_chat_query(query: str) -> bool:
    """Heuristic fallback for obvious casual greetings and small talk."""
    normalized = (query or "").strip().lower()
    if not normalized:
        return False

    if normalized in GENERIC_PHRASES:
        return True

    return any(normalized.startswith(f"{phrase} ") for phrase in GENERIC_PHRASES)


def should_retrieve_for_query(query: str) -> bool:
    """Ask the LLM whether the question is about the indexed website; fall back to simple heuristics if needed."""
    normalized = (query or "").strip()
    if not normalized:
        return False

    if is_generic_chat_query(normalized):
        logger.info("Heuristic relevance gate: non-site query detected for %s", query)
        return False

    try:
        prompt = SITE_RELEVANCE_PROMPT.format(query=query)
        response = invoke_with_backoff(llm, prompt)
        content = (response.content or "").strip()
        payload = json.loads(content)

        if isinstance(payload, dict):
            site_relevant = bool(payload.get("site_relevant", False))
            reason = payload.get("reason") or ""
            logger.info("LLM relevance check: site_relevant=%s reason=%s", site_relevant, reason)
            return site_relevant

        if isinstance(payload, str):
            lowered = payload.strip().lower()
            if lowered in {"true", "site_relevant"}:
                logger.info("LLM relevance check: model echoed a string value; defaulting to site_relevant=True")
                return True
            if lowered in {"false", "not_site_relevant"}:
                logger.info("LLM relevance check: model echoed a string value; defaulting to site_relevant=False")
                return False
    except Exception as exc:  # pragma: no cover - external model output may vary
        logger.warning("LLM relevance check failed for '%s'; using fallback heuristic. Error: %s", query, exc)

    return True


def retrieve_node(state):
    logger.info("retrieve_node called")
    query = state["query"]
    logger.info("Processing query: %s", query)

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

    if not documents:
        answer = "I don't have enough context in the indexed website to answer this question accurately."
        logger.info("No retrieved documents available; refusing to answer from model knowledge")
        return {
            "answer": answer,
            "sources": [],
        }

    context = format_context(documents)
    prompt = SYSTEM_PROMPT.format(
        context=context,
        query=query,
    )
    logger.info("System prompt prepared; invoking LLM")

    response = invoke_with_backoff(llm, prompt)
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

    response = invoke_with_backoff(llm, prompt)
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

    if is_generic_chat_query(query):
        message = (
            "I can answer questions about the indexed website, but this looks like a general conversation message. "
            "Please ask a question related to the site content."
        )
        logger.info("No-answer response prepared for conversational query")
        return {
            "answer": message,
            "sources": [],
            "final_response": message,
        }

    fallback = build_fallback_answer(query, documents)
    message = fallback if fallback else NO_CONTEXT_MESSAGE
    logger.info("No-answer response prepared using strict no-context fallback")

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