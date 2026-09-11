#!/usr/bin/env bash
#SBATCH -A lu2026-2-51
#SBATCH -p lu48
#SBATCH -J m2p3-scoredry
#SBATCH -t 00:20:00
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -o /projects/hep/fs12/scratch/scyiu-m2trav/logs/m2p3scoredry_%j.out
# Validates m2p3_score.py end-to-end on REAL data with a known answer: M2-P2's eight worlds,
# PARENT_GF_D4 (from the _gf runs) vs RESET (from the _ocm5 runs), assembled into the layout the
# scorer expects. Expected from the independent calibration (LUNARC 3599978): 7/8 pass the 50 %
# bar, hc08 fails, median ratio about -0.877. This touches no M2-P3 data.
set -euo pipefail
B=/projects/hep/fs12/scratch/scyiu-m2trav
PY=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
T=$B/tmp_scoredry; rm -rf $T; mkdir -p $T
for d in $B/runs/m2p2_M2P2_WORLD_*_gf; do
  w=$(basename "$d"); w=${w#m2p2_M2P2_WORLD_}; w=${w%_gf}
  o=$B/runs/m2p2_M2P2_WORLD_${w}_ocm5
  [ -f "$d/arm_PARENT_GF_D4.json" ] && [ -f "$o/arm_RESET.json" ] || continue
  mkdir -p "$T/m2p3_${w}_scored"
  cp "$d/arm_PARENT_GF_D4.json" "$o/arm_RESET.json" "$T/m2p3_${w}_scored/"
done
echo "assembled worlds: $(ls -d $T/m2p3_*_scored | wc -l)"
$PY $B/m2p3_score.py "$T" "$T/DRYRUN_RESULT.json"
$PY - <<'PYEOF'
import json
r=json.load(open("/projects/hep/fs12/scratch/scyiu-m2trav/tmp_scoredry/DRYRUN_RESULT.json"))
per=[(x["world"],x.get("ratio_minus_1"),x.get("holm"),x.get("passes_50pct_bar")) for x in r["per_world"]]
for p in sorted(per): print("  %-24s ratio %+.4f holm %.4f pass %s" % p)
print("scorer says: k=%d/%d terminal=%s median=%.4f" % (r["k_passing"], r["worlds_scored"], r["terminal"], r["median_ratio_minus_1"]))
exp_k, exp_fail = 7, "hc08-drawn-lot-b"
ok = r["k_passing"]==exp_k and not [x for x in r["per_world"] if x["world"]==exp_fail and x["passes_50pct_bar"]] and abs(r["median_ratio_minus_1"]+0.877)<0.01
print("VALIDATION", "PASS" if ok else "FAIL", "(expected k=7, hc08 failing, median about -0.877)")
PYEOF
