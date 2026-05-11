# convert-to-a4.py

Converts A3 pages inside PDFs to A4 while preserving the page orientation.

The script uses a print-style conversion path: each A3 page is rendered through Ghostscript onto an A4 page sized to match the page's effective orientation.

## Requirements

- Python 3.10+
- PyMuPDF (`pymupdf`)
- Ghostscript (`gs` or `ghostscript`) on your `PATH`

Install dependency:

```bash
pip install pymupdf
```

## Usage

Run from the repository root:

```bash
python3 convert-to-a4.py
```

Behavior:

1. Searches `data/` recursively for PDF files.
2. Skips files that already end in `_A4.pdf`.
3. Detects A3 pages from displayed page size.
4. Creates a new PDF next to the source with `_A4` appended.

Example input and output paths:

```bash
data/<project>/<drawing-set>/<drawing-name>.pdf
data/<project>/<drawing-set>/<drawing-name>_A4.pdf
```

## Docker

Build image:

```bash
docker build -t pdf-tools .
```

Run converter:

```bash
docker run --rm \
	-v "$PWD/data:/app/data" \
	pdf-tools
```

If you want output files written back to the host, ensure mounted folders are writable.