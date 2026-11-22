"""Edukacije: popis, prijava na edukaciju i uvoz plana edukacija iz XML-a."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from kadrovska.edukacije import uvoz
from kadrovska.platforma.autentikacija import Prijavljeni, VoditeljIliAdmin
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx, SirovoTijelo

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/edukacije")


@router.get("")
def popis(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.edukacije.sve()


@router.post("/{edukacija_id}/prijava", status_code=201)
def prijava(edukacija_id: int, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    prijava_id = ctx.edukacije.prijavi(edukacija_id, korisnik)
    return {"id": prijava_id, "edukacijaId": edukacija_id, "zaposlenik": korisnik.username}


@router.post("/uvoz")
def uvezi(xml: SirovoTijelo, korisnik: VoditeljIliAdmin, ctx: Ctx) -> dict[str, Any]:
    """Uvoz plana edukacija iz XML-a (voditelj ili administrator)."""
    stavke = uvoz.procitaj(xml)
    for stavka in stavke:
        if not 1 <= stavka.kapacitet <= 500:
            raise ApiGreska.neispravno("Kapacitet edukacije mora biti između 1 i 500.")
    uvezene = []
    with ctx.baza.transakcija() as baza:
        for stavka in stavke:
            edukacija_id = baza.umetni(
                "INSERT INTO edukacije (naziv, datum, kapacitet, prijavljeno) VALUES (?, ?, ?, 0)",
                (stavka.naziv, stavka.datum.isoformat(), stavka.kapacitet),
            )
            uvezene.append({"id": edukacija_id, "naziv": stavka.naziv})
    log.info("Korisnik %s uvezao je %d edukacija", korisnik.username, len(uvezene))
    return {"uvezeno": len(uvezene), "edukacije": uvezene}
