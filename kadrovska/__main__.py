"""Pokretanje: ``python -m kadrovska`` (http://localhost:8000)."""

import uvicorn

from kadrovska.postavke import Postavke


def main() -> None:
    uvicorn.run("kadrovska.main:app", host="127.0.0.1", port=Postavke().port)


if __name__ == "__main__":
    main()
