#!/usr/bin/env bash
#SBATCH -J zoo-smoke-a2
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH --qos=test
#SBATCH -t 00:15:00
#SBATCH -c 2
#SBATCH -o logs/smoke_a2_%j.out
#SBATCH -e logs/smoke_a2_%j.err
# Amend-2 execution-host gate: full test suite + amendment sha chain +
# hook-determinism assertion (hooks=None replay) + smoke of all 8
# (pair, encoding) cells (ZOO_SMOKE=1 writes SMOKE_QDA2_* only).
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
echo "== pytest =="
$ZOO_PY -m pytest tests/ -q
echo "== amendment invariants =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, sys
root = sys.argv[1]
a2 = json.load(open(root + "/FREEZE_V1_AMEND_2.json"))
v1 = hashlib.sha256(open(root + "/FREEZE_V1.json", "rb").read()).hexdigest()
a1 = hashlib.sha256(open(root + "/FREEZE_V1_AMEND_1.json", "rb").read()).hexdigest()
assert v1 == a2["freeze_v1_sha256"], "freeze chain broken"
assert a1 == a2["amend_1_sha256"], "amend-1 chain broken"
assert len(a2["arms_amend2"]["pairs"]) == 4 and len(a2["arms_amend2"]["seeds"]) == 3
assert a2["scoring_rules_amend2"]["terminal_rule_FROZEN"]["ENCODING_CHOICE_DOMINATES"]
print("AMEND2 INVARIANTS OK")
PY
echo "== hook determinism: hooks=None == legacy call =="
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
from search import map_elites, random_search
a = map_elites.run(budget=120, seed=7, archive="S_structural_3d", res=10)
b = map_elites.run(budget=120, seed=7, archive="S_structural_3d", res=10,
                   sampler=None, mutator=None, crossover_fn=None)
ka = [sorted((k, json.dumps(v, sort_keys=True)))[0:2] for k, v in
      sorted((e["phenotype_digest"], e) for e in a["archive"])]
kb = [sorted((k, json.dumps(v, sort_keys=True)))[0:2] for k, v in
      sorted((e["phenotype_digest"], e) for e in b["archive"])]
assert ka == kb and a["evals"] == b["evals"] and a["qd_score"] == b["qd_score"], \
    "hooks=None changed behaviour"
c = random_search.run(budget=80, seed=3)
d = random_search.run(budget=80, seed=3, sampler=None)
c.pop("elapsed_s"), d.pop("elapsed_s")  # wall clock is not behaviour
assert json.dumps(c, sort_keys=True) == json.dumps(d, sort_keys=True), \
    "sampler=None changed behaviour"
print("HOOK DETERMINISM OK")
PY
echo "== smoke all 8 (pair, enc) cells =="
for p in R01 M03 M05 M06; do
  for e in E0 E1; do
    ZOO_SMOKE=1 $ZOO_PY hpc/qd_run_amend2.py "$ZOO_ROOT" "$p" "$e" 0 > /dev/null
    test "$(cat results/SMOKE_QDA2_${p}_${e}_s0.status | cut -d' ' -f1)" = "ok"
    echo "smoke ok: $p $e"
  done
done
echo "SMOKE OK"
