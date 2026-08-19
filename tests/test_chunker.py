from app.ingestion.chunker import (
    SemanticChunker,
)

from app.models.page import (
    ContentBlock,
    ExtractedPage,
)


def create_test_page():

    blocks = [
        ContentBlock(
            block_type="heading",
            content="Ranking and Scoring",
            level=1,
        ),

        ContentBlock(
            block_type="paragraph",
            content=(
                "Ranking expressions allow search "
                "results to be scored and ordered."
            ),
        ),

        ContentBlock(
            block_type="heading",
            content="How Ranking Works",
            level=2,
        ),

        ContentBlock(
            block_type="paragraph",
            content=(
                "Chroma uses distance based scoring "
                "where lower scores indicate better "
                "matches."
            ),
        ),

        ContentBlock(
            block_type="heading",
            content="Expression Evaluation",
            level=3,
        ),

        ContentBlock(
            block_type="paragraph",
            content=(
                "An expression can contain one or "
                "more KNN operations."
            ),
        ),

        ContentBlock(
            block_type="code",
            content=(
                'rank = Knn(query="machine learning")'
            ),
            language="python",
        ),
    ]

    return ExtractedPage(
        url="https://docs.trychroma.com/ranking",
        canonical_url=(
            "https://docs.trychroma.com/ranking"
        ),
        title="Ranking and Scoring",
        description=None,
        blocks=blocks,
    )


def test_chunk_page():

    page = create_test_page()

    chunker = SemanticChunker(
        target_tokens=100,
        overlap_tokens=20,
        max_tokens=150,
    )

    chunks = chunker.chunk_page(
        page,
        page_id=1,
    )

    assert len(chunks) > 0

    for chunk in chunks:

        assert chunk.content

        assert chunk.chunk_id

        assert chunk.content_hash

        assert chunk.token_count > 0

        assert chunk.source_url == page.url


def test_section_path_preserved():

    page = create_test_page()

    chunker = SemanticChunker(
        target_tokens=500,
        overlap_tokens=50,
        max_tokens=700,
    )

    chunks = chunker.chunk_page(
        page,
        page_id=1,
    )

    assert any(
        "Ranking and Scoring"
        in chunk.section_path
        for chunk in chunks
    )


def test_code_block_preserved():

    page = create_test_page()

    chunker = SemanticChunker(
        target_tokens=500,
        overlap_tokens=50,
        max_tokens=700,
    )

    chunks = chunker.chunk_page(
        page,
        page_id=1,
    )

    code_chunks = [
        chunk
        for chunk in chunks
        if chunk.chunk_type
        in {"code", "mixed"}
    ]

    assert len(code_chunks) > 0

    assert any(
        "Knn("
        in chunk.content
        for chunk in code_chunks
    )


def test_token_count():

    chunker = SemanticChunker()

    text = (
        "ChromaDB provides vector search "
        "capabilities for retrieval systems."
    )

    count = chunker.count_tokens(
        text
    )

    assert count > 0
    
def test_small_chunks_are_merged():
    
    chunker = SemanticChunker(
        target_tokens=600,
        overlap_tokens=80,
        max_tokens=800,
    )

    chunks = [
        {
            "content": "Section A\n\n" + ("word " * 40),
            "chunk_type": "text",
            "section_path": ["A"],
            "heading": "A",
            "heading_level": 2,
            "code_language": None,
        },
        {
            "content": "Section B\n\n" + ("word " * 40),
            "chunk_type": "text",
            "section_path": ["B"],
            "heading": "B",
            "heading_level": 2,
            "code_language": None,
        },
    ]

    result = chunker._merge_small_chunks(
        chunks
    )

    assert len(result) == 1

    assert "Section A" in result[0]["content"]

    assert "Section B" in result[0]["content"]