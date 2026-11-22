CREATE TABLE korisnici (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email         TEXT,
    ime           TEXT,
    prezime       TEXT,
    uloga         TEXT NOT NULL,
    oib           TEXT
);

CREATE TABLE reset_tokeni (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL,
    token      TEXT    NOT NULL,
    istjece    TEXT,
    iskoristen INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE postavke (
    username   TEXT PRIMARY KEY,
    podsjetnik INTEGER NOT NULL,
    sati_prije INTEGER NOT NULL,
    kanal      TEXT    NOT NULL
);

CREATE TABLE zaposlenici (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ime     TEXT NOT NULL,
    prezime TEXT NOT NULL,
    odjel   TEXT NOT NULL,
    email   TEXT NOT NULL
);

-- Zahtjevi za godišnji odmor (razdoblje datum_od – datum_do).
CREATE TABLE zahtjevi (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    zaposlenik TEXT NOT NULL,
    datum_od   TEXT NOT NULL,
    datum_do   TEXT NOT NULL,
    razlog     TEXT NOT NULL,
    oib        TEXT,
    status     TEXT NOT NULL,
    kreirano   TEXT NOT NULL
);

CREATE TABLE platne_liste (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    zaposlenik TEXT NOT NULL,
    razdoblje  TEXT NOT NULL,
    datoteka   TEXT NOT NULL
);

CREATE TABLE edukacije (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv       TEXT    NOT NULL,
    datum       TEXT    NOT NULL,
    kapacitet   INTEGER NOT NULL,
    prijavljeno INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE prijave_edukacije (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    edukacija_id INTEGER NOT NULL REFERENCES edukacije (id),
    zaposlenik   TEXT    NOT NULL,
    kreirano     TEXT    NOT NULL,
    oznaka_lms   TEXT
);
