# PDF Tools

This repository is a growing collection of PDF-focused scripts for technical drawings and document processing.

## Scripts

- [convert-to-a4.py](docs/convert-to-a4.md): convert A3 pages to A4 using a print-style fit-to-page Ghostscript workflow.
- [compress-pdf.py](docs/compress-pdf.md): compress large PDFs with configurable Ghostscript presets and image downsampling.
- [clean-pdf.py](docs/clean-pdf.md): remove annotations and bookmarks (outline) from a PDF.

## ⚠️ Disclaimer

**Always backup your files and directories before running these scripts.**

These scripts modify PDF files in place or create new files in your working directories. While we strive to ensure reliability, there is a risk of:

- File corruption during processing
- Loss of data if operations fail midway
- Unintended modifications to the original PDFs
- Disk space issues when creating processed copies

**Best Practices:**

1. **Create a backup** of all files and folders before processing
2. **Test with a small sample** of files first
3. **Keep the original files** in a separate location
4. **Verify output files** before deleting originals
5. **Monitor disk space** to ensure sufficient storage for both original and processed files

The authors of these scripts are not responsible for any data loss, corruption, or other issues resulting from the use of these tools. Use at your own risk.

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

### Option 1: Pull Pre-built Image

Pull the pre-built image from GitHub Container Registry (no build required):

```bash
docker pull ghcr.io/mantonovic/pdf-tools/pdf-tools:latest
docker tag ghcr.io/mantonovic/pdf-tools/pdf-tools:latest pdf-tools
```

### Option 2: Build Locally

Build the image yourself:

```bash
docker build -t pdf-tools .
```

Run the interactive menu:

```bash
docker run --rm -it \
	-v "$PWD/data:/app/data" \
	pdf-tools
```

The default container command scans `/app/data` recursively, ignores generated files ending in `_clean.pdf`, `_compressed.pdf`, or `_A4.pdf`, and prompts you to run one of these actions across the discovered source PDFs:

- clean
- compress
- convert to A4
- all in sequence (`clean -> convert -> compress`)

Interactive selection requires `-it`. If you prefer a non-interactive run, pass an explicit command after the image name.

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

Convert all PDFs in a mounted directory recursively without the menu:

```bash
docker run --rm \
	-v "$PWD/data:/app/data" \
	pdf-tools python3 convert-to-a4.py /app/data --recursive
```

For detailed options and examples, see the script docs in [docs/](docs).
