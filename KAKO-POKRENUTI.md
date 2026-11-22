# Kadrovska – kako pokrenuti

Interni HR portal tvrtke: imenik zaposlenika, zahtjevi za godišnji odmor, platne liste i prijave na edukacije.
Python 3.12+, FastAPI, SQLite baza u memoriji (podaci se pune pri svakom pokretanju).

## Preduvjeti

- Python 3.12 ili noviji (`python --version`; na Windowsu i `py --version`)
- VS Code (proširenja Python i Pylance) ili PyCharm: otvori mapu projekta

## Virtualno okruženje i ovisnosti

```bash
python -m venv .venv
source .venv/bin/activate            # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Pokretanje

```bash
python -m kadrovska
```

ili `uvicorn kadrovska.main:app --reload --port 8000`, ili u IDE-u pokreni `run.py` (u VS Codeu: *Run and Debug →
Kadrovska*).

- početna stranica: http://localhost:8000/
- prijava obrascem: http://localhost:8000/prijava
- provjera rada: http://localhost:8000/api/health
- dokumentacija API-ja (Swagger UI): http://localhost:8000/docs

Primjeri zahtjeva za REST API nalaze se u `http/kadrovska.http` (VS Code REST Client, PyCharm HTTP Client).

## Testovi

```bash
pytest                       # svi testovi
pytest -m funkcionalno       # funkcionalni testovi
pytest -m primjer            # primjer testa
pytest --cov --cov-report=html   # pokrivenost koda → htmlcov/index.html
```

Vlastite testove možeš temeljiti na fixture funkcijama iz `tests/conftest.py` (`client`, `prijava`, `novi_korisnik`,
`mape`) – pogledaj `tests/primjer/test_primjer_sigurnosnog_testa.py`. Svaki test dobiva svježu aplikaciju i bazu.

## Alati za analizu (neobavezno)

```bash
ruff check kadrovska                     # stil i pravila iz Bandita (S…)
bandit -c pyproject.toml -r kadrovska    # Bandit
pip-audit -r requirements.txt            # provjera ovisnosti u bazama sigurnosnih savjeta
cyclonedx-py requirements requirements.txt -o bom.json   # popis ovisnosti (SBOM)
```

`bom.json` možeš provjeriti i alatima poput OSV-Scanner ili Trivy.

## Korisnici

| Korisničko ime | Lozinka | Uloga |
|---|---|---|
| ana | `Ana12345!` | KORISNIK |
| marko | `Marko12345!` | KORISNIK |
| voditelj | `Ovlasteni12345!` | VODITELJ |
| admin | `Admin12345!` | ADMIN |

API prihvaća token u zaglavlju `Authorization: Bearer <token>` (dobiva se s `POST /api/auth/login`)
ili kolačić `SESSION` koji postavlja prijava obrascem.

## Konfiguracija (varijable okruženja, vidi `kadrovska/postavke.py`)

| Varijabla | Značenje | Zadano |
|---|---|---|
| `APP_STORAGE_DIR` | mapa s datotekama platnih lista | `./data/dokumenti` |
| `APP_MAILBOX_DIR` | mapa u koju se „šalju” e-poruke (tekstualne datoteke) | `./data/posta` |
| `APP_CORS_ALLOWED_ORIGINS` | origini frontend aplikacije (odvojeni zarezom) | `http://localhost:5173` |
| `APP_PORT` | port aplikacije | `8000` |

Poruke za promjenu lozinke ne šalju se stvarno, nego se zapisuju u `APP_MAILBOX_DIR`
(datoteka `<korisnik>-<vrijeme>.txt` s tokenom i poveznicom).
