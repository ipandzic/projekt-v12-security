"""Korisnički računi: prijava, registracija i promjena lozinke."""

from __future__ import annotations

import logging
import re
import sqlite3
from dataclasses import dataclass

from pydantic import BaseModel

from kadrovska.platforma.autentikacija import PrijavljeniKorisnik
from kadrovska.platforma.baza import Baza
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.lozinke import LozinkaHasher

log = logging.getLogger(__name__)

KORISNICKO_IME = re.compile(r"[A-Za-z0-9._-]{3,50}")
MIN_DULJINA_LOZINKE = 8


class PrijavaZahtjev(BaseModel):
    username: str | None = None
    password: str | None = None


class RegistracijaZahtjev(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    ime: str | None = None
    prezime: str | None = None


@dataclass(frozen=True)
class Korisnik:
    id: int
    username: str
    password_hash: str
    email: str | None
    ime: str | None
    prezime: str | None
    uloga: str
    oib: str | None

    def prijavljeni(self) -> PrijavljeniKorisnik:
        return PrijavljeniKorisnik(self.id, self.username, self.uloga)


def provjeri_lozinku(lozinka: str | None) -> None:
    if lozinka is None or len(lozinka) < MIN_DULJINA_LOZINKE:
        raise ApiGreska.neispravno(f"Lozinka mora imati najmanje {MIN_DULJINA_LOZINKE} znakova.")


class KorisnikService:
    def __init__(self, baza: Baza, hasher: LozinkaHasher) -> None:
        self._baza = baza
        self._hasher = hasher

    def pronadi(self, username: str | None) -> Korisnik | None:
        if username is None:
            return None
        red = self._baza.jedan(
            "SELECT id, username, password_hash, email, ime, prezime, uloga, oib FROM korisnici WHERE username = ?",
            (username,),
        )
        return Korisnik(**red) if red else None

    def prijava(self, zahtjev: PrijavaZahtjev) -> Korisnik | None:
        if zahtjev.username is None or zahtjev.password is None:
            return None
        username = zahtjev.username
        log.info("Zahtjev za prijavu korisnika: %s", username)
        korisnik = self.pronadi(username)
        if korisnik is not None and self._hasher.provjeri(zahtjev.password, korisnik.password_hash):
            return korisnik
        return None

    def registriraj(self, zahtjev: RegistracijaZahtjev) -> Korisnik:
        if zahtjev.username is None or not KORISNICKO_IME.fullmatch(zahtjev.username):
            raise ApiGreska.neispravno("Korisničko ime mora imati 3–50 znakova (slova, brojke, točka, crtica).")
        provjeri_lozinku(zahtjev.password)
        if zahtjev.email is None or "@" not in zahtjev.email:
            raise ApiGreska.neispravno("Neispravna adresa e-pošte.")
        if self.pronadi(zahtjev.username) is not None:
            raise ApiGreska(409, "Korisničko ime je zauzeto.")
        try:
            self.kreiraj(zahtjev.username, zahtjev.password, zahtjev.email, zahtjev.ime, zahtjev.prezime, "KORISNIK")
        except sqlite3.IntegrityError as e:
            raise ApiGreska(409, "Korisničko ime je zauzeto.") from e
        log.info("Registriran novi korisnik %s", zahtjev.username)
        korisnik = self.pronadi(zahtjev.username)
        if korisnik is None:
            raise RuntimeError("Novi korisnik nije pronađen u bazi")
        return korisnik

    def kreiraj(
        self,
        username: str,
        lozinka: str,
        email: str | None,
        ime: str | None,
        prezime: str | None,
        uloga: str,
        oib: str | None = None,
    ) -> int:
        return self._baza.umetni(
            "INSERT INTO korisnici (username, password_hash, email, ime, prezime, uloga, oib) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, self._hasher.hash(lozinka), email, ime, prezime, uloga, oib),
        )

    def promijeni_lozinku(self, username: str, nova_lozinka: str) -> None:
        provjeri_lozinku(nova_lozinka)
        self._baza.izvrsi(
            "UPDATE korisnici SET password_hash = ? WHERE username = ?", (self._hasher.hash(nova_lozinka), username)
        )
        log.info("Promijenjena lozinka korisnika %s", username)
