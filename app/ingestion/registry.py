import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class IngestionRegistry:
    """
    SQLite-based registry for tracking websites, pages,
    and embedded chunks.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

        # Make sure the database directory exists
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    # ========================================================
    # Database connection
    # ========================================================

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = sqlite3.Row

        # Enable foreign key constraints
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    # ========================================================
    # Initialize database
    # ========================================================

    def _initialize_database(self) -> None:

        with self._connect() as connection:

            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL UNIQUE,
                    seed_url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_crawled_at TEXT
                );

                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    website_id INTEGER NOT NULL,

                    url TEXT NOT NULL,
                    canonical_url TEXT NOT NULL,

                    title TEXT,

                    content_hash TEXT,

                    status TEXT NOT NULL DEFAULT 'discovered',

                    http_status INTEGER,

                    last_crawled_at TEXT,
                    last_embedded_at TEXT,

                    chunk_count INTEGER NOT NULL DEFAULT 0,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    UNIQUE (
                        website_id,
                        canonical_url
                    ),

                    FOREIGN KEY (
                        website_id
                    )
                    REFERENCES websites(id)
                    ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    chunk_id TEXT NOT NULL UNIQUE,

                    page_id INTEGER NOT NULL,

                    chunk_index INTEGER NOT NULL,

                    content_hash TEXT NOT NULL,

                    chroma_id TEXT,

                    embedding_model TEXT,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (
                        page_id
                    )
                    REFERENCES pages(id)
                    ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS
                idx_pages_canonical_url
                ON pages(canonical_url);

                CREATE INDEX IF NOT EXISTS
                idx_pages_content_hash
                ON pages(content_hash);

                CREATE INDEX IF NOT EXISTS
                idx_pages_status
                ON pages(status);

                CREATE INDEX IF NOT EXISTS
                idx_chunks_page_id
                ON chunks(page_id);
                """
            )

    # ========================================================
    # Utility
    # ========================================================

    @staticmethod
    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    # ========================================================
    # Website operations
    # ========================================================

    def get_or_create_website(
        self,
        domain: str,
        seed_url: str
    ) -> int:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT id
                FROM websites
                WHERE domain = ?
                """,
                (domain,)
            ).fetchone()

            if row:
                return row["id"]

            now = self._now()

            cursor = connection.execute(
                """
                INSERT INTO websites (
                    domain,
                    seed_url,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    domain,
                    seed_url,
                    now
                )
            )

            return cursor.lastrowid

    # ========================================================
    # Page operations
    # ========================================================

    def get_page(
        self,
        website_id: int,
        canonical_url: str
    ) -> Optional[sqlite3.Row]:

        with self._connect() as connection:

            return connection.execute(
                """
                SELECT *
                FROM pages
                WHERE website_id = ?
                  AND canonical_url = ?
                """,
                (
                    website_id,
                    canonical_url
                )
            ).fetchone()

    def upsert_page(
        self,
        website_id: int,
        url: str,
        canonical_url: str,
        title: Optional[str] = None,
        content_hash: Optional[str] = None,
        status: str = "discovered",
        http_status: Optional[int] = None,
    ) -> int:

        now = self._now()

        with self._connect() as connection:

            existing = connection.execute(
                """
                SELECT id
                FROM pages
                WHERE website_id = ?
                  AND canonical_url = ?
                """,
                (
                    website_id,
                    canonical_url
                )
            ).fetchone()

            if existing:

                connection.execute(
                    """
                    UPDATE pages
                    SET
                        url = ?,
                        title = ?,
                        content_hash = ?,
                        status = ?,
                        http_status = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        url,
                        title,
                        content_hash,
                        status,
                        http_status,
                        now,
                        existing["id"]
                    )
                )

                return existing["id"]

            cursor = connection.execute(
                """
                INSERT INTO pages (
                    website_id,
                    url,
                    canonical_url,
                    title,
                    content_hash,
                    status,
                    http_status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    website_id,
                    url,
                    canonical_url,
                    title,
                    content_hash,
                    status,
                    http_status,
                    now,
                    now
                )
            )

            return cursor.lastrowid

    # ========================================================
    # Page status
    # ========================================================

    def mark_page_crawled(
        self,
        page_id: int
    ) -> None:

        now = self._now()

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE pages
                SET
                    status = 'crawled',
                    last_crawled_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    now,
                    page_id
                )
            )

    def mark_page_embedded(
        self,
        page_id: int,
        chunk_count: int
    ) -> None:

        now = self._now()

        with self._connect() as connection:

            connection.execute(
                """
                UPDATE pages
                SET
                    status = 'embedded',
                    last_embedded_at = ?,
                    chunk_count = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    chunk_count,
                    now,
                    page_id
                )
            )

    # ========================================================
    # Incremental ingestion check
    # ========================================================

    def is_page_unchanged(
        self,
        website_id: int,
        canonical_url: str,
        content_hash: str
    ) -> bool:

        page = self.get_page(
            website_id,
            canonical_url
        )

        if not page:
            return False

        return (
            page["content_hash"] == content_hash
            and page["status"] == "embedded"
        )

    # ========================================================
    # Chunk operations
    # ========================================================

    def add_chunk(
        self,
        chunk_id: str,
        page_id: int,
        chunk_index: int,
        content_hash: str,
        chroma_id: Optional[str],
        embedding_model: Optional[str]
    ) -> int:

        now = self._now()

        with self._connect() as connection:

            cursor = connection.execute(
                """
                INSERT OR REPLACE INTO chunks (
                    chunk_id,
                    page_id,
                    chunk_index,
                    content_hash,
                    chroma_id,
                    embedding_model,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    page_id,
                    chunk_index,
                    content_hash,
                    chroma_id,
                    embedding_model,
                    now
                )
            )

            return cursor.lastrowid

    # ========================================================
    # Delete chunks belonging to a page
    # ========================================================

    def delete_page_chunks(
        self,
        page_id: int
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                DELETE FROM chunks
                WHERE page_id = ?
                """,
                (page_id,)
            )

    # ========================================================
    # Statistics
    # ========================================================

    def get_statistics(self) -> dict:

        with self._connect() as connection:

            websites = connection.execute(
                "SELECT COUNT(*) AS count FROM websites"
            ).fetchone()["count"]

            pages = connection.execute(
                "SELECT COUNT(*) AS count FROM pages"
            ).fetchone()["count"]

            embedded_pages = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM pages
                WHERE status = 'embedded'
                """
            ).fetchone()["count"]

            chunks = connection.execute(
                "SELECT COUNT(*) AS count FROM chunks"
            ).fetchone()["count"]

            return {
                "websites": websites,
                "pages": pages,
                "embedded_pages": embedded_pages,
                "chunks": chunks,
            }