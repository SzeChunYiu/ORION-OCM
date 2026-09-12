#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p4-scoredry
#SBATCH -t 00:20:00
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p4scoredry_%j.out
# Validates m2p4_score.py end-to-end on REAL data with a known answer, BEFORE any scored arm runs.
# M2P4_STAGE3_FREEZE_V1 makes this a precondition: if the reproduction fails, the scorer is wrong
# and the study stops here.
#
# Inputs are M2-P2's eight worlds: PARENT_GF_D4 from the _gf runs, RESET from the _ocm5 runs,
# assembled into the m2p4_*_scored layout this scorer globs. Expected from the independent
# calibration (LUNARC 3599978, reproduced by M2-P3 at 3600816): 7/8 pass the 50 % bar, hc08 fails,
# median ratio about -0.877.
#
# This writes ONLY into its own tmp_scoredry_m2p4 tree. M2-P3's tmp_scoredry is never read,
# renamed or reused, and no M2-P3 or M2-P4 run data is touched.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
T=$B/tmp_scoredry_m2p4; rm -rf $T; mkdir -p $T
for d in $B/runs/m2p2_M2P2_WORLD_*_gf; do
  w=$(basename "$d"); w=${w#m2p2_M2P2_WORLD_}; w=${w%_gf}
  o=$B/runs/m2p2_M2P2_WORLD_${w}_ocm5
  [ -f "$d/arm_PARENT_GF_D4.json" ] && [ -f "$o/arm_RESET.json" ] || continue
  mkdir -p "$T/m2p4_${w}_scored"
  cp "$d/arm_PARENT_GF_D4.json" "$o/arm_RESET.json" "$T/m2p4_${w}_scored/"
done
echo "assembled worlds: $(ls -d $T/m2p4_*_scored | wc -l)"
# the scorer under test, bound by sha in M2P4_STAGE3_FREEZE_V1
$PY -c "import hashlib,sys;print('scorer sha256:',hashlib.sha256(open('$B/m2p4_score.py','rb').read()).hexdigest())"
$PY $B/m2p4_score.py "$T" "$T/DRYRUN_RESULT.json"
$PY - <<'PYEOF'
import json
r = json.load(open("/projects/hep/fs12/scratch/scyiu-m2trav/tmp_scoredry_m2p4/DRYRUN_RESULT.json"))
scored = [x for x in r["per_world"] if "p_effect" in x]
for x in sorted(scored, key=lambda z: z["world"]):
    print("  %-24s n %3d ratio %+.4f holm %.5f pass %s" %
          (x["world"], x["n"], x["ratio_minus_1"], x["holm"], x["passes_50pct_bar"]))
print("scorer says: k=%d/%d terminal=%s median=%s" %
      (r["k_passing"], r["worlds_scored"], r["terminal"], r["median_ratio_minus_1"]))
print("point_prediction field:", r["point_prediction"])
EXP_K, EXP_FAIL, EXP_MED = 7, "hc08-drawn-lot-b", -0.877
seen = {x["world"] for x in scored}
checks = {
  "k_passing==7":        r["k_passing"] == EXP_K,
  "worlds_scored==8":    r["worlds_scored"] == 8,
  "hc08_present":        EXP_FAIL in seen,
  "hc08_fails":          any(x["world"] == EXP_FAIL and not x["passes_50pct_bar"] for x in scored),
  "median~-0.877":       r["median_ratio_minus_1"] is not None and abs(r["median_ratio_minus_1"] - EXP_MED) < 0.01,
  "no_point_prediction": r["point_prediction"] == "NONE_REGISTERED_median_is_descriptive_only",
}
for name, ok in checks.items():
    print("  %-22s %s" % (name, "ok" if ok else "MISMATCH"))
# distinct exit codes: 0 reproduced, 3 ran but disagreed. A crash exits non-zero on its own and is
# never read as agreement -- "could not check" must not become "checked and fine".
if all(checks.values()):
    print("VALIDATION PASS -- scorer reproduces the known answer; the scored run may proceed")
else:
    print("VALIDATION FAIL -- scorer does NOT reproduce the known answer; the scored run must NOT run")
    raise SystemExit(3)
PYEOF
