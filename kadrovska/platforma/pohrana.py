"""Mape s dokumentima i poslanim porukama (``storage_dir``, ``mailbox_dir``)."""

from __future__ import annotations

from pathlib import Path

from kadrovska.postavke import Postavke


class Pohrana:
    def __init__(self, postavke: Postavke) -> None:
        self.dokumenti = Path(postavke.storage_dir)
        self.posta = Path(postavke.mailbox_dir)

    def pripremi(self) -> None:
        self.dokumenti.mkdir(parents=True, exist_ok=True)
        self.posta.mkdir(parents=True, exist_ok=True)

    def zapisi_ako_ne_postoji(self, naziv: str, sadrzaj: str) -> None:
        datoteka = self.dokumenti / naziv
        if not datoteka.exists():
            datoteka.write_text(sadrzaj, encoding="utf-8")
