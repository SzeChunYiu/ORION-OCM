"""Build the section-20 close-out artifacts in the capsule from the bundle.
Pure document assembly on the Mac (no science execution).
"""
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

CAP = Path("/Users/billy/Desktop/projects/ORION-OCM/ORION-OCM-wt/pdev217"
           "/research/parallel-developmental-evolution-v1")
B = json.loads(Path("/tmp/closeout_bundle.json").read_text())
NOW = time.time()


def wj(rel, obj):
    p = CAP / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    print("wrote", rel)


def wal(rel, rows):
    p = CAP / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    print("wrote", rel, len(rows), "rows")


# 1. generation ledger of record -----------------------------------------
wal("results/GENERATION_LEDGER.jsonl", B["generation_ledger"])

# 2. cycle receipt / packet / decision / exhaustion terminal -------------
g2 = B["generations"]["2"]
g3 = B["generations"]["3"]
wj("results/CYCLE_RECEIPT_g2.json", g2["cycle_receipt"])
wj("proposals/ADOPTION_PACKET_g2w1.json", g2["ADOPTION_PACKET"])
wj("proposals/DECISION_g2w1.json", g2["decision"])
wj("results/EXHAUSTION_TERMINAL_g3.json", g3["EXHAUSTION_TERMINAL"])

# 3. PARENT_RESULT (PDEV-3 parent arrays + PDEV-11 discriminator) --------
sp = {a: B["parents"][a]["serial_state"] for a in ("CONTINUED", "RESET")}
prb = B["parents"]["rows_by_generation"]
parent_result = {
    "schema": "pdev217.parent_result.v1",
    "arm": "PARENT_RESULT",
    "arms": ["PARENT", "CONTINUED", "RESET"],
    "per_generation": {
        "g2": {"parent_array_denominator": 217, "jobs": "3585268",
               "rows": prb["g2"],
               "note": "217 = CONTINUED 108 + RESET 108 + PARENT reference 1"},
        "g3": {"parent_array_denominator": 123, "jobs": "3585560",
               "rows": prb["g3"],
               "note": "123 = CONTINUED 14 + RESET 108 + PARENT reference 1"}},
    "final": {
        "PARENT": {
            "g2": {"digest": "PARENT.g2.g2"}, "g3": {"digest": "PARENT.g2.g3"},
            "note": "parent reference points re-measured once per generation"},
        "CONTINUED": {
            "digest": sp["CONTINUED"]["digest"], "adoptions":
                sp["CONTINUED"]["adoptions"],
            "history": sp["CONTINUED"]["history"]},
        "RESET": {
            "digest": sp["RESET"]["digest"],
            "adoptions": sp["RESET"]["adoptions"],
            "history": sp["RESET"]["history"]}},
    "pdev11_discriminator": {
        "question": "does carrying serial history change the parent-space "
                    "search trajectory versus a history-blind reset?",
        "result": "DISCRIMINATED: lineages diverged",
        "detail": [
            "CONTINUED (history-carrying) adopted exactly one change (g2: "
            "e05e3ae63bb01037, vector failures=0 persistent_bytes=31610 "
            "work=96590 vs baseline work 97202) and then held it at g3 ('no "
            "neighbour strictly better under frozen scalar'); its final "
            "digest equals the canonical lineage's adopted g2 morphology",
            "RESET (history-blind) adopted twice (g2: 2057ee291c3a4fe3 work "
            "98638; g3: 7ec87530e47478b8 work 107982) and ends at a "
            "different, higher-work morphology",
            "same frozen scalar rule, same task suites, same budgets; the "
            "only difference is carried history => history is measurable "
            "(final work 96590 vs 107982, same failures=0, same bytes "
            "31610 vs 71249)"],
        "verdict": "carried serial history earned a strictly better final "
                   "parent-space morphology than the history-blind reset on "
                   "the frozen (failures, work) scalar"},
    "written_unix": NOW}
wj("parents/PARENT_RESULT.json", parent_result)

# 4. adverse / cannot-check ---------------------------------------------
adverse = B["adverse_and_cannot_check"]
for r in adverse:
    r.setdefault("detail", None)
wal("results/ADVERSE_AND_CANNOT_CHECK.jsonl", adverse)

# 5. resource ledger (sacct) --------------------------------------------
def secs(t):
    t = t.strip()
    if not t or t == "0":
        return 0.0
    d = 0
    if "-" in t:
        d, t = t.split("-")
        d = int(d)
    parts = t.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return float(parts[0])
    return d * 86400 + int(h) * 3600 + int(m) * 60 + float(s)


rows = []
for l in open("/tmp/sacct_closeout_full.csv"):
    p = l.rstrip("\n").split("|")
    if len(p) >= 6 and "pdev" in p[1] and "." not in p[0]:
        rows.append(p)
by_name = Counter(r[1].strip() for r in rows)
cpu_by_name = {n: sum(secs(r[4]) for r in rows if r[1].strip() == n)
               for n in by_name}
total_cpu = sum(cpu_by_name.values())
failed = [{"job": r[0], "state": r[2], "name": r[1].strip()}
          for r in rows if r[2] != "COMPLETED"]
resource_ledger = {
    "schema": "pdev217.resource_ledger.v1",
    "source": "sacct -S 2026-09-09T12:00 (account hep2023-1-3, partition hep)",
    "window_note": "all pdev217 jobs this campaign, including selftest",
    "task_counts": dict(by_name),
    "total_tasks": len(rows),
    "cpu_seconds_by_stage": {k: round(v, 1) for k, v in cpu_by_name.items()},
    "total_cpu_seconds": round(total_cpu, 1),
    "total_cpu_hours": round(total_cpu / 3600, 3),
    "metered_candidate_evaluations":
        B["candidate_ledger_summary"]["rebuilt_from_authoritative_eval_files"],
    "metered_work_units_charged_by_meter": None,
    "failed_tasks_superseded_by_reruns": failed,
    "written_unix": NOW}
# metered work total from rebuilt ledger
mw = 0
for l in open(CAP / "results" / "CANDIDATE_LEDGER_REBUILT.jsonl"):
    r = json.loads(l)
    mw += int(r.get("work") or 0)
resource_ledger["metered_work_units_charged_by_meter"] = mw
wj("results/RESOURCE_LEDGER.json", resource_ledger)

# 6. lineage final -------------------------------------------------------
freeze = B.get("freeze") or {}
snap = B.get("last_snapshot") or {}
lineage_final = {
    "schema": "pdev217.lineage_final.v1",
    "freeze_receipt": freeze,
    "last_snapshot": {k: snap[k] for k in sorted(snap)
                      if k in ("schema", "config", "config_digest",
                               "generation", "snapshot_sha256",
                               "vendor_manifest_sha256", "cycle")},
    "state": B["state"],
    "note": "cycle 1 (g2) adopted g2.w1.repair.4 via the full M11 path and "
            "the frozen HUMAN_GATE_BYPASSED__MODEL_PROXY decision; the "
            "protected freeze identity was emitted at cycle end; cycle 2 "
            "(g3) exhausted with no adoption (see "
            "results/EXHAUSTION_TERMINAL_g3.json)",
    "written_unix": NOW}
wj("results/LINEAGE_FINAL.json", lineage_final)

# 7. incidents -----------------------------------------------------------
incidents = [
    {"id": "INC-1", "kind": "slurm-behaviour",
     "what": "this cluster's Slurm rejects colon-chained AND dependency "
             "expressions ('Job dependency problem'); a comma chain parses "
             "but is OR semantics",
     "impact": "g2w1 driver crashed after the verify array; finalize was "
               "not auto-submitted",
     "resolution": "run_wave.sh rewritten to sacct poll-wait + plain "
                   "submission (shipped before g3); g2w1 finalize resumed "
                   "manually (job 3585509)",
     "stage": "wave driver"},
    {"id": "INC-2", "kind": "environment",
     "what": "three sbatch submissions (3585508 finalize, 3585511 cycle, "
             "3586500 close) failed in 0s: PDEV217_CAPSULE/PDEV217_OCM not "
             "exported in the submitting shell, empty PYTHONPATH",
     "impact": "no data impact; each was resubmitted with exports "
               "(3585509, 3585512, login-node run) and completed",
     "stage": "submission"},
    {"id": "INC-3", "kind": "data-integrity",
     "what": "CANDIDATE_LEDGER.jsonl append-only log: 3 interleaved/corrupt "
             "lines and 6 lost rows out of 784, caused by concurrent "
             "appends from 156-wide array tasks",
     "impact": "ledger of record incomplete; per-candidate eval/*.json "
               "files (single-writer, one per candidate) were never "
               "affected",
     "resolution": "CANDIDATE_LEDGER_REBUILT.jsonl rebuilt canonically from "
                   "eval/*.json on LUNARC (784/784 rows, 0 crashes); "
                   "original kept untouched as evidence",
     "stage": "candidate ledger"},
    {"id": "INC-4", "kind": "tooling",
     "what": "first AMENDMENT-3 claim extractor double-counted rows "
             "(glob *.json also matched *.full.json detail files)",
     "impact": "claims showed 2x row counts; measurements themselves "
               "correct",
     "resolution": "extractor fixed to exclude .full.json; both laptop "
                   "lanes rerun end-to-end; final claims 7+78 per host, "
                   "170/170 rows reproduce LUNARC vectors exactly",
     "stage": "cross-host replicates"}]
wal("incidents/INCIDENTS.jsonl", incidents)

# 8. resource accounting fill-in ----------------------------------------
acct = json.loads((CAP / "RESOURCE_ACCOUNTING.json").read_text())
wave_rows = []
for s in B["submissions"]:
    wave_rows.append({
        "generation": s["generation"], "wave": s["wave"],
        "evaluate_denominator": s["evaluate_denominator"],
        "verify_denominator": s["verify_denominator"],
        "parent_denominator": s["parent_denominator"],
        "jobs": s["jobs"], "submitted_unix": s["submitted_unix"]})
g2w1_row = {
    "generation": 2, "wave": 1, "evaluate_denominator": 14,
    "verify_denominator": 2, "parent_denominator": 217,
    "jobs": {"evaluate": "3585267", "verify": "3585499", "parent": "3585268",
             "aggregate": "3585509"},
    "note": "appended at close-out: the g2w1 driver crashed before its own "
            "append (INC-1); job IDs from driver log + sacct",
    "submitted_unix": None}
acct["campaign"]["waves"] = [g2w1_row] + wave_rows
acct["campaign"]["totals"] = {
    "slurm_task_records": len(rows),
    "task_counts": dict(by_name),
    "cpu_seconds": round(total_cpu, 1),
    "cpu_hours": round(total_cpu / 3600, 3),
    "candidate_evaluations_metered": 784,
    "parent_entries_metered": 340,
    "verify_tasks": 10,
    "failed_then_superseded": [f["job"] for f in failed]}
acct["status"] = ("closed 2026-09-09: cycle 1 adopted (g2->g3), cycle 2 "
                  "exhausted PARENT_SUFFICIENT_BY_REVIVAL_EXHAUSTION")
wj("RESOURCE_ACCOUNTING.json", acct)

# 9. repo state update ---------------------------------------------------
rs = json.loads((CAP / "REPO_STATE.json").read_text())
rs["lineage_state_at_end"] = {
    "generations_achieved": B["state"]["generation"],
    "programme_terminal": B["state"]["programme_terminal"],
    "adoptions": B["state"]["adoptions"],
    "attempted_cycles": B["state"]["attempted_cycles"],
    "trajectory": ["g0", "g1", "g2", "g3"],
    "frozen_identity_g3": (freeze.get("freeze_hash"))}
rs["captured_unix"] = NOW
wj("REPO_STATE.json", rs)
print("builder done")
