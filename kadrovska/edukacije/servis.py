"""Edukacije: popis i prijava zaposlenika na edukaciju."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from kadrovska.edukacije.sustav_za_edukacije import SustavZaEdukacijeKlijent
from kadrovska.platforma.autentikacija import PrijavljeniKorisnik
from kadrovska.platforma.baza import Baza
from kadrovska.platforma.greske import ApiGreska

log = logging.getLogger(__name__)


def _edukacija(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "naziv": red["naziv"],
        "datum": red["datum"],
        "kapacitet": red["kapacitet"],
        "prijavljeno": red["prijavljeno"],
        "slobodno": red["kapacitet"] - red["prijavljeno"],
    }


class EdukacijaService:
    def __init__(self, baza: Baza, lms: SustavZaEdukacijeKlijent) -> None:
        self._baza = baza
        self._lms = lms

    def sve(self) -> list[dict[str, Any]]:
        redovi = self._baza.upit("SELECT id, naziv, datum, kapacitet, prijavljeno FROM edukacije ORDER BY datum, id")
        return [_edukacija(red) for red in redovi]

    def prijavi(self, edukacija_id: int, korisnik: PrijavljeniKorisnik) -> int:
        with self._baza.transakcija():
            if self._baza.jedan("SELECT id FROM edukacije WHERE id = ?", (edukacija_id,)) is None:
                raise ApiGreska.nije_pronadeno("Edukacija nije pronađena.")
            prijava = self._baza.jedan(
                "SELECT id FROM prijave_edukacije WHERE edukacija_id = ? AND zaposlenik = ?",
                (edukacija_id, korisnik.username),
            )
            if prijava is not None:
                raise ApiGreska(409, "Već ste prijavljeni na ovu edukaciju.")
            stanje = self._baza.jedan("SELECT kapacitet, prijavljeno FROM edukacije WHERE id = ?", (edukacija_id,))
            if stanje is None or stanje["prijavljeno"] >= stanje["kapacitet"]:
                raise ApiGreska(409, "Nema slobodnih mjesta.")
            oznaka = self._lms.upisi_polaznika(edukacija_id, korisnik.username)
            self._baza.izvrsi("UPDATE edukacije SET prijavljeno = prijavljeno + 1 WHERE id = ?", (edukacija_id,))
            return self._spremi(edukacija_id, korisnik, oznaka)

    def _spremi(self, edukacija_id: int, korisnik: PrijavljeniKorisnik, oznaka_lms: str) -> int:
        prijava_id = self._baza.umetni(
            "INSERT INTO prijave_edukacije (edukacija_id, zaposlenik, kreirano, oznaka_lms) VALUES (?, ?, ?, ?)",
            (edukacija_id, korisnik.username, datetime.now().isoformat(timespec="seconds"), oznaka_lms),
        )
        log.info("Zaposlenik %s prijavljen na edukaciju %s", korisnik.username, edukacija_id)
        return prijava_id
