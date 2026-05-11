# PDF to A4 Conversion

This repository contains a single script, `convert-to-a4.py`, that scans the `data/` folder recursively and creates A4 copies of PDF drawings that are A3-sized.

The script uses a print-style conversion path: each A3 page is rendered through Ghostscript onto an A4 page sized to match the page's effective orientation. The converted files are saved next to the originals with an `_A4` suffix.

## Requirements

- Python 3.10+
- PyMuPDF (`pymupdf`)
- Ghostscript (`gs` or `ghostscript`) on your `PATH`

If you are using the provided virtual environment, install the Python dependency with:

```bash
pip install pymupdf
```

## Local Usage

Run the script from the repository root:

```bash
python3 convert-to-a4.py
```

The script will:

1. Search `data/` recursively for PDF files.
2. Skip files that already end in `_A4.pdf`.
3. Detect A3 pages using their displayed page size.
4. Create a new PDF next to the original with `_A4` appended to the filename.

Example input and output paths:

```bash
data/<project>/<drawing-set>/<drawing-name>.pdf
data/<project>/<drawing-set>/<drawing-name>_A4.pdf
```

## Docker Usage

The repository includes a `Dockerfile` so you can run the conversion without installing Python packages or Ghostscript on the host.

### Build the image

From the repository root, build the image with:

```bash
docker build -t pdf-to-a4 .
```

### Run the container

Mount the folder that contains the A3 PDFs as `/app/data` inside the container. The script scans `/app/data` recursively, so you can mount either the repository `data/` folder or any other folder that contains PDFs.

Repository folder example:

```bash
docker run --rm \
	-v "$PWD/data:/app/data" \
	pdf-to-a4
```

External folder example:

```bash
docker run --rm \
	-v "/path/to/your/pdf-folder:/app/data" \
	pdf-to-a4
```

If you want the output files to be written back to the host, make sure the mounted folder is writable.

## Notes

- Existing `_A4.pdf` files are ignored when scanning the `data/` tree.
- The output preserves the source page orientation as it would appear in a print dialog.
- Non-A3 PDFs are left unchanged.
