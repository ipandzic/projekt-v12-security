"""Servisi jedne instance aplikacije (dostupni endpointima preko ``Depends``)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from kadrovska.platforma.autentikacija import TokenStore
from kadrovska.platforma.baza import Baza
from kadrovska.platforma.korisnici import KorisnikService
from kadrovska.platforma.lozinke import LozinkaHasher
from kadrovska.platforma.ogranicenje import OgranicenjePrijave
from kadrovska.platforma.pohrana import Pohrana
from kadrovska.platforma.posta import PostaService
from kadrovska.platforma.reset_lozinke import ResetLozinkeService
from kadrovska.postavke import Postavke

if TYPE_CHECKING:
    from kadrovska.edukacije.servis import EdukacijaService
    from kadrovska.zahtjevi.servis import ZahtjevService


@dataclass
class Kontekst:
    postavke: Postavke
    baza: Baza
    pohrana: Pohrana
    tokeni: TokenStore
    hasher: LozinkaHasher
    korisnici: KorisnikService
    posta: PostaService
    reset: ResetLozinkeService
    zahtjevi: ZahtjevService
    edukacije: EdukacijaService
    ogranicenje_prijave: OgranicenjePrijave


def kontekst(request: Request) -> Kontekst:
    return request.app.state.kontekst


Ctx = Annotated[Kontekst, Depends(kontekst)]


async def _sirovo_tijelo(request: Request) -> bytes:
    return await request.body()


# Tijelo zahtjeva kao bajtovi (XML, YAML)
SirovoTijelo = Annotated[bytes, Depends(_sirovo_tijelo)]
