"""Čitanje XML-a s planom edukacija::

    <edukacije><edukacija><naziv>Excel za početnike</naziv><datum>2026-12-03</datum>
    <kapacitet>15</kapacitet></edukacija></edukacije>
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from lxml import etree

from kadrovska.platforma.greske import ApiGreska


@dataclass(frozen=True)
class Stavka:
    naziv: str
    datum: date
    kapacitet: int


def procitaj(xml: bytes) -> list[Stavka]:
    try:
        korijen = _ucitaj(xml)
    except etree.XMLSyntaxError as e:
        raise ApiGreska.neispravno("Neispravan XML.") from e
    stavke: list[Stavka] = []
    for redni_broj, edukacija in enumerate(korijen.iter("edukacija"), start=1):
        try:
            stavke.append(
                Stavka(
                    naziv=_tekst(edukacija, "naziv"),
                    datum=date.fromisoformat(_tekst(edukacija, "datum")),
                    kapacitet=int(_tekst(edukacija, "kapacitet")),
                )
            )
        except ValueError as e:
            raise ApiGreska.neispravno(f"Neispravni podaci u edukaciji {redni_broj}.") from e
    return stavke


def _ucitaj(xml: bytes) -> etree._Element:
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    return etree.fromstring(xml, parser)


def _tekst(roditelj: etree._Element, naziv: str) -> str:
    element = next(roditelj.iter(naziv), None)
    vrijednost = None if element is None else "".join(element.itertext()).strip()
    if not vrijednost:
        raise ValueError(f"Nedostaje element {naziv}")
    return vrijednost
