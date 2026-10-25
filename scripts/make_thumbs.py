#!/usr/bin/env python3
"""Regenerate the document thumbnails for oversightengineering.com.

Every certificate, letter, photograph and completion notice on the site needs a 420px
preview in docs/assets/thumbs/, and build.py refuses to build when one is missing (no
card is ever a blank rectangle). Run this after adding or replacing anything in
docs/assets/docs/ or docs/assets/proof/, then rebuild.

    /usr/bin/python3 scripts/make_thumbs.py

Needs PIL and poppler's pdftoppm. System python3 on macOS has both.
"""
import os
import pathlib
import subprocess
import sys

from PIL import Image

REPO = pathlib.Path(os.environ.get(
    "SITE_REPO", pathlib.Path.home() / "Documents" / "GitHub" / "oversightengineering"))
DOCS = REPO / "docs" / "assets" / "docs"      # site-wide PDFs, doc(href, label)
PROOF = REPO / "docs" / "assets" / "proof"    # image proofs, opened in the viewer
THUMBS = REPO / "docs" / "assets" / "thumbs"
TMP = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "oe-thumbs"

WIDTH = 420          # card width is ~195px; 420 stays sharp on a 2x display
PDF_DPI = 90         # page one only: the preview has to read as a document, not be legible
JPEG_QUALITY = 82

if not DOCS.exists() or not PROOF.exists():
    sys.exit(f"{REPO} does not look like the site repo")

THUMBS.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)


def save(im, dest):
    im = im.convert("RGB")
    if im.size[0] > WIDTH:
        h = round(im.size[1] * WIDTH / im.size[0])
        im = im.resize((WIDTH, h), Image.LANCZOS)
    im.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    print(f"{dest.name:48} {im.size[0]}x{im.size[1]}  {dest.stat().st_size // 1024} KB")


for pdf in sorted(DOCS.glob("*.pdf")):
    stem = TMP / pdf.stem
    subprocess.run(["pdftoppm", "-r", str(PDF_DPI), "-f", "1", "-l", "1", "-png",
                    "-singlefile", str(pdf), str(stem)], check=True)
    save(Image.open(str(stem) + ".png"), THUMBS / f"{pdf.stem}.jpg")

# Image proofs: certificates and letters arrive as PNG, photographs as JPEG.
PROOF_IMAGES = [p for p in sorted(PROOF.iterdir())
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
for img in PROOF_IMAGES:
    save(Image.open(img), THUMBS / f"{img.stem}.jpg")

built = {p.stem for p in THUMBS.iterdir()}
expected = {p.stem for p in DOCS.glob("*.pdf")} | {p.stem for p in PROOF_IMAGES}
orphans = sorted(built - expected)
if orphans:
    print("\nthumbnails with no source document (safe to delete):")
    for o in orphans:
        print(f"  {o}.jpg")

print("\ntotal:", sum(p.stat().st_size for p in THUMBS.iterdir()) // 1024, "KB")
