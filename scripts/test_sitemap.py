from app.config import (
    ALLOWED_DOMAIN,
    SEED_URL,
)

from app.ingestion.sitemap import (
    SitemapDiscovery,
)


def main():

    discovery = SitemapDiscovery(
        allowed_domain=ALLOWED_DOMAIN
    )

    urls = discovery.discover_from_website(
        SEED_URL
    )

    print("\n" + "=" * 70)
    print("SITEMAP DISCOVERY RESULT")
    print("=" * 70)

    print(
        f"\nTotal valid URLs discovered: "
        f"{len(urls)}"
    )

    for index, url in enumerate(
        urls[:30],
        start=1,
    ):

        print(
            f"{index:02d}. {url}"
        )


if __name__ == "__main__":
    main()