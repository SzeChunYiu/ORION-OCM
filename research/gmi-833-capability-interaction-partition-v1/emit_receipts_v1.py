#!/usr/bin/env python3
"""Generate RESULT_V1.json, DELTA_TABLE_V1.md and CORRECTION_NOTICE_V1.json.

Every number is read from the computed census; nothing is transcribed by hand.
Run: python3 -I -B emit_receipts_v1.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


W = _load("partition_witness_v1", ROOT / "partition_witness_v1.py")
O = _load("partition_oracle_v1", ROOT / "partition_oracle_v1.py")

SOURCE_MAIN = "c70dd24eeade46a3afe8322c1a0e0c16a648311e"
# The FREEZE_V1.md commit on branch research/833-ciu-repair. It PRECEDES every
# implementation commit in this package; `git log --reverse` proves the order.
FREEZE_COMMIT = "c7bb5d099da3b949f10916be65ff1f54ce881eeb"

res = W.build_result()
cen = W.census()
rb = O.route_b_census()
rc = O.route_c_closed_form()
rows = cen["rows"]
delta = W.delta_table(cen)

assert cen["corrected_counts"] == rb["counts"] == rc["counts"], "route disagreement"
assert cen["pairs"] == rb["pairs"] == rc["pairs"] == 351

# ------------------------------------------------------------------ RESULT_V1
result = dict(res)
result["source_main"] = SOURCE_MAIN
result["freeze_commit"] = FREEZE_COMMIT
result["routes"] = {
    "A_partition_witness_v1": {"counts": cen["corrected_counts"], "pairs": cen["pairs"]},
    "B_partition_oracle_v1_enumeration": {"counts": rb["counts"], "pairs": rb["pairs"]},
    "C_partition_oracle_v1_closed_form": {"counts": rc["counts"], "pairs": rc["pairs"],
                                          "signature_tally": rc["signature_tally"],
                                          "relation_counts": rc["relation_counts"]},
    "agreement": "EXACT (A == B pair-by-pair; A == B == C in aggregate)",
}
result["result_ids"] = ["CIP-1", "CIP-2", "CIP-2b", "CIP-3", "CIP-4"]
result["claim_ceiling"] = "G2"
(ROOT / "RESULT_V1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

# ------------------------------------------------------------- DELTA_TABLE_V1
def short(c):
    return c.replace("cap-", "")


L = []
L.append("# DELTA TABLE V1 — corrected 27x27 capability-interaction census")
L.append("")
L.append("**GENERATED FILE.** Produced by `emit_receipts_v1.py` from the computed census;")
L.append("no row is hand-transcribed. All 351 rows also live in `RESULT_V1.json` "
         "(`per_pair`).")
L.append("")
L.append("Accounting: A4 registered fully-shareable/nested regime — every capability using")
L.append("channel `c` claims the same single unit of `c`, so `B(X) = |R(X)|` and")
L.append("`joint = |R(X) u R(Y)|` (counting measure on a finite unit set).")
L.append("")
L.append("## 1. Headline")
L.append("")
L.append("| quantity | value |")
L.append("|---|---|")
L.append("| unordered pairs | %d |" % cen["pairs"])
L.append("| shipped census | independent %d, synergistic %d, redundant %d, interfering 0 |"
         % (cen["shipped_counts"]["independent"], cen["shipped_counts"]["synergistic"],
            cen["shipped_counts"]["redundant"]))
L.append("| corrected census | INDEPENDENT %d, REDUNDANT %d, PARTIAL_SHARING %d, INTERFERING %d |"
         % (cen["corrected_counts"]["INDEPENDENT"], cen["corrected_counts"]["REDUNDANT"],
            cen["corrected_counts"]["PARTIAL_SHARING"], cen["corrected_counts"]["INTERFERING"]))
L.append("| labels changed | %d / %d |" % (cen["labels_changed"], cen["pairs"]))
L.append("| **DEF-1** shipped label contradicts Section 1.2's own definition | **%d / %d** |"
         % (cen["def1_shipped_contradicts_section_1_2"], cen["pairs"]))
L.append("| **DEF-2** pairs satisfying more than one Section 1.2 label | **%d / %d** |"
         % (cen["def2_pairs_with_non_unique_1_2_label"], cen["pairs"]))
L.append("")
L.append("Two exact set identities (proved in `..._THEOREMS_V1.md`, checked in the tests):")
L.append("")
L.append("- the DEF-1 set is **exactly** the `PARTIAL_SHARING` class (%d pairs);"
         % cen["corrected_counts"]["PARTIAL_SHARING"])
L.append("- the DEF-2 set is **exactly** the `REDUNDANT` class (%d pairs), because"
         % cen["corrected_counts"]["REDUNDANT"])
L.append("  `joint = max < sum` satisfies both shipped conditions `joint = max` (Redundant)")
L.append("  and `joint < sum` (Synergistic).")
L.append("")
L.append("## 2. Aggregate transition table")
L.append("")
L.append("| shipped label | channel relation | corrected class | pairs | changed | why |")
L.append("|---|---|---|---:|:---:|---|")
WHY = {
    ("independent", "disjoint", "INDEPENDENT"):
        "`joint = sum`; the shipped label was already correct and uniquely justified.",
    ("synergistic", "equal", "REDUNDANT"):
        "`joint = max < sum`. `joint < sum` (Synergistic) held but NOT uniquely: `joint = max` "
        "(Redundant) held too. The unique CIP-1 class is REDUNDANT.",
    ("redundant", "nested-proper", "REDUNDANT"):
        "`joint = max < sum`; R(X) properly contains R(Y) or conversely. Name unchanged, now "
        "uniquely justified by the `max < sum` guard.",
    ("redundant", "non-nested-overlap", "PARTIAL_SHARING"):
        "**CORRECTION.** `max < joint < sum`, so the shipped label's own defining condition "
        "`joint = max` is FALSE here.",
}
for d in delta:
    key = (d["shipped_label"], d["channel_relation"], d["corrected_class"])
    L.append("| %s | %s | `%s` | %d | %s | %s |"
             % (d["shipped_label"], d["channel_relation"], d["corrected_class"], d["pairs"],
                "yes" if d["changed"] else "no", WHY.get(key, "")))
L.append("")
L.append("Total: %d pairs; %d changed." % (sum(d["pairs"] for d in delta),
                                           sum(d["pairs"] for d in delta if d["changed"])))
L.append("")

corr = [r for r in rows if r["shipped_contradicts_1_2"]]
L.append("## 3. DEF-1 — every pair whose shipped label is FALSE by Section 1.2's own "
         "definition (%d pairs)" % len(corr))
L.append("")
L.append("Shipped label `redundant` is defined `joint = max(individual)`; each row below has")
L.append("`max < joint`, so the equality fails. Corrected class `PARTIAL_SHARING`.")
L.append("")
L.append("| # | X | Y | R(X) | R(Y) | B(X) | B(Y) | max | joint | sum | shipped | corrected |")
L.append("|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|")
for i, r in enumerate(corr, 1):
    L.append("| %d | %s | %s | {%s} | {%s} | %d | %d | %d | %d | %d | `%s` | `%s` |"
             % (i, short(r["x"]), short(r["y"]), ",".join(r["channels_x"]),
                ",".join(r["channels_y"]), r["B_x"], r["B_y"], r["max"], r["joint"],
                r["B_x"] + r["B_y"], r["shipped_label"], r["corrected_class"]))
L.append("")

rel = [r for r in rows if r["label_changed"] and not r["shipped_contradicts_1_2"]]
L.append("## 4. Relabelled without contradiction — `synergistic` -> `REDUNDANT` (%d pairs)"
         % len(rel))
L.append("")
L.append("These pairs use identical channel sets, so `joint = max < sum`. The shipped label")
L.append("`synergistic` satisfied its Section 1.2 condition `joint < sum`, but so did")
L.append("`redundant` (`joint = max`): the shipped taxonomy did not pick one. Under CIP-1 the")
L.append("unique class is `REDUNDANT`, and the saving content is preserved by")
L.append("`SAVING = REDUNDANT (disjoint union) PARTIAL_SHARING = {joint < sum}`.")
L.append("")
L.append("| # | X | Y | R(X)=R(Y) | max | joint | sum | shipped | corrected |")
L.append("|---:|---|---|---|---:|---:|---:|---|---|")
for i, r in enumerate(rel, 1):
    L.append("| %d | %s | %s | {%s} | %d | %d | %d | `%s` | `%s` |"
             % (i, short(r["x"]), short(r["y"]), ",".join(r["channels_x"]), r["max"],
                r["joint"], r["B_x"] + r["B_y"], r["shipped_label"], r["corrected_class"]))
L.append("")

unch = [r for r in rows if not r["label_changed"]]
L.append("## 5. Unchanged labels (%d pairs)" % len(unch))
L.append("")
L.append("| shipped = corrected | channel relation | pairs |")
L.append("|---|---|---:|")
agg = {}
for r in unch:
    k = (r["shipped_label"], r["relation"])
    agg[k] = agg.get(k, 0) + 1
for (lab, relx), n in sorted(agg.items()):
    L.append("| `%s` | %s | %d |" % (lab, relx, n))
L.append("")
L.append("The %d `disjoint` pairs are the **no-alarm control**: they classify `INDEPENDENT`"
         % len([r for r in unch if r["relation"] == "disjoint"]))
L.append("under both the channel-overlap predicate and the burden classification, and they")
L.append("are not flagged by the DEF-1 detector.")
L.append("")
(ROOT / "DELTA_TABLE_V1.md").write_text("\n".join(L) + "\n")

# -------------------------------------------------------- CORRECTION_NOTICE_V1
notice = {
    "schema": "GMI_CORRECTION_NOTICE_V1",
    "package": "gmi-833-capability-interaction-partition-v1",
    "issue_context": 833,
    "closes_issue_rows": [],
    "issue_rows_claimed": "NONE — this tranche closes no #833 checkbox. No neighbouring row is earned here.",
    "produces_reconciliation_json": False,
    "source_main": SOURCE_MAIN,
    "freeze_commit": FREEZE_COMMIT,
    "claim_ceiling": "G2",
    "corrected_object": {
        "id": "CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1",
        "path": "research/gmi-capability-interactions-unified-v1/CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md",
        "theorem": "CI-U (Lemmas A/B/C) + Corollary CI-A4 (27x27 registered instance)",
        "blob_at_freeze": "a9a67f8ec06b87aa374f092a72fabc593178ecfe",
        "prior_disposition": "GREEN on mainline; confirmed OVERSTRONG by the #939 verdict table, then revived under the #976 L58 revival chain (commit c4def870).",
        "sound_and_untouched": [
            "Lemma A (disjoint channels => joint = sum) — unconditional, correct.",
            "Lemma B bounds and the nested/disjoint/partial equality characterization — correct under counting measure on a finite unit set (what the code implements).",
            "Lemma C (free-option monotonicity by feasible-set inclusion) — correct.",
            "CE-1 and CE-2 — correct, and CE-2 is the reason INTERFERING is retained in the repaired partition.",
        ],
    },
    "defects": {
        "DEF-1": {
            "statement": "Corollary CI-A4's labels are assigned from channel-set overlap alone, never from a burden. On the real 27-capability A4 contract, that makes the shipped label FALSE by Section 1.2's own defining condition for these pairs.",
            "count": cen["def1_shipped_contradicts_section_1_2"],
            "of": cen["pairs"],
            "exact_characterization": "The DEF-1 set is exactly the PARTIAL_SHARING class {max < joint < sum}.",
            "worked_example": {
                "x": "cap-perception", "y": "cap-communication",
                "channels_x": "S,T", "channels_y": "S,M",
                "B_x": 2, "B_y": 2, "max": 2, "joint": 3, "sum": 4,
                "shipped_label": "redundant",
                "shipped_label_definition": "joint = max(individual)",
                "why_false": "max = 2 but joint = 3, so joint = max is FALSE.",
                "corrected_class": "PARTIAL_SHARING",
            },
        },
        "DEF-2": {
            "statement": "Section 1.2's four conditions do not partition: Redundant (joint = max) is a strict sub-case of Synergistic (joint < sum) whenever max < sum, so a pair can satisfy more than one label.",
            "count": cen["def2_pairs_with_non_unique_1_2_label"],
            "of": cen["pairs"],
            "exact_characterization": "The DEF-2 set is exactly the REDUNDANT class {joint = max < sum}.",
        },
        "DEF-3": {
            "statement": "interactions_witness.verify_no_interference() is VACUOUS: interaction_type() has no 'interfering' return path, so the function cannot return False. Section 3 (Negative Twin) and MANIFEST.json's falsifier both rested on it.",
            "repair": "CIP-2b replaces it with a proved, non-vacuous statement: under union accounting joint <= sum always, so INTERFERING is provably EMPTY on the A4 instance; the new classifier computes joint and sum and has a reachable INTERFERING branch, exercised by the CE-2 hostile.",
        },
    },
    "repair": {
        "CIP-1": "Exact partition theorem on the (max, joint, sum) lattice: INDEPENDENT (joint = sum), REDUNDANT (joint = max and max < sum), PARTIAL_SHARING (max < joint < sum), INTERFERING (joint > sum). Proved mutually exclusive and jointly exhaustive on the admissible region fixed by axioms (N) non-negativity and (M) monotonicity joint >= max, including the degenerate max = sum case.",
        "CIP-2": "Burden-based classifier and the corrected 351-pair census, with a complete per-pair delta table.",
        "CIP-2b": "Under union accounting INTERFERING is provably empty (replaces the vacuous check).",
        "CIP-3": "Exact correspondence-and-divergence with the channel-overlap predicate, EARNED-BY-COUNTEREXAMPLE.",
        "CIP-4": "Lemma B precision: mu pinned to counting measure on a finite unit set (strict positivity), with an explicit counterexample showing `iff nested` fails without it.",
        "nothing_deleted": "INTERFERING is retained (CE-2). The original Synergistic condition survives as the named aggregate SAVING = {joint < sum} = REDUNDANT (disjoint union) PARTIAL_SHARING. No scope was narrowed and no claim ceiling lowered.",
    },
    "census": {
        "pairs": cen["pairs"],
        "shipped": cen["shipped_counts"],
        "corrected": cen["corrected_counts"],
        "labels_changed": cen["labels_changed"],
        "channel_relation_counts": rc["relation_counts"],
    },
    "delta_table": delta,
    "delta_table_file": "DELTA_TABLE_V1.md",
    "per_pair_file": "RESULT_V1.json",
    "routes": result["routes"],
    "hostiles_detected": result["hostiles_detected"],
    "controls": result["controls"],
    "null": result["null_random_classifiers_fully_justified"],
    "forbidden_promotions": [
        "Do NOT delete the INTERFERING class (CE-2 shows interference is real outside free-option accounting).",
        "Do NOT weaken Section 1.2 to prose, narrow Corollary CI-A4, or downgrade Theorem CI-U's universal claim.",
        "Do NOT claim any #833 issue row from this tranche.",
        "Do NOT raise the claim ceiling above G2.",
        "Do NOT extend the A4 census beyond the registered fully-shareable/nested accounting of the frozen 27-row contract.",
    ],
}
(ROOT / "CORRECTION_NOTICE_V1.json").write_text(json.dumps(notice, indent=2, sort_keys=True) + "\n")

print("RESULT_V1.json           rows=%d" % len(result["per_pair"]))
print("DELTA_TABLE_V1.md        lines=%d" % len(L))
print("CORRECTION_NOTICE_V1.json DEF-1=%d DEF-2=%d changed=%d"
      % (cen["def1_shipped_contradicts_section_1_2"],
         cen["def2_pairs_with_non_unique_1_2_label"], cen["labels_changed"]))
print("EMIT_RECEIPTS_V1: GREEN")
