"""Sigurnosni test za sortiranje imenika zaposlenika."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def test_sortiranje_odbija_sql_izraz(
    client: TestClient,
    prijava: Callable[..., dict[str, str]],
) -> None:
    odgovor = client.get(
        "/api/zaposlenici",
        params={"sort": "CASE WHEN 1=1 THEN prezime ELSE ime END", "smjer": "asc"},
        headers=prijava("ana"),
    )

    assert odgovor.status_code == 400
    assert odgovor.json() == {"greska": "Neispravno sortiranje."}

