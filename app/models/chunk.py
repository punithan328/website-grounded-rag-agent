from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChunkRecord:
    chunk_id: str
    page_id: int
    chunk_index: int
    content_hash: str
    chroma_id: Optional[str] = None
    embedding_model: Optional[str] = None
    created_at: Optional[datetime] = None