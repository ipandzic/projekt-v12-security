"""Sigurnosni test za pohranu lozinki."""

from kadrovska.platforma.lozinke import LozinkaHasher


def test_argon2_koristi_nasumicnu_sol() -> None:
    hasher = LozinkaHasher()

    prvi_hash = hasher.hash("Lozinka123!")
    drugi_hash = hasher.hash("Lozinka123!")

    assert prvi_hash != drugi_hash
    assert hasher.provjeri("Lozinka123!", prvi_hash)
    assert hasher.provjeri("Lozinka123!", drugi_hash)

