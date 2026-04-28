#!/usr/bin/env python3
"""Split extracted PDF text into per-chapter source files.

Detects chapter boundaries by scanning for common heading patterns.
Writes one file per detected chapter under the given output directory.

Usage:
  python split_chapters.py book.raw.txt source_chapters/
"""

import argparse
import re
import sys
from pathlib import Path

_PATTERNS = [
    re.compile(r"^(Chapter\s+\d+[^:\n]*)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^(CHAPTER\s+\d+[^:\n]*)", re.MULTILINE),
    re.compile(r"^(\d+\.\s+[A-Z][^\n]{3,60})$", re.MULTILINE),
]


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:48] or "chapter"


def _detect_boundaries(text: str):
    best, best_n = None, 1
    for pat in _PATTERNS:
        hits = list(pat.finditer(text))
        if len(hits) > best_n:
            best_n, best = len(hits), pat
    return list(best.finditer(text)) if best else []


def main() -> None:
    parser = argparse.ArgumentParser(description="Split raw PDF text into chapter files.")
    parser.add_argument("source", help="Source text file from extract_pdf_text.py")
    parser.add_argument("output_dir", help="Output directory for chapter .en.txt files")
    args = parser.parse_args()

    src = Path(args.source)
    out_dir = Path(args.output_dir)

    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="utf-8")
    matches = _detect_boundaries(text)

    if not matches:
        print("warning: no chapter boundaries found — writing full text as single chapter")
        dest = out_dir / "01_full_text.en.txt"
        dest.write_text(text, encoding="utf-8")
        print(f"  wrote {dest}")
        return

    positions = [(m.start(), m.group(1).strip()) for m in matches]
    positions.append((len(text), None))

    written = 0
    for i, (start, heading) in enumerate(positions[:-1]):
        end = positions[i + 1][0]
        chunk = text[start:end].strip()
        slug = _slugify(heading)
        dest = out_dir / f"{i + 1:02d}_{slug}.en.txt"
        dest.write_text(chunk, encoding="utf-8")
        print(f"  [{i + 1:02d}] {dest.name}  ({len(chunk):,} chars)")
        written += 1

    print(f"\nsplit into {written} chapters -> {out_dir}/")


if __name__ == "__main__":
    main()
