import hashlib
import re
from collections import Counter

from app.models.page import (
    ContentBlock,
    ExtractedPage,
)


class ContentValidator:
    """
    Validates and normalizes extracted website content
    before it enters the chunking pipeline.
    """

    def __init__(
        self,
        min_words: int = 20,
        min_characters: int = 120,
        # max_repeated_line_ratio: float = 0.35,
    ):
        self.min_words = min_words
        self.min_characters = min_characters
        # self.max_repeated_line_ratio = (
        #     max_repeated_line_ratio
        # )

    # ========================================================
    # Public API
    # ========================================================

    def validate(
        self,
        page: ExtractedPage,
    ) -> ExtractedPage:

        # ----------------------------------------------------
        # Clean blocks
        # ----------------------------------------------------

        page.blocks = self._clean_blocks(
            page.blocks
        )

        # ----------------------------------------------------
        # Rebuild text
        # ----------------------------------------------------

        page.raw_text = self._build_text(
            page.blocks
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        page.word_count = len(
            page.raw_text.split()
        )

        page.character_count = len(
            page.raw_text
        )

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        reason = self._validation_failure(
            page
        )

        if reason:

            page.is_valid = False
            page.rejection_reason = reason

            return page

        # ----------------------------------------------------
        # Final semantic content hash
        # ----------------------------------------------------

        page.content_hash = (
            self._calculate_hash(
                page.raw_text
            )
        )

        page.is_valid = True
        page.rejection_reason = None

        return page

    # ========================================================
    # Block cleaning
    # ========================================================

    @staticmethod
    def _clean_blocks(
        blocks: list[ContentBlock],
    ) -> list[ContentBlock]:

        cleaned = []

        for block in blocks:

            content = (
                block.content.strip()
            )

            if not content:
                continue

            # Normalize whitespace while
            # preserving code formatting.
            if block.block_type != "code":

                content = re.sub(
                    r"[ \t]+",
                    " ",
                    content,
                )

                content = re.sub(
                    r"\n{3,}",
                    "\n\n",
                    content,
                )

            cleaned.append(
                ContentBlock(
                    block_type=block.block_type,
                    content=content,
                    level=block.level,
                    language=block.language,
                )
            )

        return cleaned

    # ========================================================
    # Build text
    # ========================================================

    @staticmethod
    def _build_text(
        blocks: list[ContentBlock],
    ) -> str:

        parts = []

        for block in blocks:

            if block.block_type == "heading":

                parts.append(
                    block.content
                )

            elif block.block_type == "code":

                parts.append(
                    "```"
                )

                parts.append(
                    block.content
                )

                parts.append(
                    "```"
                )

            else:

                parts.append(
                    block.content
                )

        return "\n\n".join(
            parts
        ).strip()

    # ========================================================
    # Validation rules
    # ========================================================

    def _validation_failure(
        self,
        page: ExtractedPage,
    ) -> str | None:

        if not page.raw_text.strip():

            return "empty_content"

        # Allow shorter pages if they contain useful blocks
        if (
            page.word_count < self.min_words
            and page.character_count < self.min_characters
        ):

            return (
                f"too_few_words:{page.word_count}"
            )

        # if self._is_mostly_repeated(
        #     page.raw_text
        # ):

        #     return "mostly_repeated_content"

        if self._contains_no_useful_blocks(
            page.blocks
        ):

            return "no_useful_content_blocks"

        return None

    # ========================================================
    # Repeated content detection
    # ========================================================

    # def _is_mostly_repeated(
    #     self,
    #     text: str,
    # ) -> bool:

    #     lines = [
    #         line.strip()
    #         for line in text.splitlines()
    #         if line.strip()
    #     ]

    #     if len(lines) < 5:
    #         return False

    #     counts = Counter(
    #         lines
    #     )

    #     repeated_lines = sum(
    #         count
    #         for count in counts.values()
    #         if count > 1
    #     )

    #     ratio = (
    #         repeated_lines
    #         / len(lines)
    #     )

    #     return (
    #         ratio
    #         >= self.max_repeated_line_ratio
    #     )

    # ========================================================
    # Useful block detection
    # ========================================================

    @staticmethod
    def _contains_no_useful_blocks(
        blocks: list[ContentBlock],
    ) -> bool:

        useful_types = {
            "heading",
            "paragraph",
            "list",
            "code",
            "blockquote",
        }

        return not any(
            block.block_type
            in useful_types
            and block.content.strip()
            for block in blocks
        )

    # ========================================================
    # Content hash
    # ========================================================

    @staticmethod
    def _calculate_hash(
        text: str,
    ) -> str:

        normalized = (
            text.strip()
        )

        return hashlib.sha256(
            normalized.encode(
                "utf-8"
            )
        ).hexdigest()