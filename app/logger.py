import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR

# Log file at project root
LOG_FILE = BASE_DIR / "log.log"


def _configure_logging() -> logging.Logger:

    logger = logging.getLogger("website_rag")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(ch_formatter)

    # File handler with rotation
    fh = RotatingFileHandler(
        filename=str(LOG_FILE),
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(ch_formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


# Configure on import
logger = _configure_logging()


def get_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logger

    return logging.getLogger(f"website_rag.{name}")
