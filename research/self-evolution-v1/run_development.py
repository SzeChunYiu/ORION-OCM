"""Run a new DEVELOPMENT-only M11 trajectory on pinned real ladder components."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import resource
import shutil
import time

from evolution import EvolutionCell, digest
from intake import load_cases, ingest_case
import ladder_adapter as A
from ocm.selfmodel.diagnose import diagnose
from ocm.selfmodel.govern import ExternalAdopter, monitor

HERE = Path(__file__).resolve().parent
PROTOCOL = {
    "schema": "ocm.self_evolution.actual_source_development.v1",
    "resource_keys": ["work", "persistent_bytes"],
    "budgets": {"work": 100_000_000, "persistent_bytes": 100_000_000},
    "resource_aggregation": {"work": "sum", "persistent_bytes": "max"},
    "probe_limit": 10, "proposal_budget": 10, "adoption_budget": 3,
    "quality_margin": 0,
    "edit_classes": {"route_s": ["C1"], "route_d": ["C1"]},
    "origin": "EXISTING_ALTERNATIVES_SELECTED_BY_MACHINE",
    "protected": "NOT_RUN",
}


def cycles():
    return [
        {"source": "F3", "dev": [A.task("s", 3, 0, "probe")],
         "shadow": {"target": [A.task("s", 3, 1, "shadow")],
                    "preservation": [A.task("s", 1, 2, "preserve")]},
         "fresh": [A.task("s", 3, 10, "restart")]},
        {"source": "F4", "dev": [A.task("d", 1, 0, "probe")],
         "shadow": {"target": [A.task("d", 2, 1, "shadow")],
                    "preservation": [A.task("s", 3, 3, "preserve")]},
         "fresh": [A.task("d", 3, 0, "restart")]},
        {"source": "F2", "dev": [A.task("s", 10, 4, "probe")],
         "shadow": {"target": [A.task("s", 30, 5, "shadow")],
                    "preserve_d": [A.task("d", 1, 1, "preserve")],
                    "preserve_s": [A.task("s", 3, 6, "preserve")]},
         "fresh": [A.task("s", 20, 11, "restart")]},
    ]


def registered_packet():
    return {"protocol": PROTOCOL, "initial_config": A.INITIAL_CONFIG,
            "allowed_edits": A.ALLOWED, "candidates": [asdict(c) for c in A.candidates()],
            "cycles": cycles(),
            "parent": "same finite ordered search = conventional AutoML parent by construction",
            "additional_parents": "random policy replay diagnostic; other search/neural parents NOT_RUN",
            "interpretation": "three attempted cycles; count only earned admissions, never force g3"}


def execute(out):
    if out.exists():
        raise ValueError("choose a new output path; previous attempts are immutable")
    out.mkdir(parents=True)
    start, cpu = time.perf_counter_ns(), time.process_time_ns()
    packet = registered_packet()
    (out / "registered_packet.json").write_text(json.dumps(packet, indent=2) + "\n")
    A.TRACE_SINK = out / "external_raw_traces"
    cell = EvolutionCell(out / "machine", A.INITIAL_CONFIG,
                         allowed_edits=A.ALLOWED, protocol=PROTOCOL)
    cases = load_cases()
    initial = []
    for case in cases:
        failure = ingest_case(cell.self_model, case)
        initial.append({"case_id": case["case_id"], "diagnosis": asdict(diagnose(failure)),
                        "uncertainty": failure.uncertainty})
    cell._save()
    # Host-owned mapping/adopter stay outside the finite proposal policy.
    audit = json.loads((HERE / "sources" / "EXTERNAL_AUDIT_MANIFEST.json").read_text())
    by_source = {r["external_failure_key"]: r["case_id"] for r in audit["entries"]}
    by_id = {c["case_id"]: c for c in cases}
    adopter = ExternalAdopter("external-host-development-policy-v1")
    records, fresh_rows = [], []
    for number, phase in enumerate(cycles()):
        case = by_id[by_source[phase["source"]]]
        observation = {"ecology": "development", "failure_id": case["case_id"],
                       "task_id": phase["dev"][0]["task_id"],
                       "observed": "pinned numeric development observation",
                       "expected": "exact quality and registered resource frontier",
                       "uncertainty": "UNKNOWN", "source_observation": case,
                       "resources": {}}
        before = cell.config
        receipt = cell.develop(observation, A.candidates(), dev_tasks=phase["dev"],
                               shadow_suites=phase["shadow"], runner=A.runner,
                               external_adopter=adopter)
        records.append(receipt)
        (out / f"cycle-{number}.json").write_text(json.dumps(receipt, indent=2) + "\n")
        cell = EvolutionCell(out / "machine", A.INITIAL_CONFIG,
                             allowed_edits=A.ALLOWED, protocol=PROTOCOL)
        # Fresh causal use is measured after a real OCM/M11 cold restart.
        # The old config receives full recomputation as a compensated ablation.
        fresh = {"cycle": number, "generation": cell.generation,
                 "current": A.runner(cell.config, phase["fresh"]),
                 "compensated_previous": A.runner(before, phase["fresh"])}
        fresh["retained_frontier_improvement"] = cell._dominates(fresh["current"], fresh["compensated_previous"])
        fresh["resource_noninferiority"] = all(
            fresh["current"]["resources"][k] <= fresh["compensated_previous"]["resources"][k]
            for k in PROTOCOL["resource_keys"])
        ratios = [fresh["current"]["resources"][k] / max(1, fresh["compensated_previous"]["resources"][k])
                  for k in PROTOCOL["resource_keys"]]
        fresh["monitor"] = monitor([{
            "target_success": fresh["current"]["success"] / fresh["current"]["n"],
            "preservation_success": int(fresh["current"]["preservation_violations"] == 0),
            "authority_violations": fresh["current"]["preservation_violations"],
            "resource_ratio": max(ratios),
        }], target_threshold=1.0, preservation_min=1.0)
        fresh["monitor_scope"] = "quality, preservation and measured resource ratio; fresh numeric prediction calibration not gated"
        fresh["resource_prediction_calibration"] = {
            k: {"predicted_per_task_delta": receipt.get("prediction", {}).get("resource_delta", {}).get(k),
                "measured_per_task_delta": (fresh["current"]["resources"][k] - fresh["compensated_previous"]["resources"][k]) / fresh["current"]["n"]}
            for k in PROTOCOL["resource_keys"]}
        if receipt["terminal"] == "DEVELOPMENT_CHANGE_ADOPTED" and (
                fresh["monitor"]["rollback_recommended"] or not fresh["resource_noninferiority"]):
            fresh["external_monitor_rollback"] = cell.rollback_latest()
        cell.state["seen_tasks"].extend(t["task_id"] for t in phase["fresh"])
        cell.state["seen_semantic_ids"].extend(t["semantic_id"] for t in phase["fresh"])
        cell.self_model.record("host-fresh-development-monitor:" + str(number), fresh)
        cell._save()
        fresh_rows.append(fresh)
        (out / f"fresh-{number}.json").write_text(json.dumps(fresh, indent=2) + "\n")
        print(json.dumps({"cycle": number, "generation": cell.generation,
                          "terminal": receipt["terminal"],
                          "fresh_improvement": fresh["retained_frontier_improvement"]}), flush=True)
    # Actual data rollback on a cloned host store, preserving the evolved arm.
    rollback = {"status": "NO_ADOPTION_TO_ROLL_BACK"}
    if cell.generation:
        shutil.copytree(out / "machine", out / "rollback_audit")
        copy_cell = EvolutionCell(out / "rollback_audit", A.INITIAL_CONFIG,
                                  allowed_edits=A.ALLOWED, protocol=PROTOCOL)
        rollback = copy_cell.rollback_latest()
        restored = EvolutionCell(out / "rollback_audit", A.INITIAL_CONFIG,
                                  allowed_edits=A.ALLOWED, protocol=PROTOCOL)
        rollback["restart_generation"] = restored.generation
        rollback["replay_identical"] = restored.runtime.replay()["identical"]
    frozen = cell.freeze_for_protected(
        comparator={"registered": "matched adaptive parent suite", "status": "NOT_IMPLEMENTED_ALL_PARENTS"},
        budgets=PROTOCOL["budgets"], protected_protocol_hash=digest({"status": "E0_NOT_READY", "packet": packet}))
    total_work = sum(r["measured_runner_cost"]["work"] for r in records)
    total_work += sum(r[a]["resources"]["work"] for r in fresh_rows for a in ("current", "compensated_previous"))
    result = {"status": "DEVELOPMENT_ONLY", "initial_diagnoses": initial,
              "actual_adopted_generations": cell.generation,
              "attempted_cycles": len(records), "config": cell.config,
              "cycles": [{k: r.get(k) for k in ("cycle", "generation_before", "generation_after", "terminal", "diagnosis", "challengers_evaluated", "measured_runner_cost", "peak_runner_resources", "prediction_calibration")} for r in records],
              "fresh": fresh_rows, "rollback": rollback, "freeze": frozen,
              "terminal": "NO_MULTI_GENERATION_IMPROVEMENT" if cell.generation < 3 else "THREE_DEVELOPMENT_ADOPTIONS_ONLY",
              "parent_terminal": "AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION",
              "further_parent_trajectories": "NOT_RUN", "protected_execution": "NOT_RUN",
              "invention": "NOT_ESTABLISHED_EXISTING_LIBRARY_SELECTION",
              "resources": {"measured_work_all_probes_shadow_and_fresh": total_work,
                            "host_wall_ns": time.perf_counter_ns() - start,
                            "host_cpu_ns": time.process_time_ns() - cpu,
                            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
              "evidence_class": "E2/L0; actual-source development continuations, no independent domains"}
    result["resources"]["output_bytes_before_summary"] = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--print-registration", action="store_true")
    args = parser.parse_args()
    if args.print_registration:
        print(json.dumps(registered_packet(), indent=2))
    elif args.out:
        execute(args.out)
    else:
        parser.error("use --out NEW_PATH or --print-registration")
