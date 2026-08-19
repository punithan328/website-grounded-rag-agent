from app.ingestion.link_discovery import (
    InternalLinkDiscovery,
)


BASE_URL = (
    "https://docs.trychroma.com/"
)


MOCK_HTML = """
<!DOCTYPE html>

<html>

<head>
    <title>ChromaDB Documentation</title>
</head>

<body>

    <nav>

        <a href="/docs">
            Documentation
        </a>

        <a href="/docs/collections/">
            Collections
        </a>

        <a href="https://docs.trychroma.com/docs/embeddings">
            Embeddings
        </a>

        <a href="https://github.com/chroma-core/chroma">
            GitHub
        </a>

    </nav>

    <main>

        <h1>ChromaDB</h1>

        <a href="/docs/getting-started">
            Getting Started
        </a>

        <a href="/docs#collections">
            Collections Section
        </a>

        <a href="/logo.png">
            Logo
        </a>

        <a href="mailto:test@example.com">
            Email
        </a>

        <a href="javascript:void(0)">
            JavaScript
        </a>

    </main>

</body>

</html>
"""


def test_internal_link_discovery():

    discovery = InternalLinkDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.discover(
        html=MOCK_HTML,
        base_url=BASE_URL,
    )

    assert (
        "https://docs.trychroma.com/docs"
        in urls
    )

    assert (
        "https://docs.trychroma.com/docs/collections"
        in urls
    )

    assert (
        "https://docs.trychroma.com/docs/embeddings"
        in urls
    )

    assert (
        "https://docs.trychroma.com/docs/getting-started"
        in urls
    )


def test_external_links_are_removed():

    discovery = InternalLinkDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.discover(
        html=MOCK_HTML,
        base_url=BASE_URL,
    )

    assert (
        "https://github.com/chroma-core/chroma"
        not in urls
    )


def test_assets_are_removed():

    discovery = InternalLinkDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.discover(
        html=MOCK_HTML,
        base_url=BASE_URL,
    )

    assert (
        "https://docs.trychroma.com/logo.png"
        not in urls
    )


def test_fragments_are_normalized():

    discovery = InternalLinkDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.discover(
        html=MOCK_HTML,
        base_url=BASE_URL,
    )

    # /docs and /docs#collections represent
    # the same page.
    assert urls.count(
        "https://docs.trychroma.com/docs"
    ) == 1


def test_empty_html():

    discovery = InternalLinkDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.discover(
        html="",
        base_url=BASE_URL,
    )

    assert urls == []