#!/usr/bin/env python3
"""Route B - independent oracle for AA19, AA31 and AA37.

Imports nothing from `fallacy_detectors_v1.py`, and for AA31 it does not
execute the parent at all: it re-derives the divergence from the parent's
COMMITTED RECEIPT (`gmi-833-g0-grammar-bias-v1/RESULT_V1.json`), a materially
different source from route A's live instrumentation. AA19 and AA37 are
re-implemented without regular expressions.

stdlib only; exact Fraction arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CENSUS = ROOT / "research" / "gmi-833-corpus-census-v1"
GRAMMAR_RECEIPT = (ROOT / "research" / "gmi-833-g0-grammar-bias-v1"
                   / "RESULT_V1.json")


class OracleError(RuntimeError):
    pass


def rows_from_freeze() -> Dict[str, str]:
    text = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
    block = text.split("Verbatim from comment 5684607872 under the anchor above:", 1)[1]
    block = block.split("**No neighboring row is earned here.**", 1)[0]
    rows = [l.strip() for l in block.split("\n") if l.strip().startswith("- [ ]")]
    if len(rows) != 3:
        raise OracleError("freeze does not quote exactly three AA rows: %d" % len(rows))
    out = {}
    for row in rows:
        low = row.lower()
        if "reachability" in low:
            out["AA19"] = row
        elif "grammar" in low:
            out["AA31"] = row
        else:
            out["AA37"] = row
    if len(out) != 3:
        raise OracleError("could not key the three rows")
    return out


# --------------------------------------------------------------------------
# AA19 - independent recount over the object corpus.
# --------------------------------------------------------------------------
def aa19() -> Dict[str, object]:
    with (CENSUS / "CORPUS_INDEX_V1.json").open("r", encoding="utf-8") as fh:
        objects = json.load(fh)["scientific_objects"]
    queued_ids = set()
    records = 0
    files = set()
    clean = 0
    alarms = 0
    overlap = 0
    for obj in objects:
        quant = obj["quantifier_class"]
        mode = obj["proof_evidence_mode"]
        experimental = mode in ("EMPIRICAL_EXPERIMENT", "STATISTICAL_EXPERIMENT")
        finite_cert = mode in ("COMPUTER_ASSISTED_EXHAUSTIVE",
                               "FINITE_EXECUTABLE_CERTIFICATE")
        if quant == "UNIVERSAL" and experimental:
            records += 1
            queued_ids.add(obj["object_id"])
            files.add(obj["source_path"])
            if finite_cert:
                overlap += 1
            continue
        clean += 1
        if quant == "UNIVERSAL" and experimental:
            alarms += 1
    # AA21's population, recomputed here so the disjointness claim is checked
    # rather than asserted.
    fin2univ = set(o["object_id"] for o in objects
                   if o["quantifier_class"] == "UNIVERSAL"
                   and o["proof_evidence_mode"] in ("COMPUTER_ASSISTED_EXHAUSTIVE",
                                                    "FINITE_EXECUTABLE_CERTIFICATE"))
    return {
        "objects_scanned": len(objects),
        "queued_records": records,
        "queued_distinct_object_ids": len(queued_ids),
        "queued_distinct_source_files": len(files),
        "queued_object_ids": sorted(queued_ids),
        "real_clean_total": clean,
        "real_alarms_total": alarms,
        "overlap_with_aa21_fin2univ": len(queued_ids & fin2univ),
    }


# --------------------------------------------------------------------------
# AA31 - divergence from the parent's COMMITTED RECEIPT, not from execution.
# --------------------------------------------------------------------------
def _exact(cell):
    if isinstance(cell, dict):
        return dict((k, _exact(v)) for k, v in sorted(cell.items()))
    if isinstance(cell, str) and "/" in cell:
        return Fraction(cell)
    if isinstance(cell, float):
        raise OracleError("float in a committed bias row")
    return cell


def aa31() -> Dict[str, object]:
    with GRAMMAR_RECEIPT.open("r", encoding="utf-8") as fh:
        receipt = json.load(fh)
    hostile = receipt["nonisometric_same_semantics_hostile"]
    ga = hostile["GA_bias"]
    gb = hostile["GB_bias"]
    cells = []
    for cls in sorted(set(ga) | set(gb)):
        a = ga.get(cls)
        b = gb.get(cls)
        if a is None or b is None:
            cells.append((cls, "(class absent)"))
            continue
        for field in sorted(set(a) | set(b)):
            if _exact(a.get(field)) != _exact(b.get(field)):
                cells.append((cls, field))
    cert = receipt["isometric_remint_certificate"]
    return {
        "source": "the parent's committed RESULT_V1.json, not a live run",
        "semantic_classes": sorted(set(ga) | set(gb)),
        "divergent_cells": len(cells),
        "divergent_cells_detail": [list(c) for c in cells],
        "divergent_semantic_classes": sorted({c[0] for c in cells}),
        "parent_certified_permutations": int(cert["permutations"]),
        "parent_invariant_failures": int(cert["invariant_failures"]),
        "nonisometric_pair_queued": bool(cells),
    }


# --------------------------------------------------------------------------
# AA37 - independent markdown scan, no regex, no ledger-gate import.
# --------------------------------------------------------------------------
NEW_FORM = ("novel implementation", "novel architecture",
            "novel algorithmic mechanism", "novel model class",
            "novel computational paradigm", "novel capability profile",
            "unseen form", "novel intelligence", "novel mechanism",
            "new computational class", "predicted morphology",
            "held-out architecture", "new-form")
PARENT_LABELS = ("strongest parents", "strongest parent", "parents", "parent")


def _norm(text: str) -> str:
    out = []
    for ch in text.lower():
        out.append(" " if ch in "-\t\n\r" else ch)
    return " ".join("".join(out).split())


def _tracked_md() -> List[str]:
    import subprocess
    proc = subprocess.run(["git", "ls-files"], cwd=str(ROOT),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise OracleError("git ls-files failed")
    return sorted(r for r in proc.stdout.decode("utf-8").split("\n")
                  if r.startswith("research/") and r.endswith(".md"))


def _leading_bold(line: str) -> Optional[str]:
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


def _has_identifier(title: str) -> bool:
    """Route A uses a regex; this is the same rule by index scan."""
    def upper_alnum(token):
        return token.isalnum() and not any(c.islower() for c in token)

    words = title.replace("(", " ").replace(")", " ").split()
    for w in words:
        core = w.strip(".,;:`*")
        while "-" in core:
            left, _, right = core.partition("-")
            tail = right.split("-", 1)[0]
            if (1 <= len(left) <= 8 and left[:1].isalpha() and left[:1].isupper()
                    and upper_alnum(left)
                    and 1 <= len(tail) <= 5 and upper_alnum(tail)):
                return True
            core = right
    head = title.strip().lower()
    if head[:1].isdigit():
        head = head.split(".", 1)[-1].strip()
    for word in ("theorem", "lemma", "proposition", "corollary"):
        if head.startswith(word):
            return True
    return False


def aa37() -> Dict[str, object]:
    total = 0
    tier1 = 0
    tier1_identified = 0
    cleared = 0
    queued = []
    for rel in _tracked_md():
        name = rel.rsplit("/", 1)[-1].upper()
        if "THEOREM" not in name:
            continue
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        title = None
        body = []  # type: List[str]
        fenced = False
        spans = []  # type: List[Tuple[str, List[str]]]
        for raw in text.split("\n"):
            if raw[:3] == "```":
                fenced = not fenced
                continue
            if fenced:
                continue
            if raw[:3] == "## " and raw[:4] != "### ":
                if title is not None:
                    spans.append((title, body))
                title = raw[3:].strip()
                body = []
                continue
            if title is not None:
                body.append(raw)
        if title is not None:
            spans.append((title, body))
        for head, lines in spans:
            low = head.strip().lower()
            if low.startswith("definition"):
                continue
            total += 1
            blob = _norm(head + " " + " ".join(lines))
            if not any(_norm(t) in blob for t in NEW_FORM):
                continue
            tier1 += 1
            if not _has_identifier(head):
                continue
            tier1_identified += 1
            labels = set()
            for line in lines:
                lab = _leading_bold(line)
                if lab:
                    labels.add(lab)
            if any(a in labels for a in PARENT_LABELS):
                cleared += 1
            else:
                queued.append({"path": rel, "result": head})
    return {
        "named_results_scanned": total,
        "tier1_triggered": tier1,
        "tier1_identified": tier1_identified,
        "tier1_cleared_by_a_parent_ledger": cleared,
        "tier1_queued": len(queued),
        "queue": queued,
    }


def derive() -> Dict[str, object]:
    return {
        "schema": "GMI_833_AA_FALLACY_DETECTORS_ORACLE_V1",
        "route": "B",
        "rows_recovered_from_freeze": sorted(rows_from_freeze()),
        "AA19": aa19(),
        "AA31": aa31(),
        "AA37": aa37(),
    }


if __name__ == "__main__":
    out = derive()
    out["AA19"] = {k: v for k, v in out["AA19"].items() if k != "queued_object_ids"}
    print(json.dumps(out, indent=2, sort_keys=True))
