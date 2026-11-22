"""Izrada jednostavnog jednostraničnog PDF dokumenta s tekstom (bez vanjskih biblioteka)."""

from __future__ import annotations

import unicodedata


def izradi(naslov: str, retci: list[str]) -> bytes:
    tok = "BT\n/F1 16 Tf\n50 790 Td\n18 TL\n(" + _tekst(naslov) + ") Tj\nT*\n/F1 11 Tf\n14 TL\n"
    for redak in retci:
        tok += "T*\n(" + _tekst(redak) + ") Tj\n"
    tok += "ET"
    objekti = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        f"<< /Length {len(tok.encode('ascii'))} >>\nstream\n{tok}\nendstream",
    ]
    izlaz = bytearray(b"%PDF-1.4\n")
    pomaci = []
    for broj, objekt in enumerate(objekti, start=1):
        pomaci.append(len(izlaz))
        izlaz += f"{broj} 0 obj\n{objekt}\nendobj\n".encode("ascii")
    xref = len(izlaz)
    tablica = f"xref\n0 {len(objekti) + 1}\n0000000000 65535 f \n"
    tablica += "".join(f"{pomak:010d} 00000 n \n" for pomak in pomaci)
    tablica += f"trailer\n<< /Size {len(objekti) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    izlaz += tablica.encode("ascii")
    return bytes(izlaz)


def _tekst(vrijednost: str | None) -> str:
    """Standardni PDF font nema sva hrvatska slova pa se dijakritici uklanjaju."""
    bez = unicodedata.normalize("NFD", vrijednost or "")
    bez = "".join(z for z in bez if not unicodedata.combining(z))
    bez = bez.replace("đ", "d").replace("Đ", "D").replace("–", "-").replace("—", "-")
    rezultat = []
    for znak in bez:
        if znak in "()\\":
            rezultat.append("\\" + znak)
        elif 32 <= ord(znak) < 127:
            rezultat.append(znak)
        else:
            rezultat.append("?")
    return "".join(rezultat)
