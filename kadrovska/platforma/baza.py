"""Rad s SQLite bazom u memoriji (jedna veza po instanci aplikacije)."""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any


class Baza:
    """Omotač oko jedne SQLite veze u memoriji; pristup vezi štiti brava pa je siguran za više dretvi."""

    def __init__(self) -> None:
        # isolation_level=None: svaka naredba se odmah potvrđuje; transakcije se otvaraju s transakcija()
        self._veza = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
        self._veza.row_factory = sqlite3.Row
        self._veza.execute("PRAGMA foreign_keys = ON")
        self._brava = threading.RLock()

    def skripta(self, sql: str) -> None:
        with self._brava:
            self._veza.executescript(sql)

    def izvrsi(self, sql: str, parametri: Sequence[Any] = ()) -> int:
        """Izvršava INSERT/UPDATE/DELETE i vraća broj promijenjenih redaka."""
        with self._brava:
            return self._veza.execute(sql, parametri).rowcount

    def umetni(self, sql: str, parametri: Sequence[Any] = ()) -> int:
        """Izvršava INSERT i vraća id novog retka."""
        with self._brava:
            return int(self._veza.execute(sql, parametri).lastrowid)

    def upit(self, sql: str, parametri: Sequence[Any] = ()) -> list[dict[str, Any]]:
        with self._brava:
            return [dict(red) for red in self._veza.execute(sql, parametri).fetchall()]

    def jedan(self, sql: str, parametri: Sequence[Any] = ()) -> dict[str, Any] | None:
        redovi = self.upit(sql, parametri)
        return redovi[0] if redovi else None

    def zatvori(self) -> None:
        with self._brava:
            self._veza.close()

    @contextmanager
    def transakcija(self) -> Iterator[Baza]:
        """Naredbe unutar bloka ``with`` izvršavaju se kao jedna transakcija (iznimka → ROLLBACK)."""
        with self._brava:
            self._veza.execute("BEGIN")
            try:
                yield self
            except BaseException:
                self._veza.execute("ROLLBACK")
                raise
            else:
                self._veza.execute("COMMIT")
