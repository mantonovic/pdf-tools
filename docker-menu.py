#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


DATA_DIR = Path(os.environ.get("TOOL_PDF_DATA_DIR", "/app/data"))
GENERATED_SUFFIX_RE = re.compile(r"_(?:a4|clean|compressed)(?:_\d+)?$", re.IGNORECASE)
MENU_OPTIONS = {
    "1": "clean",
    "2": "compress",
    "3": "convert",
    "4": "all",
    "5": "quit",
}


def discover_source_pdfs(data_dir: Path) -> list[Path]:
    return sorted(
        path for path in data_dir.rglob("*.pdf")
        if path.is_file() and not GENERATED_SUFFIX_RE.search(path.stem)
    )


def print_pdf_summary(files: list[Path], data_dir: Path) -> None:
    print(f"Found {len(files)} PDF file(s) under {data_dir}:")
    preview = files[:10]
    for path in preview:
        print(f"  - {path.relative_to(data_dir)}")
    if len(files) > len(preview):
        print(f"  ... and {len(files) - len(preview)} more")


def prompt_choice() -> str:
    print("\nSelect an action:")
    print("  1. Clean PDFs")
    print("  2. Compress PDFs")
    print("  3. Convert A3 pages to A4")
    print("  4. Run all in sequence (clean -> convert -> compress)")
    print("  5. Quit")

    while True:
        try:
            choice = input("Enter choice [1-5]: ").strip()
        except EOFError:
            print("Interactive input is required. Re-run Docker with -it to use the menu.")
            sys.exit(1)

        if choice in MENU_OPTIONS:
            return MENU_OPTIONS[choice]

        print("Invalid choice. Enter a number from 1 to 5.")


def run_command(command: list[str]) -> int:
    completed = subprocess.run(command)
    return completed.returncode


def clean_file(source_pdf: Path) -> int:
    output_pdf = source_pdf.with_name(f"{source_pdf.stem}_clean.pdf")
    return run_command(["python3", "clean-pdf.py", str(source_pdf), str(output_pdf)])


def compress_file(source_pdf: Path) -> int:
    return run_command(
        [
            "python3",
            "compress-pdf.py",
            str(source_pdf),
            "--preset",
            "ebook",
            "--skip-if-larger",
            "--overwrite",
            "--min-size-mb",
            "0",
        ]
    )


def convert_file(source_pdf: Path) -> int:
    return run_command(["python3", "convert-to-a4.py", str(source_pdf)])


def process_single_action(action: str, files: list[Path], data_dir: Path) -> int:
    failures = 0

    for source_pdf in files:
        print(f"\n[{action}] {source_pdf.relative_to(data_dir)}")
        if action == "clean":
            exit_code = clean_file(source_pdf)
        elif action == "compress":
            exit_code = compress_file(source_pdf)
        else:
            exit_code = convert_file(source_pdf)

        if exit_code != 0:
            failures += 1

    return failures


def process_all(files: list[Path], data_dir: Path) -> int:
    failures = 0

    for source_pdf in files:
        print(f"\n[all] {source_pdf.relative_to(data_dir)}")

        if clean_file(source_pdf) != 0:
            failures += 1
            continue

        cleaned_pdf = source_pdf.with_name(f"{source_pdf.stem}_clean.pdf")

        if convert_file(cleaned_pdf) != 0:
            failures += 1
            continue

        converted_pdf = cleaned_pdf.with_name(f"{cleaned_pdf.stem}_A4.pdf")
        compression_source = converted_pdf if converted_pdf.exists() else cleaned_pdf

        if compress_file(compression_source) != 0:
            failures += 1

    return failures


def main() -> None:
    if len(sys.argv) > 1:
        raise SystemExit(run_command(sys.argv[1:]))

    if not DATA_DIR.is_dir():
        print(f"Data directory not found: {DATA_DIR}")
        print("Mount your PDF folder with: docker run --rm -it -v \"$PWD/data:/app/data\" pdf-tools")
        sys.exit(1)

    pdf_files = discover_source_pdfs(DATA_DIR)
    if not pdf_files:
        print(f"No source PDFs found under {DATA_DIR}.")
        print("Generated files ending in _clean.pdf, _compressed.pdf, or _A4.pdf are ignored.")
        return

    print_pdf_summary(pdf_files, DATA_DIR)
    action = prompt_choice()
    if action == "quit":
        print("No action selected.")
        return

    if action == "all":
        failures = process_all(pdf_files, DATA_DIR)
    else:
        failures = process_single_action(action, pdf_files, DATA_DIR)

    if failures:
        print(f"\nCompleted with {failures} failure(s).")
        sys.exit(1)

    print("\nCompleted successfully.")


if __name__ == "__main__":
    main()