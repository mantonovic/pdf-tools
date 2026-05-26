# clean-pdf.py

Removes annotations, bookmarks, and transparent backgrounds from PDF files.

The script is aimed at technical drawings exported from CAD tools, which often embed interactive annotations, outline trees, and transparent page backgrounds that cause issues when printing or archiving.

## Requirements

- Python 3.10+
- pikepdf (`pikepdf`)

Install dependency:

```bash
pip install pikepdf
```

## What it does

For every processed page the script:

1. **Removes annotations** — deletes all interactive elements stored in `/Annots` (comments, markups, hyperlinks, form fields, etc.).
2. **Adds a white background** — prepends a white filled rectangle covering the full `MediaBox` beneath the existing content, replacing any transparent or undefined background.
3. **Removes the outline** — deletes the document's bookmark tree (`/Outlines`) from the PDF catalog.

## Usage

Single file:

```bash
python3 clean-pdf.py input.pdf output.pdf
```

Directory (all PDFs in the folder):

```bash
python3 clean-pdf.py /path/to/directory/
```

Default output naming when processing a directory:

```
<name>.pdf → <name>_clean.pdf
```

Files already ending in `_clean.pdf` are skipped automatically to avoid re-processing outputs.

## Docker

Build image:

```bash
docker build -t pdf-tools .
```

Clean a single PDF:

```bash
docker run --rm \
	-v "/path/to/dir:/data" \
	pdf-tools python3 clean-pdf.py /data/input.pdf /data/output_clean.pdf
```

Clean all PDFs in a directory:

```bash
docker run --rm \
	-v "/path/to/dir:/data" \
	pdf-tools python3 clean-pdf.py /data
```

If you want output files written back to the host, ensure mounted folders are writable.
