"""FREEZE_V1_AMEND_5 freezing TOOL (quality-gated D-archive admission — the
revival iteration amend-4's own frozen rule 3 owes: MIXED_INTERMEDIATE_NO_TERMINAL
/ amend3_terminal_status=UNDERMINED_QUALITY).

This tool — not a hand-written file — writes FREEZE_V1_AMEND_5.json, and
stamps created_utc ITSELF at freeze time (the amend-3 timing-erratum lesson).

THE ONE VARIED DIMENSION: map_elites.run(admission_bar=b) admits a feasible
record to the D-archive only if dev_score >= b (rejected evaluations still
charged).  admission_bar=None (the control arms) is byte-identical to every
previous amendment's loop — try_insert consumes no RNG.

THE BAR IS CHOSEN MECHANICALLY, PROSPECTIVELY, BY THIS TOOL from the frozen
GATE-CEILING census truth (archives/GATE_CEILING_TRUTH.json, unscored,
produced BEFORE this freeze): the ceiling of a bar b on axis X is the number
of census-occupied cells whose in-cell max dev >= b — the largest own-axis
recovery ANY gated archive can reach at b regardless of search.  Selection
rule (frozen here, executed here, before any scored run):

    bar = the STRICTEST ladder quantile (q in 0.5, 0.4, 0.3, 0.25, 0.2, 0.15,
    0.1 over the feasible-census dev distribution) whose ceil_D2d_recovery
    >= 0.25 AND ceil_D3d_recovery >= 0.25

i.e. the coordinator's census-median default (q0.5 == HZD9 quality_bar_T2
0.224507, asserted) unless it leaves the amend-3 terminal bar 0.25
structurally unreachable on either gated axis, in which case the strictest
bar that keeps it reachable is frozen, with the ladder embedded verbatim as
the justification.  If NO ladder bar keeps 0.25 reachable on both axes the
tool REFUSES (a bar below q0.1 would be a different amendment, not a
relaxation).  Never post-hoc: no amend-5 scored result exists yet (asserted).

Refuses to run when:
  - FREEZE_V1_AMEND_5.json already exists (append-only)
  - the ancestor chain V1 -> A1 -> A2 -> A3 -> A4 is broken anywhere
  - archives/GATE_CEILING_TRUTH.json is missing or any of its P00C/HZD9
    xchecks is false (unscored truth precedes the freeze)
  - any scored amend-5 result status (QDA5_) already exists

Usage: python3 hpc/freeze_amend5.py <capsule_root>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

FREEZE_PATH = os.path.join(ROOT, "FREEZE_V1_AMEND_5.json")
if os.path.exists(FREEZE_PATH):
    raise SystemExit("FREEZE_V1_AMEND_5.json exists — amendments are "
                     "append-only; write AMEND_6 instead")
_chain = [("FREEZE_V1.json",), ("FREEZE_V1_AMEND_1.json",),
          ("FREEZE_V1_AMEND_2.json",), ("FREEZE_V1_AMEND_3.json",),
          ("FREEZE_V1_AMEND_4.json",)]
shas = {}
for (fn,) in _chain:
    shas[fn] = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
with open(os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")) as f:
    A4 = json.load(f)
assert shas["FREEZE_V1.json"] == A4["freeze_v1_sha256"], "V1 sha drift in A4"
assert shas["FREEZE_V1_AMEND_1.json"] == A4["amend_1_sha256"], "A1 sha drift in A4"
assert shas["FREEZE_V1_AMEND_2.json"] == A4["amend_2_sha256"], "A2 sha drift in A4"
assert shas["FREEZE_V1_AMEND_3.json"] == A4["amend_3_sha256"], "A3 sha drift in A4"

TRUTH_GC = os.path.join(ROOT, "archives", "GATE_CEILING_TRUTH.json")
if not os.path.exists(TRUTH_GC):
    raise SystemExit("archives/GATE_CEILING_TRUTH.json missing — run "
                     "hpc/gate_ceiling.py (LUNARC) BEFORE freezing amend-5")
with open(TRUTH_GC) as f:
    GC = json.load(f)["summary"]
for k, v in GC["xcheck_vs_P00C_HZD9"].items():
    if isinstance(v, bool):
        assert v is True, "GATE-CEILING xcheck %s false — census not deterministic" % k
assert GC["ladder"]["q0.5"]["bar"] == A4["quality_bar_T2"], \
    "ladder q0.5 != HZD9/A4 census-median quality bar"

# ---- MECHANICAL bar selection (strictest ladder bar keeping 0.25 reachable)
OWN_AXIS_BAR = 0.25  # the amend-3/amend-4 absolute own-axis terminal bar
LADDER_ORDER = ["q0.5", "q0.4", "q0.3", "q0.25", "q0.2", "q0.15", "q0.1"]
chosen_q = None
for q in LADDER_ORDER:
    e = GC["ladder"][q]
    if e["ceil_D2d_recovery"] >= OWN_AXIS_BAR and e["ceil_D3d_recovery"] >= OWN_AXIS_BAR:
        chosen_q = q
        break
if chosen_q is None:
    raise SystemExit("no ladder bar keeps ceil >= 0.25 on both gated axes — "
                     "refusing to freeze (a sub-q0.1 bar is a different "
                     "amendment, not a relaxation)")
BAR = GC["ladder"][chosen_q]["bar"]
if chosen_q == "q0.5":
    SELECTION_BASIS = (
        "strictest ladder quantile with ceil_D2d_recovery >= 0.25 AND "
        "ceil_D3d_recovery >= 0.25 over the frozen GATE-CEILING truth "
        "(receipt %s): the census-median default q0.5 (== HZD9 "
        "quality_bar_T2) was itself the strictest admissible bar, so the "
        "coordinator's default is frozen and no relaxation was needed"
        % GC["receipt_head"][:16])
else:
    SELECTION_BASIS = (
        "strictest ladder quantile with ceil_D2d_recovery >= 0.25 AND "
        "ceil_D3d_recovery >= 0.25 over the frozen GATE-CEILING truth "
        "(receipt %s): the census-median default q0.5 (%s) left a ceiling "
        "below the 0.25 terminal bar, so the bar is relaxed PROSPECTIVELY "
        "to %s = %r with the embedded ladder as justification (frozen "
        "BEFORE any scored run; never post-hoc)"
        % (GC["receipt_head"][:16], GC["ladder"]["q0.5"]["bar"], chosen_q, BAR))

with open(os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json")) as f:
    P00C = json.load(f)["summary"]
DEN = dict(A4["census_truth_P00C"]["denominators"])  # the amend-3/4 frozen set
assert DEN["PARETO_T2"] == 792 and DEN["D2d@10_occupied"] == 50 \
    and DEN["D3d@10_occupied"] == 83 and DEN["CVTD_occupied_niches"] == 64

# P01 reference from the amend-3 SCORED aggregate (best_dev clause of the
# amend-3 DIVERSE rule is re-evaluated verbatim on the gated arms)
AGG3 = os.path.join(ROOT, "results", "AGGREGATE_AMEND3.json")
if not os.path.exists(AGG3):
    raise SystemExit("results/AGGREGATE_AMEND3.json missing — the P01 "
                     "best_dev reference must be embedded from the scored "
                     "amend-3 aggregate")
with open(AGG3) as f:
    agg3 = json.load(f)
P01_BEST = agg3["cells"]["P01_random_search_T2"]["best_dev_T2"]
assert P01_BEST == 0.571144, "P01 best_dev_T2 seed-mean drifted from 0.571144"

for st in ("QDA5_",):
    hits = [fn for fn in os.listdir(os.path.join(ROOT, "results"))
            if fn.startswith(st) and fn.endswith(".status")]
    if hits:
        raise SystemExit("scored amend-5 statuses exist (%s...) — freeze must "
                         "precede scored runs" % hits[0])

ARMS = [
    {"arm_id": "G01_gate_D2d", "gated": True, "archive": "D_dev_2d",
     "own_axis": "D2d_cell_recovery",
     "nogate_twin": "P05_map_elites_D2d"},
    {"arm_id": "G00_nogate_D2d", "gated": False, "archive": "D_dev_2d",
     "own_axis": "D2d_cell_recovery",
     "nogate_twin": "P05_map_elites_D2d"},
    {"arm_id": "G01_gate_D3d", "gated": True, "archive": "D_dev_3d",
     "own_axis": "D3d_cell_recovery",
     "nogate_twin": "P09_map_elites_D3d"},
    {"arm_id": "G00_nogate_D3d", "gated": False, "archive": "D_dev_3d",
     "own_axis": "D3d_cell_recovery",
     "nogate_twin": "P09_map_elites_D3d"},
]

CREATED = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
freeze = {
    "amendment_id": "FREEZE_V1_AMEND_5_QUALITY_GATE",
    "amends": "FREEZE_V1_AMEND_4.json",
    "freeze_v1_sha256": shas["FREEZE_V1.json"],
    "amend_1_sha256": shas["FREEZE_V1_AMEND_1.json"],
    "amend_2_sha256": shas["FREEZE_V1_AMEND_2.json"],
    "amend_3_sha256": shas["FREEZE_V1_AMEND_3.json"],
    "amend_4_sha256": shas["FREEZE_V1_AMEND_4.json"],
    "created_utc": CREATED,
    "created_utc_by": "hpc/freeze_amend5.py at freeze time (tool-stamped)",
    "supersedes_sha256": None,
    "refreeze_reason": None,
    "motivation": (
        "Revival iteration owed by amend-4's own frozen rule 3 "
        "(mzd9): MIXED_INTERMEDIATE_NO_TERMINAL with amend3_terminal_status "
        "UNDERMINED_QUALITY — P05/P09 D-archive coverage was junk-borne "
        "(seed-mean junk_free_ratio 0.326667 / 0.288597 < 0.5 at the "
        "census-median bar).  Lever (#221 diagnose-revive: attribute to ONE "
        "stage, apply the matching lever, re-test): the QUALITY stage of "
        "archive admission.  A quality gate on admission makes junk-free "
        "coverage the archive's own objective, so the amend-3 DIVERSE "
        "terminal either stands cleanly at scope with the gate ON, or the "
        "claim is honestly revised to quality-conditional.  The gate is the "
        "ONE varied dimension: G00 no-gate twins (identical budget/seeds/axis, "
        "byte-identical map_elites loop) run in the same array for "
        "attribution, and double as in-array determinism xchecks against the "
        "frozen QDA3 archives."),
    "quality_gate_amend5": {
        "mechanism": "map_elites.run(admission_bar=bar): a FEASIBLE record is "
                     "admitted to the D-archive only if dev_score >= bar; "
                     "rejected evaluations remain charged to the budget and "
                     "counted as feasible-found; try_insert consumes no RNG "
                     "so admission_bar=None is byte-identical to the "
                     "pre-amendment loop (G00 arms must reproduce the QDA3 "
                     "archives exactly — asserted in the worker)",
        "admission_bar": BAR,
        "admission_bar_quantile": chosen_q,
        "bar_selection_rule_FROZEN": "strictest ladder quantile (q in 0.5, "
                                     "0.4, 0.3, 0.25, 0.2, 0.15, 0.1 over the "
                                     "feasible-census dev distribution) with "
                                     "ceil_D2d_recovery >= 0.25 AND "
                                     "ceil_D3d_recovery >= 0.25",
        "bar_selection_basis": SELECTION_BASIS,
        "ceiling_ladder": GC["ladder"],
        "chosen_bar_ceilings": {
            "D2d_cells": GC["ladder"][chosen_q]["ceil_D2d_cells"],
            "D2d_recovery": GC["ladder"][chosen_q]["ceil_D2d_recovery"],
            "D3d_cells": GC["ladder"][chosen_q]["ceil_D3d_cells"],
            "D3d_recovery": GC["ladder"][chosen_q]["ceil_D3d_recovery"],
            "CVTD_niches": GC["ladder"][chosen_q]["ceil_CVTD_niches"],
            "CVTD_recovery": GC["ladder"][chosen_q]["ceil_CVTD_recovery"]},
        "census_median_bar_hz9": A4["quality_bar_T2"],
        "precedence": "GATE-CEILING truth produced and this bar chosen BEFORE "
                      "any amend-5 scored run (QDA5_ statuses asserted "
                      "absent); the ladder is embedded verbatim so the "
                      "choice is auditable against the rule",
    },
    "census_truth_P00C": {
        "run_id": P00C["run_id"], "tier": "T2",
        "denominators": DEN,
        "frozen_grid_bounds": P00C["frozen_grid_bounds"],
        "t2_scalar_refs": P00C["t2_scalar_refs"],
    },
    "census_truth_GATE_CEILING": {
        "run_id": GC["run_id"], "tier": "T2", "unscored": True,
        "receipt_head": GC["receipt_head"], "config_digest": GC["config_digest"],
        "feasible": GC["feasible"], "denominators": GC["denominators"],
        "xcheck_vs_P00C_HZD9": GC["xcheck_vs_P00C_HZD9"],
    },
    "arms_amend5": {
        "budget": 40000,
        "seeds": [0, 1, 2],
        "res": 10,
        "arms": ARMS,
        "gated_arms": ["G01_gate_D2d", "G01_gate_D3d"],
        "nogate_arms": ["G00_nogate_D2d", "G00_nogate_D3d"],
    },
    "metrics_amend5": [
        "own_axis_recovery (D2d@10 vs 50 / D3d@10 vs 83 census cells), recomputed uniformly at T2 from the archive records",
        "junk_free_own_axis_recovery at the frozen admission bar (== own_axis for G01 by construction, asserted)",
        "junk_free_ratio (== 1.0 for G01, asserted per task)",
        "pareto_recovery_T2 (vs 792), best_dev_T2, n_elites, min_dev_elite (>= bar for G01, asserted)",
        "n_admissible_feasible (feasible evals with dev >= bar; charged-budget accounting of what the gate rejected)",
        "gate_vs_control deltas per axis: seed-mean own_axis_recovery, best_dev_T2, pareto_recovery_T2, n_elites (attribution; reported, never rule-firing)",
        "G00 determinism xchecks: archive records == frozen QDA3 twin archive; best_dev == frozen QDA3 value; raw own_axis == frozen QDA3 metric",
    ],
    "thresholds_amend5": {
        "own_axis_absolute_bar": 0.25,
        "best_dev_ref_P01": P01_BEST,
        "best_dev_slack": 0.01,
        "best_dev_bar": round(P01_BEST - 0.01, 6),
        "ceiling_constraint": "ceil_recovery(chosen bar) >= 0.25 on both "
                              "gated axes (structural reachability, checked "
                              "at freeze time)",
    },
    "scoring_rules_amend5": {
        "amend3_diverse_rule_verbatim": [
            r for r in json.load(open(os.path.join(
                ROOT, "FREEZE_V1_AMEND_3.json")))["scoring_rules_amend3"]
            ["terminal_rule_FROZEN"]
            if r.startswith("DIVERSE_HIGH_PERFORMING")][0],
        "terminal_rule_FROZEN_first_match": [
            "1 DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE (RESTORED_QUALITY_GATED_AT_SCOPE): some GATED arm (G01_gate_D2d / G01_gate_D3d) has seed-mean own_axis_recovery >= 0.25 AND seed-mean best_dev_T2 >= 0.561144 (P01 0.571144 - 0.01, the amend-3 DIVERSE clause verbatim); junk-free holds by construction (every admitted elite >= admission_bar, junk_free_ratio == 1.0 asserted per task)",
            "2 NO_MEANINGFUL_BEHAVIORAL_DIVERSITY (REVISED_QUALITY_CONDITIONAL): EVERY gated arm seed-mean own_axis_recovery < 0.25 — under the frozen census-quality bar the D-archive coverage collapses below the scope bar on both axes; the amend-3 diversity terminal is honestly revised: its raw coverage was quality-conditional (junk-borne), not restored by the lever",
            "3 else MIXED_INTERMEDIATE_NO_TERMINAL (PARTIAL_RESTORATION): some but not all conditions of rule 1 hold (one axis restored, or recovery restored without the best_dev clause)",
        ],
        "aggregation": "aggregate_amend5.py runs only when all 12 tasks (4 arms x 3 seeds) have ok dispositions and verifiable receipts, GATE_CEILING truth is present, and every G00 byte-identity xcheck passed; verdicts are computed mechanically from these rules, never narrated",
    },
    "controls": {
        "one_varied_dimension": "admission_bar is the ONLY difference between "
                                "G01_gate_X and G00_nogate_X (same algorithm, "
                                "budget 40000, seeds, axis, res); attribution "
                                "deltas are computed per axis in the aggregate",
        "g00_byte_identity": "G00 arms must reproduce the frozen amend-3 "
                             "archives (QDA3_P05_map_elites_D2d_s{0,1,2}, "
                             "QDA3_P09_map_elites_D3d_s{0,1,2}) record-for-"
                             "record: in-array determinism audit of the "
                             "admission_bar=None path against the scored "
                             "amend-3 layer",
        "hzd9r_crosscheck": "when the chosen bar == HZD9 quality_bar_T2, G00 "
                            "junk_free_own_axis_recovery must equal the "
                            "frozen HZD9R value for the twin arm/seed",
        "t0_untouched": "T0 scoring path and all amend-1..4 truth unchanged "
                        "and still reproducible",
        "encoding_fixed": "E0_direct everywhere; no codec arms",
    },
    "status": "FROZEN pre-score",
}
with open(FREEZE_PATH, "w") as f:
    json.dump(freeze, f, indent=1)
print(json.dumps({"frozen": FREEZE_PATH, "created_utc": CREATED,
                  "admission_bar": BAR, "quantile": chosen_q,
                  "ceilings": freeze["quality_gate_amend5"]["chosen_bar_ceilings"],
                  "amend_5_sha256": hashlib.sha256(
                      open(FREEZE_PATH, "rb").read()).hexdigest()},
                 sort_keys=True))
