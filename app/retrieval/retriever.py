# from typing import Any

# from app.config import (
#     CHROMA_COLLECTION_NAME,
#     CHROMA_DIR,
#     EMBEDDING_MODEL,
# )

# from app.embedding.embedder import (
#     SentenceTransformerEmbedder,
# )

# from app.vectorstore.chroma_store import (
#     ChromaStore,
# )

# from app.retrieval.models import (
#     RetrievalResult,
# )


# class WebsiteRetriever:

#     def __init__(
#         self,
#         top_k: int = 5,
#     ):

#         self.top_k = top_k

#         self.embedder = (
#             SentenceTransformerEmbedder(
#                 model_name=EMBEDDING_MODEL
#             )
#         )

#         self.vector_store = (
#             ChromaStore(
#                 persist_directory=str(
#                     CHROMA_DIR
#                 ),
#                 collection_name=(
#                     CHROMA_COLLECTION_NAME
#                 ),
#             )
#         )

#     def retrieve(
#         self,
#         query: str,
#         top_k: int | None = None,
#         max_distance: float | None = None,
#     ) -> list[RetrievalResult]:

#         if not query or not query.strip():
#             return []

#         k = top_k or self.top_k

#         # ------------------------------------------------
#         # Embed query
#         # ------------------------------------------------

#         query_embedding = (
#             self.embedder.embed(
#                 query.strip()
#             )
#         )

#         # ------------------------------------------------
#         # ChromaDB search
#         # ------------------------------------------------

#         results = (
#             self.vector_store.query(
#                 query_embedding=query_embedding,
#                 n_results=k,
#             )
#         )

#         # return self._convert_results(
#         #     results
#         # )
#         results = self._convert_results(
#             results
#         )

#         if max_distance is not None:

#             results = [
#                 result
#                 for result in results
#                 if result.distance <= max_distance
#             ]

#         return results

#     @staticmethod
#     def _convert_results(
#         results: dict[str, Any],
#     ) -> list[RetrievalResult]:

#         if not results:
#             return []

#         ids = (
#             results.get("ids", [[]])[0]
#         )

#         documents = (
#             results.get(
#                 "documents",
#                 [[]],
#             )[0]
#         )

#         metadatas = (
#             results.get(
#                 "metadatas",
#                 [[]],
#             )[0]
#         )

#         distances = (
#             results.get(
#                 "distances",
#                 [[]],
#             )[0]
#         )

#         output = []

#         for index, chunk_id in enumerate(ids):

#             metadata = (
#                 metadatas[index]
#                 if index < len(metadatas)
#                 else {}
#             )

#             content = (
#                 documents[index]
#                 if index < len(documents)
#                 else ""
#             )

#             distance = (
#                 distances[index]
#                 if index < len(distances)
#                 else float("inf")
#             )

#             output.append(
#                 RetrievalResult(
#                     chunk_id=chunk_id,
#                     content=content,
#                     distance=distance,
#                     metadata=metadata,
#                 )
#             )

#         return output

from app.embedding.embedder import SentenceTransformerEmbedder
from app.vectorstore.chroma_store import ChromaStore
from app.retrieval.models import RetrievalResult
from app.config import (
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
)
from app.logger import logger


class WebsiteRetriever:

    def __init__(self, top_k: int = 5):
        logger.info("Initializing WebsiteRetriever with top_k=%s", top_k)
        self.top_k = top_k

        self.embedder = SentenceTransformerEmbedder(
            model_name=EMBEDDING_MODEL
        )
        logger.info("Embedder initialized with model=%s", EMBEDDING_MODEL)

        self.vector_store = ChromaStore(
            persist_directory=str(CHROMA_DIR),
            collection_name=CHROMA_COLLECTION_NAME,
        )
        logger.info(
            "ChromaStore initialized: persist_directory=%s collection_name=%s",
            CHROMA_DIR,
            CHROMA_COLLECTION_NAME,
        )

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        max_distance: float | None = None,
    ) -> list[RetrievalResult]:
        logger.info("retrieve() called with query=%s top_k=%s max_distance=%s", query, top_k, max_distance)

        if not query or not query.strip():
            logger.warning("retrieve() called with empty query")
            return []

        normalized_query = query.strip()
        logger.info("Embedding query: %s", normalized_query)
        query_embedding = self.embedder.embed(normalized_query)

        n_results = top_k or self.top_k
        logger.info("Querying vector store with n_results=%s", n_results)
        raw_results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
        )

        results = self._convert(raw_results)
        logger.info("Raw vector-store results converted to %s retrieval items", len(results))

        if max_distance is not None:
            logger.info("Filtering results with max_distance=%s", max_distance)
            results = [
                r
                for r in results
                if r.distance <= max_distance
            ]
            logger.info("Results after max_distance filter=%s", len(results))

        logger.info("retrieve() returning %s results", len(results))
        return results

    def _convert(self, raw):
        logger.info("_convert() called with raw result keys=%s", list(raw.keys()) if isinstance(raw, dict) else type(raw))

        ids = raw["ids"][0]
        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]
        logger.info("_convert() raw counts: ids=%s docs=%s metas=%s distances=%s", len(ids), len(docs), len(metas), len(distances))

        output = []

        for i in range(len(ids)):
            result = RetrievalResult(
                chunk_id=ids[i],
                content=docs[i],
                distance=distances[i],
                metadata=metas[i],
            )
            logger.info("Converted item %s: chunk_id=%s distance=%s", i, result.chunk_id, result.distance)
            output.append(result)

        return output