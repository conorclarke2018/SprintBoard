"""Logging setup: everything goes to the console and to logs/app.log."""

import logging
from logging.handlers import RotatingFileHandler

from app.config import BACKEND_DIR

LOG_DIR = BACKEND_DIR / "logs"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger once. Safe to call more than once (e.g. with --reload)."""
    root = logging.getLogger()
    if getattr(root, "_sprintboard_configured", False):
        return

    LOG_DIR.mkdir(exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    # The HTTP client used by tests logs every request; keep only its warnings.
    for noisy in ("httpx", "httpx2"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    root._sprintboard_configured = True  # type: ignore[attr-defined]
