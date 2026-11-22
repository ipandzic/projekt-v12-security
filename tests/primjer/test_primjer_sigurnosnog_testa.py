"""Primjer testa koji provjerava kontrolu pristupa. Vlastite testove napiši u istom stilu:
pripremi stanje (prijava, podaci), pošalji zahtjev i provjeri status i sadržaj odgovora."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.primjer


def test_popis_vlastitih_zahtjeva_bez_prijave_vraca_401(client: TestClient) -> None:
    odgovor = client.get("/api/zahtjevi/moji")

    assert odgovor.status_code == 401
    assert odgovor.json()["greska"] == "Potrebna je prijava."


def test_izmisljeni_token_ne_daje_pristup(client: TestClient) -> None:
    odgovor = client.get("/api/ja", headers={"Authorization": "Bearer izmisljeni-token"})

    assert odgovor.status_code == 401
