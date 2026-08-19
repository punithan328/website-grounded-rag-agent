from app.logger import logger


class Reranker:
    """Placeholder reranker with logging hooks."""

    def __init__(self, *args, **kwargs):
        logger.info("Reranker initialized with args=%s kwargs=%s", args, kwargs)

    def rerank(self, results):
        logger.info("rerank() called with %s results", len(results) if results else 0)
        return results


logger.info("Retrieval reranker module loaded")