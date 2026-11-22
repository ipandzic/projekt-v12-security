"""Zahtjevi za godišnji odmor: podnošenje, pregled i povlačenje."""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from kadrovska.platforma.autentikacija import PrijavljeniKorisnik
from kadrovska.platforma.baza import Baza
from kadrovska.platforma.greske import ApiGreska

log = logging.getLogger(__name__)

OIB = re.compile(r"\d{11}")
MAX_DULJINA_RAZLOGA = 500

SELECT = "SELECT id, zaposlenik, datum_od, datum_do, razlog, status, kreirano FROM zahtjevi"


class NoviZahtjev(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    od: date | None = None
    do_: date | None = Field(default=None, alias="do")
    razlog: str | None = None
    oib: str | None = None


def _zahtjev(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "zaposlenik": red["zaposlenik"],
        "od": red["datum_od"],
        "do": red["datum_do"],
        "razlog": red["razlog"],
        "status": red["status"],
        "kreirano": red["kreirano"],
    }


class ZahtjevService:
    def __init__(self, baza: Baza) -> None:
        self._baza = baza

    def pronadi(self, zahtjev_id: int) -> dict[str, Any] | None:
        red = self._baza.jedan(SELECT + " WHERE id = ?", (zahtjev_id,))
        return _zahtjev(red) if red else None

    def zahtjevi_zaposlenika(self, username: str) -> list[dict[str, Any]]:
        redovi = self._baza.upit(SELECT + " WHERE zaposlenik = ? ORDER BY datum_od, id", (username,))
        return [_zahtjev(red) for red in redovi]

    def kreiraj(self, zahtjev: NoviZahtjev, korisnik: PrijavljeniKorisnik) -> int:
        if zahtjev.od is None or zahtjev.do_ is None:
            raise ApiGreska.neispravno("Razdoblje (od, do) je obavezno.")
        if zahtjev.do_ < zahtjev.od:
            raise ApiGreska.neispravno("Datum završetka ne može biti prije datuma početka.")
        if zahtjev.razlog is None or not zahtjev.razlog.strip() or len(zahtjev.razlog) > MAX_DULJINA_RAZLOGA:
            raise ApiGreska.neispravno(f"Razlog je obavezan (najviše {MAX_DULJINA_RAZLOGA} znakova).")
        if zahtjev.oib is None or not OIB.fullmatch(zahtjev.oib):
            raise ApiGreska.neispravno("OIB mora imati 11 znamenki.")
        log.info("Novi zahtjev za godišnji odmor: (zaposlenik %s)", korisnik.username)
        return self._baza.umetni(
            "INSERT INTO zahtjevi (zaposlenik, datum_od, datum_do, razlog, oib, status, kreirano) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                korisnik.username,
                zahtjev.od.isoformat(),
                zahtjev.do_.isoformat(),
                zahtjev.razlog,
                zahtjev.oib,
                "PODNESEN",
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    def obrisi_zapis(self, zahtjev_id: int) -> None:
        """Briše zahtjev; ovlasti (vlasnik/ADMIN) provjerava ovisnost ``VlastitiZahtjev`` u ruti."""
        self._baza.izvrsi("DELETE FROM zahtjevi WHERE id = ?", (zahtjev_id,))
        log.info("Zahtjev %s je povučen", zahtjev_id)
