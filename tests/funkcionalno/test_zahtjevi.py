import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno


def _moji(client: TestClient, zaglavlja: dict[str, str]) -> list[int]:
    return [z["id"] for z in client.get("/api/zahtjevi/moji", headers=zaglavlja).json()]


def _podnesi(client: TestClient, zaglavlja: dict[str, str], od: str, do: str, razlog: str, oib: str):
    return client.post(
        "/api/zahtjevi", json={"od": od, "do": do, "razlog": razlog, "oib": oib}, headers=zaglavlja
    )


def test_novi_zahtjev_je_vidljiv_u_mojim_zahtjevima(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    odgovor = _podnesi(client, zaglavlja, "2027-07-01", "2027-07-14", "Ljetni odmor", "48291736504")
    assert odgovor.status_code == 201
    zahtjev = odgovor.json()
    assert zahtjev["od"] == "2027-07-01"
    assert zahtjev["do"] == "2027-07-14"
    assert zahtjev["razlog"] == "Ljetni odmor"
    assert zahtjev["status"] == "PODNESEN"
    assert zahtjev["id"] in _moji(client, zaglavlja)


def test_moji_zahtjevi_sadrze_samo_vlastite_zahtjeve(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/zahtjevi/moji", headers=prijava("ana"))
    assert odgovor.status_code == 200
    zahtjevi = odgovor.json()
    assert [z["id"] for z in zahtjevi] == [1]
    assert zahtjevi[0]["razlog"] == "Obiteljsko putovanje"
    assert zahtjevi[0]["zaposlenik"] == "ana"


def test_datum_zavrsetka_prije_pocetka_vraca_400(client: TestClient, prijava) -> None:
    odgovor = _podnesi(client, prijava("ana"), "2027-07-14", "2027-07-01", "Odmor", "48291736504")
    assert odgovor.status_code == 400


def test_neispravan_oib_vraca_400(client: TestClient, prijava) -> None:
    odgovor = _podnesi(client, prijava("ana"), "2027-07-01", "2027-07-02", "Odmor", "12AB")
    assert odgovor.status_code == 400


def test_zaposlenik_moze_povuci_vlastiti_zahtjev(client: TestClient, prijava) -> None:
    zaglavlja = prijava("marko")
    zahtjev_id = _podnesi(client, zaglavlja, "2027-08-03", "2027-08-07", "Vjenčanje", "73019485267").json()["id"]

    odgovor = client.delete(f"/api/zahtjevi/{zahtjev_id}", headers=zaglavlja)

    assert odgovor.status_code == 204
    assert zahtjev_id not in _moji(client, zaglavlja)


def test_potvrda_za_ispis_sadrzi_razlog(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    zahtjev_id = _podnesi(
        client, zaglavlja, "2027-09-01", "2027-09-05", "Upis djeteta u školu", "48291736504"
    ).json()["id"]
    odgovor = client.get(f"/ispis/zahtjevi/{zahtjev_id}", headers=zaglavlja)
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("text/html")
    assert "Zahtjev za godišnji odmor" in odgovor.text
    assert "Upis djeteta u školu" in odgovor.text
    assert "01.09.2027." in odgovor.text
