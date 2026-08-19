from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()


# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DATABASE_DIR = BASE_DIR / "database"
CHROMA_DIR = BASE_DIR / "chroma_db"


# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Website configuration
# ============================================================

SEED_URL = os.getenv(
    "SEED_URL",
    "https://docs.trychroma.com/"
)

ALLOWED_DOMAIN = os.getenv(
    "ALLOWED_DOMAIN",
    "docs.trychroma.com"
)

MAX_PAGES = int(
    os.getenv("MAX_PAGES", "30")
)


# ============================================================
# Crawling configuration
# ============================================================

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "20")
)

REQUEST_DELAY = float(
    os.getenv("REQUEST_DELAY", "0.5")
)


# ============================================================
# Content configuration
# ============================================================

MIN_CONTENT_LENGTH = int(
    os.getenv("MIN_CONTENT_LENGTH", "300")
)


# ============================================================
# Chunking configuration
# ============================================================

CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "600")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "80")
)


# ============================================================
# Embedding configuration
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

EMBEDDING_DIMENSION = 384


# ============================================================
# ChromaDB configuration
# ============================================================

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "chromadb_docs"
)


# ============================================================
# Database configuration
# ============================================================

REGISTRY_DB = DATABASE_DIR / "ingestion.db"

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)

USER_AGENT = os.getenv(
    "USER_AGENT",
    "WebsiteGroundedRAGAgent/1.0"
)

CRAWL_RAW_HTML = (
    os.getenv("CRAWL_RAW_HTML", "true").lower()
    == "true"
)

CHROMA_DIR = (
    BASE_DIR
    / "data"
    / "chroma"
)

# CHROMA_COLLECTION_NAME = os.getenv(
#     "CHROMA_COLLECTION_NAME",
#     "website_knowledge",
# )
CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "chromadb_docs",
)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

EMBEDDING_BATCH_SIZE = int(
    os.getenv(
        "EMBEDDING_BATCH_SIZE",
        "32",
    )
)

import os

from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-5.2",
)

OPENROUTER_MAX_TOKENS = int(
    os.getenv(
        "OPENROUTER_MAX_TOKENS",
        "1000",
    )
)

OPENROUTER_TEMPERATURE = float(
    os.getenv(
        "OPENROUTER_TEMPERATURE",
        "0",
    )
)