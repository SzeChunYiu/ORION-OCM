#!/usr/bin/env python3
"""Generate GMI_WORK_MANIFEST_V1.json. Reproducible: re-running preserves claims and done-marks by unit_id.

Sizing is measured, not guessed: a B1 recovery run at 20 000 evaluations took ~1 200-1 500 s of CPU on the container
under contention, so 20 000 evals is budgeted at 1 500 core-seconds and scaled linearly. The exact microscopes are
seconds (dn_serve_law 6.0 s, smooth_dense_max 45.8 s, witness_dg7 80.9 s measured).

CLASSES map to machines, not to importance:
  tiny   < 2 min      any machine, including 'laptop old'
  small  < 15 min     either laptop
  medium < 2 h        a laptop overnight, or LUNARC
  large  < 12 h       LUNARC, or a laptop left running
  hpc    array job    LUNARC only
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "GMI_WORK_MANIFEST_V1.json")
ECOS = ["E_smooth1", "E_smooth3", "E_sym3", "E_sym5", "E_parity"]
SEC_PER_20K = 1500

U = []


def add(uid, lane, klass, sec, title, cmd, receipt, frozen, revival, note=""):
    U.append({"unit_id": uid, "lane": lane, "class": klass, "est_core_seconds": sec, "title": title,
              "cmd": cmd, "receipt": receipt, "frozen": frozen, "revival_id": revival, "note": note,
              "claim": None, "done": None})


# ---- LANE RV100x: B1 recovery across ALL FIVE registered ecologies, 3 seeds, 20k.
# Possible only since the harness repair of RV-377-089b (b1.main hardcoded 3 of 5 ecologies). E_sym3 seeds 0-2 are
# already running on the container as RV-377-100 and are NOT re-queued.
n = 0
for eco in ECOS:
    for seed in (0, 1, 2):
        if eco == "E_sym3":
            continue
        n += 1
        add(f"U-R{n:03d}", "RV100x", "medium", SEC_PER_20K,
            f"B1 recovery 20k, {eco}, seed {seed} (full-family exposure census)",
            ["python3", "-u", "-m", "gmi_microscope.b1", str(seed), "20000", eco,
             f"logs/b1_{eco}_s{seed}_{{HOST}}.log", "V40_B1_CENSUS_{HOST}"],
            f"microscopes/results/STAGE_B1_V40_B1_CENSUS_{{HOST}}_{eco}_S{seed}.json",
            False, None,
            "NEEDS FREEZE: extends RV-377-100's exposure question to every registered ecology. Freeze before running.")

# ---- LANE DG7: re-sweep the class-level negatives that are cheap exact microscopes.
add("U-D001", "DG7", "tiny", 90, "Coefficient-witness sweep, all 5 ecologies, full intervention family (re-run)",
    ["python3", "-u", "-m", "gmi_microscope.witness_dg7"],
    "microscopes/results/STAGE_B1_V31b_DG7_COEFFICIENT_WITNESS_ALL5.json", True, "RV-377-089b",
    "already executed on the container; queued so any machine can reproduce it bit-identically as a cross-host check")
add("U-D002", "DG7", "tiny", 50, "Parent-maximal dense sweep on E_smooth2/E_smooth/E_smooth3 (re-run)",
    ["python3", "-u", "-m", "gmi_microscope.smooth_dense_max"],
    "microscopes/results/STAGE_DE_SMOOTH_V30_DENSE_PARENT_MAXIMAL.json", True, "RV-377-088",
    "reproduction check; deterministic, so a differing receipt sha is itself a finding")
add("U-D003", "DG7", "tiny", 10, "N10 serve law exact graph predictors (re-run)",
    ["python3", "-u", "-m", "gmi_microscope.dn_serve_law"],
    "microscopes/results/STAGE_DN_V29_N10_SERVE_LAW.json", True, "RV-377-053",
    "reproduction check")

# ---- LANE DG8: the off-diagonal sample of A x d x p x F. THE headline HPC lane.
add("U-G001", "DG8", "hpc", 0, "Off-diagonal sample of A x d x p x F (design + freeze, then array)",
    ["python3", "-u", "-m", "gmi_microscope.dg8_offdiagonal"],
    "microscopes/results/STAGE_DG8_OFFDIAGONAL_{HOST}.json", False, None,
    "NEEDS DESIGN AND FREEZE FIRST. DG-8's own closure criterion requires a declared low-discrepancy sample and a "
    "stated hit probability registered BEFORE the run. The module does not exist yet. This unit is a placeholder so "
    "the lane is visible in status; it must not be claimed until frozen=true.")

# ---- LANE BUDGET: higher-budget recovery, the G15 note's 1e6 question.
for i, (eco, seed) in enumerate([(e, s) for e in ("E_sym3", "E_smooth1") for s in (0, 1)], 1):
    add(f"U-B{i:03d}", "BUDGET", "large", SEC_PER_20K * 10,
        f"B1 recovery 200k, {eco}, seed {seed} (budget axis)",
        ["python3", "-u", "-m", "gmi_microscope.b1", str(seed), "200000", eco,
         f"logs/b1_big_{eco}_s{seed}_{{HOST}}.log", "V41_B1_BIG_{HOST}"],
        f"microscopes/results/STAGE_B1_V41_B1_BIG_{{HOST}}_{eco}_S{seed}.json", False, None,
        "NEEDS FREEZE. E_smooth1 at 200k duplicates RV-377-084, already running on the container -- queue the E_sym3 "
        "pair first, since that is the ecology with exposure and therefore the one where budget can matter.")

prev = {}
if os.path.exists(OUT):
    for u in json.load(open(OUT))["units"]:
        prev[u["unit_id"]] = (u.get("claim"), u.get("done"))
for u in U:
    if u["unit_id"] in prev:
        u["claim"], u["done"] = prev[u["unit_id"]]

json.dump({
    "schema": "GMIWorkManifestV1",
    "branch": "claude/gmi-d0-d1-research-dnbp8i",
    "machines_declared": ["container (this remote session, 4 cores, currently saturated)",
                          "laptop billy", "laptop old", "lunarc (SLURM, account lu2026-2-51, partition lu48)"],
    "collision_defence": "every receipt path carries {HOST}; claims prevent duplicated work, host-keying prevents "
                         "corruption. Do not rely on the claim alone -- a receipt collision has already destroyed "
                         "two committed receipts in this programme (recorded alongside RV-377-078).",
    "freeze_rule": "gmi_work.py run REFUSES any unit with frozen=false. The revival record must be committed before "
                   "the run, per the #373 protocol.",
    "units": U,
}, open(OUT, "w"), indent=1, sort_keys=True)
print(f"wrote {OUT}: {len(U)} units")
for c in ("tiny", "small", "medium", "large", "hpc"):
    cu = [u for u in U if u["class"] == c]
    if cu:
        print(f'  {c:7s} {len(cu):3d} units, {sum(u["est_core_seconds"] for u in cu)/3600:7.2f} core-hours, '
              f'{sum(1 for u in cu if u["frozen"])} frozen')
