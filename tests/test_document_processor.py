from app.ingestion.document_processor import (
    DocumentProcessor,
)


MOCK_HTML = """
<html>

<head>
    <title>Chroma Collections</title>
</head>

<body>

<main>

<h1>Collections</h1>

<p>
A collection is a logical grouping of documents
and embeddings. Collections allow applications
to organize related information and perform
semantic search over stored documents. This is
important when building retrieval augmented
generation applications because the collection
provides a persistent location for vectorized
information.
</p>

<h2>Creating Collections</h2>

<p>
Applications can create collections using a client
API. After creating the collection, applications
can add documents, metadata, and embeddings to it.
The collection can then be queried for semantically
similar information during retrieval.
</p>

<pre>
<code class="language-python">
collection = client.create_collection(
    name="documents"
)
</code>
</pre>

</main>

</body>

</html>
"""


def test_document_processing():

    processor = DocumentProcessor()

    page = processor.process(
        html=MOCK_HTML,
        url="https://docs.trychroma.com/docs",
    )

    assert page is not None

    assert page.is_valid

    assert page.content_hash

    assert page.word_count > 0

    assert len(page.blocks) > 0

    assert any(
        block.block_type == "heading"
        for block in page.blocks
    )

    assert any(
        block.block_type == "paragraph"
        for block in page.blocks
    )

    assert any(
        block.block_type == "code"
        for block in page.blocks
    )