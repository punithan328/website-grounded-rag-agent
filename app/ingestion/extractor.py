import hashlib
import re
from pathlib import Path
from typing import Optional

import trafilatura
from bs4 import BeautifulSoup

from app.models.page import (
    ContentBlock,
    ExtractedPage,
)


class ContentExtractor:
    """
    Extracts useful, structured content from HTML pages.
    """

    # ========================================================
    # Public API
    # ========================================================

    def extract(
        self,
        html: str,
        url: str,
    ) -> Optional[ExtractedPage]:
        """
        Extract structured content from HTML.
        """

        if not html or not html.strip():
            return None

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        # ----------------------------------------------------
        # Remove elements that are not useful knowledge
        # ----------------------------------------------------

        self._remove_noise(soup)

        # ----------------------------------------------------
        # Extract metadata
        # ----------------------------------------------------

        title = self._extract_title(
            soup
        )

        description = (
            self._extract_description(
                soup
            )
        )

        # ----------------------------------------------------
        # Extract structured blocks
        # ----------------------------------------------------

        blocks = (
            self._extract_blocks(
                soup
            )
        )

        # ----------------------------------------------------
        # Fallback extraction
        # ----------------------------------------------------

        if not blocks:

            blocks = (
                self._extract_with_trafilatura(
                    html
                )
            )

        # ----------------------------------------------------
        # Build raw text
        # ----------------------------------------------------

        raw_text = self._build_raw_text(
            blocks
        )

        raw_text = self._clean_text(
            raw_text
        )

        if not raw_text:
            return None

        # ----------------------------------------------------
        # Calculate statistics
        # ----------------------------------------------------

        word_count = len(
            raw_text.split()
        )

        character_count = len(
            raw_text
        )

        content_hash = (
            self._calculate_hash(
                raw_text
            )
        )

        return ExtractedPage(
            url=url,
            canonical_url=url,
            title=title or "",
            description=description,
            blocks=blocks,
            raw_text=raw_text,
            content_hash=content_hash,
            word_count=word_count,
            character_count=character_count,
        )

    # ========================================================
    # Remove noise
    # ========================================================
    def _is_table_of_contents(
    self,
    element,
    ) -> bool:
        """
        Detect common documentation TOC/navigation sections.
        """

        text = element.get_text(
            " ",
            strip=True,
        )

        if not text:
            return False

        text_lower = text.lower()

        toc_indicators = {
            "on this page",
            "table of contents",
            "contents",
        }

        # Check heading immediately before the element
        previous_heading = element.find_previous(
            ["h1", "h2", "h3", "h4"]
        )

        if previous_heading:

            heading_text = (
                previous_heading
                .get_text(
                    " ",
                    strip=True,
                )
                .lower()
            )

            if heading_text in toc_indicators:
                return True

        # A large list of short items is commonly a TOC
        if element.name in {"ul", "ol"}:

            items = element.find_all(
                "li",
                recursive=False,
            )

            if len(items) >= 5:

                short_items = 0

                for item in items:

                    item_text = item.get_text(
                        " ",
                        strip=True,
                    )

                    if (
                        2
                        <= len(item_text.split())
                        <= 12
                    ):
                        short_items += 1

                if (
                    short_items / len(items)
                    >= 0.7
                ):
                    return True

        return False

    @staticmethod
    def _remove_noise(
        soup: BeautifulSoup,
    ) -> None:

        noise_tags = [
            "script",
            "style",
            "noscript",
            "svg",
            "iframe",
            "canvas",
        ]

        for tag_name in noise_tags:

            for tag in soup.find_all(
                tag_name
            ):

                tag.decompose()
        # --------------------------------------------------------
        # Remove common website navigation
        # --------------------------------------------------------

        for selector in [
            "nav",
            "header",
            "footer",
        ]:

            for tag in soup.select(
                selector
            ):
                tag.decompose()

    # ========================================================
    # Extract title
    # ========================================================

    @staticmethod
    def _extract_title(
        soup: BeautifulSoup,
    ) -> str:

        # Prefer the page <title>
        if soup.title:

            title = soup.title.get_text(
                " ",
                strip=True,
            )

            if title:
                return title

        # Fallback to H1
        h1 = soup.find("h1")

        if h1:

            return h1.get_text(
                " ",
                strip=True,
            )

        return ""

    # ========================================================
    # Extract meta description
    # ========================================================

    @staticmethod
    def _extract_description(
        soup: BeautifulSoup,
    ) -> Optional[str]:

        tag = soup.find(
            "meta",
            attrs={
                "name": "description"
            },
        )

        if not tag:
            return None

        content = tag.get(
            "content"
        )

        if not content:
            return None

        return content.strip()

    # ========================================================
    # Extract structured blocks
    # ========================================================

    def _extract_blocks(
        self,
        soup: BeautifulSoup,
    ) -> list[ContentBlock]:

        blocks: list[ContentBlock] = []

        # ----------------------------------------------------
        # Find main content
        # ----------------------------------------------------

        main = (
            soup.find("main")
            or
            soup.find(
                "article"
            )
            or
            soup.body
        )

        if not main:
            return blocks

        # ----------------------------------------------------
        # Iterate through relevant elements
        # ----------------------------------------------------

        # elements = main.find_all(
        #     [
        #         "h1",
        #         "h2",
        #         "h3",
        #         "h4",
        #         "p",
        #         "ul",
        #         "ol",
        #         "pre",
        #         "blockquote",
        #     ]
        # )
        elements = main.find_all(
    [
        "h1",
        "h2",
        "h3",
        "h4",
        "p",
        "ul",
        "ol",
        "pre",
        "blockquote",
    ]
)

        for element in elements:
            if self._is_table_of_contents(
                element
            ):
                continue

            tag_name = (
                element.name.lower()
            )

            # ----------------------------------------------
            # Headings
            # ----------------------------------------------

            if tag_name in {
                "h1",
                "h2",
                "h3",
                "h4",
            }:

                text = element.get_text(
                    " ",
                    strip=True,
                )

                text = self._clean_text(
                    text
                )
                if self._is_ui_text(text):
                    continue

                if not text:
                    continue

                level = int(
                    tag_name[1]
                )

                blocks.append(
                    ContentBlock(
                        block_type="heading",
                        content=text,
                        level=level,
                    )
                )

            # ----------------------------------------------
            # Paragraph
            # ----------------------------------------------

            elif tag_name == "p":

                text = element.get_text(
                    " ",
                    strip=True,
                )

                text = self._clean_text(
                    text
                )

                if not text:
                    continue

                blocks.append(
                    ContentBlock(
                        block_type="paragraph",
                        content=text,
                    )
                )

            # ----------------------------------------------
            # Lists
            # ----------------------------------------------

            elif tag_name in {
                "ul",
                "ol",
            }:

                items = []

                for li in element.find_all(
                    "li",
                    recursive=False,
                ):

                    text = li.get_text(
                        " ",
                        strip=True,
                    )

                    text = self._clean_text(
                        text
                    )

                    if text:
                        items.append(
                            text
                        )

                if not items:
                    continue

                list_text = "\n".join(
                    f"- {item}"
                    for item in items
                )

                blocks.append(
                    ContentBlock(
                        block_type="list",
                        content=list_text,
                    )
                )

            # ----------------------------------------------
            # Code blocks
            # ----------------------------------------------

            elif tag_name == "pre":

                code_element = (
                    element.find("code")
                )

                if code_element:

                    code = (
                        code_element.get_text(
                            "\n",
                            strip=False,
                        )
                    )

                    language = (
                        self._detect_code_language(
                            code_element
                        )
                    )

                else:

                    code = (
                        element.get_text(
                            "\n",
                            strip=False,
                        )
                    )

                    language = None

                code = code.strip()

                if not code:
                    continue

                blocks.append(
                    ContentBlock(
                        block_type="code",
                        content=code,
                        language=language,
                    )
                )

            # ----------------------------------------------
            # Blockquote
            # ----------------------------------------------

            elif tag_name == "blockquote":

                text = element.get_text(
                    " ",
                    strip=True,
                )

                text = self._clean_text(
                    text
                )

                if not text:
                    continue

                blocks.append(
                    ContentBlock(
                        block_type="blockquote",
                        content=text,
                    )
                )

        return self._remove_duplicate_blocks(
            blocks
        )
    @staticmethod
    def _is_ui_text(
        text: str,
    ) -> bool:

        normalized = (
            text.strip()
            .lower()
        )

        ui_patterns = {
            "was this page helpful?",
            "was this helpful?",
            "did this page help?",
            "give us feedback",
            "feedback",
        }

        return normalized in ui_patterns

    # ========================================================
    # Detect code language
    # ========================================================

    @staticmethod
    def _detect_code_language(
        code_element,
    ) -> Optional[str]:

        classes = (
            code_element.get(
                "class",
                []
            )
        )

        for class_name in classes:

            if class_name.startswith(
                "language-"
            ):

                return class_name[
                    len("language-"):
                ]

            if class_name.startswith(
                "lang-"
            ):

                return class_name[
                    len("lang-"):
                ]

        return None

    # ========================================================
    # Trafilatura fallback
    # ========================================================

    @staticmethod
    def _extract_with_trafilatura(
        html: str,
    ) -> list[ContentBlock]:

        extracted = (
            trafilatura.extract(
                html,
                include_links=True,
                include_formatting=True,
                include_tables=True,
                output_format="txt",
            )
        )

        if not extracted:
            return []

        return [
            ContentBlock(
                block_type="paragraph",
                content=extracted.strip(),
            )
        ]

    # ========================================================
    # Build text
    # ========================================================

    @staticmethod
    def _build_raw_text(
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
                    f"```"
                )

                parts.append(
                    block.content
                )

                parts.append(
                    f"```"
                )

            else:

                parts.append(
                    block.content
                )

        return "\n\n".join(
            parts
        )

    # ========================================================
    # Clean text
    # ========================================================

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        if not text:
            return ""

        # Normalize non-breaking spaces
        text = text.replace(
            "\xa0",
            " ",
        )

        # Normalize line endings
        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        # Remove excessive spaces
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Remove excessive blank lines
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # ========================================================
    # Remove duplicate blocks
    # ========================================================

    @staticmethod
    def _remove_duplicate_blocks(
        blocks: list[ContentBlock],
    ) -> list[ContentBlock]:

        result = []

        seen = set()

        for block in blocks:

            # Code is allowed to contain repeated lines,
            # but duplicate complete blocks are unnecessary.
            key = (
                block.block_type,
                block.content,
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(block)

        return result

    # ========================================================
    # Hash
    # ========================================================

    @staticmethod
    def _calculate_hash(
        text: str,
    ) -> str:

        return hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()