#!/usr/bin/env python3
"""
Compress PDF files using Ghostscript.

This script can compress one PDF file or scan a directory recursively.
It is designed for large drawing/document repositories and provides
configurable compression presets and image downsampling parameters.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PDF_PRESETS = {
	"screen": "Lowest quality, smallest files (72 dpi)",
	"ebook": "Good balance for on-screen reading (150 dpi)",
	"printer": "High quality for desktop printing (300 dpi)",
	"prepress": "High quality, print production oriented",
	"default": "Ghostscript default profile",
}


@dataclass(frozen=True)
class CompressionResult:
	source: Path
	output: Path
	source_bytes: int
	output_bytes: int

	@property
	def saved_bytes(self) -> int:
		return self.source_bytes - self.output_bytes

	@property
	def saved_percent(self) -> float:
		if self.source_bytes == 0:
			return 0.0
		return (self.saved_bytes / self.source_bytes) * 100.0


def _find_ghostscript() -> str:
	gs = shutil.which("gs") or shutil.which("ghostscript")
	if not gs:
		print("Ghostscript is required. Install it and ensure 'gs' is on PATH.")
		sys.exit(1)
	return gs


def _positive_int(value: str) -> int:
	try:
		parsed = int(value)
	except ValueError as exc:
		raise argparse.ArgumentTypeError(f"invalid integer value: {value}") from exc
	if parsed <= 0:
		raise argparse.ArgumentTypeError("value must be > 0")
	return parsed


def _non_negative_float(value: str) -> float:
	try:
		parsed = float(value)
	except ValueError as exc:
		raise argparse.ArgumentTypeError(f"invalid float value: {value}") from exc
	if parsed < 0:
		raise argparse.ArgumentTypeError("value must be >= 0")
	return parsed


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Compress PDF files with Ghostscript.",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	)

	parser.add_argument(
		"input_path",
		type=Path,
		help="Input PDF file or directory containing PDFs.",
	)
	parser.add_argument(
		"-o",
		"--output-dir",
		type=Path,
		default=None,
		help="Output directory. If omitted, outputs are written next to source files.",
	)
	parser.add_argument(
		"--suffix",
		default="_compressed",
		help="Suffix added before .pdf for generated files.",
	)
	parser.add_argument(
		"--preset",
		choices=sorted(PDF_PRESETS.keys()),
		default="ebook",
		help="Ghostscript /PDFSETTINGS preset.",
	)
	parser.add_argument(
		"--compatibility",
		default="1.4",
		help="Output PDF compatibility level passed to Ghostscript.",
	)
	parser.add_argument(
		"--dpi",
		type=_positive_int,
		default=None,
		help="Override all image DPI settings (color/gray/mono).",
	)
	parser.add_argument(
		"--color-dpi",
		type=_positive_int,
		default=None,
		help="Override color image DPI.",
	)
	parser.add_argument(
		"--gray-dpi",
		type=_positive_int,
		default=None,
		help="Override grayscale image DPI.",
	)
	parser.add_argument(
		"--mono-dpi",
		type=_positive_int,
		default=None,
		help="Override monochrome image DPI.",
	)
	parser.add_argument(
		"--min-size-mb",
		type=_non_negative_float,
		default=5.0,
		help="Only process source PDFs with size >= this threshold in MB.",
	)
	parser.add_argument(
		"--recursive",
		action="store_true",
		help="If input is a directory, scan recursively.",
	)
	parser.add_argument(
		"--overwrite",
		action="store_true",
		help="Overwrite output file if it already exists.",
	)
	parser.add_argument(
		"--skip-if-larger",
		action="store_true",
		help="Delete output when compressed file is larger than input.",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Show what would be compressed without running Ghostscript.",
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help="Print full Ghostscript command per file.",
	)

	return parser.parse_args()


def gather_pdf_files(input_path: Path, recursive: bool) -> list[Path]:
	if input_path.is_file():
		return [input_path] if input_path.suffix.lower() == ".pdf" else []

	if not input_path.is_dir():
		return []

	pattern = "**/*.pdf" if recursive else "*.pdf"
	return sorted(path for path in input_path.glob(pattern) if path.is_file())


def build_output_path(
	source_pdf: Path,
	input_root: Path,
	output_dir: Path | None,
	suffix: str,
) -> Path:
	out_name = f"{source_pdf.stem}{suffix}.pdf"
	if output_dir is None:
		return source_pdf.with_name(out_name)

	if input_root.is_file():
		return output_dir / out_name

	relative_parent = source_pdf.parent.relative_to(input_root)
	return output_dir / relative_parent / out_name


def build_command(
	gs_exec: str,
	source_pdf: Path,
	output_pdf: Path,
	compatibility: str,
	preset: str,
	dpi: int | None,
	color_dpi: int | None,
	gray_dpi: int | None,
	mono_dpi: int | None,
) -> list[str]:
	command = [
		gs_exec,
		"-sDEVICE=pdfwrite",
		f"-dCompatibilityLevel={compatibility}",
		f"-dPDFSETTINGS=/{preset}",
		"-dNOPAUSE",
		"-dQUIET",
		"-dBATCH",
		"-dDetectDuplicateImages=true",
		"-dCompressFonts=true",
		"-dSubsetFonts=true",
	]

	effective_color_dpi = color_dpi if color_dpi is not None else dpi
	effective_gray_dpi = gray_dpi if gray_dpi is not None else dpi
	effective_mono_dpi = mono_dpi if mono_dpi is not None else dpi

	if effective_color_dpi is not None:
		command.extend(
			[
				"-dDownsampleColorImages=true",
				"-dColorImageDownsampleType=/Bicubic",
				f"-dColorImageResolution={effective_color_dpi}",
			]
		)
	if effective_gray_dpi is not None:
		command.extend(
			[
				"-dDownsampleGrayImages=true",
				"-dGrayImageDownsampleType=/Bicubic",
				f"-dGrayImageResolution={effective_gray_dpi}",
			]
		)
	if effective_mono_dpi is not None:
		command.extend(
			[
				"-dDownsampleMonoImages=true",
				"-dMonoImageDownsampleType=/Subsample",
				f"-dMonoImageResolution={effective_mono_dpi}",
			]
		)

	command.extend([f"-sOutputFile={output_pdf}", str(source_pdf)])
	return command


def compress_pdf(
	gs_exec: str,
	source_pdf: Path,
	output_pdf: Path,
	compatibility: str,
	preset: str,
	dpi: int | None,
	color_dpi: int | None,
	gray_dpi: int | None,
	mono_dpi: int | None,
	verbose: bool,
) -> CompressionResult:
	output_pdf.parent.mkdir(parents=True, exist_ok=True)

	command = build_command(
		gs_exec=gs_exec,
		source_pdf=source_pdf,
		output_pdf=output_pdf,
		compatibility=compatibility,
		preset=preset,
		dpi=dpi,
		color_dpi=color_dpi,
		gray_dpi=gray_dpi,
		mono_dpi=mono_dpi,
	)

	if verbose:
		print("[cmd] " + " ".join(command))

	completed = subprocess.run(command, capture_output=True, text=True)
	if completed.returncode != 0:
		message = completed.stderr.strip() or completed.stdout.strip() or "unknown Ghostscript error"
		raise RuntimeError(f"Ghostscript failed for {source_pdf}: {message}")

	source_bytes = source_pdf.stat().st_size
	output_bytes = output_pdf.stat().st_size
	return CompressionResult(
		source=source_pdf,
		output=output_pdf,
		source_bytes=source_bytes,
		output_bytes=output_bytes,
	)


def format_mb(num_bytes: int) -> str:
	return f"{num_bytes / (1024 * 1024):.2f} MB"


def main() -> None:
	args = parse_args()

	input_path = args.input_path.expanduser().resolve()
	output_dir = args.output_dir.expanduser().resolve() if args.output_dir else None

	if args.input_path and not input_path.exists():
		print(f"Input path does not exist: {input_path}")
		sys.exit(1)

	if output_dir:
		output_dir.mkdir(parents=True, exist_ok=True)

	pdf_files = gather_pdf_files(input_path, args.recursive)
	if not pdf_files:
		print("No PDF files found to process.")
		return

	gs_exec = _find_ghostscript()

	min_size_bytes = int(args.min_size_mb * 1024 * 1024)
	processed = 0
	skipped = 0
	failed = 0
	total_saved = 0

	for source_pdf in pdf_files:
		source_size = source_pdf.stat().st_size
		if source_size < min_size_bytes:
			skipped += 1
			print(f"SKIP {source_pdf} (below min size: {format_mb(source_size)})")
			continue

		output_pdf = build_output_path(
			source_pdf=source_pdf,
			input_root=input_path,
			output_dir=output_dir,
			suffix=args.suffix,
		)

		if output_pdf.exists() and not args.overwrite:
			skipped += 1
			print(f"SKIP {source_pdf} (output exists: {output_pdf})")
			continue

		if args.dry_run:
			processed += 1
			print(f"DRY-RUN {source_pdf} -> {output_pdf}")
			continue

		try:
			result = compress_pdf(
				gs_exec=gs_exec,
				source_pdf=source_pdf,
				output_pdf=output_pdf,
				compatibility=args.compatibility,
				preset=args.preset,
				dpi=args.dpi,
				color_dpi=args.color_dpi,
				gray_dpi=args.gray_dpi,
				mono_dpi=args.mono_dpi,
				verbose=args.verbose,
			)
		except Exception as exc:  # noqa: BLE001 - show and continue with other files
			failed += 1
			print(f"FAIL {source_pdf}: {exc}")
			continue

		if args.skip_if_larger and result.output_bytes >= result.source_bytes:
			result.output.unlink(missing_ok=True)
			skipped += 1
			print(
				f"SKIP {source_pdf} (compressed file not smaller: "
				f"{format_mb(result.source_bytes)} -> {format_mb(result.output_bytes)})"
			)
			continue

		processed += 1
		total_saved += max(result.saved_bytes, 0)
		print(
			f"OK   {source_pdf} -> {result.output} "
			f"[{format_mb(result.source_bytes)} -> {format_mb(result.output_bytes)}, "
			f"saved {result.saved_percent:.1f}%]"
		)

	print("\nSummary")
	print(f"Processed: {processed}")
	print(f"Skipped:   {skipped}")
	print(f"Failed:    {failed}")
	print(f"Saved:     {format_mb(total_saved)}")

	if failed > 0:
		sys.exit(2)


if __name__ == "__main__":
	main()
