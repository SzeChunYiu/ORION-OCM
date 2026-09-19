#!/usr/bin/env python3
"""Route B - independent ledger-emission oracle (issue #833, AA02-AA06).

Written from FREEZE_V1.md section 5 alone.  It imports nothing from
`ledger_gate_v1.py` and shares no parsing code with it: where route A cuts a
file into spans with a heading regex and then regex-matches block labels, route
B walks the file line by line through an explicit state machine and extracts
bold labels by scanning for asterisk delimiters by index, with no regular
expression anywhere in the parsing path.

The two routes are compared per (path, result title) by set equality in the
test module.

stdlib only; exact integer arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

ACCEPTED = {
    "assumptions": ("assumptions", "assumption"),
    "dependency": ("dependencies", "dependency", "depends on"),
    "falsifier": ("falsifiers", "falsifier", "counterexamples", "counterexample"),
    "strongest_parent": ("strongest parents", "strongest parent", "parents", "parent"),
}
EXPERIMENT_ACCEPTED = {
    "leakage": ("leakage",),
    "search_space": ("search space",),
    "cost_model": ("cost model",),
    "evaluation": ("evaluation",),
    "sampling_bias": ("sampling bias",),
}
EXPERIMENT_SCHEMA = "GMI_EXPERIMENT_LEDGER_V1"


class OracleError(RuntimeError):
    pass


def _listing(root: Optional[Path]) -> List[str]:
    if root is not None:
        return sorted(str(p.relative_to(root)) for p in root.rglob("*.md"))
    proc = subprocess.run(["git", "ls-files"], cwd=str(ROOT),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise OracleError("git ls-files failed")
    rows = proc.stdout.decode("utf-8").split("\n")
    return sorted(r for r in rows
                  if r.startswith("research/") and r.endswith(".md"))


def _basename_upper(path: str) -> str:
    return path.rsplit("/", 1)[-1].upper()


def _leading_bold(line: str) -> Optional[str]:
    """Return the label of a block-leading `**Label.**` run, else None.

    Index scan only - deliberately no regular expression, so a shared regex bug
    cannot make both routes agree.
    """
    if not line.startswith("**"):
        return None
    close = line.find("**", 2)
    if close <= 2:
        return None
    inner = line[2:close]
    if "*" in inner:
        return None
    label = inner.strip()
    while label and label[-1] in ".:":
        label = label[:-1]
    return label.strip().lower() or None


def _is_definition_heading(title: str) -> bool:
    head = title.strip().lower()
    return head.startswith("definition ") or head in ("definition", "definitions") \
        or head.startswith("definitions ")


def scan_theorem_file(text: str) -> List[Tuple[str, Dict[str, bool]]]:
    out = []  # type: List[Tuple[str, Dict[str, bool]]]
    title = None  # type: Optional[str]
    labels = set()
    fenced = False

    def flush():
        if title is None:
            return
        if _is_definition_heading(title):
            return
        emits = {}
        for key, accepted in ACCEPTED.items():
            emits[key] = any(a in labels for a in accepted)
        out.append((title, emits))

    for raw in text.split("\n"):
        if raw[:3] == "```":
            fenced = not fenced
            continue
        if fenced:
            continue
        if raw[:3] == "## " and raw[:4] != "### ":
            flush()
            title = raw[3:].strip()
            labels = set()
            continue
        if title is None:
            continue
        lab = _leading_bold(raw)
        if lab is not None:
            labels.add(lab)
    flush()
    return out


def scan_experiment_file(text: str) -> Dict[str, bool]:
    labels = set()
    fenced = False
    for raw in text.split("\n"):
        if raw[:3] == "```":
            fenced = not fenced
            continue
        if fenced:
            continue
        lab = _leading_bold(raw)
        if lab is not None:
            labels.add(lab)
    emits = {}
    for key, accepted in EXPERIMENT_ACCEPTED.items():
        emits[key] = any(a in labels for a in accepted)
    return emits


def derive(root: Optional[Path] = None) -> Dict[str, object]:
    base = root if root is not None else ROOT
    per_result = {}   # (path, title) -> complete
    totals = dict((k, 0) for k in ACCEPTED)
    files = 0
    results = 0
    complete = 0
    exp_files = 0
    exp_complete = 0
    exp_totals = dict((k, 0) for k in EXPERIMENT_ACCEPTED)
    empty_files = []

    for rel in _listing(root):
        path = base / rel
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        name = _basename_upper(rel)
        if "THEOREM" in name:
            files += 1
            scanned = scan_theorem_file(text)
            if not scanned:
                empty_files.append(rel)
            for title, emits in scanned:
                results += 1
                done = all(emits.values())
                complete += int(done)
                per_result[rel + "::" + title] = done
                for key in totals:
                    totals[key] += int(emits[key])
        elif "EXPERIMENT" in name and "LEDGER" in name and EXPERIMENT_SCHEMA in text:
            exp_files += 1
            emits = scan_experiment_file(text)
            exp_complete += int(all(emits.values()))
            for key in exp_totals:
                exp_totals[key] += int(emits[key])

    return {
        "schema": "GMI_833_LEDGER_ORACLE_V1",
        "route": "B",
        "theorem_files": files,
        "named_results": results,
        "complete_named_results": complete,
        "non_compliant_named_results": results - complete,
        "emission_by_ledger": totals,
        "unparsed_theorem_artifacts": len(empty_files),
        "experiment_files": exp_files,
        "experiment_complete": exp_complete,
        "experiment_emission_by_ledger": exp_totals,
        "per_result": per_result,
    }


if __name__ == "__main__":
    out = derive()
    print(json.dumps({k: v for k, v in out.items() if k != "per_result"},
                     indent=2, sort_keys=True))
