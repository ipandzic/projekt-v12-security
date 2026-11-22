"""Zajedničke pytest "fixture" funkcije.

* ``app`` – svježa instanca aplikacije za svaki test (baza u memoriji, privremene mape za dokumente i poštu),
* ``client`` – ``TestClient`` nad tom aplikacijom (ponaša se kao stvarni poslužitelj: greška → odgovor 500),
* ``prijava("ana")`` – zaglavlje ``Authorization: Bearer <token>`` za početnog korisnika,
* ``novi_korisnik("prefiks", "Lozinka123!")`` – registrira korisnika s jedinstvenim imenom i vraća ime.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kadrovska.app import create_app
from kadrovska.postavke import Postavke

LOZINKE = {
    "ana": "Ana12345!",
    "marko": "Marko12345!",
    "voditelj": "Ovlasteni12345!",
    "admin": "Admin12345!",
}


@dataclass
class Mape:
    dokumenti: Path
    posta: Path


@pytest.fixture
def mape(tmp_path: Path) -> Mape:
    return Mape(dokumenti=tmp_path / "dokumenti", posta=tmp_path / "posta")


@pytest.fixture
def app(mape: Mape) -> Iterator[FastAPI]:
    aplikacija = create_app(Postavke(storage_dir=str(mape.dokumenti), mailbox_dir=str(mape.posta)))
    yield aplikacija
    aplikacija.state.baza.zatvori()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False, follow_redirects=False) as test_client:
        yield test_client


def token(client: TestClient, username: str, lozinka: str | None = None) -> str:
    odgovor = client.post(
        "/api/auth/login", json={"username": username, "password": lozinka or LOZINKE[username]}
    )
    assert odgovor.status_code == 200, f"prijava nije uspjela za {username}: {odgovor.text}"
    return odgovor.json()["token"]


@pytest.fixture
def prijava(client: TestClient) -> Callable[..., dict[str, str]]:
    """prijava("ana") ili prijava("novi", "Lozinka123!") → zaglavlje za autentikaciju."""

    def _prijava(username: str, lozinka: str | None = None) -> dict[str, str]:
        return {"Authorization": f"Bearer {token(client, username, lozinka)}"}

    return _prijava


@pytest.fixture
def novi_korisnik(client: TestClient) -> Callable[[str, str], str]:
    def _novi(prefiks: str, lozinka: str) -> str:
        username = prefiks + uuid.uuid4().hex[:10]
        odgovor = client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": lozinka,
                "email": f"{username}@primjer.hr",
                "ime": "Test",
                "prezime": "Korisnik",
            },
        )
        assert odgovor.status_code == 201, f"registracija nije uspjela: {odgovor.text}"
        return username

    return _novi
