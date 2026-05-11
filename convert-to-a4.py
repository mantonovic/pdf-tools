#!/usr/bin/env python3
"""
Scan the data/ folder for A3 PDFs and convert them to A4 using a print-style
fit-to-page workflow.

Each A3 page is sent through Ghostscript with an A4 page device sized to match
the page's effective orientation, which is closer to the manual PDF Arranger
page-size operation.
Output files are placed alongside the originals with an '_A4' suffix.
"""

import shutil
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from typing import Any

try:
    fitz = import_module("fitz")  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install pymupdf")
    sys.exit(1)

# A3 and A4 dimensions in points (1 pt = 1/72 inch)
# A3: 297 x 420 mm  →  841.89 x 1190.55 pt
# A4: 210 x 297 mm  →  595.28 x  841.89 pt

A3_SHORT_PT = 841.89   # shorter side of A3 (= longer side of A4)
A3_LONG_PT  = 1190.55  # longer  side of A3
TOLERANCE   = 5.0      # points tolerance for dimension matching
A4_SHORT_PT = 595.28   # 210 mm in points
A4_LONG_PT  = 841.89   # 297 mm in points


def _ghostscript_executable() -> str:
    executable = shutil.which("gs") or shutil.which("ghostscript")
    if executable:
        return executable

    print("Ghostscript is required. Install it and ensure 'gs' is on PATH.")
    sys.exit(1)


def is_a3(page: Any) -> bool:
    """Return True if the page dimensions match A3 (portrait or landscape)."""
    w, h = page.rect.width, page.rect.height
    short, long = sorted([w, h])
    return (
        abs(short - A3_SHORT_PT) <= TOLERANCE and
        abs(long  - A3_LONG_PT)  <= TOLERANCE
    )


def _convert_page_with_ghostscript(src_path: Path, page_number: int, landscape: bool):
    """Render one source page to a temporary PDF that fits A4 like a print job."""
    gs = _ghostscript_executable()
    width = 842 if landscape else 595
    height = 595 if landscape else 842

    temp_dir = tempfile.TemporaryDirectory(prefix="tool-pdf-a4-")
    temp_path = Path(temp_dir.name) / f"page-{page_number + 1}.pdf"

    command = [
        gs,
        "-q",
        "-o",
        str(temp_path),
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.7",
        "-dPDFSETTINGS=/prepress",
        "-dFIXEDMEDIA",
        f"-dDEVICEWIDTHPOINTS={width}",
        f"-dDEVICEHEIGHTPOINTS={height}",
        "-dPDFFitPage",
        "-dAutoRotatePages=/None",
        f"-dFirstPage={page_number + 1}",
        f"-dLastPage={page_number + 1}",
        str(src_path),
    ]

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        temp_dir.cleanup()
        message = completed.stderr.strip() or completed.stdout.strip() or "unknown Ghostscript error"
        raise RuntimeError(f"Ghostscript failed for page {page_number + 1}: {message}")

    return temp_dir, temp_path


def convert_pdf(src_path: Path) -> Path | None:
    """
    Convert all A3 pages in *src_path* to A4 using a print-style fit-to-page pass.
    Returns the output Path on success, or None if no A3 pages were found.
    """
    doc = fitz.open(str(src_path))

    a3_pages = [i for i in range(len(doc)) if is_a3(doc[i])]
    if not a3_pages:
        doc.close()
        return None

    out_doc = fitz.open()  # blank output document
    temp_dirs = []

    for page_index in range(len(doc)):
        src_page = doc[page_index]

        if page_index in a3_pages:
            eff_w, eff_h = src_page.rect.width, src_page.rect.height
            temp_dir, converted_path = _convert_page_with_ghostscript(src_path, page_index, eff_w >= eff_h)
            temp_dirs.append(temp_dir)

            converted_doc = fitz.open(str(converted_path))
            out_doc.insert_pdf(converted_doc, from_page=0, to_page=0)
            converted_doc.close()
        else:
            # Non-A3 pages are copied as-is
            out_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

    # Force generated files to always use lowercase .pdf extension.
    dst_path = src_path.with_name(f"{src_path.stem}_A4.pdf")
    out_doc.save(str(dst_path), garbage=4, deflate=True)
    out_doc.close()
    doc.close()

    for temp_dir in temp_dirs:
        temp_dir.cleanup()

    return dst_path


def main() -> None:
    data_dir = Path(__file__).parent / "data"
    if not data_dir.is_dir():
        print(f"Data folder not found: {data_dir}")
        sys.exit(1)

    pdf_files = sorted(
        path for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )
    if not pdf_files:
        print("No PDF files found in data/")
        return

    converted = 0
    skipped   = 0

    for pdf in pdf_files:
        if pdf.stem.lower().endswith("_a4"):
            continue

        print(f"Checking: {pdf.relative_to(data_dir.parent)}", end=" … ")
        result = convert_pdf(pdf)
        if result:
            print(f"converted → {result.name}")
            converted += 1
        else:
            print("not A3, skipped")
            skipped += 1

    print(f"\nDone. {converted} file(s) converted, {skipped} skipped.")


if __name__ == "__main__":
    main()
