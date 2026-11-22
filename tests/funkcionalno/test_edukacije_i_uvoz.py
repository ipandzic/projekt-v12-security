import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

# Edukacija 3 je rezervirana za posebne provjere i ne koristi se u ovim testovima.
IZUZETA_EDUKACIJA = 3

XML = """<?xml version="1.0" encoding="UTF-8"?>
<edukacije>
  <edukacija>
    <naziv>Excel za početnike</naziv>
    <datum>2026-12-03</datum>
    <kapacitet>15</kapacitet>
  </edukacija>
</edukacije>
"""


def _uvoz(client: TestClient, zaglavlja: dict[str, str], xml: str):
    return client.post(
        "/api/edukacije/uvoz", content=xml.encode("utf-8"), headers={**zaglavlja, "Content-Type": "application/xml"}
    )


def _nova_edukacija(client: TestClient, prijava, kapacitet: int) -> int:
    xml = (
        "<edukacije><edukacija><naziv>Radionica timskog rada</naziv><datum>2027-02-10</datum>"
        f"<kapacitet>{kapacitet}</kapacitet></edukacija></edukacije>"
    )
    odgovor = _uvoz(client, prijava("voditelj"), xml)
    assert odgovor.status_code == 200
    return odgovor.json()["edukacije"][0]["id"]


def _edukacija(client: TestClient, zaglavlja: dict[str, str], edukacija_id: int) -> dict:
    return next(e for e in client.get("/api/edukacije", headers=zaglavlja).json() if e["id"] == edukacija_id)


def _prijavi(client: TestClient, zaglavlja: dict[str, str], edukacija_id: int):
    return client.post(f"/api/edukacije/{edukacija_id}/prijava", headers=zaglavlja)


def test_popis_edukacija_prikazuje_kapacitet_i_slobodna_mjesta(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    odgovor = client.get("/api/edukacije", headers=zaglavlja)
    assert odgovor.status_code == 200
    edukacije = odgovor.json()
    assert len(edukacije) >= 5
    for edukacija in edukacije:
        assert edukacija["slobodno"] == edukacija["kapacitet"] - edukacija["prijavljeno"]
    assert _edukacija(client, zaglavlja, IZUZETA_EDUKACIJA)["kapacitet"] == 20


def test_prijava_na_edukaciju_povecava_broj_prijavljenih(client: TestClient, prijava) -> None:
    edukacija_id = _nova_edukacija(client, prijava, 10)
    zaglavlja = prijava("ana")

    odgovor = _prijavi(client, zaglavlja, edukacija_id)

    assert odgovor.status_code == 201
    assert odgovor.json()["edukacijaId"] == edukacija_id
    assert odgovor.json()["zaposlenik"] == "ana"
    assert _edukacija(client, zaglavlja, edukacija_id)["prijavljeno"] == 1


def test_ponovna_prijava_istog_zaposlenika_vraca_409(client: TestClient, prijava) -> None:
    edukacija_id = _nova_edukacija(client, prijava, 10)
    zaglavlja = prijava("marko")
    assert _prijavi(client, zaglavlja, edukacija_id).status_code == 201

    assert _prijavi(client, zaglavlja, edukacija_id).status_code == 409


def test_prijava_na_popunjenu_edukaciju_vraca_409(client: TestClient, prijava) -> None:
    edukacija_id = _nova_edukacija(client, prijava, 1)
    assert _prijavi(client, prijava("ana"), edukacija_id).status_code == 201

    odgovor = _prijavi(client, prijava("marko"), edukacija_id)

    assert odgovor.status_code == 409
    assert odgovor.json()["greska"] == "Nema slobodnih mjesta."


def test_prijava_na_nepostojecu_edukaciju_vraca_404(client: TestClient, prijava) -> None:
    assert _prijavi(client, prijava("ana"), 999999).status_code == 404


def test_voditelj_uvozi_edukacije_iz_xml(client: TestClient, prijava) -> None:
    zaglavlja = prijava("voditelj")
    odgovor = _uvoz(client, zaglavlja, XML)
    assert odgovor.status_code == 200
    assert odgovor.json()["uvezeno"] == 1
    edukacija = odgovor.json()["edukacije"][0]
    assert edukacija["naziv"] == "Excel za početnike"
    assert edukacija["id"] in [e["id"] for e in client.get("/api/edukacije", headers=zaglavlja).json()]


def test_administrator_moze_uvoziti_edukacije(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("admin"), XML).status_code == 200


def test_korisnik_ne_moze_uvoziti_edukacije(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("ana"), XML).status_code == 403


def test_neispravan_xml_vraca_400(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("voditelj"), "<edukacije><edukacija>").status_code == 400
