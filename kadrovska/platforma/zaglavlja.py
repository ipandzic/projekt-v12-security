"""Sigurnosna zaglavlja za svaki HTTP odgovor (čisti ASGI middleware)."""

from __future__ import annotations

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

SIGURNOSNA_ZAGLAVLJA = {
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class SigurnosnaZaglavlja:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.zaglavlja = dict(SIGURNOSNA_ZAGLAVLJA)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def posalji(poruka: Message) -> None:
            if poruka["type"] == "http.response.start":
                zaglavlja = MutableHeaders(scope=poruka)
                for ime, vrijednost in self.zaglavlja.items():
                    zaglavlja.setdefault(ime, vrijednost)
            await send(poruka)

        await self.app(scope, receive, posalji)
