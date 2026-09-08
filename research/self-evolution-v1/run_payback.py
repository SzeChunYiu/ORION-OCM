"""Frozen, read-only development continuation; never feeds the proposal cell."""
import argparse
import json
from pathlib import Path
import time

import ladder_adapter as A

HERE = Path(__file__).resolve().parent
REGISTRATION = {
    "schema": "ocm.self_evolution.development_payback.v1",
    "status": "E2_DEVELOPMENT_FOLLOWUP_ON_FROZEN_IMPLEMENTATIONS",
    "reason": "v1 development overhead exceeded initial observed savings",
    "tasks": [A.task("d", scale, scale % 2, "payback") for scale in range(4, 28)],
    "horizon": 24,
    "endpoints": ["quality", "counted work including all v1 self-change work", "wall time", "peak donor bytes"],
    "stop": "all 24 episodes regardless of whether or when payback occurs",
    "claims": "no proposal updates, no g3, no protected or independent-domain evidence",
    "counterfactual": "initial two-component dispatcher with full original algorithm recomputation",
    "strong_parent": "same evolved library route available to ordinary adaptive parent; no novel residual",
}


def execute(source, out):
    if out.exists():
        raise ValueError("choose a new output directory")
    out.mkdir(parents=True)
    A.TRACE_SINK = out / "external_raw_traces"
    summary = json.loads((source / "summary.json").read_text())
    genotype = dict(summary["config"])
    spent = summary["resources"]["measured_work_all_probes_shadow_and_fresh"]
    old_total = 0
    new_total = spent
    old_wall = 0
    new_wall = summary["resources"]["host_wall_ns"]
    rows, first_work_payback, first_wall_payback = [], None, None
    for index, task in enumerate(REGISTRATION["tasks"]):
        measured = {}
        # Alternate arm execution order. Fields are rebuilt per actual episode.
        arms = [("initial", A.INITIAL_CONFIG), ("evolved", genotype)]
        if index % 2:
            arms.reverse()
        for name, config in arms:
            start = time.perf_counter_ns()
            measured[name] = A.runner(config, [task])
            measured[name]["wall_ns"] = time.perf_counter_ns() - start
        old_total += measured["initial"]["resources"]["work"]
        new_total += measured["evolved"]["resources"]["work"]
        old_wall += measured["initial"]["wall_ns"]
        new_wall += measured["evolved"]["wall_ns"]
        if first_work_payback is None and new_total < old_total:
            first_work_payback = index + 1
        if first_wall_payback is None and new_wall < old_wall:
            first_wall_payback = index + 1
        rows.append({"episode": index + 1, "task": task, **measured,
                     "cumulative_initial_work": old_total, "cumulative_evolved_work": new_total,
                     "cumulative_initial_wall_ns": old_wall, "cumulative_evolved_wall_ns": new_wall})
    result = {"registration": REGISTRATION, "source_summary": str(source / "summary.json"),
              "self_improvement_work_fully_charged": spent,
              "first_counted_work_payback_episode": first_work_payback,
              "first_observed_wall_payback_episode": first_wall_payback,
              "initial_verified_episodes": sum(r["initial"]["success"] for r in rows),
              "evolved_verified_episodes": sum(r["evolved"]["success"] for r in rows),
              "quality_contract": "all five revision decisions exact, no stale/collateral invalidations",
              "final_initial_work": old_total, "final_evolved_work": new_total,
              "final_initial_wall_ns": old_wall, "final_evolved_wall_ns": new_wall,
              "generation": summary["actual_adopted_generations"], "rows": rows,
              "claim_ceiling": "actual-source development trajectory; compute/storage/host-cost tradeoff; parents sufficient"}
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "registration")}))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--register", action="store_true")
    p.add_argument("--source", type=Path, default=HERE / "results/run-v1")
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    if a.register:
        print(json.dumps(REGISTRATION, indent=2))
    elif a.out:
        execute(a.source, a.out)
    else:
        p.error("--register or --out required")
