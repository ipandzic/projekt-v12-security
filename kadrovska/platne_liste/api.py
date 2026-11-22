"""Platne liste: popis, prikaz (JSON ili PDF) i preuzimanje datoteke platne liste."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Annotated, Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from kadrovska.platforma.autentikacija import Prijavljeni, VlastitaPlatnaLista
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx, Kontekst
from kadrovska.platne_liste import pdf

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/platne-liste")

SELECT = "SELECT id, zaposlenik, razdoblje, datoteka FROM platne_liste"


class Format(Enum):
    JSON = "json"
    PDF = "pdf"

    @classmethod
    def procitaj(cls, vrijednost: str) -> Format | None:
        return next((f for f in cls if f.value == vrijednost.strip().lower()), None)


@router.get("/moje")
def moje(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.baza.upit(SELECT + " WHERE zaposlenik = ? ORDER BY razdoblje DESC, id", (korisnik.username,))


@router.get("/preuzmi")
def preuzmi(datoteka: str, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    """Preuzimanje datoteke platne liste: ``GET /api/platne-liste/preuzmi?datoteka=placa-ana-2026-10.txt``."""
    lista = ctx.baza.jedan(SELECT + " WHERE datoteka = ?", (datoteka,))
    if lista is None or not (korisnik.is_admin or lista["zaposlenik"] == korisnik.username):
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    putanja = ctx.pohrana.dokumenti / datoteka
    if not putanja.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    return Response(
        content=putanja.read_bytes(),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{putanja.name}"'},
    )


@router.get("/{lista_id}")
def platna_lista(
    lista: VlastitaPlatnaLista,
    ctx: Ctx,
    oblik: Annotated[str | None, Query(alias="format")] = None,
) -> Response:
    """Platna lista u JSON obliku (podaci i sadržaj) ili kao PDF: ``GET /api/platne-liste/1?format=pdf``."""
    trazeni = "json" if oblik is None else oblik
    odabrani = Format.JSON
    napomena = None
    try:
        odabrani = Format[trazeni.strip().upper()]
    except KeyError as e:
        log.warning("Neuspjela obrada zahtjeva za platnu listu %s", lista["id"], exc_info=True)
        napomena = f"Format nije prepoznat, prikazuje se JSON ({e!r})"
    return _prikazi(ctx, lista, odabrani, napomena)


def _prikazi(ctx: Kontekst, lista: dict[str, Any], odabrani: Format, napomena: str | None) -> Response:
    datoteka = ctx.pohrana.dokumenti / lista["datoteka"]
    if not datoteka.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka platne liste nije pronađena.")
    sadrzaj = datoteka.read_text(encoding="utf-8")
    if odabrani is Format.PDF:
        return Response(
            content=pdf.izradi(f"Platna lista {lista['razdoblje']}", sadrzaj.splitlines()),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="platna-lista-{lista["id"]}.pdf"'},
        )
    tijelo = {**lista, "sadrzaj": sadrzaj}
    if napomena is not None:
        tijelo["napomena"] = napomena
    return JSONResponse(tijelo)
