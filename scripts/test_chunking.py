from app.config import RAW_DATA_DIR

from app.ingestion.document_processor import (
    DocumentProcessor,
)

from app.ingestion.chunker import (
    SemanticChunker,
)


def main():

    html_files = list(
        RAW_DATA_DIR.glob("*.html")
    )

    if not html_files:

        print(
            "No raw HTML files found."
        )

        return

    html_path = html_files[0]

    html = html_path.read_text(
        encoding="utf-8"
    )

    processor = (
        DocumentProcessor()
    )

    page = processor.process(
        html=html,
        url="unknown",
    )

    if page is None:

        print(
            "Extraction failed."
        )

        return

    if not page.is_valid:

        print(
            "Page rejected:"
        )

        print(
            page.rejection_reason
        )

        return

    chunker = SemanticChunker(
        target_tokens=600,
        overlap_tokens=80,
        max_tokens=800,
    )

    chunks = chunker.chunk_page(
        page,
        page_id=1,
    )

    print("\n" + "=" * 70)
    print("CHUNKING RESULT")
    print("=" * 70)

    print(
        f"\nPage: {page.title}"
    )

    print(
        f"Total page tokens: "
        f"{chunker.count_tokens(page.raw_text)}"
    )

    print(
        f"Total chunks: "
        f"{len(chunks)}"
    )

    print("\n" + "-" * 70)

    for chunk in chunks:

        print(
            f"\nChunk #{chunk.chunk_index}"
        )

        print(
            f"Tokens: "
            f"{chunk.token_count}"
        )

        print(
            f"Type: "
            f"{chunk.chunk_type}"
        )

        print(
            f"Section: "
            f"{' > '.join(chunk.section_path)}"
        )

        print(
            f"Content:\n"
            f"{chunk.content[:1500]}"
        )

        print(
            "-" * 70
        )


if __name__ == "__main__":
    main()