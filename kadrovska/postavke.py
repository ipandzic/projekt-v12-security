"""Postavke aplikacije. Zadane vrijednosti mogu se promijeniti varijablama okruženja."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _origini() -> list[str]:
    vrijednost = os.environ.get("APP_CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in vrijednost.split(",") if origin.strip()]


@dataclass
class Postavke:
    naziv: str = "Kadrovska"
    # mapa s datotekama platnih lista (APP_STORAGE_DIR)
    storage_dir: str = field(default_factory=lambda: os.environ.get("APP_STORAGE_DIR", "./data/dokumenti"))
    # mapa u koju se „šalju” e-poruke kao tekstualne datoteke (APP_MAILBOX_DIR)
    mailbox_dir: str = field(default_factory=lambda: os.environ.get("APP_MAILBOX_DIR", "./data/posta"))
    # origini frontend aplikacije, odvojeni zarezom (APP_CORS_ALLOWED_ORIGINS)
    cors_allowed_origins: list[str] = field(default_factory=_origini)
    # port na kojem se aplikacija pokreće (APP_PORT); koristi se i u poveznicama u e-porukama
    port: int = field(default_factory=lambda: int(os.environ.get("APP_PORT", "8000")))
    # maksimalan broj pokušaja prijave u minuti po IP (APP_PRIJAVA_POKUSAJA)
    prijava_pokusaja_u_minuti: int = field(
        default_factory=lambda: int(os.environ.get("APP_PRIJAVA_POKUSAJA", "20"))
    )
