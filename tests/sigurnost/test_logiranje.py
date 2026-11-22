"""Sigurnosni test za zaštitu osjetljivih podataka u logu."""

import logging

import pytest
from fastapi.testclient import TestClient


def test_lozinka_oib_i_razlog_nisu_u_logu(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="kadrovska")
    lozinka = "Ana12345!"
    oib = "48291736504"
    razlog = "POVJERLJIV RAZLOG TESTA"

    prijava = client.post("/api/auth/login", json={"username": "ana", "password": lozinka})
    token = prijava.json()["token"]
    odgovor = client.post(
        "/api/zahtjevi",
        json={"od": "2027-07-01", "do": "2027-07-14", "razlog": razlog, "oib": oib},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert odgovor.status_code == 201
    assert lozinka not in caplog.text
    assert oib not in caplog.text
    assert razlog not in caplog.text

