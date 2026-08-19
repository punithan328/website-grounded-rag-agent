from app.config import REGISTRY_DB
from app.ingestion.registry import IngestionRegistry


def test_registry_initialization(tmp_path):

    db_path = tmp_path / "test_ingestion.db"

    registry = IngestionRegistry(
        db_path
    )

    stats = registry.get_statistics()

    assert stats["websites"] == 0
    assert stats["pages"] == 0
    assert stats["embedded_pages"] == 0
    assert stats["chunks"] == 0


def test_create_website(tmp_path):

    db_path = tmp_path / "test_ingestion.db"

    registry = IngestionRegistry(
        db_path
    )

    website_id = registry.get_or_create_website(
        domain="docs.trychroma.com",
        seed_url="https://docs.trychroma.com/"
    )

    assert website_id == 1

    # Calling again should return the same ID
    same_website_id = registry.get_or_create_website(
        domain="docs.trychroma.com",
        seed_url="https://docs.trychroma.com/"
    )

    assert same_website_id == website_id


def test_page_lifecycle(tmp_path):

    db_path = tmp_path / "test_ingestion.db"

    registry = IngestionRegistry(
        db_path
    )

    website_id = registry.get_or_create_website(
        domain="docs.trychroma.com",
        seed_url="https://docs.trychroma.com/"
    )

    page_id = registry.upsert_page(
        website_id=website_id,
        url="https://docs.trychroma.com/docs",
        canonical_url="https://docs.trychroma.com/docs",
        title="Documentation",
        content_hash="abc123",
        status="discovered",
        http_status=200
    )

    assert page_id == 1

    page = registry.get_page(
        website_id,
        "https://docs.trychroma.com/docs"
    )

    assert page is not None
    assert page["title"] == "Documentation"
    assert page["content_hash"] == "abc123"
    assert page["status"] == "discovered"

    registry.mark_page_crawled(page_id)

    page = registry.get_page(
        website_id,
        "https://docs.trychroma.com/docs"
    )

    assert page["status"] == "crawled"

    registry.add_chunk(
        chunk_id="page_1_chunk_0",
        page_id=page_id,
        chunk_index=0,
        content_hash="chunk_hash_123",
        chroma_id="chroma_123",
        embedding_model="all-MiniLM-L6-v2"
    )

    registry.mark_page_embedded(
        page_id,
        chunk_count=1
    )

    page = registry.get_page(
        website_id,
        "https://docs.trychroma.com/docs"
    )

    assert page["status"] == "indexed"
    assert page["chunk_count"] == 1

    assert registry.is_page_unchanged(
        website_id=website_id,
        canonical_url="https://docs.trychroma.com/docs",
        content_hash="abc123"
    )

# def test_chunks_table_has_token_count_column(
#     registry,
# ):
#     with registry._connect() as conn:

#         columns = {
#             row["name"]
#             for row in conn.execute(
#                 "PRAGMA table_info(chunks)"
#             ).fetchall()
#         }

#     assert "token_count" in columns
def test_chunks_table_has_token_count_column(
    tmp_path,
):
    from app.ingestion.registry import (
        IngestionRegistry,
    )

    db_path = tmp_path / "test_registry.db"

    registry = IngestionRegistry(
        db_path
    )

    with registry._connect() as conn:

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(chunks)"
            ).fetchall()
        }

    assert "token_count" in columns
    
    
def test_changed_page_requires_reingestion(tmp_path):

    db_path = tmp_path / "test_ingestion.db"

    registry = IngestionRegistry(
        db_path
    )

    website_id = registry.get_or_create_website(
        domain="docs.trychroma.com",
        seed_url="https://docs.trychroma.com/"
    )

    page_id = registry.upsert_page(
        website_id=website_id,
        url="https://docs.trychroma.com/docs",
        canonical_url="https://docs.trychroma.com/docs",
        title="Documentation",
        content_hash="old_hash",
        status="embedded",
        http_status=200
    )

    registry.mark_page_embedded(
        page_id,
        chunk_count=2
    )

    # Same hash → unchanged
    assert registry.is_page_unchanged(
        website_id,
        "https://docs.trychroma.com/docs",
        "old_hash"
    )

    # New hash → changed
    assert not registry.is_page_unchanged(
        website_id,
        "https://docs.trychroma.com/docs",
        "new_hash"
    )