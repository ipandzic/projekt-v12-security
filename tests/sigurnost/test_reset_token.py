"""Sigurnosni test za token obnove lozinke."""

from fastapi import FastAPI


def test_svaki_zahtjev_za_obnovu_dobiva_novi_token(app: FastAPI) -> None:
    ctx = app.state.kontekst

    ctx.reset.zatrazi("ana")
    ctx.reset.zatrazi("ana")

    tokeni = ctx.baza.upit("SELECT token FROM reset_tokeni WHERE username = ? ORDER BY id", ("ana",))
    assert tokeni[0]["token"] != tokeni[1]["token"]

