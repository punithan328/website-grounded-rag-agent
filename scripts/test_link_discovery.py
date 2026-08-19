import httpx

from app.config import (
    ALLOWED_DOMAIN,
    REQUEST_TIMEOUT,
    SEED_URL,
)

from app.ingestion.link_discovery import (
    InternalLinkDiscovery,
)


def main():

    print(
        f"Fetching: {SEED_URL}"
    )

    response = httpx.get(
        SEED_URL,
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "WebsiteGroundedRAGAgent/1.0"
            )
        },
    )

    print(
        f"HTTP status: {response.status_code}"
    )

    response.raise_for_status()

    discovery = InternalLinkDiscovery(
        allowed_domain=ALLOWED_DOMAIN
    )

    urls = discovery.discover(
        html=response.text,
        base_url=str(response.url),
    )

    print("\n" + "=" * 70)
    print("INTERNAL LINK DISCOVERY")
    print("=" * 70)

    print(
        f"\nTotal valid internal URLs: "
        f"{len(urls)}"
    )

    for index, url in enumerate(
        urls[:50],
        start=1,
    ):
        print(
            f"{index:02d}. {url}"
        )


if __name__ == "__main__":
    main()