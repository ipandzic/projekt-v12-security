"""Hashiranje lozinki preko pwdlib (Argon2id; stari argon2 hashevi se i dalje provjeravaju)."""

from __future__ import annotations

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class LozinkaHasher:
    """Izračun i provjera sažetka lozinke (registracija, prijava, promjena lozinke, početni podaci)."""

    def __init__(self) -> None:
        self._hasher = PasswordHash((Argon2Hasher(),))

    def hash(self, lozinka: str) -> str:
        return self._hasher.hash(lozinka)

    def provjeri(self, lozinka: str, spremljeni_hash: str | None) -> bool:
        if spremljeni_hash is None:
            return False
        valjan, _ = self._hasher.verify_and_update(lozinka, spremljeni_hash)
        return valjan
