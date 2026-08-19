from pathlib import Path

from app.config import RAW_DATA_DIR
from app.ingestion.extractor import (
    ContentExtractor,
)


def main():

    html_files = list(
        RAW_DATA_DIR.glob("*.html")
    )

    if not html_files:

        print(
            "No raw HTML files found."
        )

        print(
            "Run the crawler first:"
        )

        print(
            "uv run python scripts/crawl.py"
        )

        return

    html_path = html_files[0]

    print(
        f"Processing: {html_path}"
    )

    html = html_path.read_text(
        encoding="utf-8"
    )

    extractor = ContentExtractor()

    page = extractor.extract(
        html=html,
        url="unknown",
    )

    if not page:

        print(
            "Extraction failed."
        )

        return

    print("\n" + "=" * 70)
    print("EXTRACTION RESULT")
    print("=" * 70)

    print(
        f"\nTitle: {page.title}"
    )

    print(
        f"Description: "
        f"{page.description}"
    )

    print(
        f"Words: {page.word_count}"
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

    print("\n" + "-" * 70)
    print("STRUCTURED BLOCKS")
    print("-" * 70)

    for index, block in enumerate(
        page.blocks,
        start=1,
    ):

        print(
            f"\n[{index}] "
            f"{block.block_type}"
        )

        if block.level:

            print(
                f"Level: "
                f"{block.level}"
            )

        if block.language:

            print(
                f"Language: "
                f"{block.language}"
            )

        print(
            f"Content:\n"
            f"{block.content[:500]}"
        )


if __name__ == "__main__":
    main()
    