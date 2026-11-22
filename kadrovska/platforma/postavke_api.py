"""Postavke obavijesti korisnika u YAML obliku, npr.

    podsjetnik: true
    satiPrije: 24
    kanal: email
"""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter

from kadrovska.platforma.autentikacija import Prijavljeni
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx, SirovoTijelo

router = APIRouter(prefix="/api/postavke")

KANALI = {"email", "sms"}


@router.get("")
def dohvati(korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    red = ctx.baza.jedan(
        "SELECT podsjetnik, sati_prije, kanal FROM postavke WHERE username = ?", (korisnik.username,)
    )
    if red is None:
        return {"postavke": _postavke(True, 24, "email")}
    return {"postavke": _postavke(bool(red["podsjetnik"]), red["sati_prije"], red["kanal"])}


@router.post("")
def spremi(tijelo: SirovoTijelo, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    try:
        dokument = yaml.safe_load(tijelo)
    except yaml.YAMLError as e:
        raise ApiGreska.neispravno("Neispravan YAML.") from e
    if not isinstance(dokument, dict):
        raise ApiGreska.neispravno("Neispravne postavke.")
    podsjetnik = _vrijednost(dokument, "podsjetnik", bool, True)
    sati_prije = _vrijednost(dokument, "satiPrije", int, 24)
    kanal = _vrijednost(dokument, "kanal", str, "email")
    if not 1 <= sati_prije <= 168 or kanal not in KANALI:
        raise ApiGreska.neispravno("Neispravne postavke.")
    ctx.baza.izvrsi(
        "INSERT INTO postavke (username, podsjetnik, sati_prije, kanal) VALUES (?, ?, ?, ?) "
        "ON CONFLICT (username) DO UPDATE SET podsjetnik = excluded.podsjetnik, "
        "sati_prije = excluded.sati_prije, kanal = excluded.kanal",
        (korisnik.username, podsjetnik, sati_prije, kanal),
    )
    return {"postavke": _postavke(podsjetnik, sati_prije, kanal)}


def _vrijednost(mapa: dict[Any, Any], kljuc: str, tip: type, zadano: Any) -> Any:
    vrijednost = mapa.get(kljuc)
    if vrijednost is None:
        return zadano
    # bool je podtip od int pa se "satiPrije: true" ne prihvaća kao broj
    if not isinstance(vrijednost, tip) or (tip is int and isinstance(vrijednost, bool)):
        raise ApiGreska.neispravno("Neispravne postavke.")
    return vrijednost


def _postavke(podsjetnik: bool, sati_prije: int, kanal: str) -> dict[str, Any]:
    return {"podsjetnik": podsjetnik, "satiPrije": sati_prije, "kanal": kanal}
