import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno


def test_health_radi_bez_prijave(client: TestClient) -> None:
    odgovor = client.get("/api/health")
    assert odgovor.status_code == 200
    assert odgovor.json()["status"] == "UP"


def test_prijava_ispravnim_podacima_vraca_token_i_ulogu(client: TestClient) -> None:
    odgovor = client.post("/api/auth/login", json={"username": "ana", "password": "Ana12345!"})
    assert odgovor.status_code == 200
    tijelo = odgovor.json()
    assert tijelo["token"]
    assert tijelo["username"] == "ana"
    assert tijelo["uloga"] == "KORISNIK"


def test_prijava_pogresnom_lozinkom_vraca_401(client: TestClient) -> None:
    odgovor = client.post("/api/auth/login", json={"username": "ana", "password": "kriva-lozinka"})
    assert odgovor.status_code == 401
    assert odgovor.json()["greska"] == "Neispravno korisničko ime ili lozinka."


def test_podaci_prijavljenog_korisnika(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/ja", headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert odgovor.json() == {
        "username": "ana",
        "ime": "Ana",
        "prezime": "Anić",
        "email": "ana@primjer.hr",
        "uloga": "KORISNIK",
    }


def test_voditelj_ima_ulogu_voditelj(client: TestClient) -> None:
    odgovor = client.post("/api/auth/login", json={"username": "voditelj", "password": "Ovlasteni12345!"})
    assert odgovor.status_code == 200
    assert odgovor.json()["uloga"] == "VODITELJ"


def test_registracija_i_prijava(client: TestClient, prijava, novi_korisnik) -> None:
    username = novi_korisnik("zaposlenik", "Zaposlenik12345!")
    ja = client.get("/api/ja", headers=prijava(username, "Zaposlenik12345!"))
    assert ja.status_code == 200
    assert ja.json()["username"] == username
    assert ja.json()["uloga"] == "KORISNIK"


def test_registracija_zauzetog_imena_vraca_409(client: TestClient) -> None:
    odgovor = client.post(
        "/api/auth/register",
        json={
            "username": "ana",
            "password": "Nesto12345!",
            "email": "druga.ana@primjer.hr",
            "ime": "Ana",
            "prezime": "Druga",
        },
    )
    assert odgovor.status_code == 409


def test_registracija_s_prekratkom_lozinkom_vraca_400(client: TestClient) -> None:
    odgovor = client.post(
        "/api/auth/register",
        json={"username": "kratka1", "password": "abc", "email": "kratka@primjer.hr", "ime": "K", "prezime": "L"},
    )
    assert odgovor.status_code == 400
