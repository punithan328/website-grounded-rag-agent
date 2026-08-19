from app.ingestion.extractor import (
    ContentExtractor,
)

from app.ingestion.validator import (
    ContentValidator,
)

from app.models.page import (
    ContentBlock,
    ExtractedPage,
)


def create_valid_page():

    blocks = [
        ContentBlock(
            block_type="heading",
            content="Collections",
            level=1,
        ),
        ContentBlock(
            block_type="paragraph",
            content=(
                "A collection is a logical grouping "
                "of documents and embeddings. "
                "Collections allow applications to "
                "organize related information and "
                "perform semantic search over stored "
                "documents."
            ),
        ),
        ContentBlock(
            block_type="heading",
            content="Creating a Collection",
            level=2,
        ),
        ContentBlock(
            block_type="paragraph",
            content=(
                "Applications can create a collection "
                "using the ChromaDB client. The "
                "collection can then be used to add "
                "documents, embeddings, and metadata."
            ),
        ),
    ]

    return ExtractedPage(
        url="https://docs.trychroma.com/docs",
        canonical_url="https://docs.trychroma.com/docs",
        title="Collections",
        description=None,
        blocks=blocks,
    )


def test_valid_content():

    page = create_valid_page()

    validator = ContentValidator(
        min_words=20,
        min_characters=100,
    )

    result = validator.validate(
        page
    )

    assert result.is_valid

    assert result.rejection_reason is None

    assert result.content_hash

    assert result.word_count > 20


def test_empty_content():

    page = ExtractedPage(
        url="https://docs.trychroma.com/",
        canonical_url="https://docs.trychroma.com/",
        title="",
        description=None,
        blocks=[],
    )

    validator = ContentValidator()

    result = validator.validate(
        page
    )

    assert not result.is_valid

    assert (
        result.rejection_reason
        == "empty_content"
    )


def test_short_content():

    page = ExtractedPage(
        url="https://docs.trychroma.com/test",
        canonical_url="https://docs.trychroma.com/test",
        title="Test",
        description=None,
        blocks=[
            ContentBlock(
                block_type="paragraph",
                content="This is short.",
            )
        ],
    )

    validator = ContentValidator(
        min_words=80,
        min_characters=400,
    )

    result = validator.validate(
        page
    )

    assert not result.is_valid

    assert result.rejection_reason.startswith(
        "too_few_words"
    )


# def test_repeated_content():

#     repeated = (
#         "Navigation navigation navigation.\n"
#         * 20
#     )

#     page = ExtractedPage(
#         url="https://docs.trychroma.com/test",
#         canonical_url="https://docs.trychroma.com/test",
#         title="Test",
#         description=None,
#         blocks=[
#             ContentBlock(
#                 block_type="paragraph",
#                 content=repeated,
#             )
#         ],
#     )

#     validator = ContentValidator(
#         min_words=10,
#         min_characters=50,
#     )

#     result = validator.validate(
#         page
#     )

#     assert not result.is_valid

#     assert (
#         result.rejection_reason
#         == "mostly_repeated_content"
#     )


def test_hash_is_based_on_clean_content():

    page1 = create_valid_page()

    page2 = create_valid_page()

    validator = ContentValidator(
        min_words=20,
        min_characters=100,
    )

    result1 = validator.validate(
        page1
    )

    result2 = validator.validate(
        page2
    )

    assert (
        result1.content_hash
        == result2.content_hash
    )