# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional


# @dataclass
# class ChunkRecord:
#     chunk_id: str
#     page_id: int
#     chunk_index: int
#     content_hash: str
#     chroma_id: Optional[str] = None
#     embedding_model: Optional[str] = None
#     created_at: Optional[datetime] = None

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChunkRecord:
    """
    A retrieval-ready document chunk.
    """

    chunk_id: str

    page_id: int

    chunk_index: int

    content: str

    content_hash: str

    token_count: int

    chunk_type: str

    page_title: str

    source_url: str

    canonical_url: str

    section_path: list[str] = field(
        default_factory=list
    )

    heading: Optional[str] = None

    heading_level: Optional[int] = None

    code_language: Optional[str] = None

    chroma_id: Optional[str] = None

    embedding_model: Optional[str] = None