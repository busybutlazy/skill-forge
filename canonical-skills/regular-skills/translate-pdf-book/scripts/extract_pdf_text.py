#!/usr/bin/env python3
"""Extract text from a PDF file.

Tries pdftotext first (poppler-utils), then pdfminer.six.
Install one of:
  brew install poppler        # provides pdftotext
  pip install pdfminer.six
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _try_pdftotext(pdf: Path, out: Path) -> bool:
    try:
        r = subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(out)],
            capture_output=True,
        )
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _try_pdfminer(pdf: Path, out: Path) -> bool:
    try:
        from pdfminer.high_level import extract_text  # type: ignore

        text = extract_text(str(pdf))
        out.write_text(text, encoding="utf-8")
        return True
    except ImportError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from a PDF file.")
    parser.add_argument("pdf", help="Path to the source PDF")
    parser.add_argument("output", help="Destination text file")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    out = Path(args.output)

    if not pdf.exists():
        print(f"error: {pdf} not found", file=sys.stderr)
        sys.exit(1)

    out.parent.mkdir(parents=True, exist_ok=True)

    if _try_pdftotext(pdf, out):
        print(f"extracted with pdftotext -> {out}")
        return

    if _try_pdfminer(pdf, out):
        print(f"extracted with pdfminer -> {out}")
        return

    print(
        "error: neither pdftotext nor pdfminer.six is available.\n"
        "  install poppler:    brew install poppler\n"
        "  or pdfminer.six:    pip install pdfminer.six",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
