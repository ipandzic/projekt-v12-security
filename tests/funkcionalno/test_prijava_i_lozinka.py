import re

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

TOKEN = re.compile(r"Token:\s*(\S+)")


def test_pocetna_stranica_je_html(client: TestClient) -> None:
    odgovor = client.get("/")
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("text/html")
    assert "Kadrovska" in odgovor.text
    assert "/prijava" in odgovor.text


def test_obrazac_za_prijavu_sadrzi_polja_i_povratnu_adresu(client: TestClient) -> None:
    odgovor = client.get("/prijava", params={"returnUrl": "/moji"})
    assert odgovor.status_code == 200
    for dio in ('name="username"', 'name="password"', 'name="returnUrl"', 'value="/moji"'):
        assert dio in odgovor.text


def test_prijava_obrascem_preusmjerava_i_postavlja_kolacic(client: TestClient) -> None:
    odgovor = client.post("/prijava", data={"username": "ana", "password": "Ana12345!", "returnUrl": "/moji"})
    assert odgovor.status_code == 302
    assert odgovor.headers["location"] == "/moji"
    kolacic = odgovor.headers["set-cookie"]
    assert kolacic.startswith("SESSION=")
    assert "httponly" in kolacic.lower()


def test_kolacic_session_vrijedi_za_api(client: TestClient) -> None:
    prijava = client.post("/prijava", data={"username": "marko", "password": "Marko12345!", "returnUrl": "/"})
    kolacic = prijava.headers["set-cookie"].split(";")[0]
    client.cookies.clear()
    ja = client.get("/api/ja", headers={"Cookie": kolacic})
    assert ja.status_code == 200
    assert ja.json()["username"] == "marko"


def test_neuspjela_prijava_obrascem_prikazuje_poruku(client: TestClient) -> None:
    odgovor = client.post("/prijava", data={"username": "ana", "password": "pogresno", "returnUrl": "/"})
    assert odgovor.status_code == 200
    assert "Neispravno korisničko ime ili lozinka." in odgovor.text
    assert "set-cookie" not in odgovor.headers


def test_cijeli_tok_promjene_lozinke(client: TestClient, mape, novi_korisnik) -> None:
    username = novi_korisnik("zaboravni", "Stara12345!")
    zahtjev = client.post("/api/auth/reset-zahtjev", json={"username": username})
    assert zahtjev.status_code == 202
    assert zahtjev.json()["poruka"] == "Ako korisnik postoji, poslali smo upute na e-mail."

    poruke = sorted(mape.posta.glob(f"{username}-*.txt"))
    assert len(poruke) == 1
    poruka = poruke[0].read_text(encoding="utf-8")
    assert "/reset?token=" in poruka
    pogodak = TOKEN.search(poruka)
    assert pogodak is not None

    reset = client.post("/api/auth/reset", json={"token": pogodak.group(1), "novaLozinka": "Nova12345!"})
    assert reset.status_code == 200
    assert reset.json()["poruka"] == "Lozinka je promijenjena."
    assert client.post("/api/auth/login", json={"username": username, "password": "Nova12345!"}).status_code == 200
    assert client.post("/api/auth/login", json={"username": username, "password": "Stara12345!"}).status_code == 401


def test_zahtjev_za_nepostojeceg_korisnika_vraca_202_bez_poruke(client: TestClient, mape) -> None:
    zahtjev = client.post("/api/auth/reset-zahtjev", json={"username": "nepostojeci"})
    assert zahtjev.status_code == 202
    assert list(mape.posta.glob("nepostojeci-*.txt")) == []


def test_izmisljeni_token_vraca_400(client: TestClient) -> None:
    reset = client.post("/api/auth/reset", json={"token": "ovo-nije-token", "novaLozinka": "Nova12345!"})
    assert reset.status_code == 400
