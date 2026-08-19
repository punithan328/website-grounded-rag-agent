from typing import List

from bs4 import BeautifulSoup

from app.ingestion.url_manager import (
    is_valid_page_url,
    resolve_url,
)


class InternalLinkDiscovery:
    """
    Extracts and validates internal HTML links from a page.
    """

    def __init__(
        self,
        allowed_domain: str,
    ):
        self.allowed_domain = allowed_domain

    # ========================================================
    # Discover links
    # ========================================================

    def discover(
        self,
        html: str,
        base_url: str,
    ) -> List[str]:
        """
        Extract all valid internal page URLs from HTML.
        """

        if not html:
            return []

        soup = BeautifulSoup(
            html,
            "lxml",
        )

        discovered_urls = []

        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            href = anchor.get("href")

            if not href:
                continue

            url = resolve_url(
                href,
                base_url,
            )

            if not url:
                continue

            if not is_valid_page_url(
                url,
                self.allowed_domain,
            ):
                continue

            discovered_urls.append(url)

        return self._deduplicate(
            discovered_urls
        )

    # ========================================================
    # Deduplicate
    # ========================================================

    @staticmethod
    def _deduplicate(
        urls: List[str],
    ) -> List[str]:

        return list(
            dict.fromkeys(urls)
        )