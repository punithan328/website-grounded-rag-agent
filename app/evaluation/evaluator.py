import json
from pathlib import Path

from app.retrieval.retriever import (
    WebsiteRetriever,
)

from app.evaluation.metrics import (
    QuestionEvaluation,
    mean_reciprocal_rank,
    recall_at_k,
)
from app.logger import logger


class RetrievalEvaluator:

    def __init__(
        self,
        retriever: WebsiteRetriever,
    ):
        self.retriever = retriever

    @staticmethod
    def load_questions(
        path: str | Path,
    ) -> list[dict]:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    @staticmethod
    def normalize_url(
        url: str,
    ) -> str:

        return (
            url
            .strip()
            .rstrip("/")
            .lower()
        )

    def evaluate_question(
        self,
        question: dict,
        top_k: int = 5,
    ) -> QuestionEvaluation:

        results = self.retriever.retrieve(
            query=question["question"],
            top_k=top_k,
        )

        retrieved_urls = []

        for result in results:

            url = (
                result.metadata.get(
                    "source_url"
                )
                or result.metadata.get(
                    "url"
                )
            )

            if url:
                retrieved_urls.append(
                    self.normalize_url(url)
                )

        expected_urls = [
            self.normalize_url(url)
            for url in question.get(
                "expected_urls",
                [],
            )
        ]

        # ------------------------------------------------
        # Find first relevant result
        # ------------------------------------------------

        reciprocal_rank = 0.0
        hit_at_k = False

        for rank, url in enumerate(
            retrieved_urls,
            start=1,
        ):

            if url in expected_urls:

                hit_at_k = True

                reciprocal_rank = (
                    1.0 / rank
                )

                break

        return QuestionEvaluation(
            question_id=question["id"],
            category=question["category"],
            retrieved_urls=retrieved_urls,
            expected_urls=expected_urls,
            answerable=question["answerable"],
            hit_at_k=hit_at_k,
            reciprocal_rank=reciprocal_rank,
        )

    def evaluate(
        self,
        questions: list[dict],
        top_k: int = 5,
    ) -> list[QuestionEvaluation]:

        evaluations = []

        for question in questions:

            evaluation = (
                self.evaluate_question(
                    question,
                    top_k=top_k,
                )
            )

            evaluations.append(
                evaluation
            )

        return evaluations

    @staticmethod
    def print_summary(
        evaluations: list[QuestionEvaluation],
    ) -> None:

        logger.info("%s", "\n")
        logger.info("%s", "=" * 80)
        logger.info("RETRIEVAL EVALUATION")
        logger.info("%s", "=" * 80)

        recall = recall_at_k(evaluations)

        mrr = mean_reciprocal_rank(evaluations)

        logger.info("Recall@K: %.3f", recall)

        logger.info("MRR:      %.3f", mrr)

        logger.info("\nPer-question results:")
        logger.info("%s", "-" * 80)

        for evaluation in evaluations:

            status = ("PASS" if evaluation.hit_at_k else "MISS")

            logger.info(
                "%s | %s | %s | RR=%.3f",
                evaluation.question_id,
                f"{evaluation.category:15}",
                status,
                evaluation.reciprocal_rank,
            )
    def print_category_summary(
        self,
        evaluations,
    ) -> None:

        from collections import defaultdict

        grouped = defaultdict(list)

        for evaluation in evaluations:

            grouped[
                evaluation.category
            ].append(evaluation)

        logger.info("%s", "\n")
        logger.info("%s", "=" * 80)
        logger.info("CATEGORY RESULTS")
        logger.info("%s", "=" * 80)

        for category, items in grouped.items():

            answerable = [
                item
                for item in items
                if item.answerable
            ]

            if not answerable:

                logger.info("%s N/A", f"{category:20}")

                continue

            hits = sum(item.hit_at_k for item in answerable)

            recall = hits / len(answerable)

            logger.info("%s Recall@K=%.3f", f"{category:20}", recall)
    