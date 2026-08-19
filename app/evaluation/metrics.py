from dataclasses import dataclass


@dataclass
class QuestionEvaluation:
    question_id: str
    category: str

    retrieved_urls: list[str]
    expected_urls: list[str]

    answerable: bool

    hit_at_k: bool
    reciprocal_rank: float

def false_positive_rate(
    evaluations,
) -> float:

    unanswerable = [
        item
        for item in evaluations
        if not item.answerable
    ]

    if not unanswerable:
        return 0.0

    false_positives = sum(
        bool(item.retrieved_urls)
        for item in unanswerable
    )

    return (
        false_positives
        / len(unanswerable)
    )
def recall_at_k(
    evaluations: list[QuestionEvaluation],
) -> float:

    if not evaluations:
        return 0.0

    hits = sum(
        evaluation.hit_at_k
        for evaluation in evaluations
        if evaluation.answerable
    )

    total = sum(
        evaluation.answerable
        for evaluation in evaluations
    )

    if total == 0:
        return 0.0

    return hits / total


def mean_reciprocal_rank(
    evaluations: list[QuestionEvaluation],
) -> float:

    answerable = [
        evaluation
        for evaluation in evaluations
        if evaluation.answerable
    ]

    if not answerable:
        return 0.0

    return sum(
        evaluation.reciprocal_rank
        for evaluation in answerable
    ) / len(answerable)