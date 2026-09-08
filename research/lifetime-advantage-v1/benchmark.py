"""Frozen finite lifetime comparison. Coordinator owns oracle; engines see tasks only."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from fractions import Fraction
from itertools import product
import json
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time
import traceback

from ocm.learning import methods as M
from semantic_session import SemanticSearchSession, _normal_form_cost
from inverse_parent import InverseSession

ROOT = Path(__file__).resolve().parent
ARMS = ("primitive", "learned", "semantic_reset", "semantic_persistent", "inverse")
SEEDS = tuple(range(4101, 4109))
SLOTS = 2 * (1 + 4 + 16 + 64 + 256) + 2


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def task_data(task):
    return {"task_id": task.task_id, "coefficients": [str(x) for x in task.coefficients],
            "fingerprint": task.fingerprint}


def read_task(value):
    task = M.PolynomialTask(value["task_id"], tuple(Fraction(x) for x in value["coefficients"]))
    if task.fingerprint != value["fingerprint"]:
        raise ValueError("task identity changed")
    return task


@contextmanager
def baseline_accounting(work):
    """Count operations on the actually executed incumbent path; never patch new engines."""
    old_normal, old_execute, old_evaluate = M.normal_form, M.execute, M.evaluate_polynomial

    def normal(program):
        a, m = _normal_form_cost(program)
        work["arithmetic_additions"] += a
        work["arithmetic_multiplications"] += m
        work["normal_form_calls"] += 1
        return old_normal(program)

    def execute(program, x):
        for op in program:
            work["arithmetic_additions" if op in ("inc", "dec") else "arithmetic_multiplications"] += 1
        work["numeric_execution_calls"] += 1
        return old_execute(program, x)

    def evaluate(coefficients, x):
        work["arithmetic_additions"] += len(coefficients)
        work["arithmetic_multiplications"] += len(coefficients)
        work["polynomial_evaluation_calls"] += 1
        return old_evaluate(coefficients, x)

    M.normal_form, M.execute, M.evaluate_polynomial = normal, execute, evaluate
    try:
        yield
    finally:
        M.normal_form, M.execute, M.evaluate_polynomial = old_normal, old_execute, old_evaluate


def worker(request):
    arm = request["arm"]
    training = [read_task(x) for x in request["training"]]
    targets = [read_task(x) for x in request["targets"]]
    wall, cpu = time.perf_counter(), time.process_time()
    work, archived = Counter(), Counter()
    engine = None
    if arm.startswith("semantic"):
        engine = SemanticSearchSession(4)
    elif arm == "inverse":
        engine = InverseSession(4)
    method = M.GeneratorMethod()
    training_results, rows = [], []
    checkpoint_info = None
    learned_bytes = 0

    def total():
        return dict(archived + Counter(engine.work)) if engine is not None else dict(work)

    def query(task, phase):
        before = Counter(total())
        started = time.perf_counter()
        if engine is None:
            with baseline_accounting(work):
                result = M.solve(task, M.SearchBudget(SLOTS, 4), method)
                verified = M.verify_solution(task, result)
                work["answer_checks"] += 1
                work["answer_program_length"] += len(result.program or ())
            work["search_slots"] += result.slots
            work["candidates_checked"] += result.candidates_checked
            body = {"status": result.status, "program": result.program, "verified": verified}
            if phase == "training":
                training_results.append((task, result))
        else:
            if arm == "semantic_reset":
                engine.reset()
            body = engine.query(task, 100000)
        after = Counter(total())
        row = {"phase": phase, "fingerprint": task.fingerprint, "status": body["status"],
               "program": body["program"], "verified": body["verified"],
               "work": dict(after - before), "wall_s": time.perf_counter() - started}
        if "indexed_states" in body:
            row["indexed_states"] = body["indexed_states"]
            row["zero_transition_hit"] = row["work"].get("transitions", 0) == 0
        rows.append(row)

    for task in training:
        query(task, "training")
    if arm == "learned" and training:
        with baseline_accounting(work):
            method = M.learn_generator(training_results)
        work["acquisition_answer_checks"] += len(training_results)
        for _, result in training_results:
            n = len(result.program)
            work["fragment_candidates"] += sum(1 for a in range(n) for b in range(a+2, n+1) if b-a < n)
        learned_bytes = len(json.dumps({"fragments": method.fragments, "training_tasks": method.training_tasks}).encode())
        work["learned_serialized_bytes"] = learned_bytes
    training_work = total()
    # tempfile creation/cleanup and actual filesystem checkpoint are inside timings.
    with tempfile.TemporaryDirectory(prefix="ocm-semantic-lifetime-") as directory:
        for position, task in enumerate(targets):
            query(task, "evaluation")
            if (arm == "semantic_persistent" and request["kind"] == "lifetime" and
                    position + 1 == len(targets) // 2):
                payload = engine.checkpoint()
                checkpoint_path = Path(directory) / "state.json"
                with checkpoint_path.open("wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                archived.update(engine.work)
                readback = checkpoint_path.read_bytes()
                engine = SemanticSearchSession.restore(readback)
                checkpoint_info = {"bytes": len(payload), "after_targets": position+1,
                                   "replay_transitions": engine.work["restore_transitions"],
                                   "fsync": True}
        # Report canonical serialized size without writing an unrequested second checkpoint.
        # The serialization and its cost are within solver timing.
        if arm.startswith("semantic"):
            persistent_bytes = len(json.dumps(engine._state(), sort_keys=True, separators=(",", ":")).encode())
        else:
            persistent_bytes = learned_bytes
    elapsed_cpu, elapsed_wall = time.process_time()-cpu, time.perf_counter()-wall
    evaluation = [r for r in rows if r["phase"] == "evaluation"]
    return {"schema": "ocm.lifetime-advantage.run.v1", "arm": arm,
            "kind": request["kind"], "seed": request["seed"],
            "intervention_origin": "HUMAN_SUPPLIED_REPAIR", "training_count": len(training),
            "evaluation_count": len(evaluation), "verified_count": sum(r["verified"] for r in evaluation),
            "training_work": training_work, "work": total(), "wall_s": elapsed_wall,
            "cpu_s": elapsed_cpu, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "persistent_serialized_bytes": persistent_bytes, "checkpoint": checkpoint_info,
            "fragments": method.fragments, "rows": rows,
            "runtime_integration": "NOT_RUN_IN_THIS_BENCHMARK"}


def oracle():
    unique = {}
    for depth in range(5):
        for program in product(M.PRIMITIVES, repeat=depth):
            task = M.PolynomialTask("registered-polynomial", M.normal_form(program))
            unique.setdefault(task.fingerprint, (depth, task))
    train = [task for key, (depth, task) in sorted(unique.items()) if depth == 3][:12]
    targets = [task for key, (depth, task) in sorted(unique.items()) if depth == 4]
    assert len(train) == 12 and not ({t.fingerprint for t in train} & {t.fingerprint for t in targets})
    return train, targets


def summarize(runs):
    summary = {}
    for kind in ("lifetime", "single_query"):
        summary[kind] = {}
        for arm in ARMS:
            selected = [r for r in runs if r.get("kind") == kind and r.get("arm") == arm and "error" not in r]
            metrics = ("wall_s", "cpu_s", "subprocess_elapsed_s", "peak_rss_kib", "persistent_serialized_bytes")
            row = {"runs": len(selected), "verified": sum(r["verified_count"] for r in selected),
                   "tasks": sum(r["evaluation_count"] for r in selected), "metrics": {}}
            for metric in metrics:
                values = [r[metric] for r in selected]
                if values:
                    row["metrics"][metric] = {"median": statistics.median(values), "min": min(values), "max": max(values)}
            keys = sorted(set().union(*(r["work"] for r in selected)))
            row["work"] = {}
            for key in keys:
                values = [r["work"].get(key, 0) for r in selected]
                row["work"][key] = {"median": statistics.median(values), "min": min(values), "max": max(values)}
            summary[kind][arm] = row
    return summary


def coordinate(out):
    out = Path(out)
    if out.exists():
        raise ValueError("output must be a new directory; preserve previous runs")
    out.mkdir(parents=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--", str(ROOT)], cwd=ROOT, text=True)
    # Output directory itself is expected untracked. Frozen input files must match HEAD.
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", str(ROOT)], cwd=ROOT, check=True, capture_output=True)
    train, targets = oracle()
    write_json(out/"manifest.json", {"freeze_commit": commit, "seeds": SEEDS, "training": [task_data(t) for t in train],
                                    "targets": [task_data(t) for t in targets], "status_before": dirty,
                                    "evidence": "E2/L0; one finite ecology; HUMAN_SUPPLIED_REPAIR"})
    runs = []
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT.parents[1]/"src") + os.pathsep + str(ROOT)
    for kind in ("lifetime", "single_query"):
        for index, seed in enumerate(SEEDS):
            ordered = list(targets)
            random.Random(seed).shuffle(ordered)
            selected = ordered if kind == "lifetime" else [targets[index]]
            for arm in ARMS:
                request = {"arm": arm, "kind": kind, "seed": seed,
                           "training": [task_data(t) for t in train] if kind == "lifetime" else [],
                           "targets": [task_data(t) for t in selected]}
                started = time.perf_counter()
                process = subprocess.run([sys.executable, str(Path(__file__)), "--worker"], input=json.dumps(request),
                                         capture_output=True, text=True, env=env)
                elapsed = time.perf_counter()-started
                stem = f"{kind}-{seed}-{arm}"
                if process.returncode:
                    result = {"arm": arm, "kind": kind, "seed": seed, "error": "WORKER_FAILED",
                              "returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr}
                else:
                    result = json.loads(process.stdout)
                result["subprocess_elapsed_s"] = elapsed
                write_json(out/"raw"/(stem+".json"), result)
                runs.append(result)
                print(json.dumps({"run": stem, "verified": result.get("verified_count"), "tasks": result.get("evaluation_count"),
                                  "error": result.get("error"), "wall_s": result.get("wall_s")}), flush=True)
    report = {"freeze_commit": commit, "summary": summarize(runs),
              "errors": [r for r in runs if "error" in r],
              "correctness_gate": all("error" not in r and r["verified_count"] == r["evaluation_count"] for r in runs),
              "claim_ceiling": "HUMAN_SUPPLIED_REPAIR; conventional parent adoption; E2/L0 finite ecology"}
    write_json(out/"summary.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.worker:
        try:
            print(json.dumps(worker(json.load(sys.stdin))))
        except Exception:
            traceback.print_exc()
            raise
    elif args.out:
        coordinate(args.out)
    else:
        parser.error("choose --out NEW_DIRECTORY")
