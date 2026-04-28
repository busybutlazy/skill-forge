#!/usr/bin/env python3
"""Merge per-chapter Markdown files into one combined output.

Reads all *.zh-TW.md files from the translated/ directory in sorted order
and writes them into a single Markdown file.

Usage:
  python merge_markdown.py translated/ Book_Title_zh-TW_full.md
"""

import argparse
import sys
from pathlib import Path

_DEFAULT_SEPARATOR = "\n\n---\n\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge translated chapter files into one Markdown.")
    parser.add_argument("translated_dir", help="Directory containing *.zh-TW.md files")
    parser.add_argument("output", help="Output merged Markdown file path")
    parser.add_argument(
        "--separator",
        default=_DEFAULT_SEPARATOR,
        help="String inserted between chapters (default: horizontal rule)",
    )
    args = parser.parse_args()

    src_dir = Path(args.translated_dir)
    out_path = Path(args.output)

    if not src_dir.exists():
        print(f"error: {src_dir} not found", file=sys.stderr)
        sys.exit(1)

    files = sorted(src_dir.glob("*.zh-TW.md"))
    if not files:
        print(f"error: no *.zh-TW.md files in {src_dir}", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []
    for f in files:
        content = f.read_text(encoding="utf-8").strip()
        parts.append(content)
        print(f"  included: {f.name}  ({len(content.splitlines()):,} lines)")

    merged = args.separator.join(parts) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(merged, encoding="utf-8")

    total = len(merged.splitlines())
    print(f"\nmerged {len(parts)} chapters -> {out_path}  ({total:,} lines total)")


if __name__ == "__main__":
    main()
