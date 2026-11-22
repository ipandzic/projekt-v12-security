"""Ograničavanje broja pokušaja prijave (limits): N/min po IP → 429 + Retry-After."""

from __future__ import annotations

import math
import time

from fastapi import Request
from limits import RateLimitItemPerMinute
from limits.storage import MemoryStorage, Storage
from limits.strategies import FixedWindowRateLimiter

from kadrovska.platforma.greske import ApiGreska

PREVISE_POKUSAJA = "Previše pokušaja prijave. Pokušajte ponovno kasnije."


class OgranicenjePrijave:
    def __init__(self, pokusaja_u_minuti: int = 5, spremiste: Storage | None = None) -> None:
        self._limit = RateLimitItemPerMinute(pokusaja_u_minuti)
        self._limiter = FixedWindowRateLimiter(spremiste or MemoryStorage())

    def provjeri(self, kljuc: str) -> None:
        if self._limiter.hit(self._limit, "prijava", kljuc):
            return
        reset, _ = self._limiter.get_window_stats(self._limit, "prijava", kljuc)
        sekundi = max(1, math.ceil(reset - time.time()))
        raise ApiGreska(429, PREVISE_POKUSAJA, headers={"Retry-After": str(sekundi)})


def ogranicenje_prijave(request: Request) -> None:
    ip = request.client.host if request.client else "nepoznato"
    request.app.state.kontekst.ogranicenje_prijave.provjeri(ip)
