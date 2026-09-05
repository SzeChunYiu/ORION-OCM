#!/usr/bin/env python3
"""Word counts for docs/paper/manuscript/main.md under the paper plan's accounting.

Stdlib only. Prints four counts:

    body prose        words outside tables, headings, table captions, the header note and the reference list
    prose+headings    body prose plus headings, table captions and the header note
    excluding refs    everything before the reference list, tables included
    total             the whole file

The paper plan's 6,000-9,000 bound is applied to "body prose". Table lines start with "|",
headings with "#", captions with "**Table", and the header note is the first non-title paragraph.

Usage: python tools/paper/prose_wordcount.py [path/to/main.md]
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "..", "docs/paper/manuscript/main.md")
    text = open(path, encoding="utf-8").read()
    before_refs = text.split("\n## References")[0]
    lines = before_refs.splitlines()
    header_note = next((l for l in lines[1:] if l.strip() and not l.startswith("#")), "")
    prose_lines = [l for l in lines if not l.strip().startswith("|")]
    body_lines = [l for l in prose_lines if not l.startswith("#") and not l.startswith("**Table") and l != header_note]
    counts = {
        "body prose": len(" ".join(body_lines).split()),
        "prose+headings": len(" ".join(prose_lines).split()),
        "excluding refs": len(before_refs.split()),
        "total": len(text.split()),
    }
    for k, v in counts.items():
        print(f"{k:<16} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
