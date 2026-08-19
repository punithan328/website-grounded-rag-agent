from pathlib import Path

from app.retrieval.retriever import (
    WebsiteRetriever,
)

from app.evaluation.evaluator import (
    RetrievalEvaluator,
)
from app.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[1]

QUESTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "retrieval_questions.json"
)


def main():

    logger.info("%s", "=" * 80)
    logger.info("RETRIEVAL EVALUATION")
    logger.info("%s", "=" * 80)

    retriever = WebsiteRetriever(
        top_k=5
    )

    evaluator = RetrievalEvaluator(
        retriever
    )

    questions = (
        evaluator.load_questions(
            QUESTIONS_FILE
        )
    )

    logger.info("Questions: %s", len(questions))

    evaluations = evaluator.evaluate(
        questions,
        top_k=5,
    )

    evaluator.print_summary(
        evaluations
    )
            
    
            
    evaluator.print_category_summary(
        evaluations
    )
    
    
    def unanswerable_retrieval_rate(
        evaluations,
    ):
    
        unanswerable = [
            item
            for item in evaluations
            if not item.answerable
        ]
    
        if not unanswerable:
            return 0.0
    
        false_positive = sum(
            bool(item.retrieved_urls)
            for item in unanswerable
        )
    
        return (
            false_positive
            / len(unanswerable)
        )


if __name__ == "__main__":
    main()