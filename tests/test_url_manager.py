from app.ingestion.url_manager import (
    normalize_url,
    is_same_domain,
    is_valid_page_url,
    has_ignored_extension,
    has_ignored_path,
    resolve_url,
)


BASE_URL = "https://docs.trychroma.com/"


# ============================================================
# Normalization tests
# ============================================================

def test_normalize_relative_url():

    result = normalize_url(
        "/docs",
        base_url=BASE_URL,
    )

    assert result == (
        "https://docs.trychroma.com/docs"
    )


def test_remove_trailing_slash():

    result = normalize_url(
        "https://docs.trychroma.com/docs/"
    )

    assert result == (
        "https://docs.trychroma.com/docs"
    )


def test_remove_fragment():

    result = normalize_url(
        "https://docs.trychroma.com/docs#collections"
    )

    assert result == (
        "https://docs.trychroma.com/docs"
    )


def test_remove_tracking_parameters():

    result = normalize_url(
        "https://docs.trychroma.com/docs"
        "?utm_source=google"
        "&utm_campaign=test"
    )

    assert result == (
        "https://docs.trychroma.com/docs"
    )


def test_preserve_meaningful_query_parameters():

    result = normalize_url(
        "https://docs.trychroma.com/docs"
        "?version=1"
    )

    assert result == (
        "https://docs.trychroma.com/docs"
        "?version=1"
    )


# ============================================================
# Domain tests
# ============================================================

def test_same_domain():

    assert is_same_domain(
        "https://docs.trychroma.com/docs"
    )


def test_external_domain():

    assert not is_same_domain(
        "https://github.com/chroma-core/chroma"
    )


def test_similar_but_different_domain():

    assert not is_same_domain(
        "https://evil-docs.trychroma.com/docs"
    )


# ============================================================
# Extension tests
# ============================================================

def test_image_extension():

    assert has_ignored_extension(
        "https://docs.trychroma.com/logo.png"
    )


def test_css_extension():

    assert has_ignored_extension(
        "https://docs.trychroma.com/style.css"
    )


def test_html_page_not_ignored():

    assert not has_ignored_extension(
        "https://docs.trychroma.com/docs"
    )


# ============================================================
# Path tests
# ============================================================

def test_login_path():

    assert has_ignored_path(
        "https://docs.trychroma.com/login"
    )


def test_search_path():

    assert has_ignored_path(
        "https://docs.trychroma.com/search"
    )


def test_normal_path():

    assert not has_ignored_path(
        "https://docs.trychroma.com/docs/collections"
    )


# ============================================================
# Final validation
# ============================================================

def test_valid_chroma_page():

    assert is_valid_page_url(
        "https://docs.trychroma.com/docs/collections"
    )


def test_external_page_invalid():

    assert not is_valid_page_url(
        "https://github.com/chroma-core/chroma"
    )


def test_image_invalid():

    assert not is_valid_page_url(
        "https://docs.trychroma.com/logo.png"
    )


def test_mailto_invalid():

    assert not is_valid_page_url(
        "mailto:test@example.com"
    )


# ============================================================
# Relative URL resolution
# ============================================================

def test_resolve_relative_url():

    result = resolve_url(
        "/docs/collections",
        BASE_URL,
    )

    assert result == (
        "https://docs.trychroma.com/docs/collections"
    )