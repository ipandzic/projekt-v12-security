import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

FRONTEND = "http://localhost:5173"


def _polje(odgovor, naziv: str) -> list[str]:
    return [zaposlenik[naziv] for zaposlenik in odgovor.json()]


def test_imenik_po_prezimenu_uzlazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/zaposlenici", params={"sort": "prezime", "smjer": "asc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert _polje(odgovor, "prezime") == ["Anić", "Babić", "Horvat", "Jurić", "Marić", "Tomić", "Vidović", "Zorić"]


def test_imenik_po_prezimenu_silazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/zaposlenici", params={"sort": "prezime", "smjer": "desc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert _polje(odgovor, "prezime") == ["Zorić", "Vidović", "Tomić", "Marić", "Jurić", "Horvat", "Babić", "Anić"]


def test_imenik_po_imenu_i_odjelu(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    po_imenu = client.get("/api/zaposlenici", params={"sort": "ime", "smjer": "asc"}, headers=zaglavlja)
    po_odjelu = client.get("/api/zaposlenici", params={"sort": "odjel", "smjer": "asc"}, headers=zaglavlja)
    assert _polje(po_imenu, "ime") == ["Ana", "Davor", "Ivan", "Lucija", "Maja", "Marko", "Sanja", "Tomislav"]
    odjeli = _polje(po_odjelu, "odjel")
    assert odjeli == sorted(odjeli)
    assert odjeli[0] == "Financije"


def test_zadano_sortiranje_je_po_prezimenu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/zaposlenici", headers=prijava("ana"))
    assert odgovor.status_code == 200
    prezimena = _polje(odgovor, "prezime")
    assert len(prezimena) == 8
    assert prezimena[0] == "Anić"


def test_imenik_trazi_prijavu(client: TestClient) -> None:
    assert client.get("/api/zaposlenici").status_code == 401


def test_cors_za_dopusteni_origin(client: TestClient) -> None:
    odgovor = client.get("/api/health", headers={"Origin": FRONTEND})
    assert odgovor.status_code == 200
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
    assert odgovor.headers.get("Access-Control-Allow-Credentials") == "true"


def test_preflight_s_dopustenog_origina(client: TestClient) -> None:
    odgovor = client.options(
        "/api/ja",
        headers={
            "Origin": FRONTEND,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert 200 <= odgovor.status_code < 300
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
