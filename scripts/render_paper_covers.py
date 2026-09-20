"""Genera la portada (página 1) de cada informe semanal de papers/manifest.json.

Uso (desde la raíz del repo):  python scripts/render_paper_covers.py
Requiere:  pip install pymupdf

Escribe papers/covers/<num>.jpg. Es idempotente: solo renderiza las portadas que
faltan (usar --force para rehacerlas todas). La home (loadPapersManifest) muestra
esa imagen en lugar del texto; si falta, cae al título como respaldo.
"""
import json
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"
COVERS = PAPERS / "covers"


def main(force=False):
    COVERS.mkdir(exist_ok=True)
    manifest = json.loads((PAPERS / "manifest.json").read_text(encoding="utf-8"))
    for p in manifest:
        out = COVERS / f"{p['num']}.jpg"
        if out.exists() and not force:
            continue
        pdf = PAPERS / p["file"]
        if not pdf.exists():
            print(f"[skip] {p['num']}: falta {pdf.name}")
            continue
        page = pymupdf.open(pdf)[0]
        page.get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(out, jpg_quality=82)
        print(f"[ok]   {p['num']} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
