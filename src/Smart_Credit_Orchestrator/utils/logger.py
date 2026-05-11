"""
Logger Utility – Smart Credit Orchestrator

Configures a project-wide structured logger.
Call `setup_logger()` once at application startup (done in main.py).
"""

import logging
import os
import sys
from pathlib import Path


def setup_logger(
    name: str = "smart_credit_orchestrator",
    level: str | None = None,
    log_file: str | None = None,
) -> logging.Logger:
    """
    Configure and return the root project logger.

    Args:
        name:     Logger name (default: 'smart_credit_orchestrator').
        level:    Log level string. Defaults to LOG_LEVEL env var or INFO.
        log_file: Optional path to write logs to a file as well.

    Returns:
        Configured logging.Logger instance.
    """
    resolved_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, resolved_level, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    if logger.handlers:
        return logger  # Already configured

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
