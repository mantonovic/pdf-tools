# PDF Tools

This repository is a growing collection of PDF-focused scripts for technical drawings and document processing.

## Scripts

- [convert-to-a4.py](docs/convert-to-a4.md): convert A3 pages to A4 using a print-style fit-to-page Ghostscript workflow.
- [compress-pdf.py](docs/compress-pdf.md): compress large PDFs with configurable Ghostscript presets and image downsampling.

## Requirements

- Python 3.10+
- Ghostscript (`gs` or `ghostscript`) on your `PATH`
- PyMuPDF (`pymupdf`) for `convert-to-a4.py`

Install Python dependency:

```bash
pip install pymupdf
```

## Quick Start

```bash
# Convert A3 pages to A4
python3 convert-to-a4.py

# Compress PDFs in data/ recursively
python3 compress-pdf.py data --recursive --preset ebook --skip-if-larger
```

## Docker

```bash
docker build -t pdf-tools .
```

Run converter:

```bash
docker run --rm \
	-v "$PWD/data:/app/data" \
	pdf-tools
```

Run compressor:

```bash
docker run --rm \
	-v "$PWD:/app" \
	pdf-tools python3 compress-pdf.py data --recursive --preset ebook --skip-if-larger
```

For detailed options and examples, see the script docs in [docs/](docs).
