"""Jedinstven format grešaka: ``{"greska": "<poruka>"}``."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger(__name__)


class ApiGreska(Exception):
    """Greška koja se klijentu vraća kao ``{"greska": "..."}`` sa zadanim statusom."""

    def __init__(self, status: int, poruka: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(poruka)
        self.status = status
        self.poruka = poruka
        self.headers = headers

    @classmethod
    def nije_pronadeno(cls, poruka: str) -> ApiGreska:
        return cls(404, poruka)

    @classmethod
    def neispravno(cls, poruka: str) -> ApiGreska:
        return cls(400, poruka)

    @classmethod
    def zabranjeno(cls) -> ApiGreska:
        return cls(403, "Nemate ovlasti za ovu radnju.")


def greska(status: int, poruka: str, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"greska": poruka}, headers=headers)


_PORUKE = {
    401: "Potrebna je prijava.",
    404: "Resurs nije pronađen.",
    405: "Metoda nije podržana.",
    406: "Traženi format odgovora nije podržan.",
    415: "Vrsta sadržaja nije podržana.",
}


def registriraj(app: FastAPI) -> None:
    @app.exception_handler(ApiGreska)
    async def api_greska(_: Request, ex: ApiGreska) -> JSONResponse:
        return greska(ex.status, ex.poruka, ex.headers)

    @app.exception_handler(RequestValidationError)
    async def neispravan_zahtjev(_: Request, __: RequestValidationError) -> JSONResponse:
        return greska(400, "Neispravan zahtjev.")

    @app.exception_handler(StarletteHTTPException)
    async def http_greska(_: Request, ex: StarletteHTTPException) -> JSONResponse:
        if ex.status_code >= 500:
            return greska(ex.status_code, "Došlo je do pogreške.")
        return greska(ex.status_code, _PORUKE.get(ex.status_code, "Neispravan zahtjev."))

    @app.exception_handler(Exception)
    async def ostalo(_: Request, ex: Exception) -> JSONResponse:
        log.error("Neobrađena greška", exc_info=ex)
        return greska(500, "Došlo je do pogreške.")
