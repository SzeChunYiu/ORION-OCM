"""E9 appends: tranche-2 ledger revival record + v1 reconciliation e9_note.

Run from the repository root. Strictly additive: existing ledger keys,
entries and statuses are untouched (the record itself documents the
GAP-T2-2 closure); the reconciliation spec gains one additive field.
"""
import json

LEDGER = "research/gmi-833-g0-grammar-growth-v2/SCIENTIFIC_LEDGER_V2.json"
RECON = "research/gmi-833-g0-grammar-growth-v1/ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V1.json"

REVIVAL = {
    "id": "REV-E9-1",
    "package": "gmi-833-g0-exec-rank-revival-v1",
    "issue": 897,
    "parent_issue": 833,
    "lead": "GAP-E8-3 rank-fragility note: 19/200 exec-nulls beat the recursive library at rho=1 (v1ref), 0/200 under count",
    "rung": "3 (structural frontier) with rung 1 closed negative earned-by-counterexample and rung 2 closed negative earned-by-construction for the frozen five-charge class",
    "verdict": (
        "RANK1_UNDER_BOTH_METRICS_RESTORED_ON_EVERY_BATTERY_CORPUS_BY_THE"
        "_NESTING_LADDER_WITNESS__EXACT_AFFINE_EXCHANGE_LAW__RECURSIVE_LIBRARY"
        "_COUNT_OPTIMAL_ONLY"
    ),
    "headline": {
        "v1ref": {"inv": {"cb": 0, "eb": 19, "breakeven": 164},
                  "witness_flat_pair": {"cb": 0, "eb": 0, "breakeven": 314,
                                        "ties_identity_draws": 19}},
        "c3_c4_c5": {"inv": {"cb": 0, "eb": 0}, "flat_rung": {"cb": 0, "eb": 0,
                                                              "strict_margins_c4_c5": True}},
        "trap1": {"inv": {"cb": 52, "eb": 49, "breakeven": 5},
                  "witness_ab_abab": {"cb": 0, "eb": 0, "breakeven": 53,
                                      "ties_identity_draws": 4}},
        "trap3": {"inv": {"cb": 33, "eb": 33, "breakeven": 1},
                  "witness_ab": {"cb": 0, "eb": 0, "breakeven": 41,
                                 "ties_identity_draws": 16}},
    },
    "theorems": [
        "T-E1 dispatch decomposition opcost = |Expand| + rho*D; exec net affine in rho (closed-form break-evens)",
        "T-E2 flattening invariance + exact exchange law Net_exec(flat,rho)-Net_exec(nested,rho) = -rho*dD*V + dK (37/37 pairs exact at rho 1,2,4)",
        "T-E3 exec-MDL degeneracy (empty library uniquely optimal; exec benefit is enumeration-horizon-side)",
        "T-E4 charge-class forcing: no Phi in {count, exec, max, sum, countdisp} invents a both-rank-1 library on all six corpora",
        "T-E5 exec-argmin is flat on every battery corpus; rung-1 strongest claim FALSE earned-by-counterexample",
    ],
    "closes_gap": "GAP-T2-2 (closed-form flat-vs-recursive crossover: the T-E2 exchange law is affine in rho with exact per-corpus dD*V and dK; the recorded OPEN status of GAP-T2-2 is superseded by this record without editing it)",
    "gap_t2_1_note": "GAP-T2-1 (depth-favoring admission head-to-head) remains open; out of E9 scope",
    "discipline_append": "gmi-833-claim-discipline-v1/REGISTRATIONS_E9_APPEND.json (METRIC_RELATIVE_RANK1 note on the grammar-growth claim's forbidden_extrapolations)",
}

NOTE = {
    "field": "e9_note",
    "text": (
        "E9 metric-conditionality note (#897 follow-up, "
        "gmi-833-g0-exec-rank-revival-v1): the NULL-1 rank-1 statement "
        "reconciled by this spec is count-metric; under EXEC-B at rho=1, "
        "19/200 equal-cardinality nulls beat the recursive library. Rank-1 "
        "is restored under BOTH accountings by the nesting-ladder witness "
        "(flat pair {ab, abab}, break-even 314 vs 164); see "
        "REGISTRATIONS_E9_APPEND.json."
    ),
}

d = json.load(open(LEDGER))
assert "revival_records" not in d
d["revival_records"] = [REVIVAL]
json.dump(d, open(LEDGER, "w"), indent=1)
open(LEDGER, "a").write("\n")

r = json.load(open(RECON))
assert "e9_note" not in r
r["e9_note"] = NOTE["text"]
json.dump(r, open(RECON, "w"), indent=1)
open(RECON, "a").write("\n")
print("ledger and reconciliation appended")
