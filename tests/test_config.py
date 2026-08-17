from app.config import (
    SEED_URL,
    ALLOWED_DOMAIN,
    MAX_PAGES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    CHROMA_COLLECTION_NAME,
)


def test_configuration():
    assert SEED_URL == "https://docs.trychroma.com/"
    assert ALLOWED_DOMAIN == "docs.trychroma.com"

    assert MAX_PAGES > 0

    assert CHUNK_SIZE > CHUNK_OVERLAP

    assert EMBEDDING_MODEL == "all-MiniLM-L6-v2"

    assert CHROMA_COLLECTION_NAME == "chromadb_docs"