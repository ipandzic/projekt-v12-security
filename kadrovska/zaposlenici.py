"""Imenik zaposlenika, npr. ``GET /api/zaposlenici?sort=prezime&smjer=asc``."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from kadrovska.platforma.autentikacija import Prijavljeni
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx

router = APIRouter(prefix="/api/zaposlenici")

POLJA_ZA_SORTIRANJE = {"ime", "prezime", "odjel", "email"}
SMJEROVI = {"asc", "desc"}

@router.get("")
def popis(korisnik: Prijavljeni, ctx: Ctx, sort: str = "prezime", smjer: str = "asc") -> list[dict[str, Any]]:
    if sort not in POLJA_ZA_SORTIRANJE or smjer not in SMJEROVI:
        raise ApiGreska.neispravno("Neispravno sortiranje.")
    sql = f"SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY {sort} {smjer}"  # noqa: S608
    return ctx.baza.upit(sql)
