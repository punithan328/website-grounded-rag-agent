from dataclasses import dataclass
from typing import Any

from app.logger import logger


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
        score = 1.0 / (1.0 + self.distance)
        logger.info("RetrievalResult.score computed: distance=%s score=%s", self.distance, score)
        return score

    @property
    def confidence(self) -> str:
        if self.distance <= 0.25:
            logger.info("RetrievalResult.confidence: HIGH for distance=%s", self.distance)
            return "HIGH"

        if self.distance <= 0.45:
            logger.info("RetrievalResult.confidence: MEDIUM for distance=%s", self.distance)
            return "MEDIUM"

        logger.info("RetrievalResult.confidence: LOW for distance=%s", self.distance)
        return "LOW"


logger.info("RetrievalResult model loaded")