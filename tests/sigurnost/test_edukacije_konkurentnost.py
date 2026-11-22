"""Sigurnosni test za istodobnu prijavu na zadnje mjesto edukacije."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi import FastAPI

from kadrovska.platforma.autentikacija import PrijavljeniKorisnik
from kadrovska.platforma.greske import ApiGreska


def test_samo_jedan_korisnik_dobiva_zadnje_mjesto(app: FastAPI) -> None:
    ctx = app.state.kontekst
    barijera = Barrier(2)
    korisnici = [
        PrijavljeniKorisnik(1, "ana", "KORISNIK"),
        PrijavljeniKorisnik(2, "marko", "KORISNIK"),
    ]

    def prijavi(korisnik: PrijavljeniKorisnik) -> int:
        barijera.wait()
        try:
            ctx.edukacije.prijavi(3, korisnik)  # edukacija 3 ima 19/20 mjesta
            return 201
        except ApiGreska as greska:
            return greska.status

    with ThreadPoolExecutor(max_workers=2) as executor:
        rezultati = list(executor.map(prijavi, korisnici))

    stanje = ctx.baza.jedan("SELECT prijavljeno FROM edukacije WHERE id = ?", (3,))
    assert sorted(rezultati) == [201, 409]
    assert stanje is not None
    assert stanje["prijavljeno"] == 20

