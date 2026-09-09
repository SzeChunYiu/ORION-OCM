#!/usr/bin/env bash
#SBATCH -J zoo-smoke-a5
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH --qos=test
#SBATCH -t 00:20:00
#SBATCH -c 2
#SBATCH -o logs/smoke_a5_%j.out
#SBATCH -e logs/smoke_a5_%j.err
# Amend-5 execution-host gate: full test suite + amendment sha chain (incl.
# A4) + GATE-CEILING truth binding (xchecks true, frozen bar == ladder choice,
# ceilings keep 0.25 reachable) + production-branch key bindings (the SMOKE
# ternaries cannot reach them — the amend-4 interval-key lesson) + gate-path
# byte-identity microcheck (a pass-everything bar reproduces the None archive)
# + T2 smoke of one gated and one no-gate arm THROUGH THE SAME WORKER the
# production array runs (ZOO_SMOKE=1 writes SMOKE_QDA5_* only).
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
echo "== pytest =="
$ZOO_PY -m pytest tests/ -q
echo "== amendment A5 + GATE-CEILING/P00C binding invariants =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, sys
root = sys.argv[1]
a5 = json.load(open(root + "/FREEZE_V1_AMEND_5.json"))
shas = {fn: hashlib.sha256(open(root + "/" + fn, "rb").read()).hexdigest()
        for fn in ("FREEZE_V1.json", "FREEZE_V1_AMEND_1.json",
                   "FREEZE_V1_AMEND_2.json", "FREEZE_V1_AMEND_3.json",
                   "FREEZE_V1_AMEND_4.json")}
assert shas["FREEZE_V1.json"] == a5["freeze_v1_sha256"], "freeze chain broken"
assert shas["FREEZE_V1_AMEND_1.json"] == a5["amend_1_sha256"], "amend-1 chain"
assert shas["FREEZE_V1_AMEND_2.json"] == a5["amend_2_sha256"], "amend-2 chain"
assert shas["FREEZE_V1_AMEND_3.json"] == a5["amend_3_sha256"], "amend-3 chain"
assert shas["FREEZE_V1_AMEND_4.json"] == a5["amend_4_sha256"], "amend-4 chain"
assert a5["amend_4_sha256"].startswith("b51a9959"), \
    "A4 sha not the merged-main freeze (b51a9959...)"
assert "freeze_amend5.py" in a5["created_utc_by"], \
    "created_utc not tool-stamped (the amend-3 erratum pattern)"
assert a5["supersedes_sha256"] is None, "first freeze must not supersede"
gc = json.load(open(root + "/archives/GATE_CEILING_TRUTH.json"))["summary"]
for k, v in gc["xcheck_vs_P00C_HZD9"].items():
    if isinstance(v, bool):
        assert v is True, "GATE-CEILING xcheck %s false" % k
hz = json.load(open(root + "/archives/HZD9_TRUTH.json"))["summary"]
qg = a5["quality_gate_amend5"]
assert qg["ceiling_ladder"] == gc["ladder"], "ladder drift vs truth"
assert qg["admission_bar_quantile"] in gc["ladder"]
assert qg["admission_bar"] == gc["ladder"][qg["admission_bar_quantile"]]["bar"], \
    "frozen bar != ladder choice"
assert gc["ladder"]["q0.5"]["bar"] == hz["quality_bar_T2"] == 0.224507
chosen = gc["ladder"][qg["admission_bar_quantile"]]
assert chosen["ceil_D2d_recovery"] >= 0.25 and chosen["ceil_D3d_recovery"] >= 0.25, \
    "chosen bar leaves the 0.25 terminal bar structurally unreachable"
# the strictest-admissible selection rule: no STRICTER ladder bar qualified
ladder_order = ["q0.5", "q0.4", "q0.3", "q0.25", "q0.2", "q0.15", "q0.1"]
for q in ladder_order[:ladder_order.index(qg["admission_bar_quantile"])]:
    e = gc["ladder"][q]
    assert not (e["ceil_D2d_recovery"] >= 0.25 and e["ceil_D3d_recovery"] >= 0.25), \
        "a stricter bar (%s) also kept 0.25 reachable — rule misapplied" % q
arms = {a["arm_id"]: a for a in a5["arms_amend5"]["arms"]}
assert a5["arms_amend5"]["gated_arms"] == ["G01_gate_D2d", "G01_gate_D3d"]
assert a5["arms_amend5"]["nogate_arms"] == ["G00_nogate_D2d", "G00_nogate_D3d"]
assert arms["G01_gate_D2d"]["archive"] == "D_dev_2d" \
    and arms["G01_gate_D2d"]["own_axis"] == "D2d_cell_recovery" \
    and arms["G01_gate_D2d"]["gated"] is True \
    and arms["G01_gate_D2d"]["nogate_twin"] == "P05_map_elites_D2d"
assert arms["G00_nogate_D2d"]["gated"] is False \
    and arms["G00_nogate_D3d"]["nogate_twin"] == "P09_map_elites_D3d" \
    and arms["G01_gate_D3d"]["own_axis"] == "D3d_cell_recovery"
# production branches of the worker ternaries (SMOKE can never reach these)
assert a5["arms_amend5"]["budget"] == 40000
assert a5["arms_amend5"]["seeds"] == [0, 1, 2]
thr = a5["thresholds_amend5"]
agg3 = json.load(open(root + "/results/AGGREGATE_AMEND3.json"))
p01 = agg3["cells"]["P01_random_search_T2"]["best_dev_T2"]
assert thr["best_dev_ref_P01"] == p01 == 0.571144
assert thr["best_dev_slack"] == 0.01 and thr["best_dev_bar"] == 0.561144
assert thr["own_axis_absolute_bar"] == 0.25
a4 = json.load(open(root + "/FREEZE_V1_AMEND_4.json"))
a3 = json.load(open(root + "/FREEZE_V1_AMEND_3.json"))
assert a5["census_truth_P00C"]["denominators"] \
    == a4["census_truth_P00C"]["denominators"] \
    == a3["census_truth_P00C"]["denominators"], "denominator set drift"
den = a5["census_truth_P00C"]["denominators"]
assert (den["PARETO_T2"], den["D2d@10_occupied"], den["D3d@10_occupied"],
        den["CVTD_occupied_niches"]) == (792, 50, 83, 64)
assert a5["scoring_rules_amend5"]["amend3_diverse_rule_verbatim"].startswith(
    "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE"), "rule embed"
print("AMEND5 INVARIANTS OK")
PY
echo "== gate-path byte-identity microcheck (pass-everything bar == None) =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import os, sys
root = sys.argv[1]
sys.path.insert(0, root)
os.environ["ZOO_TIER"] = "T2"
from search.map_elites import run
def sig(res):
    return sorted((r["genotype_digest"], round(r["dev_score"], 9),
                   tuple(r["descriptors"])) for r in res["archive"])
a = run(budget=60, seed=1, archive="D_dev_2d", res=10, admission_bar=None)
b = run(budget=60, seed=1, archive="D_dev_2d", res=10, admission_bar=-1e9)
assert sig(a) == sig(b), "admission gate perturbed the None code path"
assert a["feasible_found"] == b["feasible_found"]
assert b["n_admissible_feasible"] == b["feasible_found"]
print("byte-identity microcheck OK: %d elites identical" % len(a["archive"]))
PY
echo "== T2 smoke: one gated + one no-gate arm through the production worker =="
for a in G01_gate_D2d G00_nogate_D2d; do
  ZOO_SMOKE=1 $ZOO_PY hpc/qd_run_amend5.py "$ZOO_ROOT" "$a" 0 > /dev/null
  test "$(cut -d' ' -f1 results/SMOKE_QDA5_${a}_s0.status)" = "ok"
  echo "smoke ok: $a"
done
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import json, sys
root = sys.argv[1]
g = json.load(open(root + "/results/SMOKE_QDA5_G01_gate_D2d_s0.json"))
assert g["gated"] is True and g["admission_bar"] == 0.0
assert g["junk_free_ratio"] in (1.0, None) or abs(g["junk_free_ratio"] - 1.0) < 1e-9, \
    "gated smoke must be junk-free at the applied bar"
assert g["xchecks_passed"]["junk_free_equals_raw"] is True
n = json.load(open(root + "/results/SMOKE_QDA5_G00_nogate_D2d_s0.json"))
assert n["gated"] is False and n["admission_bar"] is None
print("smoke outputs verified (gate n_elites=%d, control n_elites=%d)"
      % (g["n_elites"], n["n_elites"]))
PY
echo "SMOKE OK"
