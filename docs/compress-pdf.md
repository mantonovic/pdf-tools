# compress-pdf.py

Compresses one PDF or all PDFs in a directory with Ghostscript.

The script is aimed at large drawing/document repositories and provides configurable quality presets and image downsampling controls.

## Requirements

- Python 3.10+
- Ghostscript (`gs` or `ghostscript`) on your `PATH`

## Basic Usage

Single file:

```bash
python3 compress-pdf.py path/to/document.pdf
```

Directory scan:

```bash
python3 compress-pdf.py data --recursive
```

Default output naming:

```bash
<name>.pdf -> <name>_compressed.pdf
```

## Key Options

- `--preset screen|ebook|printer|prepress|default` (default: `ebook`)
- `--compatibility 1.4` to control output PDF compatibility level
- `--min-size-mb 5` to process only larger files
- `--dpi` for all images, or specific `--color-dpi`, `--gray-dpi`, `--mono-dpi`
- `--output-dir <dir>` to write outputs to a separate mirrored tree
- `--overwrite` to replace existing outputs
- `--skip-if-larger` to delete outputs that are not smaller than source
- `--dry-run` to preview actions without writing files
- `--verbose` to print full Ghostscript command lines

## Examples

Balanced compression for one big file:

```bash
python3 compress-pdf.py drawing.pdf --preset ebook --min-size-mb 10
```

Batch compression with stronger downsampling:

```bash
python3 compress-pdf.py data --recursive --preset ebook --dpi 120 --skip-if-larger
```

Keep outputs in a separate folder:

```bash
python3 compress-pdf.py data --recursive --output-dir out/compressed
```

## Docker

Build image:

```bash
docker build -t pdf-tools .
```

Run compressor:

```bash
docker run --rm \
	-v "$PWD:/app" \
	pdf-tools python3 compress-pdf.py data --recursive --preset ebook --skip-if-larger
```

If you want output files written back to the host, ensure mounted folders are writable.