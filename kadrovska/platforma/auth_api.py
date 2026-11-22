"""REST API: stanje sustava, prijava, registracija, zaboravljena lozinka i podaci prijavljenog korisnika."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from kadrovska.platforma.autentikacija import Prijavljeni, javno
from kadrovska.platforma.greske import ApiGreska, greska
from kadrovska.platforma.kontekst import Ctx
from kadrovska.platforma.korisnici import PrijavaZahtjev, RegistracijaZahtjev
from kadrovska.platforma.ogranicenje import ogranicenje_prijave

router = APIRouter(prefix="/api")


class ResetZahtjev(BaseModel):
    username: str | None = None


class NovaLozinka(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str | None = None
    nova_lozinka: str | None = Field(default=None, alias="novaLozinka")


@router.get("/health")
@javno
def health() -> dict[str, str]:
    return {"status": "UP"}


@router.post("/auth/login", dependencies=[Depends(ogranicenje_prijave)])
@javno
def login(zahtjev: PrijavaZahtjev, ctx: Ctx) -> JSONResponse:
    korisnik = ctx.korisnici.prijava(zahtjev)
    if korisnik is None:
        return greska(401, "Neispravno korisničko ime ili lozinka.")
    token = ctx.tokeni.izdaj(korisnik.prijavljeni())
    return JSONResponse({"token": token, "username": korisnik.username, "uloga": korisnik.uloga})


@router.post("/auth/register", status_code=201)
@javno
def register(zahtjev: RegistracijaZahtjev, ctx: Ctx) -> dict[str, object]:
    korisnik = ctx.korisnici.registriraj(zahtjev)
    return {"id": korisnik.id, "username": korisnik.username}


@router.post("/auth/reset-zahtjev", status_code=202)
@javno
def reset_zahtjev(zahtjev: ResetZahtjev, ctx: Ctx) -> dict[str, str]:
    if zahtjev.username and zahtjev.username.strip():
        ctx.reset.zatrazi(zahtjev.username.strip())
    return {"poruka": "Ako korisnik postoji, poslali smo upute na e-mail."}


@router.post("/auth/reset")
@javno
def reset(zahtjev: NovaLozinka, ctx: Ctx) -> dict[str, str]:
    if not ctx.reset.postavi_novu_lozinku(zahtjev.token, zahtjev.nova_lozinka):
        raise ApiGreska.neispravno("Token nije valjan ili je istekao.")
    return {"poruka": "Lozinka je promijenjena."}


@router.get("/ja")
def ja(korisnik: Prijavljeni, ctx: Ctx) -> dict[str, object]:
    podaci = ctx.korisnici.pronadi(korisnik.username)
    if podaci is None:
        raise ApiGreska(401, "Potrebna je prijava.")
    return {
        "username": podaci.username,
        "ime": podaci.ime,
        "prezime": podaci.prezime,
        "email": podaci.email,
        "uloga": podaci.uloga,
    }
