import hashlib
from dataclasses import dataclass
from typing import Optional

import tiktoken

from app.models.chunk import (
    ChunkRecord,
)

from app.models.page import (
    ContentBlock,
    ExtractedPage,
)


@dataclass
class Section:
    """
    Logical documentation section.
    """

    heading: Optional[str]

    heading_level: Optional[int]

    section_path: list[str]

    blocks: list[ContentBlock]


class SemanticChunker:
    """
    Structure-aware, token-based chunker.

    Strategy:
    - Preserve heading hierarchy.
    - Build semantic sections.
    - Keep code blocks intact where possible.
    - Split oversized sections by logical blocks.
    - Apply token-based overlap.
    """

    def __init__(
        self,
        target_tokens: int = 600,
        overlap_tokens: int = 80,
        max_tokens: int = 800,
        model_name: str = "gpt-4o-mini",
    ):

        self.target_tokens = target_tokens

        self.overlap_tokens = overlap_tokens

        self.max_tokens = max_tokens

        self.encoding = (
            tiktoken.encoding_for_model(
                model_name
            )
        )
    def _merge_small_chunks(
        self,
        chunks: list[dict],
    ) -> list[dict]:

        if not chunks:
            return []

        merged = []

        i = 0

        # A chunk below this size is considered small.
        small_threshold = 200

        while i < len(chunks):

            current = chunks[i]

            current_tokens = (
                self.count_tokens(
                    current["content"]
                )
            )

            # ------------------------------------------------
            # Try merging with next chunk
            # ------------------------------------------------

            if i + 1 < len(chunks):

                next_chunk = chunks[i + 1]

                next_tokens = (
                    self.count_tokens(
                        next_chunk["content"]
                    )
                )

                combined_tokens = (
                    current_tokens
                    + next_tokens
                )

                # --------------------------------------------
                # Both are small and combined size is safe
                # --------------------------------------------

                if (
                    current_tokens
                    < small_threshold
                    and
                    next_tokens
                    < small_threshold
                    and
                    combined_tokens
                    <= self.target_tokens
                ):

                    combined_content = (
                        current["content"]
                        + "\n\n"
                        + next_chunk["content"]
                    )

                    combined = {
                        "content": combined_content,

                        "chunk_type": (
                            "mixed"
                            if (
                                current["chunk_type"]
                                != next_chunk["chunk_type"]
                            )
                            else current["chunk_type"]
                        ),

                        "section_path": (
                            current["section_path"]
                        ),

                        "heading": (
                            current["heading"]
                        ),

                        "heading_level": (
                            current["heading_level"]
                        ),

                        "code_language": (
                            current["code_language"]
                            or
                            next_chunk["code_language"]
                        ),
                    }

                    merged.append(
                        combined
                    )

                    i += 2

                    continue

            merged.append(
                current
            )

            i += 1

        return merged
    # ========================================================
    # Public API
    # ========================================================

    def chunk_page(
        self,
        page: ExtractedPage,
        page_id: int,
    ) -> list[ChunkRecord]:

        sections = (
            self._build_sections(
                page.blocks
            )
        )

        # chunks: list[ChunkRecord] = []

        # for section in sections:

        #     section_chunks = (
        #         self._chunk_section(
        #             section
        #         )
        #     )

        #     chunks.extend(
        #         section_chunks
        #     )
        raw_chunks = []

        for section in sections:

            section_chunks = (
                self._chunk_section(
                    section
                )
            )

            raw_chunks.extend(
                section_chunks
            )

        # ----------------------------------------------------
        # Merge very small adjacent chunks
        # ----------------------------------------------------

        raw_chunks = (
            self._merge_small_chunks(
                raw_chunks
            )
        )

        chunks = raw_chunks

        # ----------------------------------------------------
        # Convert temporary chunks into ChunkRecords
        # ----------------------------------------------------

        records = []

        for index, chunk in enumerate(
            chunks
        ):

            content = chunk["content"]

            token_count = (
                self.count_tokens(
                    content
                )
            )

            chunk_hash = (
                self._hash(content)
            )

            chunk_id = (
                f"page_{page_id}_"
                f"chunk_{index}_"
                f"{chunk_hash[:12]}"
            )

            records.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    page_id=page_id,
                    chunk_index=index,
                    content=content,
                    content_hash=chunk_hash,
                    token_count=token_count,
                    chunk_type=chunk[
                        "chunk_type"
                    ],
                    page_title=page.title,
                    source_url=page.url,
                    canonical_url=(
                        page.canonical_url
                    ),
                    section_path=chunk[
                        "section_path"
                    ],
                    heading=chunk[
                        "heading"
                    ],
                    heading_level=chunk[
                        "heading_level"
                    ],
                    code_language=chunk[
                        "code_language"
                    ],
                )
            )

        return records

    # ========================================================
    # Build section hierarchy
    # ========================================================

    def _build_sections(
        self,
        blocks: list[ContentBlock],
    ) -> list[Section]:

        sections = []

        heading_stack: list[
            tuple[int, str]
        ] = []

        current_blocks = []

        current_heading = None

        current_level = None

        current_path: list[str] = []

        for block in blocks:

            if (
                block.block_type == "heading"
                and block.level is not None
            ):

                # Flush previous section
                if current_blocks:

                    sections.append(
                        Section(
                            heading=current_heading,
                            heading_level=current_level,
                            section_path=current_path.copy(),
                            blocks=current_blocks,
                        )
                    )

                    current_blocks = []

                level = block.level

                # Remove headings at same/deeper level
                heading_stack = [
                    item
                    for item in heading_stack
                    if item[0] < level
                ]

                heading_stack.append(
                    (
                        level,
                        block.content,
                    )
                )

                current_heading = (
                    block.content
                )

                current_level = level

                current_path = [
                    title
                    for _, title
                    in heading_stack
                ]

                continue

            current_blocks.append(
                block
            )

        # Flush final section
        if current_blocks:

            sections.append(
                Section(
                    heading=current_heading,
                    heading_level=current_level,
                    section_path=current_path.copy(),
                    blocks=current_blocks,
                )
            )

        return sections

    # ========================================================
    # Chunk one section
    # ========================================================

    def _chunk_section(
        self,
        section: Section,
    ) -> list[dict]:

        chunks = []

        current_blocks: list[
            ContentBlock
        ] = []

        current_tokens = 0

        for block in section.blocks:

            block_text = (
                self._format_block(
                    block
                )
            )

            block_tokens = (
                self.count_tokens(
                    block_text
                )
            )

            # ------------------------------------------------
            # Large individual block
            # ------------------------------------------------

            if block_tokens > self.max_tokens:

                # Flush current chunk first
                if current_blocks:

                    chunks.append(
                        self._create_chunk(
                            section,
                            current_blocks,
                        )
                    )

                    current_blocks = []
                    current_tokens = 0

                # Split only this large block
                pieces = (
                    self._split_large_block(
                        block_text
                    )
                )

                for piece in pieces:

                    chunks.append(
                        {
                            "content": self._add_context(
                                section,
                                piece,
                            ),
                            "chunk_type": (
                                "code"
                                if block.block_type
                                == "code"
                                else "text"
                            ),
                            "section_path": (
                                section.section_path
                            ),
                            "heading": (
                                section.heading
                            ),
                            "heading_level": (
                                section.heading_level
                            ),
                            "code_language": (
                                block.language
                            ),
                        }
                    )

                continue

            # ------------------------------------------------
            # Would exceed target?
            # ------------------------------------------------

            if (
                current_blocks
                and
                current_tokens
                + block_tokens
                > self.target_tokens
            ):

                chunks.append(
                    self._create_chunk(
                        section,
                        current_blocks,
                    )
                )

                # --------------------------------------------
                # Create overlap from previous blocks
                # --------------------------------------------

                overlap_blocks = (
                    self._get_overlap_blocks(
                        current_blocks
                    )
                )

                current_blocks = (
                    overlap_blocks
                    + [block]
                )

                current_tokens = sum(
                    self.count_tokens(
                        self._format_block(
                            b
                        )
                    )
                    for b in current_blocks
                )

            else:

                current_blocks.append(
                    block
                )

                current_tokens += (
                    block_tokens
                )

        # ----------------------------------------------------
        # Final chunk
        # ----------------------------------------------------

        if current_blocks:

            chunks.append(
                self._create_chunk(
                    section,
                    current_blocks,
                )
            )

        return chunks

    # ========================================================
    # Create chunk
    # ========================================================

    def _create_chunk(
        self,
        section: Section,
        blocks: list[ContentBlock],
    ) -> dict:

        content_parts = []

        for block in blocks:

            content_parts.append(
                self._format_block(
                    block
                )
            )

        content = "\n\n".join(
            content_parts
        ).strip()

        content = self._add_context(
            section,
            content,
        )

        chunk_type = "text"

        code_language = None

        if (
            len(blocks) == 1
            and blocks[0].block_type
            == "code"
        ):

            chunk_type = "code"

            code_language = (
                blocks[0].language
            )

        elif any(
            block.block_type == "code"
            for block in blocks
        ):

            chunk_type = "mixed"

        return {
            "content": content,
            "chunk_type": chunk_type,
            "section_path": (
                section.section_path
            ),
            "heading": (
                section.heading
            ),
            "heading_level": (
                section.heading_level
            ),
            "code_language": code_language,
        }

    # ========================================================
    # Format block
    # ========================================================

    @staticmethod
    def _format_block(
        block: ContentBlock,
    ) -> str:

        if block.block_type == "code":

            language = (
                block.language
                or ""
            )

            return (
                f"```{language}\n"
                f"{block.content}\n"
                f"```"
            )

        if block.block_type == "heading":

            return block.content

        return block.content

    # ========================================================
    # Add hierarchical context
    # ========================================================

    @staticmethod
    def _add_context(
        section: Section,
        content: str,
    ) -> str:

        if not section.section_path:

            return content

        context = (
            "Section: "
            + " > ".join(
                section.section_path
            )
        )

        return (
            f"{context}\n\n"
            f"{content}"
        )

    # ========================================================
    # Overlap
    # ========================================================

    def _get_overlap_blocks(
        self,
        blocks: list[ContentBlock],
    ) -> list[ContentBlock]:

        selected = []

        token_count = 0

        for block in reversed(
            blocks
        ):

            block_tokens = (
                self.count_tokens(
                    self._format_block(
                        block
                    )
                )
            )

            if (
                token_count
                + block_tokens
                > self.overlap_tokens
            ):
                break

            selected.insert(
                0,
                block
            )

            token_count += (
                block_tokens
            )

        return selected

    # ========================================================
    # Split oversized block
    # ========================================================

    def _split_large_block(
        self,
        text: str,
    ) -> list[str]:

        tokens = self.encoding.encode(
            text
        )

        pieces = []

        start = 0

        step = (
            self.max_tokens
            - self.overlap_tokens
        )

        while start < len(tokens):

            end = min(
                start
                + self.max_tokens,
                len(tokens),
            )

            piece_tokens = (
                tokens[start:end]
            )

            piece = (
                self.encoding.decode(
                    piece_tokens
                )
            )

            pieces.append(
                piece.strip()
            )

            if end >= len(tokens):
                break

            start += step

        return pieces

    # ========================================================
    # Token count
    # ========================================================

    def count_tokens(
        self,
        text: str,
    ) -> int:

        return len(
            self.encoding.encode(
                text
            )
        )

    # ========================================================
    # Hash
    # ========================================================

    @staticmethod
    def _hash(
        text: str,
    ) -> str:

        return hashlib.sha256(
            text.encode(
                "utf-8"
            )
        ).hexdigest()