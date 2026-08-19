from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalResult:
    chunk_id: str
    content: str
    distance: float
    metadata: dict[str, Any]

    @property
    def score(self) -> float:
        """
        Convert Chroma distance into a simple
        similarity-style score.

        Lower Chroma distance = better match.
        """
        return 1.0 / (1.0 + self.distance)
    
    

from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalResult:
    chunk_id: str
    content: str
    distance: float
    metadata: dict[str, Any]

    @property
    def score(self) -> float:
        """
        Convert cosine distance into a similarity score.
        1.0 = perfect match
        """
        return 1 / (1 + self.distance)
    
    @property
    def confidence(self) -> str:

        if self.distance <= 0.25:
            return "HIGH"

        if self.distance <= 0.45:
            return "MEDIUM"

        return "LOW"