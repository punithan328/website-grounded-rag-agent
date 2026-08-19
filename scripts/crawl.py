from app.config import (
    ALLOWED_DOMAIN,
    MAX_PAGES,
    REGISTRY_DB,
    SEED_URL,
)

from app.ingestion.crawler import (
    WebCrawler,
)

from app.ingestion.registry import (
    IngestionRegistry,
)
from app.logger import logger


def main():

    logger.info("%s", "=" * 70)
    logger.info("WEBSITE CRAWLER")
    logger.info("%s", "=" * 70)

    logger.info("Website: %s", SEED_URL)

    logger.info("Domain: %s", ALLOWED_DOMAIN)

    logger.info("Maximum pages: %s", MAX_PAGES)

    registry = IngestionRegistry(
        REGISTRY_DB
    )

    crawler = WebCrawler(
        seed_url=SEED_URL,
        allowed_domain=ALLOWED_DOMAIN,
        max_pages=MAX_PAGES,
        registry=registry,
    )

    result = crawler.crawl()

    logger.info("%s", "\n" + "=" * 70)
    logger.info("CRAWL SUMMARY")
    logger.info("%s", "=" * 70)

    logger.info("Discovered URLs: %s", result['discovered'])

    logger.info("Visited URLs: %s", result['visited'])

    logger.info("Successful pages: %s", result['successful'])

    logger.info("Failed pages: %s", result['failed'])

    logger.info("Remaining queue: %s", result['remaining_queue'])

    logger.info("Crawled pages:")

    for page in result["pages"]:

        logger.info("URL: %s", page['url'])

        logger.info("Status: %s", page['status_code'])

        logger.info("Hash: %s", page['content_hash'])

        logger.info("Raw HTML: %s", page['raw_path'])

    logger.info("%s", "\n" + "=" * 70)

    stats = registry.get_statistics()

    logger.info("REGISTRY")
    logger.info("%s", "=" * 70)

    for key, value in stats.items():
        logger.info("%s: %s", key, value)


if __name__ == "__main__":
    main()