from dataclasses import dataclass

from app.config import (
    ALLOWED_DOMAIN,
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL,
    MAX_PAGES,
    REGISTRY_DB,
    SEED_URL,
)

from app.embedding.embedder import (
    SentenceTransformerEmbedder,
)

from app.ingestion.chunker import (
    SemanticChunker,
)

from app.ingestion.crawler import (
    WebCrawler,
)

from app.ingestion.document_processor import (
    DocumentProcessor,
)

from app.ingestion.registry import (
    IngestionRegistry,
    INGESTION_STATUS_INDEXED,
    INGESTION_STATUS_REJECTED,
)

from app.vectorstore.chroma_store import (
    ChromaStore,
)
from app.logger import logger


@dataclass
class PipelineResult:

    pages_crawled: int = 0

    pages_skipped: int = 0

    pages_processed: int = 0

    pages_failed: int = 0

    chunks_created: int = 0

    vectors_upserted: int = 0


class IngestionPipeline:
    """
    End-to-end website ingestion pipeline.
    """

    def __init__(self):

        self.registry = (
            IngestionRegistry(
                REGISTRY_DB
            )
        )

        self.processor = (
            DocumentProcessor()
        )

        self.chunker = (
            SemanticChunker(
                target_tokens=600,
                overlap_tokens=80,
                max_tokens=800,
            )
        )

        self.embedder = (
            SentenceTransformerEmbedder(
                model_name=EMBEDDING_MODEL
            )
        )

        self.vector_store = (
            ChromaStore(
                persist_directory=str(
                    CHROMA_DIR
                ),
                collection_name=(
                    CHROMA_COLLECTION_NAME
                ),
            )
        )

    # ========================================================
    # Main pipeline
    # ========================================================

    def run(self) -> PipelineResult:

        result = PipelineResult()

        logger.info("%s", "=" * 70)
        logger.info("WEBSITE INGESTION PIPELINE")
        logger.info("%s", "=" * 70)

        logger.info("Website: %s", SEED_URL)

        logger.info("Maximum pages: %s", MAX_PAGES)

        # ----------------------------------------------------
        # Crawl
        # ----------------------------------------------------

        crawler = WebCrawler(
            seed_url=SEED_URL,
            allowed_domain=ALLOWED_DOMAIN,
            max_pages=MAX_PAGES,
            registry=self.registry,
        )

        crawl_result = (
            crawler.crawl()
        )

        result.pages_crawled = (
            crawl_result["successful"]
        )

        logger.info("Crawler completed.")

        # ----------------------------------------------------
        # Process each crawled page
        # ----------------------------------------------------

        for page_data in (
            crawl_result["pages"]
        ):

            self._process_crawled_page(
                page_data,
                result,
            )

        return result

    # ========================================================
    # Process page
    # ========================================================

    def _process_crawled_page(
        self,
        page_data: dict,
        result: PipelineResult,
    ) -> None:

        url = page_data[
            "final_url"
        ]

        page_id = page_data.get(
            "page_id"
        )

        if not page_id:

            result.pages_failed += 1

            return

        logger.info("%s", "\n" + "-" * 70)

        logger.info("PROCESSING PAGE: %s", url)

        # Note: crawler no longer decides freshness. The
        # pipeline computes the canonical content hash from
        # cleaned extracted content and decides whether to
        # skip processing before chunking/embedding.

        # ----------------------------------------------------
        # Read HTML
        # ----------------------------------------------------

        raw_path = page_data.get(
            "raw_path"
        )

        if not raw_path:

            logger.warning("No raw HTML path for %s", url)

            self.registry.update_page_status(
                page_id,
                "failed",
            )

            result.pages_failed += 1

            return

        try:

            with open(
                raw_path,
                "r",
                encoding="utf-8",
            ) as file:

                html = file.read()

            # ------------------------------------------------
            # Extraction
            # ------------------------------------------------

            page = (
                self.processor.process(
                    html=html,
                    url=url,
                )
            )

            if page is None:
                raise ValueError(
                    "Content extraction failed"
                )

            if not page.is_valid:

                logger.info("Page rejected: %s", page.rejection_reason)

                # Mark intentionally rejected content so it
                # isn't repeatedly retried.
                self.registry.update_page_status(
                    page_id,
                    INGESTION_STATUS_REJECTED,
                )

                result.pages_failed += 1

                return

            self.registry.update_page_status(
                page_id,
                "extracted",
            )

            # ------------------------------------------------
            # IMPORTANT: Use clean extracted content hash to
            # decide freshness BEFORE chunking/embedding.
            # ------------------------------------------------

            existing_page = self.registry.get_page_by_id(
                page_id
            )

            if (
                existing_page
                and existing_page["content_hash"]
                and existing_page["content_hash"]
                == page.content_hash
                and existing_page["status"]
                == INGESTION_STATUS_INDEXED
            ):

                logger.info("Page unchanged → skipping: %s", url)

                result.pages_skipped += 1

                return

            # Persist canonical clean-content hash
            self.registry.update_page_content_hash(
                page_id=page_id,
                content_hash=page.content_hash,
            )

            # ------------------------------------------------
            # Chunking
            # ------------------------------------------------

            chunks = (
                self.chunker.chunk_page(
                    page,
                    page_id=page_id,
                )
            )

            if not chunks:

                raise ValueError(
                    "No chunks generated"
                )

            self.registry.update_page_status(
                page_id,
                "chunked",
            )

            logger.info("Generated %s chunks for %s", len(chunks), url)

            # ------------------------------------------------
            # Delete old vectors
            # ------------------------------------------------

            old_chunk_ids = (
                self.registry.get_chunk_ids(
                    page_id
                )
            )

            if old_chunk_ids:

                logger.info(
                    "Deleting %s old vectors for %s",
                    len(old_chunk_ids),
                    url,
                )

                self.vector_store.delete_ids(
                    old_chunk_ids
                )

            # ------------------------------------------------
            # Delete old SQLite chunks
            # ------------------------------------------------

            self.registry.delete_chunks(
                page_id
            )

            # ------------------------------------------------
            # Generate embeddings
            # ------------------------------------------------

            texts = [
                chunk.content
                for chunk in chunks
            ]

            embeddings = (
                self.embedder.embed_batch(
                    texts,
                    batch_size=(
                        EMBEDDING_BATCH_SIZE
                    ),
                )
            )

            # ------------------------------------------------
            # Store vectors
            # ------------------------------------------------

            self.vector_store.upsert_chunks(
                chunks=chunks,
                embeddings=embeddings,
                embedding_model=(
                    EMBEDDING_MODEL
                ),
            )

            # ------------------------------------------------
            # Register chunks
            # ------------------------------------------------

            self.registry.register_chunks(
                chunks
            )

            # ------------------------------------------------
            # Mark indexed
            # ------------------------------------------------

            self.registry.update_page_status(
                page_id,
                "indexed",
            )

            result.pages_processed += 1

            result.chunks_created += (
                len(chunks)
            )

            result.vectors_upserted += (
                len(embeddings)
            )

            logger.info("Page indexed successfully: %s", url)

        except Exception as exc:

            logger.exception("Page processing failed: %s", exc)

            self.registry.update_page_status(
                page_id,
                "failed",
            )

            result.pages_failed += 1

    # ========================================================
    # Summary
    # ========================================================

    @staticmethod
    def print_summary(
        result: PipelineResult,
    ) -> None:
        logger.info("%s", "\n")
        logger.info("%s", "=" * 70)
        logger.info("INGESTION SUMMARY")
        logger.info("%s", "=" * 70)

        logger.info("Pages crawled: %s", result.pages_crawled)

        logger.info("Pages processed: %s", result.pages_processed)

        logger.info("Pages skipped: %s", result.pages_skipped)

        logger.info("Pages failed: %s", result.pages_failed)

        logger.info("Chunks created: %s", result.chunks_created)

        logger.info("Vectors upserted: %s", result.vectors_upserted)