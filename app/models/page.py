from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PageRecord:
    url: str
    canonical_url: str
    title: Optional[str] = None
    content_hash: Optional[str] = None
    status: str = "discovered"
    http_status: Optional[int] = None
    last_crawled_at: Optional[datetime] = None
    last_embedded_at: Optional[datetime] = None
    chunk_count: int = 0