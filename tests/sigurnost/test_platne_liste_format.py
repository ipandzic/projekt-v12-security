"""Sigurnosni test za autorizaciju pri nepoznatom formatu platne liste."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def test_nepoznat_format_ne_preskace_provjeru_vlasnika(
    client: TestClient,
    prijava: Callable[..., dict[str, str]],
) -> None:
    odgovor = client.get(
        "/api/platne-liste/2",
        params={"format": "nepoznat"},
        headers=prijava("ana"),
    )

    assert odgovor.status_code == 404
    assert odgovor.json() == {"greska": "Platna lista nije pronađena."}

