from app.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL,
    RAW_DATA_DIR,
)

from app.embedding.embedder import (
    SentenceTransformerEmbedder,
)

from app.ingestion.chunker import (
    SemanticChunker,
)

from app.ingestion.document_processor import (
    DocumentProcessor,
)

from app.vectorstore.chroma_store import (
    ChromaStore,
)


def main():

    print("=" * 70)
    print("VECTOR PIPELINE")
    print("=" * 70)

    # ========================================================
    # Find crawled page
    # ========================================================

    html_files = list(
        RAW_DATA_DIR.glob("*.html")
    )

    if not html_files:

        print(
            "No HTML files found."
        )

        print(
            "Run crawler first."
        )

        return

    html_path = html_files[0]

    print(
        f"\nHTML file: "
        f"{html_path}"
    )

    html = html_path.read_text(
        encoding="utf-8"
    )

    # ========================================================
    # Process document
    # ========================================================

    processor = (
        DocumentProcessor()
    )

    page = processor.process(
        html=html,
        url="unknown",
    )

    if page is None:

        print(
            "Document extraction failed."
        )

        return

    if not page.is_valid:

        print(
            f"Document rejected: "
            f"{page.rejection_reason}"
        )

        return

    print(
        f"\nPage title: "
        f"{page.title}"
    )

    print(
        f"Word count: "
        f"{page.word_count}"
    )

    # ========================================================
    # Chunk
    # ========================================================

    chunker = SemanticChunker(
        target_tokens=600,
        overlap_tokens=80,
        max_tokens=800,
    )

    chunks = chunker.chunk_page(
        page,
        page_id=1,
    )

    print(
        f"Chunks generated: "
        f"{len(chunks)}"
    )

    # ========================================================
    # Embedding
    # ========================================================

    print(
        "\nLoading embedding model..."
    )

    embedder = (
        SentenceTransformerEmbedder(
            model_name=EMBEDDING_MODEL
        )
    )

    texts = [
        chunk.content
        for chunk in chunks
    ]

    print(
        f"Generating embeddings "
        f"for {len(texts)} chunks..."
    )

    embeddings = (
        embedder.embed_batch(
            texts,
            batch_size=(
                EMBEDDING_BATCH_SIZE
            ),
        )
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    # ========================================================
    # ChromaDB
    # ========================================================

    store = ChromaStore(
        persist_directory=str(
            CHROMA_DIR
        ),
        collection_name=(
            CHROMA_COLLECTION_NAME
        ),
    )

    print(
        f"\nChromaDB count before: "
        f"{store.count()}"
    )

    store.upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        embedding_model=(
            EMBEDDING_MODEL
        ),
    )

    print(
        f"ChromaDB count after: "
        f"{store.count()}"
    )

    print(
        "\nVector pipeline completed."
    )


if __name__ == "__main__":
    main()