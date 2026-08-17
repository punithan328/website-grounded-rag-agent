from app.ingestion.url_manager import (
    normalize_url,
    is_valid_page_url,
    resolve_url,
)


test_urls = [
    "https://docs.trychroma.com/docs/",
    "https://docs.trychroma.com/docs#collections",
    "https://docs.trychroma.com/docs?utm_source=google",
    "https://github.com/chroma-core/chroma",
    "https://docs.trychroma.com/logo.png",
    "/docs/collections",
]


base_url = "https://docs.trychroma.com/"


for url in test_urls:

    normalized = normalize_url(
        url,
        base_url=base_url,
    )

    valid = (
        is_valid_page_url(normalized)
        if normalized
        else False
    )

    print("\nOriginal:")
    print(url)

    print("Normalized:")
    print(normalized)

    print("Valid:")
    print(valid)


print("\nRelative URL:")

print(
    resolve_url(
        "/docs/collections",
        base_url,
    )
)