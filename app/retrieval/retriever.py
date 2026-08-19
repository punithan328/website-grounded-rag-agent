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


class WebsiteRetriever:

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

        self.embedder = SentenceTransformerEmbedder(
            model_name=EMBEDDING_MODEL
        )

        self.vector_store = ChromaStore(
            persist_directory=str(CHROMA_DIR),
            collection_name=CHROMA_COLLECTION_NAME,
        )

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        max_distance: float | None = None,
    ) -> list[RetrievalResult]:

        if not query.strip():
            return []

        query_embedding = self.embedder.embed(query)

        raw_results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k or self.top_k,
        )

        results = self._convert(raw_results)

        if max_distance is not None:
            results = [
                r
                for r in results
                if r.distance <= max_distance
            ]

        return results

    def _convert(self, raw):

        ids = raw["ids"][0]
        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]

        output = []

        for i in range(len(ids)):
            output.append(
                RetrievalResult(
                    chunk_id=ids[i],
                    content=docs[i],
                    distance=distances[i],
                    metadata=metas[i],
                )
            )

        return output