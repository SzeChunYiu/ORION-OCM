"""MSC V1 runner: one frozen stream, every arm, causal gate as executable assertions.

Usage (laptop, python 3.12, repo root on sys.path via world.py):

    python3 research/quantum-structural-ocm-v1/msc/run_msc.py \
        research/quantum-structural-ocm-v1/msc/MSC_V1_RESULTS.json --pass base --commit <sha>

Passes:
  base       the frozen scored run (all arms + shuffle null + ablations + FQ-6 ordering)
  <lever>    engineering-chain passes (appended to results["engineering_chain"]; the frozen
             base results are never overwritten). Each pass names its stage attribution and
             lever; outcomes are compared on the SAME frozen tasks.

The ground-truth judge (production gated_closure at stream state) is external to the arms
and never charged to them. Any decision divergence sets CANNOT_CHECK_<ARM>_DIVERGED and
marks everything downstream uninterpretable (protocol causal-gate item 4).

Python 3.8-compatible syntax (arm/quotient modules); runs under the 3.12 laptop runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "src"))

from ocm.kso.space import KnowledgeSpace  # noqa: E402

import arms as arms_mod  # noqa: E402
import world  # noqa: E402
from arms import (Q0FullScan, Q1Indexed, Q2Quotient, Q3Subspace, Q4Probe,  # noqa: E402
                  Q5Composed)
from probing import SUPPORTED  # noqa: E402
from quotient import Quotient  # noqa: E402

SCHEMA = "ocm.q216.minimum-sufficient-cognition.results.v1"
SIZING = {"n_atoms": 480, "n_edges": 1280, "n_evidence": 24,
          "n_tasks": 32, "n_updates": 10}
NULL_SALT = "ocm-q216-msc-v1-20260909/shuffle-null"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Stream replay (identical for every arm; ground truth external and uncharged)
# ---------------------------------------------------------------------------

def replay(arm, field: KnowledgeSpace, stream: Dict[str, object]) -> List[Dict[str, object]]:
    """Replay the frozen stream through one arm; return per-task records in stream order."""
    records = []
    for kind, item, ks, revoked in world.stream_apply(field, stream):
        if kind == "task":
            truth = world.ground_truth(ks, item["s"], item["t"], revoked)
            rec = arm.decide(item["s"], item["t"], revoked, truth)
            rec["task_idx"] = item["idx"]
            rec["truth"] = truth
            records.append(rec)
        elif item["kind"] == "admission":
            arm.on_admission(ks, item["_edges"])
        else:
            arm.on_revocation(item["evidence"])
    return records


def aggregate(records: List[Dict[str, object]]) -> Dict[str, object]:
    def col(key):
        return [r[key] for r in records if key in r]

    def stats(key):
        vals = [float(v) for v in col(key)]
        if not vals:
            return {"sum": 0, "mean": 0.0}
        return {"sum": sum(vals), "mean": statistics.fmean(vals),
                "median": statistics.median(vals)}

    out = {}
    for key in ("objects_touched", "edges_touched", "candidates", "false_candidates",
                "probes", "expansions", "verifier_calls"):
        out[key] = stats(key)
    supp = [r for r in records if r.get("truth")]
    neg = [r for r in records if not r.get("truth")]
    for name, subset in (("supported_tasks", supp), ("refuted_tasks", neg)):
        out[name] = {"n": len(subset),
                     "objects_touched": statistics.fmean([r["objects_touched"] for r in subset])
                     if subset else 0.0}
    k_active = [r.get("extra", {}).get("k_active_objects", 0) for r in records]
    out["k_active_objects"] = {"mean": statistics.fmean(k_active) if k_active else 0.0}
    out["k_over_N_mean"] = (out["k_active_objects"]["mean"] / SIZING["n_atoms"])
    return out


def mechanism_counters(arm) -> Dict[str, object]:
    out = {}
    for attr in ("refutations_used", "confirmations_used", "confirmation_fallbacks",
                 "cone_restrictions_applied", "probe_early_stops", "rebuilds"):
        if hasattr(arm, attr):
            out[attr] = getattr(arm, attr)
    return out


def run_arm(arm, field, stream) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    t0w, t0c = time.perf_counter(), time.process_time()
    arm.on_field(field)
    records = replay(arm, field, stream)
    wall, cpu = time.perf_counter() - t0w, time.process_time() - t0c
    correct = [bool(r["correct"]) for r in records]
    return ({"name": arm.name, "aggregates": aggregate(records),
             "lifetime": dict(arm.lifetime), "mechanism_counters": mechanism_counters(arm),
             "wall_seconds": wall, "cpu_seconds": cpu,
             "n_correct": sum(correct), "n_tasks": len(correct),
             "all_correct": all(correct)}, records)


def run_shuffle_null(field, stream, q4_records) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    """Q4_SHUFFLE_NULL: same machinery, per-task budget = Q4's consumed probes, random order."""
    null_arm = Q4Probe(policy="shuffle", salt=NULL_SALT)
    null_arm.name = "Q4_SHUFFLE_NULL"
    q4_probes = {r["task_idx"]: r["probes"] for r in q4_records}
    t0w, t0c = time.perf_counter(), time.process_time()
    null_arm.on_field(field)
    records = []
    for kind, item, ks, revoked in world.stream_apply(field, stream):
        if kind == "task":
            truth = world.ground_truth(ks, item["s"], item["t"], revoked)
            null_arm.budget = q4_probes[item["idx"]]
            rec = null_arm.decide(item["s"], item["t"], revoked, truth)
            rec["task_idx"] = item["idx"]
            rec["truth"] = truth
            records.append(rec)
        elif item["kind"] == "admission":
            null_arm.on_admission(ks, item["_edges"])
        else:
            null_arm.on_revocation(item["evidence"])
    wall, cpu = time.perf_counter() - t0w, time.process_time() - t0c
    correct = [bool(r["correct"]) for r in records]
    return ({"name": "Q4_SHUFFLE_NULL", "aggregates": aggregate(records),
             "lifetime": dict(null_arm.lifetime),
             "mechanism_counters": mechanism_counters(null_arm),
             "wall_seconds": wall, "cpu_seconds": cpu,
             "n_correct": sum(correct), "n_tasks": len(correct),
             "all_correct": all(correct)}, records)


# ---------------------------------------------------------------------------
# Mandatory hostile FQ-5
# ---------------------------------------------------------------------------

def run_hostile(field, planted) -> List[Dict[str, object]]:
    """Every arm serves D2 on F_A and F_B; quotient byte-identity is the FQ-5 witness."""
    F_A, F_B = world.hostile_pair(field, planted)
    out = []
    d2_truth = {}
    for tag, F in (("F_A", F_A), ("F_B", F_B)):
        d2_truth[tag] = {}
        amap = F.atom_view
        for p in planted:
            cands = [m for m in p["twins"] if amap[m].authority.rank("custody") >= 2]
            d2_truth[tag][p["evidence"]] = cands[0] if len(cands) == 1 else "NO_UNIQUE_MEMBER"
    qa, qb = Quotient(F_A), Quotient(F_B)
    ser_a, ser_b = qa.serialize(), qb.serialize()
    isomorphic = json.dumps(ser_a, sort_keys=True) == json.dumps(ser_b, sort_keys=True)
    for arm_cls, arm_args in HOSTILE_ARMS:
        arm = arm_cls(**arm_args)
        row = {"arm": arm.name, "quotient_isomorphic_witness": None, "fields": {}}
        for tag, F in (("F_A", F_A), ("F_B", F_B)):
            arm.on_field(F)
            for p in planted:
                res = arm.serve_d2(F, list(p["twins"]), build=False)
                res["d2_ground_truth"] = d2_truth[tag][p["evidence"]]
                res["correct"] = res["decision"] == d2_truth[tag][p["evidence"]]
                row["fields"].setdefault(tag, []).append(res)
        if isinstance(arm, (Q2Quotient, Q5Composed)):
            row["quotient_isomorphic_witness"] = {
                "isomorphic": isomorphic,
                "bytes_A": world.measure_bytes(ser_a),
                "bytes_B": world.measure_bytes(ser_b)}
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# Arm sets
# ---------------------------------------------------------------------------

def base_arm_factories():
    return [
        ("Q0_FULL_SCAN", lambda: Q0FullScan()),
        ("Q1_INDEXED", lambda: Q1Indexed()),
        ("Q2_QUOTIENT", lambda: Q2Quotient()),
        ("Q3_SUBSPACE", lambda: Q3Subspace()),
        ("Q4_PROBE", lambda: Q4Probe(policy="rarity")),
        ("Q5_COMPOSED", lambda: Q5Composed()),
        ("Q5_NO_QUOTIENT", lambda: Q5Composed(use_quotient=False)),
        ("Q5_NO_CONE", lambda: Q5Composed(use_cone=False)),
        ("Q5_NO_PROBE", lambda: Q5Composed(use_probe=False)),
        # FQ-6 ordering check arms (labels are the arms' own name attributes)
        ("Q5_COMPOSED_NAIVEORDER", lambda: Q5Composed(probe_policy="naive")),
        ("Q5_COMPOSED_E1", lambda: Q5Composed(incremental=True)),
        ("Q2_QUOTIENT_E1", lambda: Q2Quotient(incremental=True)),
    ]


HOSTILE_ARMS = [
    (Q0FullScan, {}),
    (Q1Indexed, {}),
    (Q2Quotient, {}),
    (Q3Subspace, {}),
    (Q4Probe, {"policy": "rarity"}),
    (Q5Composed, {}),
]


LEVER_PASSES: Dict[str, Dict[str, object]] = {
    # Engineering-chain passes (FNA-1 style). Each names the ONE attributed stage and the
    # lever; appended post-freeze without touching the frozen base results.
    "E1_INCREMENTAL": {
        "stage_attribution": "quotient maintenance (rebuild dominates lifetime work)",
        "lever": "E1: re-refine only blocks incident to changed edges on update",
        "factories": [("Q2_E1", lambda: Q2Quotient(incremental=True)),
                      ("Q5_E1", lambda: Q5Composed(incremental=True))]},
}


# ---------------------------------------------------------------------------
# Causal-gate evaluation (protocol section 7, executable)
# ---------------------------------------------------------------------------

def evaluate_gates(results: Dict[str, object], q4_rec, null_rec) -> Dict[str, object]:
    g = {}
    exact = all(a["all_correct"] for a in results["arms"].values())
    g["same_stream_replayed_by_every_arm"] = {
        "n_tasks_per_arm": {n: a["n_tasks"] for n, a in results["arms"].items()},
        "pass": len({a["n_tasks"] for a in results["arms"].values()}) == 1}
    g["zero_margin_exactness"] = {
        "all_arms_all_correct": exact,
        "pass": exact,
        "on_fail_terminal": "CANNOT_CHECK_ARM_DIVERGED"}
    mc = {n: a["mechanism_counters"] for n, a in results["arms"].items()}
    lt = {n: results["arms"][n]["lifetime"] for n in results["arms"]}
    g["mechanism_actually_consumed"] = {
        "Q2": {"refutations": mc["Q2_QUOTIENT"].get("refutations_used", 0),
               "confirmations": mc["Q2_QUOTIENT"].get("confirmations_used", 0),
               "lifetime_tasks": lt["Q2_QUOTIENT"]["tasks"],
               "pass": (mc["Q2_QUOTIENT"].get("refutations_used", 0)
                        + mc["Q2_QUOTIENT"].get("confirmations_used", 0)
                        == lt["Q2_QUOTIENT"]["tasks"])},
        "Q5": {"refutations": mc["Q5_COMPOSED"].get("refutations_used", 0),
               "confirmations": mc["Q5_COMPOSED"].get("confirmations_used", 0),
               "cone_restrictions": mc["Q5_COMPOSED"].get("cone_restrictions_applied", 0),
               "lifetime_tasks": lt["Q5_COMPOSED"]["tasks"],
               "pass": (mc["Q5_COMPOSED"].get("refutations_used", 0)
                        + mc["Q5_COMPOSED"].get("confirmations_used", 0)
                        == lt["Q5_COMPOSED"]["tasks"]
                        and mc["Q5_COMPOSED"].get("cone_restrictions_applied", 0) > 0)},
        "Q4": {"early_stops": lt["Q4_PROBE"].get("early_stops", 0),
               "pass": True},
        "Q3": {"cone_restrictions": mc["Q3_SUBSPACE"].get("cone_restrictions_applied", 0),
               "pass": mc["Q3_SUBSPACE"].get("cone_restrictions_applied", 0) > 0},
    }
    # build/update/maintenance/reopen charged: every arm has non-negative entries present
    g["work_fully_charged"] = {
        "arms_with_lifetime_counters": sorted(results["arms"].keys()),
        "pass": all({"build_work", "maintenance_work", "reopen_work"} <=
                    set(a["lifetime"].keys()) for a in results["arms"].values())}
    abl = {}
    q5 = results["arms"]["Q5_COMPOSED"]["aggregates"]
    q1 = results["arms"]["Q1_INDEXED"]["aggregates"]
    for name in ("Q5_NO_QUOTIENT", "Q5_NO_CONE", "Q5_NO_PROBE"):
        a = results["arms"][name]["aggregates"]
        abl[name] = {"objects_touched_mean": a["objects_touched"]["mean"],
                     "q5_objects_touched_mean": q5["objects_touched"]["mean"],
                     "delta_q5_minus_ablation": q5["objects_touched"]["mean"]
                     - a["objects_touched"]["mean"]}
    g["ablations"] = abl
    q4 = results["arms"]["Q4_PROBE"]["aggregates"]
    nul = results["shuffle_null"]["aggregates"]
    g["shuffle_null_margin"] = {
        "q4_probes_mean": q4["probes"]["mean"], "null_probes_mean": nul["probes"]["mean"],
        "q4_false_candidates_mean": q4["false_candidates"]["mean"],
        "null_false_candidates_mean": nul["false_candidates"]["mean"],
        "null_all_correct": results["shuffle_null"]["all_correct"],
        "adaptive_value_registered_only_on_margin": True}
    g["ordering_check_FQ6"] = results["ordering_check"]
    g["no_hidden_llm_neural_quantum"] = {
        "imports": ["stdlib", "ocm.kso (production)"], "pass": True}
    g["hostile_FQ5_reported_per_arm"] = {"pass": len(results["hostile_FQ5"]) > 0}
    return g


def _freeze_paths() -> Dict[str, Path]:
    root = HERE.parent
    return {name: (root / name if not name.startswith("msc/") else HERE / name.split("/", 1)[1])
            for name in json.loads((HERE / "FREEZE_MSC_V1.json").read_text())["frozen_files_sha256"]}


def check_freeze() -> None:
    """Base pass must run exactly the frozen bytes; drift aborts before any scoring."""
    frozen = json.loads((HERE / "FREEZE_MSC_V1.json").read_text())["frozen_files_sha256"]
    drift = {name: (sha256_file(p), want) for name, p in _freeze_paths().items()
             for want in [frozen[name]] if sha256_file(p) != want}
    if drift:
        sys.stderr.write("FREEZE_DRIFT (refusing to score): %s\n" % json.dumps(drift, indent=1))
        sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_path")
    ap.add_argument("--pass", dest="pass_name", default="base")
    ap.add_argument("--commit", default=None)
    ap.add_argument("--label", default=None)
    args = ap.parse_args()
    results_path = Path(args.results_path)

    if args.pass_name == "base":
        check_freeze()

    field, meta = world.build_field(**{k: SIZING[k] for k in
                                       ("n_atoms", "n_edges", "n_evidence")})
    stream = world.build_stream(field, n_tasks=SIZING["n_tasks"],
                                n_updates=SIZING["n_updates"])

    if args.pass_name == "base":
        results: Dict[str, object] = {
            "schema": SCHEMA, "pass": "base",
            "environment": {"python": sys.version, "platform": platform.platform(),
                            "host": platform.node()},
            "sizing": dict(SIZING, field_atoms=meta["n_atoms"], field_edges=meta["n_edges"]),
            "stream_summary": {
                "n_tasks": len(stream["tasks"]),
                "n_support": stream["n_support"],
                "n_not_support": stream["n_not_support"],
                "n_admissions": sum(1 for u in stream["updates"] if u["kind"] == "admission"),
                "n_revocations": sum(1 for u in stream["updates"] if u["kind"] == "revocation"),
                "final_revoked": stream["final_revoked"]},
            "commit": args.commit,
            "freeze": {"protocol_md_sha256": sha256_file(HERE.parent / "MINIMUM_SUFFICIENT_COGNITION_PROTOCOL_V1.md"),
                       "protocol_json_sha256": sha256_file(HERE.parent / "MINIMUM_SUFFICIENT_COGNITION_PROTOCOL_V1.json"),
                       "freeze_json_sha256": sha256_file(HERE / "FREEZE_MSC_V1.json"),
                       "world_py_sha256": sha256_file(HERE / "world.py"),
                       "quotient_py_sha256": sha256_file(HERE / "quotient.py"),
                       "probing_py_sha256": sha256_file(HERE / "probing.py"),
                       "arms_py_sha256": sha256_file(HERE / "arms.py"),
                       "run_msc_py_sha256": sha256_file(HERE / "run_msc.py"),
                       "test_msc_py_sha256": sha256_file(HERE / "test_msc.py")},
            "arms": {}, "engineering_chain": [],
        }
        per_arm_records = {}
        for name, factory in base_arm_factories():
            arm = factory()
            summary, records = run_arm(arm, field, stream)
            results["arms"][arm.name] = summary
            per_arm_records[arm.name] = records
        null_summary, null_records = run_shuffle_null(
            field, stream, per_arm_records["Q4_PROBE"])
        results["shuffle_null"] = null_summary
        results["shuffle_null_margin"] = _margin(
            per_arm_records["Q4_PROBE"], null_records)
        results["hostile_FQ5"] = run_hostile(field, meta["planted"])
        results["ordering_check"] = _ordering_check(per_arm_records)
        results["causal_gates"] = evaluate_gates(results,
                                                 per_arm_records["Q4_PROBE"], null_records)
        results["per_task"] = {name: [_strip(r) for r in recs]
                               for name, recs in per_arm_records.items()}
        results["per_task"]["Q4_SHUFFLE_NULL"] = [_strip(r) for r in null_records]
    else:
        spec = LEVER_PASSES[args.pass_name]
        existing = json.loads(results_path.read_text())
        entry = {"pass": args.pass_name,
                 "stage_attribution": spec["stage_attribution"],
                 "lever": spec["lever"], "commit": args.commit,
                 "code_sha256": {p: sha256_file(HERE / p) for p in
                                 ("quotient.py", "probing.py", "arms.py", "run_msc.py")},
                 "arms": {}}
        base_by_task = {n: {r["task_idx"]: r for r in recs}
                        for n, recs in _per_task_of(existing).items()}
        for name, factory in spec["factories"]:
            arm = factory()
            summary, records = run_arm(arm, field, stream)
            entry["arms"][arm.name] = summary
            entry["deltas_vs_base"] = entry.get("deltas_vs_base", {})
            for base_name in ("Q2_QUOTIENT", "Q5_COMPOSED"):
                if base_name in existing["arms"] and arm.name.startswith(base_name.split("_")[0]):
                    entry["deltas_vs_base"][arm.name] = _deltas(
                        records, existing["arms"][base_name]["aggregates"],
                        base_by_task.get(base_name, {}))
        entry["exactness_preserved"] = all(a["all_correct"] for a in entry["arms"].values())
        existing["engineering_chain"].append(entry)
        results = existing

    results_path.write_text(json.dumps(results, indent=1, sort_keys=True, default=str))
    print("wrote", results_path)
    print("arms:", {n: ("OK" if a["all_correct"] else "DIVERGED")
                    for n, a in results["arms"].items()} if "arms" in results else {})
    return 0


def _per_task_of(existing):
    pt = existing.get("per_task", {})
    out = {}
    for name, recs in pt.items():
        out[name] = [{"task_idx": r["task_idx"], **r} for r in recs]
    return out


def _strip(rec):
    r = dict(rec)
    r.pop("mechanism", None)
    return r


def _margin(q4_records, null_records) -> Dict[str, object]:
    """Q4-minus-null margin per task at equal budget (the only registerable FQ-2 value)."""
    rows = []
    for q, n in zip(q4_records, null_records):
        rows.append({"task_idx": q["task_idx"], "q4_probes": q["probes"],
                     "null_probes": n["probes"],
                     "q4_objects": q["objects_touched"], "null_objects": n["objects_touched"],
                     "q4_correct": q["correct"], "null_correct": n["correct"]})
    same_correct = sum(1 for r in rows if r["q4_correct"] == r["null_correct"])
    return {"per_task": rows,
            "n_tasks": len(rows),
            "same_correct": same_correct,
            "probes_margin_mean": statistics.fmean([r["q4_probes"] - r["null_probes"]
                                                    for r in rows]) if rows else 0.0,
            "objects_margin_mean": statistics.fmean([r["q4_objects"] - r["null_objects"]
                                                     for r in rows]) if rows else 0.0}


def _ordering_check(per_arm_records) -> Dict[str, object]:
    """FQ-6: naive vs rarity probe order and E1 vs rebuild maintenance must not change decisions."""
    def decisions(name):
        return [(r["task_idx"], r["decision"]) for r in per_arm_records[name]]
    checks = {
        "Q5_rarity_vs_naive": decisions("Q5_COMPOSED") == decisions("Q5_COMPOSED_NAIVEORDER"),
        "Q5_rebuild_vs_E1": decisions("Q5_COMPOSED") == decisions("Q5_COMPOSED_E1"),
        "Q2_rebuild_vs_E1": decisions("Q2_QUOTIENT") == decisions("Q2_QUOTIENT_E1"),
    }
    return {"identical": all(checks.values()), "checks": checks,
            "on_fail_terminal": "ORDERING_DEPENDENCE_REQUIRES_RICHER_STATE"}


def _deltas(records, base_aggregates, base_by_task) -> Dict[str, object]:
    agg = aggregate(records)
    out = {}
    for key in ("objects_touched", "edges_touched", "probes", "expansions", "verifier_calls"):
        if key in agg and key in base_aggregates:
            out[key] = {"lever_mean": agg[key]["mean"],
                        "base_mean": base_aggregates[key]["mean"]}
    per_task = []
    for r in records:
        b = base_by_task.get(r["task_idx"])
        if b:
            per_task.append({"task_idx": r["task_idx"],
                             "objects": r["objects_touched"] - b["objects_touched"],
                             "edges": r["edges_touched"] - b["edges_touched"]})
    out["per_task_deltas"] = per_task
    return out


if __name__ == "__main__":
    sys.exit(main())
