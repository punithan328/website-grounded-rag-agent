from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)

from app.config import ALLOWED_DOMAIN


# ============================================================
# URL configuration
# ============================================================

# Query parameters that are normally tracking-related
TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "msclkid",
    "ref",
}

# File extensions that we don't want to crawl as HTML pages
IGNORED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".css",
    ".js",
    ".map",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".zip",
    ".tar",
    ".gz",
    ".pdf",
    ".xml",
    ".json",
}


# URL path patterns that are normally not useful
IGNORED_PATH_SEGMENTS = {
    "/login",
    "/logout",
    "/signin",
    "/signup",
    "/register",
    "/search",
}


# ============================================================
# Normalize URL
# ============================================================

def normalize_url(
    url: str,
    base_url: str | None = None,
) -> str | None:
    """
    Convert a URL into a canonical representation.

    Examples:

        /docs
            ->
        https://docs.trychroma.com/docs

        https://docs.trychroma.com/docs/
            ->
        https://docs.trychroma.com/docs

        https://docs.trychroma.com/docs#intro
            ->
        https://docs.trychroma.com/docs
    """

    if not url:
        return None

    url = url.strip()

    # Ignore non-web links
    if url.startswith(
        (
            "mailto:",
            "javascript:",
            "tel:",
            "data:",
        )
    ):
        return None

    # Convert relative URLs to absolute URLs
    if base_url:
        url = urljoin(base_url, url)

    parsed = urlparse(url)

    # Only HTTP/HTTPS URLs
    if parsed.scheme.lower() not in {
        "http",
        "https",
    }:
        return None

    # Hostname must exist
    if not parsed.hostname:
        return None

    scheme = parsed.scheme.lower()

    hostname = parsed.hostname.lower()

    # Remove default ports
    netloc = hostname

    if parsed.port:
        if not (
            (scheme == "http" and parsed.port == 80)
            or
            (scheme == "https" and parsed.port == 443)
        ):
            netloc = f"{hostname}:{parsed.port}"

    # Normalize path
    path = parsed.path or "/"

    # Remove repeated trailing slash
    if path != "/":
        path = path.rstrip("/")

    # Remove tracking query parameters
    query_parameters = parse_qsl(
        parsed.query,
        keep_blank_values=True,
    )

    filtered_parameters = [
        (key, value)
        for key, value in query_parameters
        if key.lower() not in TRACKING_PARAMETERS
    ]

    # Sort query parameters for deterministic URLs
    filtered_parameters.sort()

    query = urlencode(
        filtered_parameters,
        doseq=True,
    )

    # IMPORTANT:
    # Fragment (#section) is removed.
    # It points to a location inside the same page.
    normalized = urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            query,
            "",
        )
    )

    return normalized


# ============================================================
# Domain validation
# ============================================================

def is_same_domain(
    url: str,
    allowed_domain: str = ALLOWED_DOMAIN,
) -> bool:
    """
    Check whether URL belongs to the allowed domain.

    Example:

        docs.trychroma.com       -> True
        github.com                -> False
        evil-docs.trychroma.com  -> False
    """

    try:
        hostname = urlparse(url).hostname

        if not hostname:
            return False

        hostname = hostname.lower().rstrip(".")

        allowed_domain = (
            allowed_domain
            .lower()
            .rstrip(".")
        )

        return hostname == allowed_domain

    except ValueError:
        return False


# ============================================================
# File extension validation
# ============================================================

def has_ignored_extension(url: str) -> bool:
    """
    Return True if URL points to a file/resource
    that we don't want to crawl as an HTML page.
    """

    path = urlparse(url).path.lower()

    return any(
        path.endswith(extension)
        for extension in IGNORED_EXTENSIONS
    )


# ============================================================
# Path validation
# ============================================================

def has_ignored_path(url: str) -> bool:
    """
    Reject paths such as /login, /search, etc.
    """

    path = urlparse(url).path.lower().rstrip("/")

    for ignored_segment in IGNORED_PATH_SEGMENTS:

        if (
            path == ignored_segment
            or path.startswith(
                ignored_segment + "/"
            )
        ):
            return True

    return False


# ============================================================
# Page URL validation
# ============================================================

def is_valid_page_url(
    url: str,
    allowed_domain: str = ALLOWED_DOMAIN,
) -> bool:
    """
    Final validation before a URL enters the crawl queue.
    """

    if not url:
        return False

    normalized = normalize_url(url)

    if not normalized:
        return False

    # Same-domain restriction
    if not is_same_domain(
        normalized,
        allowed_domain,
    ):
        return False

    # Don't crawl assets
    if has_ignored_extension(normalized):
        return False

    # Don't crawl ignored paths
    if has_ignored_path(normalized):
        return False

    return True


# ============================================================
# Resolve relative URL
# ============================================================

def resolve_url(
    href: str,
    base_url: str,
) -> str | None:
    """
    Convert an href found on a page into a normalized
    absolute URL.
    """

    return normalize_url(
        href,
        base_url=base_url,
    )