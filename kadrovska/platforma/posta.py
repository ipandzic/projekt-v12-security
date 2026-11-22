"""Slanje e-pošte. U lokalnom okruženju poruka se ne šalje, nego se zapisuje kao tekstualna datoteka
u mapu ``mailbox_dir``."""

from __future__ import annotations

import logging
from datetime import datetime
from urllib.parse import quote

from kadrovska.platforma.korisnici import Korisnik
from kadrovska.platforma.pohrana import Pohrana
from kadrovska.postavke import Postavke

log = logging.getLogger(__name__)


class PostaService:
    def __init__(self, pohrana: Pohrana, postavke: Postavke) -> None:
        self._pohrana = pohrana
        self._postavke = postavke

    def posalji_upute_za_lozinku(self, korisnik: Korisnik, token: str) -> None:
        poveznica = f"http://localhost:{self._postavke.port}/reset?token={quote(token, safe='')}"
        poruka = (
            f"Za: {korisnik.email}\n"
            f"Predmet: {self._postavke.naziv} – promjena lozinke\n"
            "Poštovani,\n"
            f"zaprimili smo zahtjev za promjenu lozinke za korisnički račun {korisnik.username}.\n"
            "Novu lozinku možete postaviti na poveznici:\n"
            f"{poveznica}\n"
            f"Token: {token}\n"
            "Ako niste zatražili promjenu lozinke, zanemarite ovu poruku.\n"
        )
        sada = datetime.now()
        oznaka = sada.strftime("%Y%m%d%H%M%S") + f"{sada.microsecond // 1000:03d}"
        self._pohrana.posta.mkdir(parents=True, exist_ok=True)
        (self._pohrana.posta / f"{korisnik.username}-{oznaka}.txt").write_text(poruka, encoding="utf-8")
        log.info("Poslana poruka za promjenu lozinke korisniku %s", korisnik.username)
