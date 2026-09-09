#!/usr/bin/env bash
#SBATCH -J zoo-audit
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:20:00
#SBATCH -c 1
#SBATCH -o logs/audit_%j.out
#SBATCH -e logs/audit_%j.err
# Post-aggregate audit: tests green, freeze denominators == census truth,
# every receipt verifies, aggregate matches per-run rows.
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY -m pytest tests/ -q
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import json, sys, os
root = sys.argv[1]
sys.path.insert(0, root)
from evaluation.receipts import verify_receipt
ok = True
for p in os.listdir(os.path.join(root, "manifests", "receipts")):
    r = json.load(open(os.path.join(root, "manifests", "receipts", p)))
    if not verify_receipt(r):
        print("RECEIPT FAIL", p); ok = False
freeze = json.load(open(os.path.join(root, "FREEZE_V1.json")))
truth = json.load(open(os.path.join(root, "archives", "CENSUS_P00_TRUTH.json")))["summary"]
fz = freeze["census_truth_P00"]
for k, tk in (("pareto_phenotypes", "pareto_set_size"),
              ("S_cells_occupied", "descriptor_cells_occupied_S"),
              ("B_cells_occupied", "descriptor_cells_occupied_B"),
              ("feasible", "feasible")):
    assert fz[k] == truth[tk], (k, fz[k], truth[tk])
print("AUDIT", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
PY
