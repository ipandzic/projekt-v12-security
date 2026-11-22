"""Klijent sustava za e-učenje (LMS) u koji se upisuju polaznici edukacija.

U lokalnom okruženju LMS nije dostupan pa klijent nakon uobičajenog vremena odziva vraća lokalno
generiranu oznaku upisa.
"""

from __future__ import annotations

import itertools
import threading
import time

VRIJEME_ODZIVA = 0.15  # sekunde


class SustavZaEdukacijeKlijent:
    def __init__(self) -> None:
        self._brojac = itertools.count(3001)
        self._brava = threading.Lock()

    def upisi_polaznika(self, edukacija_id: int, zaposlenik: str) -> str:
        time.sleep(VRIJEME_ODZIVA)
        with self._brava:
            broj = next(self._brojac)
        return f"LMS-{edukacija_id}-{broj}"
