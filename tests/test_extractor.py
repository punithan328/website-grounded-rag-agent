from app.ingestion.extractor import (
    ContentExtractor,
)


MOCK_HTML = """
<!DOCTYPE html>

<html>

<head>

    <title>
        ChromaDB Collections
    </title>

    <meta
        name="description"
        content="Learn about ChromaDB collections."
    >

    <script>
        console.log("This should be removed");
    </script>

</head>

<body>

    <nav>
        Home
        Documentation
        Search
    </nav>

    <main>

        <h1>Collections</h1>

        <p>
            A collection is a logical grouping
            of documents and embeddings.
        </p>

        <h2>Creating a Collection</h2>

        <p>
            You can create a collection using
            the ChromaDB client.
        </p>

        <pre>
            <code class="language-python">
client.create_collection("my_collection")
            </code>
        </pre>

        <h2>Collection Features</h2>

        <ul>
            <li>Stores documents</li>
            <li>Stores embeddings</li>
            <li>Supports metadata</li>
        </ul>

        <footer>
            This should not be included.
        </footer>

    </main>

</body>

</html>
"""


def test_extract_page():

    extractor = ContentExtractor()

    page = extractor.extract(
        html=MOCK_HTML,
        url="https://docs.trychroma.com/docs/collections",
    )

    assert page is not None

    assert (
        page.title
        == "ChromaDB Collections"
    )

    assert (
        page.description
        == "Learn about ChromaDB collections."
    )

    assert page.word_count > 0

    assert page.character_count > 0

    assert page.content_hash


def test_extract_headings():

    extractor = ContentExtractor()

    page = extractor.extract(
        MOCK_HTML,
        "https://docs.trychroma.com/docs/collections",
    )

    headings = [
        block
        for block in page.blocks
        if block.block_type == "heading"
    ]

    assert len(headings) == 3

    assert headings[0].content == "Collections"
    assert headings[0].level == 1

    assert (
        headings[1].content
        == "Creating a Collection"
    )

    assert headings[1].level == 2


def test_extract_code():

    extractor = ContentExtractor()

    page = extractor.extract(
        MOCK_HTML,
        "https://docs.trychroma.com/docs/collections",
    )

    code_blocks = [
        block
        for block in page.blocks
        if block.block_type == "code"
    ]

    assert len(code_blocks) == 1

    assert (
        'client.create_collection("my_collection")'
        in code_blocks[0].content
    )

    assert (
        code_blocks[0].language
        == "python"
    )


def test_extract_list():

    extractor = ContentExtractor()

    page = extractor.extract(
        MOCK_HTML,
        "https://docs.trychroma.com/docs/collections",
    )

    list_blocks = [
        block
        for block in page.blocks
        if block.block_type == "list"
    ]

    assert len(list_blocks) == 1

    assert (
        "Stores documents"
        in list_blocks[0].content
    )

    assert (
        "Stores embeddings"
        in list_blocks[0].content
    )


def test_scripts_are_removed():

    extractor = ContentExtractor()

    page = extractor.extract(
        MOCK_HTML,
        "https://docs.trychroma.com/docs/collections",
    )

    assert (
        "console.log"
        not in page.raw_text
    )


def test_footer_is_not_extracted():

    extractor = ContentExtractor()

    page = extractor.extract(
        MOCK_HTML,
        "https://docs.trychroma.com/docs/collections",
    )

    assert (
        "This should not be included"
        not in page.raw_text
    )


def test_empty_html():

    extractor = ContentExtractor()

    page = extractor.extract(
        "",
        "https://docs.trychroma.com/",
    )

    assert page is None