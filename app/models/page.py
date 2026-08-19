# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional


# @dataclass
# class PageRecord:
#     url: str
#     canonical_url: str
#     title: Optional[str] = None
#     content_hash: Optional[str] = None
#     status: str = "discovered"
#     http_status: Optional[int] = None
#     last_crawled_at: Optional[datetime] = None
#     last_embedded_at: Optional[datetime] = None
#     chunk_count: int = 0
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContentBlock:
    """
    Represents one logical piece of extracted page content.

    Examples:
        heading
        paragraph
        list
        code
    """

    block_type: str

    content: str

    level: Optional[int] = None

    language: Optional[str] = None

@dataclass
class ExtractedPage:
    """
    Structured representation of a crawled web page.
    """

    url: str

    canonical_url: str

    title: str

    description: Optional[str]

    blocks: list[ContentBlock] = field(
        default_factory=list
    )

    raw_text: str = ""

    content_hash: Optional[str] = None

    word_count: int = 0

    character_count: int = 0

    is_valid: bool = True

    rejection_reason: Optional[str] = None