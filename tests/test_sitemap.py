from app.ingestion.sitemap import (
    SitemapDiscovery,
)


SAMPLE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

    <url>
        <loc>https://docs.trychroma.com/docs</loc>
    </url>

    <url>
        <loc>https://docs.trychroma.com/docs/collections/</loc>
    </url>

    <url>
        <loc>https://github.com/chroma-core/chroma</loc>
    </url>

    <url>
        <loc>
            https://docs.trychroma.com/logo.png
        </loc>
    </url>

</urlset>
"""


def test_parse_sitemap():

    discovery = SitemapDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.parse_sitemap(
        SAMPLE_SITEMAP
    )

    assert (
        "https://docs.trychroma.com/docs"
        in urls
    )

    assert (
        "https://docs.trychroma.com/docs/collections"
        in urls
    )

    # External domain must be removed
    assert (
        "https://github.com/chroma-core/chroma"
        not in urls
    )

    # Image must be removed
    assert (
        "https://docs.trychroma.com/logo.png"
        not in urls
    )


def test_sitemap_deduplication():

    sitemap = """<?xml version="1.0"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://docs.trychroma.com/docs</loc>
        </url>
        <url>
            <loc>https://docs.trychroma.com/docs/</loc>
        </url>
        <url>
            <loc>https://docs.trychroma.com/docs#test</loc>
        </url>
    </urlset>
    """

    discovery = SitemapDiscovery(
        allowed_domain="docs.trychroma.com"
    )

    urls = discovery.parse_sitemap(
        sitemap
    )

    assert urls == [
        "https://docs.trychroma.com/docs"
    ]