"""Checker: every GGU theorem has a falsifier+parent+assumption triple row.

Reads FALSIFIABILITY_REGISTRY_V1.md (sibling) and asserts:
1. every *THEOREM_V1.md in this dir is named in the registry;
2. every registry row has all three columns non-trivially filled;
3. every backticked witness .py filename cited in the registry exists
   somewhere in research/ (checked relative to the repo research root).
CPython 3.8 safe. No network, no sampling.
"""

from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "FALSIFIABILITY_REGISTRY_V1.md"


def registry_text():
    try:
        text = REGISTRY.read_text()
    except OSError:
        raise ValueError("registry file missing: FALSIFIABILITY_REGISTRY_V1.md")
    if len(text) < 2000:
        raise ValueError("registry file implausibly short")
    return text


def theorem_files():
    files = sorted(p.name for p in HERE.glob("*THEOREM_V1.md"))
    if not files:
        raise ValueError("no theorem files found")
    return files


def check_coverage(text, theorems):
    missing = [t for t in theorems
               if t not in text and t[:-3] not in text]  # stem or full name
    if missing:
        raise ValueError("theorems without a registry row: " + ", ".join(missing))
    return len(theorems)


def check_triples(text):
    rows = [line for line in text.splitlines()
            if line.startswith("|") and "principle" not in line
            and "file | shorthand" not in line and "---" not in line]
    if len(rows) < 50:
        raise ValueError("too few registry rows: %d" % len(rows))
    thin = []
    for row in rows:
        cols = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cols) not in (4, 5):
            thin.append(row[:60])
            continue
        content = cols[-3:]  # assumption, parent, falsifier in both layouts
        if len(content[0]) < 20 or len(content[1]) < 8 or len(content[2]) < 20:
            thin.append(row[:60])
    if thin:
        raise ValueError("rows with thin columns: " + "; ".join(thin))
    return len(rows)


def check_witnesses(text):
    cited = sorted(set(re.findall(r"`([A-Za-z0-9_]+\.py)`", text)))
    if not cited:
        raise ValueError("no witness files cited")
    research_root = HERE.parent
    missing = [c for c in cited
               if not list(research_root.rglob(c))]
    if missing:
        raise ValueError("cited witness files not found: " + ", ".join(missing))
    return cited


def run():
    text = registry_text()
    theorems = theorem_files()
    n_theorems = check_coverage(text, theorems)
    n_rows = check_triples(text)
    cited = check_witnesses(text)
    return {"theorems_covered": n_theorems, "registry_rows": n_rows,
            "witness_files_cited": len(cited), "status": "PASS"}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
