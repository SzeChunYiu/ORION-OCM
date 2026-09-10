#!/usr/bin/env python3
"""Receipt field-family coverage: DERIVED, never hand-copied (D28 F6, RH-01/RH-06).

EXPERIMENT_REGISTRY_V1.json freezes 13 receipt field families. The frozen
receipts implement a subset; before this checker the absent families were
SILENTLY absent -- a reader could not tell "emitted and zero" from "never
emitted". This tool derives the true per-file coverage from the receipts
themselves and compares it to the committed RECEIPT_COVERAGE_V1.json.

Fail-closed with distinct exit codes:

  0  PASS        committed coverage table reproduces exactly from the receipts
  20 COVERAGE_DRIFT  committed table disagrees with the derived one
  21 FAMILY_LIST_DRIFT  the 13-family source list in EXPERIMENT_REGISTRY_V1
                        changed; update FAMILIES to match (both together)
  13 SCHEMA_SHAPE receipts unreadable / registry missing / table malformed

Emit mode (`--emit`) writes the derived table; commit it together with any
receipt change, and append an amendment to FREEZE_EVIDENCE_BINDING_V1.json
naming RECEIPT_COVERAGE_V1.json (the freeze binds its hash).

Scope (justified, per absence-claim discipline): exact/receipts/*.jsonl --
the per-study machine receipts. Host receipts (D23_HOST_RECEIPT_*.json,
D23_CROSS_HOST_V1.json) and results files are different artifact classes
(host provenance / aggregate results) and are out of scope here; D23 results
carry B_exec at the results layer and are noted in findings, not counted.
"""
import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
RECEIPTS = BASE / "exact" / "receipts"
COVERAGE = BASE / "RECEIPT_COVERAGE_V1.json"
REGISTRY = BASE / "EXPERIMENT_REGISTRY_V1.json"

# The 13 frozen families, keyed by their verbatim registry names. Patterns are
# matched against receipt-row keys, lowercased, with an explicit mode sigil so
# a pattern cannot fire inside an unrelated word (defects caught while
# validating this checker: bare "io_" matched ratio_abstraction_over_direct;
# bare "verdict" matched the boolean verdicts_match agreement flag):
#   =name  exact key            ~name  key endswith
#   >name  key startswith       name   substring (only where unambiguous)
FAMILIES = {
    "raw terminal": ["=verdict", "=terminal", "~_verdict"],
    "B_exec vector": ["=b_exec", ">b_exec"],
    "obligation nodes/hyperedges/derivations/SCCs": [">obligation", ">hyperedge", ">derivation", ">scc"],
    "ambiguity size/entropy": [">ambiguity"],
    "protected round-trip errors": ["round_trip"],
    "counterexample + version-space shrinkage": ["counterexample"],
    "abstraction/refinement count": ["refinement"],
    "provenance supports/alternatives": [">provenance", ">alt_support"],
    "reduction/proof/rewrite path": [">rewrite", ">reduction"],
    "operator/library reuse identities": [">reuse", ">library", ">operator"],
    "active k / total N": ["=k", "=n"],
    "wall/CPU/GPU/IO/storage": [">wall", ">cpu", ">gpu", ">io", ">storage"],
    "negative/CANNOT_CHECK status": ["cannot_check", ">negative_or_cannot"],
}


def fail(code, msg):
    print(f"RECEIPT_COVERAGE FAIL({code}): {msg}")
    sys.exit(code)


def family_list_from_registry():
    try:
        reg = json.loads(REGISTRY.read_text())
        fields = reg["hpc_factory"]["receipt_fields"]
    except Exception as e:
        fail(13, f"EXPERIMENT_REGISTRY_V1 unreadable: {e}")
    if list(fields) != list(FAMILIES):
        fail(21, f"registry receipt_fields changed: {list(fields)} != FAMILIES {list(FAMILIES)}")
    return fields


def key_union(path):
    keys = set()
    n = 0
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            row = json.loads(line)
        except ValueError:
            fail(13, f"{path.name} row {n} unparseable")
        if isinstance(row, dict):
            keys.update(row.keys())
    return keys, n


def derive():
    files = sorted(RECEIPTS.glob("*.jsonl"))
    if not files:
        fail(13, "no *.jsonl receipts found in exact/receipts/")
    def match(pat, key):
        kl = key.lower()
        if pat.startswith("="):
            return kl == pat[1:]
        if pat.startswith("~"):
            return kl.endswith(pat[1:])
        if pat.startswith(">"):
            return kl.startswith(pat[1:])
        return pat in kl

    table, summary = {}, {}
    for f in files:
        keys, n = key_union(f)
        emitted = set()
        for fam, pats in FAMILIES.items():
            if fam == "active k / total N":
                # family name is the PAIR: active k AND total N
                if "k" in {k.lower() for k in keys} and "n" in {k.lower() for k in keys}:
                    emitted.add(fam)
                continue
            if any(match(p, k) for p in pats for k in keys):
                emitted.add(fam)
        table[f.name] = {fam: ("EMITTED" if fam in emitted else "ABSENT")
                         for fam in FAMILIES}
        summary[f.name] = {"rows": n, "families_emitted": len(emitted)}
    return table, summary


def main():
    emit = "--emit" in sys.argv[1:]
    family_list_from_registry()
    table, summary = derive()

    findings = []
    for fam in FAMILIES:
        n_emit = sum(1 for t in table.values() if t[fam] == "EMITTED")
        if n_emit == 0:
            findings.append(f"ABSENT_EVERYWHERE: '{fam}' is emitted by NO committed receipt file")
    # F6 follow-up (DEV-CAL-1/D30 propagation): a receipt file emitting ZERO of the
    # 13 families was invisible before this rule -- its rows are readable but no
    # frozen family key appears at receipt top level. The table rows already show
    # ABSENT x13; this finding names the file so a zero-family receipt is DECLARED,
    # not merely derivable (either no family applies -- recorded in that study's
    # protocol -- or the receipt violates rule_for_new_studies below).
    for fname, s in sorted(summary.items()):
        if s["families_emitted"] == 0:
            findings.append(f"ZERO_FAMILY_RECEIPT: '{fname}' ({s['rows']} rows) emits none of "
                            f"the 13 frozen field families; applicable-but-unmeasured families "
                            f"require explicit cannot_check markers under rule_for_new_studies")
    b_exec = [f for f, t in table.items() if t["B_exec vector"] == "EMITTED"]
    if b_exec:
        findings.append(f"B_exec vector emitted only by {b_exec} (D28 F6 measured it absent "
                        f"from every pre-D23 receipt; D23 results also carry it at the results layer)")

    derived = {
        "schema": "HSG_RECEIPT_COVERAGE",
        "version": "V1",
        "cause": "D28 hostile review F6 (LOW): receipts implemented 7 of 13 frozen field families "
                 "and the absent families were silently absent. This table is DERIVED from the "
                 "receipts by derive_receipt_coverage.py (never hand-copied) so absence is "
                 "declared, not silent. Retro-filling frozen receipts is forbidden (they are "
                 "evidence); the rule below applies to FUTURE studies only.",
        "source_field_list": "EXPERIMENT_REGISTRY_V1.json receipt_fields (frozen, 13 families)",
        "scope": "exact/receipts/*.jsonl (per-study machine receipts). Host receipts and results "
                 "files are different artifact classes, out of scope, see module docstring.",
        "coverage": table,
        "summary": summary,
        "findings": findings,
        "rule_for_new_studies": "Any NEW study receipt must emit every family applicable to its "
                                "machinery, and carry an explicit cannot_check marker for each "
                                "applicable-but-unmeasured family; inapplicable families are "
                                "omitted from that study's receipt schema by design (recorded in "
                                "its protocol). Receipts that silently skip an applicable family "
                                "fail their study's checker.",
    }

    if emit:
        COVERAGE.write_text(json.dumps(derived, indent=1, sort_keys=True) + "\n")
        print(f"RECEIPT_COVERAGE EMITTED: {len(table)} files x {len(FAMILIES)} families; "
              f"{len(findings)} findings")
        return 0

    try:
        committed = json.loads(COVERAGE.read_text())
    except Exception as e:
        fail(13, f"committed RECEIPT_COVERAGE_V1.json unreadable: {e}")
    if committed != derived:
        for k in set(committed) | set(derived):
            if committed.get(k) != derived.get(k):
                print(f"  field {k}: committed != derived")
                print(f"    committed: {json.dumps(committed.get(k))[:300]}")
                print(f"    derived:   {json.dumps(derived.get(k))[:300]}")
        fail(20, "committed coverage table drifted from the receipts; re-run with --emit and "
                 "commit the result with a freeze amendment")
    n_emit_total = sum(s["families_emitted"] for s in summary.values())
    print(f"RECEIPT_COVERAGE PASS: {len(table)} receipt files, {len(FAMILIES)} families, "
          f"{n_emit_total} file-family emissions, {len(findings)} declared findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
