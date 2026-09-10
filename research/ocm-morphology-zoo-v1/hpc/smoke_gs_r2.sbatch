#!/usr/bin/env bash
#SBATCH -J zoo-gs2smoke
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -t 00:15:00
#SBATCH -c 1
#SBATCH --qos=test
#SBATCH -o logs/gs2smoke_%j.out
#SBATCH -e logs/gs2smoke_%j.err
# GS-R2 smoke gate (JOB B): freeze binding + code digest + per-file sha
# chain spot-check, cross-host determinism probe (builtin impls), on-host
# pinned-impl determinism probe, T3 m>=104 battery path, and the NaN-fix
# read (holdout_mae_t1 finite on a tiny pinned GSA6_ALL run).  Prints
# SMOKE2 OK only when every check passes.
export ZOO_ROOT="${ZOO_ROOT:-$HOME/zoo221/gs_r2}"
export GS_RUN_PREFIX="GS_R2_"
export GS_FREEZE_NAME="GRAND_SEARCH_R2_FREEZE.json"
source "${SLURM_SUBMIT_DIR}/hpc/common_env.sh"
set -euo pipefail
cd "$ZOO_ROOT"
$ZOO_PY hpc/determinism_probe_r2.py "$ZOO_ROOT"
$ZOO_PY hpc/determinism_probe_r2.py "$ZOO_ROOT" --pinned
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, os, sys
ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
FN = "GRAND_SEARCH_R2_FREEZE.json"
f = json.load(open(os.path.join(ROOT, FN)))
fsha = hashlib.sha256(open(os.path.join(ROOT, FN), "rb").read()).hexdigest()
env = os.environ.get("GS_FREEZE_SHA", "")
assert env in ("", fsha), "freeze sha mismatch"
h = hashlib.sha256()
for d in ("morphology", "evaluation", "search", "hpc"):
    for fn in sorted(os.listdir(os.path.join(ROOT, d))):
        if fn.endswith(".py"):
            h.update(open(os.path.join(ROOT, d, fn), "rb").read())
assert h.hexdigest() == f["code_digest"], "code drift vs freeze"
bad = []
for rel, sha in f["code_files_sha256"].items():
    got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
    if got != sha:
        bad.append(rel)
assert not bad, "per-file sha drift: %s" % bad
assert f["evidence_class"] == "EXPLORATORY_ADAPTIVE"
assert f["decision_ledger_rule"].startswith("NO sbatch")
assert len(f["arms"]) == 5 and set(f["arms"]) == {
    "GSA6_NG", "GSA6_DP", "GSA6_SC", "GSA6_ALL", "GSA5P_fixed"}
_lv = {a: {k: bool(f["arms"][a].get(k)) for k in
           ("novelty_gate", "dedup_promotion", "surrogate_cumulative")}
       for a in f["arms"]}
assert _lv["GSA6_ALL"] == {"novelty_gate": True, "dedup_promotion": True,
                           "surrogate_cumulative": True}, _lv
assert _lv["GSA5P_fixed"] == {"novelty_gate": False, "dedup_promotion": False,
                              "surrogate_cumulative": False}, _lv
assert _lv["GSA6_NG"]["novelty_gate"] and not _lv["GSA6_NG"]["dedup_promotion"]
assert _lv["GSA6_DP"]["dedup_promotion"] and not _lv["GSA6_DP"]["novelty_gate"]
assert _lv["GSA6_SC"]["surrogate_cumulative"] and \
    not _lv["GSA6_SC"]["novelty_gate"]
assert f["heldout_t3"]["m104_extension"]["m_total_min"] >= 104
from evaluation.t3_ecology_m104 import evaluate_t3_m104
from morphology.gs_bound import gs_uniform_sample
import random
g = gs_uniform_sample(random.Random(3))
r = evaluate_t3_m104(g, f["t3_key"])
assert r["m_total"] >= 104 and r == evaluate_t3_m104(g, f["t3_key"])
print("SMOKE2 m104 m_total=%d families=%d t3_key=%s" % (
    r["m_total"], r["n_families"], f["heldout_t3"]["t3_key_id"][:24]))
PY
$ZOO_PY - "$ZOO_ROOT" <<'PY'
import hashlib, json, os, shutil, subprocess, sys, tempfile
ROOT = sys.argv[1]
FN = "GRAND_SEARCH_R2_FREEZE.json"
# tiny pinned-impl GSA6_ALL run -> NaN-fix live read (holdout_mae_t1 finite)
tmp = tempfile.mkdtemp(prefix="gs2smoke_")
try:
    rdir = os.path.join(tmp, "r")
    shutil.copytree(ROOT, rdir, ignore=shutil.ignore_patterns(
        "results", "logs", "archives", "manifests", "__pycache__"))
    for d in ("results", "logs", "archives", "manifests/receipts"):
        os.makedirs(os.path.join(rdir, d), exist_ok=True)
    spec = {"task_id": "SMOKE2fix", "base_arm": "GSA6_ALL", "seed": 11,
            "t0_budget": 243, "n0": 81,
            "freeze_sha256": hashlib.sha256(
                open(os.path.join(rdir, FN), "rb").read()).hexdigest()}
    sp = os.path.join(rdir, "spec.json")
    json.dump(spec, open(sp, "w"), sort_keys=True)
    p = subprocess.run(
        [sys.executable, os.path.join(rdir, "hpc", "gs_run.py"),
         rdir, "GSA6_ALL", "11", sp],
        capture_output=True, text=True, cwd=rdir,
        env=dict(os.environ, GS_RUN_PREFIX="GS_R2_",
                 GS_FREEZE_NAME=FN))
    assert p.returncode == 0, p.stderr[-600:]
    d = json.load(open(os.path.join(
        rdir, "results", "GS_R2_SMOKE2fix.json")))
    levers = d["revival_levers"]
    assert levers == {"dedup_promotion": True, "novelty_gate": True,
                      "surrogate_cumulative": True}, levers
    st = d["surrogate_stats"]
    assert st and st.get("holdout_mae_t1") is not None, \
        "no holdout_mae_t1 recorded"
    import math
    assert math.isfinite(st["holdout_mae_t1"]), \
        "GSA5_HOLDOUT_MAE_NAN regression: %r" % st["holdout_mae_t1"]
    print("SMOKE2 NaN-fix OK holdout_mae_t1=%.6f n_retrains=%d "
          "n_train_t0=%d distinct=%d" % (
              st["holdout_mae_t1"], st.get("n_retrains", 0),
              st.get("n_train_t0", 0),
              d["distinct_t2_viable_phenotypes"]))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
PY
echo "SMOKE2 OK freeze=${GS_FREEZE_SHA:-unset} host=$(hostname -s)"
