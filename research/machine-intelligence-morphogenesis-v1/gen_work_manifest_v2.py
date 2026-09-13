#!/usr/bin/env python3
"""Regenerate GMI_WORK_MANIFEST_V1.json for the RV-377-118 distributed batch.

Preserves claims and done-marks by unit_id, so re-running is safe while machines are working.
Sizing is MEASURED: a B1 recovery at 20 000 evaluations took 1 869 s wall on this container
(RV-377-113 recorded the 6.8x miss against the earlier linear projection), so 20 000 evals is
budgeted at 1 900 core-seconds rather than the old 1 500.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "GMI_WORK_MANIFEST_V1.json")
SEC_20K = 1900
FREEZE = "RV-377-118"
U = []


def add(uid, lane, klass, sec, title, cmd, receipt, frozen=True, revival=FREEZE, note=""):
    U.append({"unit_id": uid, "lane": lane, "class": klass, "est_core_seconds": sec,
              "title": title, "cmd": cmd, "receipt": receipt, "frozen": frozen,
              "revival_id": revival, "note": note, "claim": None, "done": None})


# ---- Lane A: LUNARC, the protected K4 V5 run -------------------------------------------
add("U-A001", "RV118-A", "hpc", 264 * 95000,
    "protected K4 V5: 264-task array at budget 1e6, beacon-gated",
    ["bash", "hpc/gmi_k4_submit.py", "--render", "--account", "lu2026-2-51",
     "--partition", "lu48", "--array", "0-263"],
    "microscopes/results/K4V5_{HOST}_*.json",
    note="Beacon FIRST: python3 hpc/gmi_k4_beacon_v5.py. No protected task may execute "
         "before GMI_K4_PUBLIC_BEACON_V5.json exists. Discharges RV-377-107 Q4.")

# ---- Lane B: laptop billy, multi-seed replication of G15 step (ii) ---------------------
for s in range(1, 10):
    add(f"U-B{s:03d}", "RV118-B", "medium", SEC_20K,
        f"B1 neutral search, E_sym5, seed {s} (G15 step ii replication)",
        ["python3", "-u", "-m", "gmi_microscope.b1", str(s), "20000", "E_sym5",
         f"logs/b1_E_sym5_s{s}_{{HOST}}.log", "V41_G15_REPLICATE_{HOST}"],
        f"microscopes/results/STAGE_B1_V41_G15_REPLICATE_{{HOST}}_E_sym5_S{s}.json",
        note="Score the recovered DENSE carrier under ALL SIX interventions and against the "
             "best constant 0.7917 in fx units. Single-intervention numbers are not verdicts.")

# ---- Lane C: laptop old, CP1 ablation extension ----------------------------------------
KINDS = ["ABSTAIN", "AFFINE", "CLOSEDFORM", "CONST", "DENSE", "EDGE", "EVIDENCE", "GATE",
         "GRAD", "INSERT", "KVSTORE", "LINEAR", "LOOKUP", "MATERIALIZE", "MORPH_RULE",
         "NEAREST", "NONLIN", "NONLIN1", "NOUPDATE", "PLACE", "PMUTATE", "PROGEXEC",
         "PROGRAM", "ROLLBACK", "SCORESELECT", "SEARCH", "SELECT", "SHADOW", "SUM",
         "TABLE", "VERIFY", "VERIFYTAB", "VERSIONED"]
n = 0
for eco in ("E_smooth1", "E_smooth3", "E_sym5"):
    for k in KINDS:
        n += 1
        add(f"U-C{n:03d}", "RV118-C", "medium", SEC_20K,
            f"CP1 ablation: drop {k}, ecology {eco}",
            ["python3", "-u", "-c",
             f"from gmi_microscope import primitive_ablation as pa;"
             f"import json;r=pa.run_one('{k}','{eco}',0,20000);print(json.dumps(r))"],
            f"microscopes/results/STAGE_B1_ABL_{k}_{eco}_S0.json",
            note="Extends RV-377-110 past the E_wit1-only scope reduction recorded in RV-377-113.")

# ---- Lane D: either laptop, DG-12 completion -------------------------------------------
for m in ("axis_a", "b1x", "b2_common", "b2_depth", "b2_norm", "b2_prenorm",
          "e1_cp", "e1_iql", "e1_lmhm", "e1_vgsc", "e1_vlc", "refine_f"):
    add(f"U-D-{m}", "RV118-D", "tiny", 120,
        f"DG-12 degeneracy audit of {m}",
        ["python3", "-u", "-c",
         f"from gmi_microscope import degeneracy_audit as da;"
         f"print(da.audit_module('{m}', host='{{HOST}}'))"],
        f"microscopes/results/STAGE_DG12_COMPLETION_{m}_{{HOST}}.json",
        note="audit_module() implemented in gmi_microscope/degeneracy_audit.py (RV-377-118 Lane D); "
             "prediction D1 and the adjudication rule are frozen in "
             "GMI_DG12_COMPLETION_RV_377_118D_FREEZE.md before any run. The module list is "
             "RV-377-112's declared uncovered set.", frozen=True)

old = {}
if os.path.exists(OUT):
    for u in json.load(open(OUT)).get("units", []):
        old[u["unit_id"]] = u
for u in U:
    o = old.get(u["unit_id"])
    if o:
        u["claim"], u["done"] = o.get("claim"), o.get("done")

m = {"schema": "GMIWorkManifestV1", "branch": "claude/gmi-d0-d1-research-dnbp8i",
     "freeze_record": FREEZE,
     "freeze_rule": "gmi_work.py run REFUSES any unit with frozen=false. The revival record "
                    "must be committed before the run, per the #373 protocol.",
     "collision_defence": "every receipt path carries {HOST}; claims prevent duplicated work, "
                          "host-keying prevents corruption. A receipt collision has already "
                          "destroyed two committed receipts in this programme (RV-377-078).",
     "machines_declared": ["container (this remote session, 4 cores, saturated)",
                           "laptop billy", "laptop old",
                           "lunarc (SLURM, account lu2026-2-51, partition lu48)"],
     "units": U}
json.dump(m, open(OUT, "w"), indent=1, sort_keys=True)
cls = {}
for u in U:
    cls.setdefault(u["class"], []).append(u)
print(f"wrote {len(U)} units")
for c, v in sorted(cls.items()):
    fr = sum(1 for x in v if x["frozen"])
    print(f"  {c:8} {len(v):4d} units  {fr:4d} frozen  "
          f"{sum(x['est_core_seconds'] for x in v)/3600:8.1f} core-hours")
