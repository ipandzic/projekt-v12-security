"""Početni podaci (baza je u memoriji pa se puni pri svakom pokretanju).

Lozinke se spremaju istom metodom kao pri registraciji.
"""

from __future__ import annotations

import logging
from datetime import datetime

from kadrovska.platforma.kontekst import Kontekst

log = logging.getLogger(__name__)

PLACA_ANA = """Kadrovska d.o.o. – platna lista za razdoblje 2026-10
Zaposlenik: Ana Anić (Financije)
Bruto plaća: 1.850,00 EUR
Doprinosi za mirovinsko osiguranje: 370,00 EUR
Porez na dohodak: 152,40 EUR
Neto isplata: 1.327,60 EUR
Isplata na račun: HR12 2340 0091 1100 0000 1
"""

PLACA_MARKO = """Kadrovska d.o.o. – platna lista za razdoblje 2026-10
Zaposlenik: Marko Marić (Prodaja)
Bruto plaća: 1.640,00 EUR
Doprinosi za mirovinsko osiguranje: 328,00 EUR
Porez na dohodak: 121,80 EUR
Neto isplata: 1.190,20 EUR
Isplata na račun: HR45 2484 0081 1200 0000 2
"""

# (ime, prezime, odjel, email) – id 1–8
ZAPOSLENICI = [
    ("Ana", "Anić", "Financije", "ana@primjer.hr"),
    ("Marko", "Marić", "Prodaja", "marko@primjer.hr"),
    ("Tomislav", "Tomić", "Ljudski potencijali", "voditelj@primjer.hr"),
    ("Lucija", "Babić", "Informatika", "lucija.babic@primjer.hr"),
    ("Davor", "Jurić", "Informatika", "davor.juric@primjer.hr"),
    ("Sanja", "Horvat", "Pravna služba", "sanja.horvat@primjer.hr"),
    ("Ivan", "Zorić", "Prodaja", "ivan.zoric@primjer.hr"),
    ("Maja", "Vidović", "Financije", "maja.vidovic@primjer.hr"),
]

# (zaposlenik, od, do, razlog, oib) – id 1–2
ZAHTJEVI = [
    ("ana", "2026-12-21", "2026-12-31", "Obiteljsko putovanje", "48291736504"),
    ("marko", "2027-01-05", "2027-01-09", "Selidba", "73019485267"),
]

# (zaposlenik, razdoblje, datoteka) – id 1–2
PLATNE_LISTE = [
    ("ana", "2026-10", "placa-ana-2026-10.txt"),
    ("marko", "2026-10", "placa-marko-2026-10.txt"),
]

# (naziv, datum, kapacitet, prijavljeno) – id 1–5
EDUKACIJE = [
    ("Uvod u GDPR", "2026-12-02", 30, 5),
    ("Excel za napredne", "2026-12-04", 15, 3),
    ("Sigurnost na radu – zadnje mjesto", "2026-12-09", 20, 19),
    ("Komunikacijske vještine", "2026-12-11", 25, 0),
    ("Prva pomoć", "2027-01-14", 12, 2),
]


def ucitaj(ctx: Kontekst) -> None:
    ctx.pohrana.pripremi()
    ctx.pohrana.zapisi_ako_ne_postoji("placa-ana-2026-10.txt", PLACA_ANA)
    ctx.pohrana.zapisi_ako_ne_postoji("placa-marko-2026-10.txt", PLACA_MARKO)

    korisnici = ctx.korisnici
    korisnici.kreiraj("ana", "Ana12345!", "ana@primjer.hr", "Ana", "Anić", "KORISNIK", "48291736504")
    korisnici.kreiraj("marko", "Marko12345!", "marko@primjer.hr", "Marko", "Marić", "KORISNIK", "73019485267")
    korisnici.kreiraj(
        "voditelj", "Ovlasteni12345!", "voditelj@primjer.hr", "Tomislav", "Tomić", "VODITELJ", "50617283940"
    )
    korisnici.kreiraj("admin", "Admin12345!", "admin@primjer.hr", "Ivana", "Admin", "ADMIN", "61728394051")

    baza = ctx.baza
    with baza.transakcija():
        for zaposlenik in ZAPOSLENICI:
            baza.izvrsi("INSERT INTO zaposlenici (ime, prezime, odjel, email) VALUES (?, ?, ?, ?)", zaposlenik)
        sada = datetime.now().isoformat(timespec="seconds")
        for zaposlenik, od, do, razlog, oib in ZAHTJEVI:
            baza.izvrsi(
                "INSERT INTO zahtjevi (zaposlenik, datum_od, datum_do, razlog, oib, status, kreirano) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (zaposlenik, od, do, razlog, oib, "PODNESEN", sada),
            )
        for platna_lista in PLATNE_LISTE:
            baza.izvrsi("INSERT INTO platne_liste (zaposlenik, razdoblje, datoteka) VALUES (?, ?, ?)", platna_lista)
        for edukacija in EDUKACIJE:
            baza.izvrsi("INSERT INTO edukacije (naziv, datum, kapacitet, prijavljeno) VALUES (?, ?, ?, ?)", edukacija)
    log.info("Početni podaci su učitani")
