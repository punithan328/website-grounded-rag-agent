from typing import Optional

import chromadb

from app.models.chunk import ChunkRecord


class ChromaStore:
    """
    Persistent ChromaDB vector store.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
    ):

        self.persist_directory = (
            persist_directory
        )

        self.collection_name = (
            collection_name
        )

        self.client = (
            chromadb.PersistentClient(
                path=persist_directory
            )
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine"
                },
            )
        )

    # ========================================================
    # Collection information
    # ========================================================

    def count(self) -> int:

        return self.collection.count()

    # ========================================================
    # Upsert chunks
    # ========================================================

    def upsert_chunks(
        self,
        chunks: list[ChunkRecord],
        embeddings: list[list[float]],
        embedding_model: str,
    ):

        if len(chunks) != len(embeddings):

            raise ValueError(
                "Chunks and embeddings must "
                "have the same length"
            )

        if not chunks:
            return

        ids = []

        documents = []

        metadatas = []

        for chunk in chunks:

            ids.append(
                chunk.chunk_id
            )

            documents.append(
                chunk.content
            )

            metadata = {
                "page_id": chunk.page_id,

                "chunk_index": (
                    chunk.chunk_index
                ),

                "source_url": (
                    chunk.source_url
                ),

                "canonical_url": (
                    chunk.canonical_url
                ),

                "page_title": (
                    chunk.page_title
                ),

                "section_path": (
                    " > ".join(
                        chunk.section_path
                    )
                ),

                "heading": (
                    chunk.heading
                    or ""
                ),

                "heading_level": (
                    chunk.heading_level
                    or 0
                ),

                "chunk_type": (
                    chunk.chunk_type
                ),

                "token_count": (
                    chunk.token_count
                ),

                "content_hash": (
                    chunk.content_hash
                ),

                "embedding_model": (
                    embedding_model
                ),

                "code_language": (
                    chunk.code_language
                    or ""
                ),
            }

            metadatas.append(
                metadata
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    # ========================================================
    # Get chunks by page
    # ========================================================

    def get_chunk_ids_for_page(
        self,
        page_id: int,
    ) -> list[str]:

        result = self.collection.get(
            where={
                "page_id": page_id
            },
            include=[],
        )

        return result.get(
            "ids",
            []
        )

    # ========================================================
    # Delete page chunks
    # ========================================================

    def delete_page(
        self,
        page_id: int,
    ) -> None:

        ids = (
            self.get_chunk_ids_for_page(
                page_id
            )
        )

        if not ids:
            return

        self.collection.delete(
            ids=ids
        )

    # ========================================================
    # Query
    # ========================================================

    
    def query(
    self,
    query_embedding: list[float],
    n_results: int = 5,
    where: dict | None = None,
):

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )
    def delete_ids(
        self,
        ids: list[str],
    ) -> None:

        if not ids:
            return

        self.collection.delete(
            ids=ids
        )