"""HTML stranice: početna, prijava obrascem (postavlja kolačić SESSION) i promjena lozinke tokenom."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from kadrovska.platforma import html
from kadrovska.platforma.autentikacija import KOLACIC, javno
from kadrovska.platforma.greske import ApiGreska
from kadrovska.platforma.kontekst import Ctx
from kadrovska.platforma.korisnici import PrijavaZahtjev
from kadrovska.platforma.ogranicenje import ogranicenje_prijave

router = APIRouter()

Polje = Annotated[str | None, Form()]
PovratnaAdresa = Annotated[str | None, Form(alias="returnUrl")]
NovaLozinka = Annotated[str | None, Form(alias="novaLozinka")]

# CSP za HTML stranice (dopušta inline style u predlošcima; API zadržava stroži default).
_HTML_CSP = "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"


@router.get("/", response_class=HTMLResponse)
@javno
def pocetna(ctx: Ctx) -> HTMLResponse:
    naziv = ctx.postavke.naziv
    tijelo = f"""<h1>{html.escape(naziv)}</h1>
<p>Interni HR portal: imenik zaposlenika, godišnji odmori, platne liste i edukacije.</p>
<ul>
<li><a href="/prijava">Prijava</a></li>
<li><a href="/api/health">Stanje sustava</a></li>
</ul>"""
    return html.odgovor(html.stranica(naziv, tijelo), csp=_HTML_CSP)


@router.get("/prijava", response_class=HTMLResponse)
@javno
def obrazac(ctx: Ctx, return_url: Annotated[str | None, Query(alias="returnUrl")] = None) -> HTMLResponse:
    return html.odgovor(_obrazac_prijave(ctx, return_url, None), csp=_HTML_CSP)


@router.post("/prijava", dependencies=[Depends(ogranicenje_prijave)])
@javno
def prijava(ctx: Ctx, username: Polje = None, password: Polje = None, return_url: PovratnaAdresa = None) -> Response:
    korisnik = ctx.korisnici.prijava(PrijavaZahtjev(username=username, password=password))
    if korisnik is None:
        return html.odgovor(_obrazac_prijave(ctx, return_url, "Neispravno korisničko ime ili lozinka."), csp=_HTML_CSP)
    token = ctx.tokeni.izdaj(korisnik.prijavljeni())
    odgovor = RedirectResponse(odrediste(return_url), status_code=302)
    odgovor.set_cookie(KOLACIC, token, httponly=True, samesite="lax", path="/")
    odgovor.headers["Content-Security-Policy"] = _HTML_CSP
    return odgovor


@router.get("/reset", response_class=HTMLResponse)
@javno
def obrazac_za_lozinku(ctx: Ctx, token: str | None = None) -> HTMLResponse:
    return html.odgovor(_obrazac_nove_lozinke(ctx, token, None), csp=_HTML_CSP)


@router.post("/reset", response_class=HTMLResponse)
@javno
def nova_lozinka(ctx: Ctx, token: Polje = None, lozinka: NovaLozinka = None) -> HTMLResponse:
    try:
        promijenjena = ctx.reset.postavi_novu_lozinku(token, lozinka)
    except ApiGreska as e:
        return html.odgovor(_obrazac_nove_lozinke(ctx, token, e.poruka), csp=_HTML_CSP)
    if not promijenjena:
        return html.odgovor(_obrazac_nove_lozinke(ctx, token, "Token nije valjan ili je istekao."), csp=_HTML_CSP)
    tijelo = '<h1>Lozinka je promijenjena</h1>\n<p><a href="/prijava">Prijava</a></p>'
    return html.odgovor(html.stranica("Lozinka je promijenjena", tijelo), csp=_HTML_CSP)


def _poruka(poruka: str | None) -> str:
    return "" if poruka is None else f'<p class="poruka">{html.escape(poruka)}</p>'


def _obrazac_prijave(ctx: Ctx, return_url: str | None, poruka: str | None) -> str:
    tijelo = f"""<h1>Prijava</h1>
{_poruka(poruka)}
<form method="post" action="/prijava">
<label>Korisničko ime <input name="username" autocomplete="username" required></label>
<label>Lozinka <input name="password" type="password" autocomplete="current-password" required></label>
<input type="hidden" name="returnUrl" value="{html.escape(return_url)}">
<p><button type="submit">Prijavi se</button></p>
</form>"""
    return html.stranica(f"Prijava – {ctx.postavke.naziv}", tijelo)


def _obrazac_nove_lozinke(ctx: Ctx, token: str | None, poruka: str | None) -> str:
    tijelo = f"""<h1>Nova lozinka</h1>
{_poruka(poruka)}
<form method="post" action="/reset">
<input type="hidden" name="token" value="{html.escape(token)}">
<label>Nova lozinka <input name="novaLozinka" type="password" autocomplete="new-password" required></label>
<p><button type="submit">Spremi</button></p>
</form>"""
    return html.stranica(f"Nova lozinka – {ctx.postavke.naziv}", tijelo)


def odrediste(return_url: str | None) -> str:
    if return_url is None or not return_url.strip():
        return "/"
    lokalni_put = (
        return_url.startswith("/")
        and not return_url.startswith("//")
        and "\\" not in return_url
        and all(ord(znak) >= 32 and ord(znak) != 127 for znak in return_url)
    )
    return return_url if lokalni_put else "/"
