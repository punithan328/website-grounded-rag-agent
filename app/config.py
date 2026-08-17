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