#!/usr/bin/env python3
"""P1-E3 taxonomy-disjointness hostile (H-P1E3-1) + controls (H-P1E3-4/5).

Builds the frozen mechanism-taxonomy token list and scans every byte of the
authored artifacts for overlaps. Any overlap alarms and (per
P1E3_AUTHORSHIP_FREEZE_V1.json) voids the family set for P1-E3 purposes:
it would mean the author unit wrote inside the mechanism's vocabulary.

Token list tiers (frozen):

  T1  ATOM_REGISTRY_V1.json atom ids (e.g. ATOM-HST-01) — distinctive.
  T2  mechanism abbreviation tokens: OCM IDENT PROV DEP TRANS EVAL ATLAS
      AUTH ME-X1 — case-sensitive whole words.
  T3  ME-X1 planter family names (X1-A_CLAIM_PROBLEM_IDENTITY ...).
  T4  ResidualKind enum names + Responsibility enum names (SCREAMING_CASE).
  T5  src/ocm module/package names (kso, selfmodel, epistemics, ...).

Calibration choice, stated: deliberately EXCLUDED are generic single English
words that also appear in the taxonomy prose (identity, support, transport,
authority, evaluator, ...). A generic word in an author's own narrative is
not taxonomy reuse; the hostile must be sensitive to mechanism-specific
tokens, not cry wolf. Sensitivity is proven by the tamper control
(H-P1E3-5): planting one T2/T3 token into a copy of a clean file MUST
alarm. The no-alarm control (H-P1E3-4) asserts zero alarms on pristine
files, and a must-match control pattern proves the scanner itself runs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

MECHANISM_ABBREVIATIONS = ["OCM", "IDENT", "PROV", "DEP", "TRANS", "EVAL", "ATLAS", "AUTH", "ME-X1"]

ME_X1_FAMILIES = [
    "X1-A_CLAIM_PROBLEM_IDENTITY",
    "X1-B_MEASUREMENT_CALIBRATION",
    "X1-C_HIDDEN_DEPENDENCE",
    "X1-D_INVALID_TRANSPORT",
    "X1-E_DEFEATED_PREREQUISITE",
    "X1-F_EVALUATOR_BLINDNESS",
    "X1-G_AUTHORITY_MISMATCH",
    "X1-H_PROOF_WRONG_SPECIFICATION",
    "X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION",
    "X1-J_FULLY_WARRANTED",
]

RESIDUAL_KINDS = [
    "MISSING_EVIDENCE", "CONTRADICTION", "CONTEXT_GAP", "REPRESENTATION_FAILURE",
    "SEARCH_COVERAGE_FAILURE", "DECOMPOSITION_FAILURE", "INTERFACE_FAILURE",
    "MEASUREMENT_FAILURE", "EVALUATOR_FAILURE", "METHOD_GAP", "UNCLASSIFIED",
]

RESPONSIBILITY_NAMES = ["QUESTION", "REPRESENTATION", "SEARCH", "ROUTING", "DECOMPOSITION", "INTERFACE", "MEASUREMENT", "EVALUATOR", "METHOD"]

OCM_MODULE_NAMES = [
    # Distinctive module/package identifiers only. Generic English words that
    # happen to be module names (work, store, chat, runtime, operators, ...)
    # are deliberately excluded: an author using ordinary English is not
    # taxonomy reuse, and a false alarm would wrongly void the family set.
    "kso", "selfmodel", "epistemics", "mex1", "dependency_audit",
    "comparators", "residuals",
]


def build_token_list() -> dict[str, list[str]]:
    tiers: dict[str, list[str]] = {
        "T1_atom_ids": [],
        "T2_abbreviations": MECHANISM_ABBREVIATIONS,
        "T3_mex1_families": ME_X1_FAMILIES,
        "T4_residual_kinds": RESIDUAL_KINDS + RESPONSIBILITY_NAMES,
        "T5_ocm_module_names": OCM_MODULE_NAMES,
    }
    reg = json.loads((ROOT / "research" / "top-tier-atomic-closure-v1" / "ATOM_REGISTRY_V1.json").read_text())
    tiers["T1_atom_ids"] = sorted({a["atom_id"] for a in reg["atoms"]})
    return tiers


def _patterns(tiers: dict[str, list[str]]) -> list[tuple[str, str, re.Pattern[str]]]:
    out = []
    for tier, tokens in tiers.items():
        for tok in tokens:
            # Word-boundary, case-sensitive match: an author writing "kso",
            # "IDENT" or an atom id exactly as the mechanism spells it is
            # precisely the leak this hostile exists to catch.
            out.append((tier, tok, re.compile(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])")))
    return out


def scan_text(text: str, patterns) -> list[dict]:
    hits = []
    for tier, tok, pat in patterns:
        m = pat.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            snippet = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            hits.append({"tier": tier, "token": tok, "line": line, "snippet": snippet})
    return hits


def scan_paths(paths: list[Path], tiers: dict[str, list[str]]) -> dict:
    patterns = _patterns(tiers)
    per_file = {}
    total = 0
    for p in paths:
        if not p.is_file():
            per_file[str(p)] = {"error": "missing"}
            total += 1
            continue
        text = p.read_text(errors="replace")
        hits = scan_text(text, patterns)
        per_file[str(p)] = {"hits": len(hits), "detail": hits[:20]}
        total += len(hits)
    return {"total_overlaps": total, "per_file": per_file}


def no_alarm_control(patterns) -> dict:
    """H-P1E3-4: pristine artifacts must produce ZERO alarms, and a must-match
    control pattern proves the scanner executes and can match at all."""
    pristine = HERE / "p1e3_author_spec.md"  # verified clean at freeze time
    text = pristine.read_text()
    hits = scan_text(text, patterns)
    # must-match control: the scanner MUST find a planted token in a modified copy
    tampered = text + "\nand a stray ATLAS token\n"
    tamper_hits = scan_text(tampered, patterns)
    scanner_alive = any(h["token"] == "ATLAS" for h in tamper_hits)
    return {
        "pristine_file": str(pristine),
        "pristine_hits": hits,
        "clean": len(hits) == 0,
        "scanner_must_match_control": scanner_alive,
        "control_passed": len(hits) == 0 and scanner_alive,
    }


def tamper_control(paths: list[Path], tiers: dict[str, list[str]]) -> dict:
    """H-P1E3-5: planting one taxonomy token into a COPY of a real authored
    artifact must alarm."""
    if not paths:
        return {"alarm": False, "error": "no artifacts to tamper"}
    target = paths[0]
    text = target.read_text(errors="replace")
    patterns = _patterns(tiers)
    tampered = text + "\n# stray note mentioning ATLAS\n"
    hits = scan_text(tampered, patterns)
    return {
        "tampered_copy_of": str(target),
        "planted_token": "ATLAS",
        "alarm": any(h["token"] == "ATLAS" for h in hits),
    }


def main() -> int:
    tiers = build_token_list()
    n_tokens = sum(len(v) for v in tiers.values())
    print(json.dumps({"tiers": {k: len(v) for k, v in tiers.items()}, "total_tokens": n_tokens}, indent=2))
    ctrl = no_alarm_control(_patterns(tiers))
    print(json.dumps(ctrl, indent=2))
    if not ctrl["control_passed"]:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
