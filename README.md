# PDF Tools

This repository is a growing collection of PDF-focused scripts for technical drawings and document processing.

## Scripts

- [convert-to-a4.py](docs/convert-to-a4.md): convert A3 pages to A4 using a print-style fit-to-page Ghostscript workflow.
- [compress-pdf.py](docs/compress-pdf.md): compress large PDFs with configurable Ghostscript presets and image downsampling.
- [clean-pdf.py](docs/clean-pdf.md): remove annotations and bookmarks (outline) from a PDF.

## Requirements

- Python 3.10+
- Ghostscript (`gs` or `ghostscript`) on your `PATH`
- PyMuPDF (`pymupdf`) for `convert-to-a4.py`
- pikepdf (`pikepdf`) for `clean-pdf.py`

Install Python dependencies:

```bash
pip install pymupdf pikepdf
```

## Quick Start

```bash
# Convert A3 pages to A4
python3 convert-to-a4.py

# Compress PDFs in data/ recursively
python3 compress-pdf.py data --recursive --preset ebook --skip-if-larger

# Clean a single PDF (remove annotations and bookmarks)
python3 clean-pdf.py input.pdf output.pdf

# Clean all PDFs in a directory (outputs named <file>_clean.pdf)
python3 clean-pdf.py /path/to/directory/
```

## Docker

All scripts are available inside the Docker image — no local Python or Ghostscript installation needed.

Build once:

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

Clean a single PDF:

```bash
docker run --rm \
	-v "/path/to/dir:/data" \
	pdf-tools python3 clean-pdf.py /data/input.pdf /data/output_TDMSA.pdf
```

Clean all PDFs in a directory:

```bash
docker run --rm \
	-v "/path/to/dir:/data" \
	pdf-tools python3 clean-pdf.py /data
```

For detailed options and examples, see the script docs in [docs/](docs).
