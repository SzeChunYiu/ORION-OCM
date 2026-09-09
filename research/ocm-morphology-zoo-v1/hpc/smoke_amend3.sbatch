#!/usr/bin/env bash
#SBATCH -J zoo-smoke-a3
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH --qos=test
#SBATCH -t 00:15:00
#SBATCH -c 2
#SBATCH -o logs/smoke_a3_%j.out
#SBATCH -e logs/smoke_a3_%j.err
# Amend-3 execution-host gate: full test suite + amendment sha chain +
# census-P00C binding (registry D-grid bounds == truth, T2 scalar refs ==
# truth medians, denominators) + T2 smoke of all 5 arms THROUGH THE SAME
# WORKER the production array runs (ZOO_SMOKE=1 writes SMOKE_QDA3_* only).
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
echo "== pytest =="
$ZOO_PY -m pytest tests/ -q
echo "== amendment + census binding invariants =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, sys
root = sys.argv[1]
a3 = json.load(open(root + "/FREEZE_V1_AMEND_3.json"))
v1 = hashlib.sha256(open(root + "/FREEZE_V1.json", "rb").read()).hexdigest()
a1 = hashlib.sha256(open(root + "/FREEZE_V1_AMEND_1.json", "rb").read()).hexdigest()
a2 = hashlib.sha256(open(root + "/FREEZE_V1_AMEND_2.json", "rb").read()).hexdigest()
assert v1 == a3["freeze_v1_sha256"], "freeze chain broken"
assert a1 == a3["amend_1_sha256"], "amend-1 chain broken"
assert a2 == a3["amend_2_sha256"], "amend-2 chain broken"
arms = a3["arms_amend3"]["arms"]
assert len(arms) == 5 and len(a3["arms_amend3"]["seeds"]) == 3
sys.path.insert(0, root)
from evaluation.descriptors import DESCRIPTOR_REGISTRY
from evaluation.objectives import W2_REF, B2_REF
truth = json.load(open(root + "/archives/CENSUS_P00C_TRUTH.json"))["summary"]
for view in ("D_dev_2d", "D_dev_3d"):
    reg = DESCRIPTOR_REGISTRY[view]["bounds"]
    frozen = tuple(tuple(b) for b in truth["frozen_grid_bounds"][view])
    assert tuple(tuple(b) for b in reg) == frozen, view + " bounds drift"
assert (W2_REF, B2_REF) == (truth["t2_scalar_refs"]["W2_REF"],
                            truth["t2_scalar_refs"]["B2_REF"]), "T2 refs drift"
den, tden = a3["census_truth_P00C"]["denominators"], truth["denominators"]
assert den["PARETO_T2"] == truth["pareto_set_size"] == 792
assert den["D2d@10_occupied"] == tden["D2d@10_occupied"] == 50
assert den["D3d@10_occupied"] == tden["D3d@10_occupied"] == 83
assert den["CVTD_occupied_niches"] == tden["CVTD_occupied_niches"] == 64
print("AMEND3 INVARIANTS OK")
PY
echo "== T2 smoke: all 5 arms through the production worker =="
for a in P01_random_search_T2 P03_map_elites_T2 P05_map_elites_D2d \
         P06_cvt_map_elites_D P09_map_elites_D3d; do
  ZOO_SMOKE=1 $ZOO_PY hpc/qd_run_amend3.py "$ZOO_ROOT" "$a" 0 > /dev/null
  test "$(cut -d' ' -f1 results/SMOKE_QDA3_${a}_s0.status)" = "ok"
  echo "smoke ok: $a"
done
echo "SMOKE OK"
