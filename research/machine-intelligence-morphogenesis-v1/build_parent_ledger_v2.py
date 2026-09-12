#!/usr/bin/env python3
"""Build PARENT_LEDGER_V2.json from PARENT_LEDGER_V1.json (Codex) + per-family primary-source
ledgers produced by the GMI-D0 reconstruction workers (families P9A_P0, P9B_P3P4, P7P8P6P5).

Usage: python3 build_parent_ledger_v2.py <family_json_dir>
Writes PARENT_LEDGER_V2.json and LEDGER_MERGE_REPORT_V2.md next to this script.

Merge rules (frozen):
  * V1 records are preserved verbatim under `v1_records`.
  * Every family entry becomes a V2 record with the #377 §4 exit fields; verification_status is
    carried per source; nothing is upgraded to FULL_TEXT_READ by merging.
  * `corrections_to_prior_ledger` from each family are listed, never silently applied to V1 text.
  * Coverage terminal is computed, not asserted: SATURATED only if every #377 §4 family P0..P8 has
    at least one FULL_TEXT_READ load-bearing entry AND no family reports missing parents; otherwise
    PARENT_COVERAGE_PARTIAL__<what is missing>.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
FAMILY_MAP = {  # #377 §4 family -> prefixes of parent_ids that serve it
    "P0": ["P0.", "P9A.INVARIANCE", "P9A.LEVIN", "P9A.BLUM"],
    "P1": ["P1."],
    "P2": ["P2."],
    "P3": ["P3."],
    "P4": ["P4."],
    "P5": ["P5."],
    "P6": ["P6."],
    "P7": ["P7."],
    "P8": ["P8."],
    "P9A": ["P9A."],
    "P9B": ["P9B."],
}
REQUIRED = ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]


def main(dirpath):
    v1 = json.load(open(os.path.join(HERE, "PARENT_LEDGER_V1.json")))
    fams = []
    for f in sorted(glob.glob(os.path.join(dirpath, "*.json"))):
        if os.path.basename(f) == "BRIEF.json":
            continue
        try:
            d = json.load(open(f))
        except Exception as e:  # noqa: BLE001
            print("skip", f, e, file=sys.stderr)
            continue
        if "entries" in d and "family_id" in d:
            fams.append(d)
    records, corrections, missing, hooks = [], [], [], defaultdict(list)
    depth = Counter()
    for fam in fams:
        for e in fam["entries"]:
            statuses = [s.get("verification_status", "FROM_MEMORY_UNVERIFIED") for s in e.get("primary_sources", [])]
            best = "NOT_ACCESSIBLE"
            for cand in ["FULL_TEXT_READ", "PARTIAL_TEXT_READ", "ABSTRACT_ONLY", "NOT_ACCESSIBLE", "FROM_MEMORY_UNVERIFIED"]:
                if cand in statuses:
                    best = cand
                    break
            depth[best] += 1
            rec = dict(e)
            rec["family_id"] = fam["family_id"]
            rec["best_verification_status"] = best
            records.append(rec)
        syn = fam.get("family_level_synthesis", {})
        corrections += [dict(c, family_id=fam["family_id"]) for c in syn.get("corrections_to_prior_ledger", []) or []]
        missing += [dict(m, family_id=fam["family_id"]) if isinstance(m, dict) else {"parent": m, "family_id": fam["family_id"]} for m in syn.get("missing_parents_you_noticed", []) or []]
        for k, v in (syn.get("suggested_theorem_hooks", {}) or {}).items():
            hooks[k].append({"family_id": fam["family_id"], "constraint": v})
    # coverage computation
    fam_full = {}
    for req in REQUIRED:
        prefixes = FAMILY_MAP[req]
        recs = [r for r in records if any(r["parent_id"].startswith(p) for p in prefixes)]
        v1_hits = [r for r in v1["records"] if req in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8") and r.get("family")]
        fam_full[req] = {"entries": len(recs), "full_text": sum(1 for r in recs if r["best_verification_status"] == "FULL_TEXT_READ")}
    unsat = [k for k, v in fam_full.items() if v["full_text"] == 0]
    if not unsat and not missing:
        terminal = "PARENT_COVERAGE_SATURATED_AT_GMI_V1_SCOPE"
    else:
        terminal = "PARENT_COVERAGE_PARTIAL__NO_FULL_TEXT_FOR_" + "_".join(unsat) if unsat else "PARENT_COVERAGE_PARTIAL__MISSING_PARENTS_REPORTED"
    out = {
        "schema": "ParentLedgerV2",
        "issue": 377,
        "status": terminal,
        "rule": v1.get("rule"),
        "merge_rules": "see build_parent_ledger_v2.py docstring",
        "families_merged": [f["family_id"] for f in fams],
        "verification_depth_histogram": dict(depth),
        "coverage_by_377_family": fam_full,
        "records": records,
        "corrections_to_v1": corrections,
        "missing_parents_reported": missing,
        "theorem_hooks": dict(hooks),
        "v1_records": v1["records"],
        "v1_status_preserved": v1.get("status"),
    }
    json.dump(out, open(os.path.join(HERE, "PARENT_LEDGER_V2.json"), "w"), indent=1, sort_keys=True)
    with open(os.path.join(HERE, "LEDGER_MERGE_REPORT_V2.md"), "w") as f:
        f.write("# Parent ledger V2 merge report\n\n")
        f.write(f"Terminal: `{terminal}`\n\nFamilies merged: {', '.join(out['families_merged'])}\n\n")
        f.write("Verification depth: " + json.dumps(dict(depth)) + "\n\n")
        f.write("| #377 family | entries | full-text |\n|---|---|---|\n")
        for k, v in fam_full.items():
            f.write(f"| {k} | {v['entries']} | {v['full_text']} |\n")
        f.write(f"\nCorrections to V1: {len(corrections)}\n\nMissing parents reported: {len(missing)}\n")
    print(terminal, dict(depth), fam_full)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user/24f4e1e0-e36e-5fcd-96f6-b0bb4c061628/scratchpad/parents")
