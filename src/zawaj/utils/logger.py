"""Configuration du logger pour les agents Zawaj Secret's."""

from __future__ import annotations
import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger configuré pour le module donné."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level, logging.INFO))

        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, level, logging.INFO))

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
