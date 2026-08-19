from app.config import RAW_DATA_DIR

from app.ingestion.document_processor import (
    DocumentProcessor,
)


def main():

    html_files = list(
        RAW_DATA_DIR.glob("*.html")
    )

    if not html_files:

        print(
            "No crawled HTML files found."
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

    print("\n" + "=" * 70)
    print("CONTENT VALIDATION")
    print("=" * 70)

    print(
        f"\nValid: "
        f"{page.is_valid}"
    )

    print(
        f"Reason: "
        f"{page.rejection_reason}"
    )

    print(
        f"Title: "
        f"{page.title}"
    )

    print(
        f"Words: "
        f"{page.word_count}"
    )

    print(
        f"Characters: "
        f"{page.character_count}"
    )

    print(
        f"Blocks: "
        f"{len(page.blocks)}"
    )

    print(
        f"Content hash: "
        f"{page.content_hash}"
    )

    print("\nCONTENT PREVIEW")
    print("-" * 70)

    print(
        page.raw_text[:3000]
    )


if __name__ == "__main__":
    main()