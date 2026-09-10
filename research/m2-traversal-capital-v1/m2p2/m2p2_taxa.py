#!/usr/bin/env python3
"""M2-P2 taxonomy-disjointness hostile (extends the P1-E3 hostile with the M2-P1 lane
vocabulary), frozen by M2P2_FREEZE_V1.json BEFORE the author session runs.

Scans every authored artifact byte for frozen mechanism/lane taxonomy tokens. Any
overlap alarms and, per the freeze, voids the authored package (terminal
AUTHORSHIP_CONTAMINATED) — it would mean the author unit wrote inside our vocabulary
rather than their own.

Token tiers (frozen):

  T1..T5  the P1-E3 tiers, imported unmodified from
          research/independent-authorship-gate-v1/p1e3_taxa.py
          (atom ids; OCM/IDENT/PROV/DEP/TRANS/EVAL/ATLAS/AUTH/ME-X1; ME-X1 family
           names; ResidualKind + Responsibility names; distinctive module names)
  T6      M2-P1/M2-P2 lane vocabulary: registered-unit code symbols, arm names,
          terminal names, schema markers, record filenames.
  T7      distinctive phrases of the lane's prose (multi-word, hence distinctive),
          matched case-sensitively like every other tier.

Calibration choice, stated (same discipline as p1e3_taxa.py): deliberately EXCLUDED
are generic single English words that also appear in the lane's prose (motif, solve,
double, square, library, shuffle, history, admission, fragment). An author using
ordinary English is not taxonomy reuse; the hostile must be sensitive to
lane-specific tokens, not cry wolf. Sensitivity is proven by the tamper control:
planting one T6 token into a copy of a clean file MUST alarm. The no-alarm control
asserts zero alarms on the frozen author spec itself, and a must-match control
pattern proves the scanner runs.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # repo root
P1E3_DIR = ROOT / "research" / "independent-authorship-gate-v1"

sys.path.insert(0, str(P1E3_DIR))
import p1e3_taxa  # noqa: E402  (frozen tier builder T1..T5)

T6_LANE_IDENTIFIERS = [
    # registered-unit code symbols (the author must never name the machinery)
    "learn_generator", "validate_generator", "verify_solution", "admit_generator",
    "load_generator", "GeneratorMethod", "SearchBudget", "PolynomialTask",
    "normal_form", "PRIMITIVES", "checked_program", "admit_solution",
    # lane + package markers
    "M2P1", "m2p1", "M2-P1", "M2P2", "m2p2", "M2-P2",
    "LANE_M2_TRAVERSAL_CAPITAL_OPUS", "ORION-OCM", "ORION", "KSO", "LUNARC",
    "billy-old", "SzeChunYiu",
    # scored-arm names (SCREAMING compounds are lane-specific)
    "CONTINUED", "RESET", "SHUFFLED_HISTORY", "LIBRARY_ONLY", "ORACLE_FAMILY",
    "ORDINARY_ADAPTIVE_PARENT", "FAMILY_PRIOR_ORDER", "FAMILY_PRIOR_PRUNE",
    "FREE_FIT_ORDER", "SHUFFLED_HISTORY_HARDENED",
    # terminal names
    "HISTORY_INDUCED_SEARCH_PRIOR", "PARENT_SUFFICIENT", "NO_FAMILY_HEADROOM",
    "FAMILY_HEADROOM_OCM_MISSES", "NO_NATIVE_EFFECT",
    "FAMILY_PREDICTABLE_WITHOUT_HISTORY", "AUTHORSHIP_CONTAMINATED",
    "SURFACE_DERIVABLE", "ASSAY_DEFECT",
    # schema / record markers
    "OCM_M2P1", "OCM_M2P2", "M2P1_DEV_STATE", "M2P1_ARM_REPORT",
    "M2P1_ECOLOGY_HEADER", "M2P1_ECOLOGY", "OCM_M2_FEATURE_SUFFICIENCY",
    "M2P1_FREEZE", "M2P2_FREEZE",
    # emitters / design docs of this lane
    "m2p1_runner", "m2p1_ecology", "m2p1_gate", "m2p1_dose", "m2p1_amort",
    "m2p1_receipt", "m2p1_summarize", "m2p1_veto", "m2p1_ledger3",
    "m2p1_attrib", "HIDDEN_FAMILY_DESIGN", "AMORTISATION.md",
    "hidden_motifs", "dev_state.json", "checkpoint.json",
]

T7_LANE_PHRASES = [
    # multi-word phrases distinctive of this lane's usage (generic single words
    # are deliberately excluded; see the calibration note above)
    "hidden motif", "motif set", "motif decompos", "hidden family", "family prior",
    "normal form", "canonical program", "fragment library", "search prior",
    "traversal capital", "interleave toll", "admission law", "admission gate",
    "held-out", "developmental history", "developmental task", "dose-response",
    "ladder successes", "work reduction", "shuffle-equal-n", "amortisation",
    "ecology", "seed world", "fresh world", "surface ordering", "surface-derivable",
]


def build_token_list() -> dict[str, list[str]]:
    tiers = p1e3_taxa.build_token_list()          # T1..T5, frozen upstream
    tiers["T6_lane_identifiers"] = T6_LANE_IDENTIFIERS
    tiers["T7_lane_phrases"] = T7_LANE_PHRASES
    return tiers


def _patterns(tiers: dict[str, list[str]]):
    out = []
    for tier, tokens in tiers.items():
        for tok in tokens:
            out.append((tier, tok, re.compile(
                r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])")))
    return out


def scan_text(text: str, patterns):
    hits = []
    for tier, tok, pat in patterns:
        m = pat.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            snippet = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
            hits.append({"tier": tier, "token": tok, "line": line, "snippet": snippet})
    return hits


def scan_paths(paths, tiers: dict[str, list[str]]) -> dict:
    patterns = _patterns(tiers)
    per_file, total = {}, 0
    for p in paths:
        p = Path(p)
        if not p.is_file():
            per_file[str(p)] = {"error": "missing"}
            total += 1
            continue
        hits = scan_text(p.read_text(errors="replace"), patterns)
        per_file[str(p)] = {"hits": len(hits), "detail": hits[:20]}
        total += len(hits)
    return {"total_overlaps": total, "per_file": per_file}


def no_alarm_control(patterns) -> dict:
    """The frozen author spec must itself be clean (it is the author's ONLY input)."""
    pristine = HERE / "m2p2_author_spec.md"
    hits = scan_text(pristine.read_text(), patterns)
    tamper_hits = scan_text(pristine.read_text() + "\n# stray note about ORACLE_FAMILY\n",
                            patterns)
    return {
        "pristine_file": str(pristine),
        "pristine_hits": hits,
        "clean": len(hits) == 0,
        "scanner_must_match_control": any(h["token"] == "ORACLE_FAMILY" for h in tamper_hits),
        "control_passed": len(hits) == 0
        and any(h["token"] == "ORACLE_FAMILY" for h in tamper_hits),
    }


def tamper_control(paths, tiers) -> dict:
    if not paths:
        return {"alarm": False, "error": "no artifacts to tamper"}
    target = Path(paths[0])
    patterns = _patterns(tiers)
    hits = scan_text(target.read_text(errors="replace") + "\n# stray note about ORACLE_FAMILY\n",
                     patterns)
    return {"tampered_copy_of": str(target), "planted_token": "ORACLE_FAMILY",
            "alarm": any(h["token"] == "ORACLE_FAMILY" for h in hits)}


def main() -> int:
    tiers = build_token_list()
    print(json.dumps({"tiers": {k: len(v) for k, v in tiers.items()},
                      "total_tokens": sum(len(v) for v in tiers.values())}, indent=2))
    ctrl = no_alarm_control(_patterns(tiers))
    print(json.dumps(ctrl, indent=2))
    return 0 if ctrl["control_passed"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
