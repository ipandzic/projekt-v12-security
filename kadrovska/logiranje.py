"""Ispis logova aplikacije u konzolu."""

from __future__ import annotations

import logging


def nastavi_logiranje(razina: int = logging.INFO) -> None:
    logger = logging.getLogger("kadrovska")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(name)s - %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(razina)
