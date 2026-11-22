"""Zaboravljena lozinka: token se šalje e-poštom, a njime se postavlja nova lozinka."""

from __future__ import annotations

import secrets

from kadrovska.platforma.baza import Baza
from kadrovska.platforma.korisnici import KorisnikService, provjeri_lozinku
from kadrovska.platforma.posta import PostaService


class ResetLozinkeService:
    def __init__(self, baza: Baza, korisnici: KorisnikService, posta: PostaService) -> None:
        self._baza = baza
        self._korisnici = korisnici
        self._posta = posta

    def zatrazi(self, username: str) -> None:
        korisnik = self._korisnici.pronadi(username)
        if korisnik is None:
            return
        token = secrets.token_urlsafe(32)
        self._baza.izvrsi("INSERT INTO reset_tokeni (username, token) VALUES (?, ?)", (username, token))
        self._posta.posalji_upute_za_lozinku(korisnik, token)

    def postavi_novu_lozinku(self, token: str | None, nova_lozinka: str | None) -> bool:
        provjeri_lozinku(nova_lozinka)
        if token is None or not token.strip():
            return False
        zapis = self._baza.jedan("SELECT username FROM reset_tokeni WHERE token = ?", (token.strip(),))
        if zapis is None:
            return False
        self._korisnici.promijeni_lozinku(zapis["username"], nova_lozinka)
        return True
