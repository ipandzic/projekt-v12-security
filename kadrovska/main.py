"""Aplikacija za uvicorn: ``uvicorn kadrovska.main:app --reload --port 8000``."""

from kadrovska.app import create_app
from kadrovska.logiranje import nastavi_logiranje

nastavi_logiranje()
app = create_app()
