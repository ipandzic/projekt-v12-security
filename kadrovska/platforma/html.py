"""Jednostavne HTML stranice (početna, prijava, promjena lozinke)."""

from __future__ import annotations

import html

from fastapi.responses import HTMLResponse


def escape(tekst: str | None) -> str:
    return "" if tekst is None else html.escape(tekst, quote=True)


def stranica(naslov: str, tijelo: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="hr">
<head>
<meta charset="UTF-8">
<title>{escape(naslov)}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }}
label {{ display: block; margin-top: .75rem; }}
.poruka {{ color: #b00020; }}
</style>
</head>
<body>
{tijelo}
</body>
</html>
"""


def odgovor(sadrzaj: str, status: int = 200, csp: str | None = None) -> HTMLResponse:
    odgovor_ = HTMLResponse(content=sadrzaj, status_code=status)
    if csp:
        odgovor_.headers["Content-Security-Policy"] = csp
    return odgovor_
