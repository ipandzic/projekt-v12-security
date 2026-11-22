"""REST API za zahtjeve za godišnji odmor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response

from kadrovska.platforma.autentikacija import Prijavljeni, VlastitiZahtjev
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx
from kadrovska.zahtjevi.servis import NoviZahtjev

router = APIRouter(prefix="/api/zahtjevi")


@router.post("", status_code=201)
def kreiraj(zahtjev: NoviZahtjev, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    zahtjev_id = ctx.zahtjevi.kreiraj(zahtjev, korisnik)
    novi = ctx.zahtjevi.pronadi(zahtjev_id)
    if novi is None:
        raise ApiGreska.nije_pronadeno("Zahtjev nije pronađen.")
    return novi


@router.get("/moji")
def moji(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.zahtjevi.zahtjevi_zaposlenika(korisnik.username)


@router.delete("/{zahtjev_id}", status_code=204)
def obrisi(zahtjev: VlastitiZahtjev, ctx: Ctx) -> Response:
    ctx.zahtjevi.obrisi_zapis(zahtjev["id"])
    return Response(status_code=204)
