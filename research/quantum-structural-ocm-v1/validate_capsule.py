"""Structural validation for the quantum-structural-ocm-v1 capsule.

Exit codes (distinct, never conflated):
  0 = all checks passed
  3 = JSON parse failure or duplicate top-level keys (FQ-6 weld class)
  4 = manifest coverage failure (file present but absent from REPO_STATE.json)
  5 = internal inconsistency (required keys / binding invariants)

The duplicate-key rejection is the FQ-6 donor lesson operationalized: the ORION
QG-34 weld showed that json.loads silently picks one authority state when an
authority-bearing file carries duplicate keys. No authority-bearing capsule
file may ever parse permissively.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_FILES = [
    "REPO_STATE.json",
    "ORION_QUANTUM_SOURCE_LEDGER.json",
    "QUANTUM_STRUCTURAL_DONOR_ATLAS_V1.json",
    "QUANTUM_TO_OCM_CONTRACT_MAP_V1.json",
    "STRONGEST_CLASSICAL_PARENT_MAP.json",
]

FORBIDDEN_TERMINALS = [
    "QUANTUM_OCM",
    "QUANTUM_COGNITION",
    "QUANTUM_ADVANTAGE",
    "TRANSFORMER_REPLACED",
    "LLM_EQUIVALENT",
    "AGI",
    "GENERAL_SUPERIORITY",
]


class DuplicateKeyError(ValueError):
    pass


def no_duplicate_keys(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise DuplicateKeyError("duplicate top-level key: %s" % key)
        seen.add(key)
    return dict(pairs)


def load_strict(path: Path):
    text = path.read_text(encoding="utf-8")
    return json.loads(text, object_pairs_hook=no_duplicate_keys)


def main() -> int:
    root = Path(__file__).resolve().parent
    failures = []

    # 1. every JSON in the capsule tree (root + subdirs, e.g. msc/) parses,
    #    strictly (duplicate-key rejection). Keyed by path relative to the
    #    capsule root so subdirectory files cannot collide by basename.
    json_files = sorted(
        p for p in root.rglob("*.json")
        if "__pycache__" not in p.parts)
    parsed = {}
    for path in json_files:
        rel = path.relative_to(root).as_posix()
        try:
            parsed[rel] = load_strict(path)
        except (ValueError, DuplicateKeyError) as exc:
            failures.append("parse/duplicate-key: %s: %s" % (rel, exc))
    if failures:
        for line in failures:
            print("FAIL", line)
        return 3

    # 2. required first-deliverable files exist.
    for name in REQUIRED_FILES:
        if name not in parsed:
            failures.append("missing required file: %s" % name)

    # 3. manifest coverage: every file in the capsule dir is declared.
    def collect_filenames(node):
        """Recursively collect leaf strings that look like file names
        (contain a dot, no whitespace) — robust to manifest reshaping;
        prose notes contain spaces and are skipped."""
        found = set()
        if isinstance(node, str):
            if "." in node and not any(ch.isspace() for ch in node):
                found.add(Path(node).name)
        elif isinstance(node, dict):
            for value in node.values():
                found |= collect_filenames(value)
        elif isinstance(node, list):
            for value in node:
                found |= collect_filenames(value)
        return found

    repo_state = parsed.get("REPO_STATE.json")
    manifest_files = collect_filenames(
        repo_state.get("capsule_file_manifest")
        if isinstance(repo_state, dict) else None)
    undeclared = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        if rel == "REPO_STATE.json" or p.suffix not in {".json", ".md", ".py"}:
            continue
        if rel not in manifest_files and p.name not in manifest_files:
            undeclared.append(rel)
    if undeclared:
        failures.append(
            "manifest coverage: files present but not in REPO_STATE.json "
            "capsule_file_manifest: %s" % ", ".join(undeclared))

    # 4. forbidden terminals never appear as emitted terminals in result JSONs.
    for name, doc in parsed.items():
        if not isinstance(doc, dict):
            continue
        emitted = doc.get("terminal") or doc.get("terminals") or []
        if isinstance(emitted, str):
            emitted = [emitted]
        for term in emitted:
            if isinstance(term, str) and term in FORBIDDEN_TERMINALS:
                failures.append(
                    "forbidden terminal %s in %s" % (term, name))

    if failures:
        for line in failures:
            print("FAIL", line)
        if any(f.startswith("manifest coverage:") for f in failures):
            return 4
        return 5

    total_files = sum(
        1 for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts)
    print(
        "PASS: %d JSON files strict-parsed, manifest covers all %d capsule "
        "files, no forbidden terminals" % (len(json_files), total_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
