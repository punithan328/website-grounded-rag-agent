from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer
from app.logger import logger


class SentenceTransformerEmbedder:
    """
    Generates embeddings using SentenceTransformer.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model_name = model_name

        logger.info("Initializing embedder with model %s", model_name)

        try:
            self.model = SentenceTransformer(
                model_name
            )
        except Exception as exc:
            logger.exception("Failed to load SentenceTransformer model: %s", exc)
            raise

    # ========================================================
    # Single text
    # ========================================================

    def embed(
        self,
        text: str,
    ) -> list[float]:

        if not text.strip():

            raise ValueError(
                "Cannot embed empty text"
            )

        vector = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    # ========================================================
    # Batch embeddings
    # ========================================================

    def embed_batch(
        self,
        texts: Sequence[str],
        batch_size: int = 32,
    ) -> list[list[float]]:

        if not texts:
            return []

        for text in texts:

            if not text.strip():

                raise ValueError(
                    "Cannot embed empty text"
                )

        vectors = self.model.encode(
            list(texts),
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return vectors.tolist()

    # ========================================================
    # Dimension
    # ========================================================

    def dimension(self) -> int:

        dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if dimension is None:

            raise RuntimeError(
                "Could not determine embedding dimension"
            )

        return int(dimension)

    # ========================================================
    # Similarity helper
    # ========================================================

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:

        a = np.asarray(
            vector_a,
            dtype=np.float32,
        )

        b = np.asarray(
            vector_b,
            dtype=np.float32,
        )

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:

            return 0.0

        return float(
            np.dot(a, b)
            / denominator
        )