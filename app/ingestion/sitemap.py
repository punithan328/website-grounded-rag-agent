import xml.etree.ElementTree as ET
from typing import List

import httpx

from app.config import REQUEST_TIMEOUT
from app.ingestion.url_manager import (
    normalize_url,
    is_valid_page_url,
)
from app.logger import logger


class SitemapDiscovery:
    """
    Discovers URLs from a website sitemap.

    Sitemap discovery is optional. If the sitemap is unavailable,
    the caller can fall back to internal-link discovery.
    """

    def __init__(
        self,
        allowed_domain: str,
        timeout: int = REQUEST_TIMEOUT,
    ):
        self.allowed_domain = allowed_domain
        self.timeout = timeout

    # ========================================================
    # Fetch sitemap
    # ========================================================

    def fetch_sitemap(
        self,
        sitemap_url: str,
    ) -> str | None:

        try:

            response = httpx.get(
                sitemap_url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "WebsiteGroundedRAGAgent/1.0"
                    )
                },
            )

            if response.status_code != 200:
                return None

            content_type = (
                response.headers
                .get("content-type", "")
                .lower()
            )

            # Some servers incorrectly return XML
            # with a text/html content type, so don't
            # reject based only on content type.
            if not response.text.strip():
                return None

            return response.text

        except (
            httpx.RequestError,
            httpx.HTTPError,
        ):
            return None

    # ========================================================
    # Parse sitemap XML
    # ========================================================

    def parse_sitemap(
        self,
        xml_content: str,
    ) -> List[str]:

        try:

            root = ET.fromstring(
                xml_content
            )

        except ET.ParseError:
            return []

        urls = []

        # XML namespaces are common in sitemap files.
        # We therefore inspect elements by their local name.
        for element in root.iter():

            if self._local_name(
                element.tag
            ) != "loc":
                continue

            if not element.text:
                continue

            raw_url = element.text.strip()

            normalized = normalize_url(
                raw_url
            )

            if not normalized:
                continue

            if not is_valid_page_url(
                normalized,
                self.allowed_domain,
            ):
                continue

            urls.append(normalized)

        return self._deduplicate(urls)

    # ========================================================
    # Discover URLs
    # ========================================================

    def discover(
        self,
        sitemap_urls: List[str],
    ) -> List[str]:

        discovered_urls = []

        for sitemap_url in sitemap_urls:

            logger.info("Checking sitemap: %s", sitemap_url)

            xml_content = self.fetch_sitemap(
                sitemap_url
            )

            if not xml_content:
                logger.info("Sitemap unavailable: %s", sitemap_url)

                continue

            urls = self.parse_sitemap(
                xml_content
            )

            logger.info("Found %s valid URLs in %s", len(urls), sitemap_url)

            discovered_urls.extend(
                urls
            )

        return self._deduplicate(
            discovered_urls
        )

    # ========================================================
    # XML helper
    # ========================================================

    @staticmethod
    def _local_name(
        tag: str,
    ) -> str:

        if "}" in tag:
            return tag.split(
                "}",
                1
            )[1]

        return tag

    # ========================================================
    # Deduplication
    # ========================================================

    @staticmethod
    def _deduplicate(
        urls: List[str],
    ) -> List[str]:

        # dict preserves insertion order
        return list(
            dict.fromkeys(urls)
        )
    
    def discover_from_robots(
        self,
        robots_url: str,
    ) -> List[str]:

        try:

            response = httpx.get(
                robots_url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "WebsiteGroundedRAGAgent/1.0"
                    )
                },
            )

            if response.status_code != 200:
                return []

        except (
            httpx.RequestError,
            httpx.HTTPError,
        ):
            return []

        sitemap_urls = []

        for line in response.text.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.lower().startswith(
                "sitemap:"
            ):

                sitemap_url = line.split(
                    ":",
                    1
                )[1].strip()

                normalized = normalize_url(
                    sitemap_url
                )

                if normalized:
                    sitemap_urls.append(
                        normalized
                    )

        return self._deduplicate(
            sitemap_urls
        )
        
    def discover_from_website(
        self,
        base_url: str,
    ) -> List[str]:

        parsed = httpx.URL(base_url)

        origin = (
            f"{parsed.scheme}://"
            f"{parsed.host}"
        )

        # ----------------------------------------------------
        # First: robots.txt
        # ----------------------------------------------------

        robots_url = (
            f"{origin}/robots.txt"
        )

        sitemap_urls = (
            self.discover_from_robots(
                robots_url
            )
        )

        # ----------------------------------------------------
        # If robots.txt didn't provide a sitemap,
        # try common locations.
        # ----------------------------------------------------

        if not sitemap_urls:

            sitemap_urls = [
                f"{origin}/sitemap.xml",
                f"{origin}/sitemap_index.xml",
            ]

        logger.info("Sitemap candidates:")

        for sitemap_url in sitemap_urls:
            logger.info("  - %s", sitemap_url)

        # ----------------------------------------------------
        # Discover pages
        # ----------------------------------------------------

        return self.discover(
            sitemap_urls
        )