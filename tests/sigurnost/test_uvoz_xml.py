"""Sigurnosni test za uvoz edukacija iz XML-a."""

from collections.abc import Callable
from pathlib import Path

from fastapi.testclient import TestClient


def test_uvoz_xml_ne_cita_vanjski_entitet(
    client: TestClient,
    prijava: Callable[..., dict[str, str]],
    tmp_path: Path,
) -> None:
    tajna = tmp_path / "tajna.txt"
    tajna.write_text("TAJNI SADRZAJ", encoding="utf-8")
    xml = f"""<!DOCTYPE edukacije [
<!ENTITY tajna SYSTEM "{tajna.as_uri()}">
]>
<edukacije>
  <edukacija>
    <naziv>&tajna;</naziv>
    <datum>2026-12-03</datum>
    <kapacitet>15</kapacitet>
  </edukacija>
</edukacije>"""

    odgovor = client.post(
        "/api/edukacije/uvoz",
        content=xml,
        headers={**prijava("voditelj"), "Content-Type": "application/xml"},
    )

    assert "TAJNI SADRZAJ" not in odgovor.text

