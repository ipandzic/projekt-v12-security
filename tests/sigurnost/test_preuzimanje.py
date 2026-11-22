"""Sigurnosni test za preuzimanje datoteke platne liste."""

from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import Mape


def test_preuzimanje_ne_dopusta_path_traversal(
    client: TestClient,
    prijava: Callable[..., dict[str, str]],
    mape: Mape,
) -> None:
    tajna = mape.dokumenti.parent / "tajna.txt"
    tajna.write_text("TAJNI SADRZAJ", encoding="utf-8")

    odgovor = client.get(
        "/api/platne-liste/preuzmi",
        params={"datoteka": "../tajna.txt"},
        headers=prijava("admin"),
    )

    assert odgovor.status_code == 404
    assert odgovor.json() == {"greska": "Datoteka nije pronađena."}

