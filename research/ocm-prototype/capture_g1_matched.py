"""Execute the prospectively frozen native/OCM stream; gold scoring stays outside."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import g1_vessel as G


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(plan_dir, model, training_path, output):
    if output.exists():
        raise ValueError("refuse to overwrite an executed lifetime")
    plan = json.loads((plan_dir / "plan.json").read_text())
    public = plan_dir / "public-items.json"
    assert digest(public) == plan["public_items_sha256"]
    items = json.loads(public.read_text())
    assert len(items) == 105 and sum(i["request"]["kind"] == "syntax" for i in items) == 100
    training = json.loads(training_path.read_text())
    model_sha = digest(model)
    if training.get("model_sha256") != model_sha:
        raise ValueError("training manifest must bind the exact completed model")
    source_files = G.identities()
    source_identity = G.content_hash(source_files)
    worker = Path(__file__).with_name("matched_g1_worker.py")
    scripts = [Path(__file__), worker, Path(__file__).with_name("freeze_g1_stream.py")]
    script_hashes = {str(p): digest(p) for p in scripts}
    assert script_hashes[str(scripts[2])] == plan["freeze_source_sha256"]
    output.mkdir(parents=True)
    record = {"role": "DEVELOPMENT_NATIVE_OCM_COMPARISON_NOT_HOSTED_OR_PROTECTED",
              "started_utc": datetime.now(timezone.utc).isoformat(), "plan": plan,
              "plan_sha256": digest(plan_dir / "plan.json"), "model_sha256": model_sha,
              "model_bytes": model.stat().st_size, "training_manifest": training,
              "training_manifest_sha256": digest(training_path),
              "runner_sha256": digest(Path(__file__)), "worker_sha256": digest(worker), "chunks": [],
              "script_hashes": script_hashes, "assigned_ids_by_arm": {a: [i["id"] for i in items] for a in ("native", "ocm")},
              "source_files": source_files, "source_identity": source_identity,
              "cost_scope": "outer worker wall and reaped process-tree CPU; includes import/replay/archive/check/persist; installation,training,hosted and energy separate"}
    (output / "run-binding.json").write_text(json.dumps(record, indent=2) + "\n")
    for chunk in range(plan["chunks"]):
        for arm in (("native", "ocm") if chunk % 2 == 0 else ("ocm", "native")):
            if {str(p): digest(p) for p in scripts} != script_hashes or G.identities() != source_files:
                record["status"] = "CANNOT_CHECK_SOURCE_CHANGED_BEFORE_CHUNK"
                break
            prefix = output / f"{chunk:02d}-{arm}"
            rows = prefix.with_suffix(".rows.jsonl")
            config = {"arm": arm, "chunk": chunk, "items": items[chunk * 21:(chunk + 1) * 21],
                      "state": str(output / (arm + "-state")), "rows": str(rows),
                      "model": str(model), "model_sha256": model_sha, "training_manifest": training}
            config_path = prefix.with_suffix(".input.json")
            config_path.write_text(json.dumps(config, ensure_ascii=False) + "\n")
            start = time.perf_counter(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
            with prefix.with_suffix(".stdout").open("w") as stdout, prefix.with_suffix(".stderr").open("w") as stderr:
                process = subprocess.Popen([sys.executable, str(worker), str(config_path)], stdout=stdout,
                                           stderr=stderr, start_new_session=True)
                timed_out = False
                try:
                    process.wait(timeout=plan["outer_seconds_per_chunk"])
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL); process.wait()
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            receipt = {"arm": arm, "chunk": chunk, "pid": process.pid, "exit_code": process.returncode,
                       "outer_timeout": timed_out, "wall_s": time.perf_counter() - start,
                       "reaped_process_tree_cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                       "complete_cpu_custody": not timed_out and process.returncode == 0,
                       "rows_written": len(rows.read_text().splitlines()) if rows.exists() else 0}
            if process.returncode == 0:
                try:
                    receipt["worker"] = json.loads(prefix.with_suffix(".stdout").read_text())
                    receipt["source_stable"] = (receipt["worker"]["source_files"] == source_files and
                        G.identities() == source_files and {str(p): digest(p) for p in scripts} == script_hashes)
                except (json.JSONDecodeError, KeyError, TypeError) as exc:
                    receipt.update(terminal="CANNOT_CHECK_WORKER_RECEIPT", complete_cpu_custody=False,
                                   source_stable=False, worker_receipt_error=str(exc))
            else:
                receipt["terminal"] = "CANNOT_CHECK_EXECUTION"
                receipt["cpu_note"] = "external termination may leave separately bounded donor descendants; full CPU then unknown"
            record["chunks"].append(receipt)
            (output / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
            print(json.dumps(receipt), flush=True)
            if process.returncode or receipt["rows_written"] != 21 or not receipt.get("source_stable"):
                record["status"] = "CANNOT_CHECK_INCOMPLETE_EXECUTION"
                break
        if record.get("status", "").startswith("CANNOT_CHECK"):
            observed = {a: [] for a in ("native", "ocm")}
            for path in sorted(output.glob("*.rows.jsonl")):
                for line in path.read_text().splitlines():
                    try:
                        row = json.loads(line); observed[row["arm"]].append(row["id"])
                    except (json.JSONDecodeError, KeyError):
                        record.setdefault("malformed_row_files", []).append(path.name)
            record["written_ids_by_arm"] = observed
            record["missing_ids_by_arm"] = {a: [i for i in record["assigned_ids_by_arm"][a] if i not in observed[a]] for a in observed}
            record["denominator_note"] = "unattempted/missing items are incomplete execution, distinct from completed refusals"
            (output / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
            return record
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["status"] = "EXECUTED_NOT_GRADED"
    (output / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("plan", "model", "training", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.plan, args.model, args.training, args.out)
    raise SystemExit(0 if receipt.get("status") == "EXECUTED_NOT_GRADED" else 2)
