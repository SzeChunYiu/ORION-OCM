#!/usr/bin/env bash
#SBATCH -J zoo-smoke-a1
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH --qos=test
#SBATCH -t 00:15:00
#SBATCH -c 2
#SBATCH -o logs/smoke_a1_%j.out
#SBATCH -e logs/smoke_a1_%j.err
# Amend-1 execution-host gate: full test suite + amendment invariants +
# smoke of ALL 8 amended arms (ZOO_SMOKE=1 writes SMOKE_QDA1_* only).
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
echo "== pytest =="
$ZOO_PY -m pytest tests/ -q
echo "== amendment invariants =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, sys
root = sys.argv[1]
a1 = json.load(open(root + "/FREEZE_V1_AMEND_1.json"))
v1 = hashlib.sha256(open(root + "/FREEZE_V1.json", "rb").read()).hexdigest()
assert v1 == a1["freeze_v1_sha256"], "freeze chain broken"
p00b = json.load(open(root + "/archives/CENSUS_P00B_TRUTH.json"))
s = p00b["summary"]
assert s["controls"]["S2d@10_occupied"] == 4, "control drift"
assert s["controls"]["B2d@10_occupied"] == 2, "control drift"
for k, v in a1["census_truth_P00B"]["denominators_amended"].items():
    assert s["denominators"][k] == v, "denominator drift: " + k
assert len(p00b["cvt_centroids"]) == a1["census_truth_P00B"]["denominators_amended"]["CVT64_occupied_niches"]
print("AMEND1 INVARIANTS OK")
PY
echo "== smoke all 8 arms =="
for a in P01_random_search P02_nsga2 P03_map_elites P04_nslc P05_map_elites_B P06_cvt_map_elites P09_mome P11_lexicase; do
  ZOO_SMOKE=1 $ZOO_PY hpc/qd_run_amend1.py "$ZOO_ROOT" "$a" 0 > /dev/null
  test "$(cat results/SMOKE_QDA1_${a}_s0.status | cut -d' ' -f1)" = "ok"
  echo "smoke ok: $a"
done
echo "SMOKE OK"
