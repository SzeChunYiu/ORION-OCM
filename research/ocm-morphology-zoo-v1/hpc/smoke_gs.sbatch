#!/usr/bin/env bash
#SBATCH -J zoo-gsmoke
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:10:00
#SBATCH -c 1
#SBATCH --qos=test
#SBATCH -o logs/gsmoke_%j.out
#SBATCH -e logs/gsmoke_%j.err
# GS-R0/R1 smoke gate (#221 sec 18 + GS-R1h) — short --qos=test job proving
# the frozen capsule end-to-end: freeze binding, code digest, pinned impls
# (env probe: ribs/sklearn whichever the freeze pins), novelty+viability SH
# mini-run, sweep enumeration mini-run, T1/T3 evaluation paths, failure
# ledger, and the GS-R1h checkpoint tool on an ISOLATED root (real ledgers
# untouched).  Prints SMOKE OK only when every check passes.
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs}"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, os, random, shutil, subprocess, sys, tempfile
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
f = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")))
fsha = hashlib.sha256(open(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json"),
                           "rb").read()).hexdigest()
env = os.environ.get("GS_FREEZE_SHA", "")
assert env in ("", fsha), "freeze sha mismatch"
h = hashlib.sha256()
for d in ("morphology", "evaluation", "search", "hpc"):
    for fn in sorted(os.listdir(os.path.join(ROOT, d))):
        if fn.endswith(".py"):
            h.update(open(os.path.join(ROOT, d, fn), "rb").read())
assert h.hexdigest() == f["code_digest"], "code drift vs freeze"
from morphology.gs_bound import enumerate_gs_bound, gs_bound_closed_form_size, \
    gs_uniform_sample
from search.successive_halving import run_successive_halving
from search.novelty_viability import make_novelty_archive
from search.surrogate_allocate import EnsembleSurrogate
from evaluation.gs_t1 import evaluate_t1
from evaluation.t3_ecology import evaluate_t3
assert gs_bound_closed_form_size() == f["search_bound"]["size"]
n_sweep = sum(1 for _ in enumerate_gs_bound(shard=(0, gs_bound_closed_form_size())))
res = run_successive_halving(t0_budget=54, seed=0, n0=27)
assert res["counts"]["T0"] > 0
g = next(enumerate_gs_bound(shard=(0, max(2, gs_bound_closed_form_size()))))
r1 = evaluate_t1(g)
assert "gates" in r1
r3 = evaluate_t3(g, f["t3_key"])
assert r3["evaluation"]["total_tasks"] >= 4
# ---- pinned impls (GS-R1h/env probe): whichever the freeze pins MUST run
impl_a = f["environment"]["novelty_archive_impl"]
arch = make_novelty_archive(impl_a, cap=64, floor=8,
                            k=f["novelty_space"]["k_nn"], seed=0)
assert arch.impl == impl_a, "archive impl %s != pinned %s" % (arch.impl, impl_a)
for i in range(12):
    rec = {"feasible": True, "phenotype_digest": "smoke%d" % i,
           "genome": {"U": ["memory"] * (1 + i % 3)},
           "evaluation": {"persistent_bytes": float(i)}}
    arch.consider(rec, (0.1 * i, 0.05 * i, 0.02 * i, 0.01 * i))
assert arch.size() == 12, "archive admitted %d/12" % arch.size()
impl_s = f["environment"]["surrogate_impl"]
sur = EnsembleSurrogate(seed=0, impl=impl_s)
rng = random.Random(1)
recs = [{"genome": gs_uniform_sample(rng).to_json_obj(),
         "feasible": (i % 2 == 0)} for i in range(20)]
sur.train_t0(recs)
assert sur.stats["n_train_t0"] == 20
sc = sur.allocation_score(gs_uniform_sample(rng))
assert 0.0 <= sc, "allocation_score %r" % sc
# ---- GS-R1h checkpoint tool on an ISOLATED root (real ledgers untouched)
tmp = tempfile.mkdtemp(prefix="gsck_smoke_")
os.makedirs(os.path.join(tmp, "manifests"), exist_ok=True)
os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
shutil.copy(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json"), tmp)
shutil.copy(os.path.join(ROOT, "manifests", "GS_R1_TASKS.json"),
            os.path.join(tmp, "manifests"))
fake = {"counts": {"T0": 100, "T1": 30, "T2": 9},
        "viable_counts": {"T0": 9}, "cpu_hours": 0.01,
        "deadline_hit": False, "n_archive": 7, "survivors": [
            {"phenotype_digest": "p%d" % i} for i in range(3)]}
json.dump(fake, open(os.path.join(tmp, "results",
                                  "GS_R1_GSA1_units_s0.json"), "w"))
open(os.path.join(tmp, "results", "GS_R1_GSA1_units_s0.status"), "w").write("ok\n")
p = subprocess.run([sys.executable,
                    os.path.join(ROOT, "hpc", "checkpoint_gs.py"), tmp],
                   capture_output=True, text=True)
assert p.returncode == 0, "checkpoint tool failed: %s" % p.stderr[-400:]
ck = open(os.path.join(tmp, "results", "GS_R1_CHECKPOINTS.jsonl")).read()
line = json.loads(ck.strip().splitlines()[-1])
assert line["checkpoint"] == 1 and line["arms"]["GSA1_units"]["tier_counts"]["T0"] == 100
st = json.load(open(os.path.join(tmp, "results", "GS_R1_STATUS.json")))
assert st["partial_terminal_preview"].startswith("PARTIAL_")
shutil.rmtree(tmp)
print("SMOKE OK n_sweep=%d t0=%d t1_feasible=%s t3_solved_fraction=%s "
      "impls=%s/%s archive=%d checkpoint_tool=verified" % (
          n_sweep, res["counts"]["T0"], r1["feasible"],
          r3["evaluation"]["solved_fraction"], impl_a, impl_s, arch.size()))
PY
