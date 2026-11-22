"""Imenik zaposlenika, npr. ``GET /api/zaposlenici?sort=prezime&smjer=asc``."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from kadrovska.platforma.autentikacija import Prijavljeni
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx

router = APIRouter(prefix="/api/zaposlenici")

# Konstantni SQL fragmenti – parametri zahtjeva nikad ne ulaze u ORDER BY izravno.
STUPCI = {"ime": "ime", "prezime": "prezime", "odjel": "odjel", "email": "email"}
SMJEROVI = {"asc": "ASC", "desc": "DESC"}


@router.get("")
def popis(korisnik: Prijavljeni, ctx: Ctx, sort: str = "prezime", smjer: str = "asc") -> list[dict[str, Any]]:
    stupac = STUPCI.get(sort)
    redoslijed = SMJEROVI.get(smjer)
    if stupac is None or redoslijed is None:
        raise ApiGreska.neispravno("Neispravno sortiranje.")
    # stupac/redoslijed dolaze isključivo iz STUPCI/SMJEROVI (konstante), ne iz zahtjeva.
    sql = f"SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY {stupac} {redoslijed}"  # noqa: S608
    return ctx.baza.upit(sql)
