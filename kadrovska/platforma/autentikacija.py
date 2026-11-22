"""Tokeni prijave, zadano zabranjeno i provjera vlasništva kao FastAPI ovisnosti."""

from __future__ import annotations

import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Request

from kadrovska.platforma.greske import ApiGreska

KOLACIC = "SESSION"
_JAVNO = "_kadrovska_javno"


@dataclass(frozen=True)
class PrijavljeniKorisnik:
    id: int
    username: str
    uloga: str

    @property
    def is_admin(self) -> bool:
        return self.uloga == "ADMIN"

    def ima_ulogu(self, *uloge: str) -> bool:
        return self.uloga in uloge


class TokenStore:
    """Tokeni prijave čuvaju se u memoriji (token → korisnik)."""

    def __init__(self) -> None:
        self._tokeni: dict[str, PrijavljeniKorisnik] = {}
        self._brava = threading.Lock()

    def izdaj(self, korisnik: PrijavljeniKorisnik) -> str:
        token = secrets.token_urlsafe(32)
        with self._brava:
            self._tokeni[token] = korisnik
        return token

    def korisnik(self, token: str | None) -> PrijavljeniKorisnik | None:
        if not token:
            return None
        with self._brava:
            return self._tokeni.get(token)


def javno[F: Callable](endpoint: F) -> F:
    """Ruta dostupna bez prijave. Sve ostale traže token (zadano zabranjeno)."""
    setattr(endpoint, _JAVNO, True)
    return endpoint


def je_javno(endpoint: object) -> bool:
    return getattr(endpoint, _JAVNO, False) is True


def token_iz_zahtjeva(request: Request) -> str | None:
    zaglavlje = request.headers.get("authorization")
    if zaglavlje and zaglavlje[:7].lower() == "bearer ":
        token = zaglavlje[7:].strip()
        return token or None
    kolacic = request.cookies.get(KOLACIC, "").strip()
    return kolacic or None


def prijavljeni_korisnik(request: Request) -> PrijavljeniKorisnik:
    tokeni: TokenStore = request.app.state.kontekst.tokeni
    korisnik = tokeni.korisnik(token_iz_zahtjeva(request))
    if korisnik is None:
        raise ApiGreska(401, "Potrebna je prijava.")
    return korisnik


def zadano_zabranjeno(request: Request) -> None:
    """Globalna ovisnost: bez @javno nema pristupa bez valjane prijave."""
    endpoint = request.scope.get("endpoint") or getattr(request.scope.get("route"), "endpoint", None)
    if je_javno(endpoint):
        return
    prijavljeni_korisnik(request)


def _uloge(*uloge: str):
    def ovisnost(korisnik: Annotated[PrijavljeniKorisnik, Depends(prijavljeni_korisnik)]) -> PrijavljeniKorisnik:
        if not korisnik.ima_ulogu(*uloge):
            raise ApiGreska.zabranjeno()
        return korisnik

    return ovisnost


def _vlasnistvo(
    pronadi: Callable[[Request, int], Any | None],
    vlasnik: Callable[[Any], str],
    ime_parametra: str,
    poruka: str = "Zapis nije pronađen.",
):
    """Tvornica ovisnosti: zapis iz putanje samo vlasniku ili ADMIN-u (inače 404)."""

    def ovisnost(request: Request, korisnik: Annotated[PrijavljeniKorisnik, Depends(prijavljeni_korisnik)]) -> Any:
        vrijednost = request.path_params.get(ime_parametra)
        if not isinstance(vrijednost, int):
            try:
                vrijednost = int(vrijednost)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                raise ApiGreska.nije_pronadeno(poruka) from None
        zapis = pronadi(request, vrijednost)
        if zapis is None or not (korisnik.is_admin or vlasnik(zapis) == korisnik.username):
            raise ApiGreska.nije_pronadeno(poruka)
        return zapis

    return ovisnost


def _pronadi_zahtjev(request: Request, zahtjev_id: int) -> dict[str, Any] | None:
    return request.app.state.kontekst.zahtjevi.pronadi(zahtjev_id)


def _pronadi_platnu_listu(request: Request, lista_id: int) -> dict[str, Any] | None:
    return request.app.state.kontekst.baza.jedan(
        "SELECT id, zaposlenik, razdoblje, datoteka FROM platne_liste WHERE id = ?",
        (lista_id,),
    )


Prijavljeni = Annotated[PrijavljeniKorisnik, Depends(prijavljeni_korisnik)]
VoditeljIliAdmin = Annotated[PrijavljeniKorisnik, Depends(_uloge("VODITELJ", "ADMIN"))]
VlastitiZahtjev = Annotated[
    dict[str, Any],
    Depends(
        _vlasnistvo(
            _pronadi_zahtjev,
            lambda z: z["zaposlenik"],
            "zahtjev_id",
            "Zahtjev nije pronađen.",
        )
    ),
]
VlastitaPlatnaLista = Annotated[
    dict[str, Any],
    Depends(
        _vlasnistvo(
            _pronadi_platnu_listu,
            lambda z: z["zaposlenik"],
            "lista_id",
            "Platna lista nije pronađena.",
        )
    ),
]
