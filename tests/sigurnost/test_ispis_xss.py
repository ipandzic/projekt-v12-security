"""Sigurnosni test za HTML stranicu ispisa zahtjeva."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def test_ispis_kodira_html_u_razlogu(
    client: TestClient,
    prijava: Callable[..., dict[str, str]],
) -> None:
    zaglavlja = prijava("ana")
    odgovor = client.post(
        "/api/zahtjevi",
        json={
            "od": "2027-07-01",
            "do": "2027-07-14",
            "razlog": "<script>alert(1)</script>",
            "oib": "48291736504",
        },
        headers=zaglavlja,
    )
    zahtjev_id = odgovor.json()["id"]

    ispis = client.get(f"/ispis/zahtjevi/{zahtjev_id}", headers=zaglavlja)

    assert "<script>alert(1)</script>" not in ispis.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in ispis.text

