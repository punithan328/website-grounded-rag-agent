import hashlib
import time
from collections import deque
from pathlib import Path
from typing import Optional

import httpx
from app.ingestion.registry import (
    IngestionRegistry,
)

from app.logger import logger
from app.config import (
    ALLOWED_DOMAIN,
    CRAWL_RAW_HTML,
    MAX_PAGES,
    MAX_RETRIES,
    RAW_DATA_DIR,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    SEED_URL,
    USER_AGENT,
)

from app.ingestion.link_discovery import (
    InternalLinkDiscovery,
)

from app.ingestion.sitemap import (
    SitemapDiscovery,
)

from app.ingestion.url_manager import (
    is_valid_page_url,
    normalize_url,
)


class WebCrawler:
    """
    Bounded website crawler.

    Responsibilities:
    - Discover URLs
    - Normalize/filter URLs
    - Fetch HTML
    - Retry failed requests
    - Calculate content hashes
    - Store raw HTML
    - Discover additional internal links
    """

    def __init__(
        self,
        seed_url: str = SEED_URL,
        allowed_domain: str = ALLOWED_DOMAIN,
        max_pages: int = MAX_PAGES,
        registry: IngestionRegistry | None = None,
    ):

        self.seed_url = normalize_url(
            seed_url
        )

        self.allowed_domain = (
            allowed_domain
        )
        self.registry = registry

        self.max_pages = max_pages

        self.link_discovery = (
            InternalLinkDiscovery(
                allowed_domain=allowed_domain
            )
        )

        self.sitemap_discovery = (
            SitemapDiscovery(
                allowed_domain=allowed_domain
            )
        )

        self.visited_urls: set[str] = set()

        self.discovered_urls: set[str] = set()

        self.failed_urls: set[str] = set()

        self.crawled_pages: list[dict] = []
        
        

    # ========================================================
    # HTTP client
    # ========================================================

    def _create_client(self) -> httpx.Client:

        return httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT
            },
        )
        
    def register_website(self) -> int:
    
        if not self.registry:

            raise RuntimeError(
                "Ingestion registry is required"
            )

        return (
            self.registry
            .get_or_create_website(
                domain=self.allowed_domain,
                seed_url=self.seed_url,
            )
        )

    # ========================================================
    # URL discovery
    # ========================================================

    def discover_initial_urls(self) -> list[str]:

        urls = []

        # ----------------------------------------------------
        # Always include seed URL
        # ----------------------------------------------------

        if self.seed_url:

            urls.append(
                self.seed_url
            )

        # ----------------------------------------------------
        # Sitemap discovery
        # ----------------------------------------------------

        try:

            sitemap_urls = (
                self.sitemap_discovery
                .discover_from_website(
                    self.seed_url
                )
            )

            urls.extend(
                sitemap_urls
            )

        except Exception as exc:

            logger.warning(
                "Sitemap discovery failed: %s",
                exc,
            )

        # ----------------------------------------------------
        # Normalize + validate + deduplicate
        # ----------------------------------------------------

        valid_urls = []

        for url in urls:

            normalized = normalize_url(
                url
            )

            if not normalized:
                continue

            if not is_valid_page_url(
                normalized,
                self.allowed_domain,
            ):
                continue

            if normalized in valid_urls:
                continue

            valid_urls.append(
                normalized
            )

        return valid_urls

    # ========================================================
    # Fetch page
    # ========================================================

    def fetch_page(
        self,
        client: httpx.Client,
        url: str,
    ) -> Optional[dict]:

        for attempt in range(
            1,
            MAX_RETRIES + 1,
        ):

            try:

                response = client.get(
                    url
                )

                status_code = (
                    response.status_code
                )

                # ------------------------------------------------
                # Successful response
                # ------------------------------------------------

                if status_code == 200:

                    content_type = (
                        response.headers
                        .get(
                            "content-type",
                            ""
                        )
                        .lower()
                    )

                    # We only want HTML pages
                    if (
                        "text/html" not in content_type
                        and "application/xhtml+xml" not in content_type
                    ):
                        logger.debug(
                            "Skipping non-HTML: %s",
                            content_type,
                        )

                        return None

                    html = response.text

                    if not html.strip():
                        logger.debug(
                            "Empty response for %s",
                            url,
                        )

                        return None

                    content_hash = (
                        self.calculate_hash(
                            html
                        )
                    )

                    return {
                        "url": url,
                        "final_url": str(
                            response.url
                        ),
                        "status_code": status_code,
                        "content_type": content_type,
                        "html": html,
                        "content_hash": content_hash,
                    }

                # ------------------------------------------------
                # Don't retry permanent client errors
                # ------------------------------------------------

                if 400 <= status_code < 500:

                    logger.warning(
                        "HTTP %s returned for %s",
                        status_code,
                        url,
                    )

                    return {
                        "url": url,
                        "final_url": str(
                            response.url
                        ),
                        "status_code": status_code,
                        "content_type": "",
                        "html": "",
                        "content_hash": None,
                    }

                # ------------------------------------------------
                # Retry server errors
                # ------------------------------------------------

                logger.info(
                    "HTTP %s, attempt %s/%s for %s",
                    status_code,
                    attempt,
                    MAX_RETRIES,
                    url,
                )

            except httpx.RequestError as exc:

                logger.warning(
                    "Request failed for %s: %s",
                    url,
                    exc,
                )

            # ----------------------------------------------------
            # Retry delay
            # ----------------------------------------------------

            if attempt < MAX_RETRIES:

                retry_delay = (
                    REQUEST_DELAY * attempt
                )

                time.sleep(
                    retry_delay
                )

        return None

    # ========================================================
    # Content hash
    # ========================================================

    @staticmethod
    def calculate_hash(
        content: str,
    ) -> str:

        return hashlib.sha256(
            content.encode(
                "utf-8",
                errors="ignore",
            )
        ).hexdigest()

    # ========================================================
    # Save raw HTML
    # ========================================================

    def save_raw_html(
        self,
        url: str,
        html: str,
    ) -> Optional[Path]:

        if not CRAWL_RAW_HTML:
            return None

        content_hash = (
            self.calculate_hash(html)
        )

        filename = (
            f"{content_hash}.html"
        )

        file_path = (
            RAW_DATA_DIR / filename
        )

        file_path.write_text(
            html,
            encoding="utf-8",
        )

        return file_path

    # ========================================================
    # Process a single page
    # ========================================================

    def process_page(
        self,
        client: httpx.Client,
        url: str,
    ) -> Optional[dict]:

        logger.info("Crawling: %s", url)

        result = self.fetch_page(
            client,
            url,
        )

        if not result:
            self.failed_urls.add(url)
            return None

        status_code = result["status_code"]

        final_url = normalize_url(
            result["final_url"]
        )

        if not final_url:
            self.failed_urls.add(url)
            return None

        # ========================================================
        # Handle HTTP errors
        # ========================================================

        if status_code != 200:

            if self.registry:

                self.registry.upsert_page(
                    website_id=self.website_id,
                    url=url,
                    canonical_url=final_url,
                    status="crawl_failed",
                    http_status=status_code,
                )

            self.failed_urls.add(url)

            return result

        html = result["html"]

        new_content_hash = result["content_hash"]

        # ========================================================
        # IMPORTANT:
        # Read existing page BEFORE updating it
        # ========================================================

        existing_page = None

        if self.registry:

            existing_page = (
                self.registry.get_page(
                    website_id=self.website_id,
                    canonical_url=final_url,
                )
            )

        # ========================================================
        # Existing page (do not decide freshness here)
        # The canonical content hash decision is made later
        # in the processing pipeline after extraction.
        # ========================================================

        if existing_page:

            old_status = existing_page["status"]

            logger.info(
                "Existing page found (status=%s) %s",
                old_status,
                final_url,
            )

        else:

            logger.info(
                "New page → processing %s",
                final_url,
            )

        # ========================================================
        # Now update registry
        # ========================================================

        page_id = None

        if self.registry:

            # Do NOT store a canonical content hash yet —
            # the canonical hash must be computed from
            # cleaned extracted content in the pipeline.
            page_id = (
                self.registry.upsert_page(
                    website_id=self.website_id,
                    url=url,
                    canonical_url=final_url,
                    content_hash=None,
                    status="crawled",
                    http_status=status_code,
                )
            )

            self.registry.mark_page_crawled(
                page_id
            )

        # ========================================================
        # Save raw HTML
        # ========================================================

        raw_path = self.save_raw_html(
            final_url,
            html,
        )

        # ========================================================
        # Discover internal links
        # ========================================================

        links = (
            self.link_discovery.discover(
                html=html,
                base_url=final_url,
            )
        )

        logger.info(
            "Discovered %s internal links for %s",
            len(links),
            final_url,
        )

        result["discovered_links"] = links
        result["raw_path"] = (
            str(raw_path)
            if raw_path
            else None
        )
        result["page_id"] = page_id
        result["unchanged"] = False

        return result

    # ========================================================
    # Main crawl
    # ========================================================

    def crawl(self) -> dict:
        if not self.registry:
    
            raise RuntimeError(
                "Ingestion registry is required"
            )

        self.website_id = (
            self.register_website()
        )

        initial_urls = (
            self.discover_initial_urls()
        )

        logger.info("Initial URLs discovered: %s", len(initial_urls))

        queue = deque()

        # ----------------------------------------------------
        # Seed queue
        # ----------------------------------------------------

        for url in initial_urls:

            if (
                url not in
                self.discovered_urls
            ):

                queue.append(url)

                self.discovered_urls.add(
                    url
                )

        # ----------------------------------------------------
        # Crawl
        # ----------------------------------------------------

        with self._create_client() as client:

            while (
                queue
                and
                len(self.visited_urls)
                < self.max_pages
            ):

                url = queue.popleft()

                # ------------------------------------------------
                # Already visited
                # ------------------------------------------------

                if url in self.visited_urls:
                    continue

                # ------------------------------------------------
                # Validate again
                # ------------------------------------------------

                if not is_valid_page_url(
                    url,
                    self.allowed_domain,
                ):
                    continue

                self.visited_urls.add(
                    url
                )

                # ------------------------------------------------
                # Fetch/process
                # ------------------------------------------------

                result = (
                    self.process_page(
                        client,
                        url,
                    )
                )

                if result:

                    self.crawled_pages.append(
                        result
                    )

                    # --------------------------------------------
                    # Add newly discovered URLs
                    # --------------------------------------------

                    for link in result.get(
                        "discovered_links",
                        [],
                    ):

                        if link in (
                            self.discovered_urls
                        ):
                            continue

                        if not is_valid_page_url(
                            link,
                            self.allowed_domain,
                        ):
                            continue

                        self.discovered_urls.add(
                            link
                        )

                        queue.append(link)

                # ------------------------------------------------
                # Respect crawl delay
                # ------------------------------------------------

                time.sleep(
                    REQUEST_DELAY
                )

        return {
            "seed_url": self.seed_url,
            "max_pages": self.max_pages,
            "discovered": len(
                self.discovered_urls
            ),
            "visited": len(
                self.visited_urls
            ),
            "successful": len(
                self.crawled_pages
            ),
            "failed": len(
                self.failed_urls
            ),
            "remaining_queue": len(
                queue
            ),
            "pages": self.crawled_pages,
        }