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


def run(plan_dir, model, training_path, output, *, donor="udpipe", profile_path=None):
    capture_start, capture_cpu = time.perf_counter(), time.process_time()
    if output.exists():
        raise ValueError("refuse to overwrite an executed lifetime")
    plan = json.loads((plan_dir / "plan.json").read_text())
    public = plan_dir / "public-items.json"
    assert digest(public) == plan["public_items_sha256"]
    items = json.loads(public.read_text())
    assert len(items) == 105 and sum(i["request"]["kind"] == "syntax" for i in items) == 100
    if plan["chunks"] != 5 or plan["restart_after_every_items"] != 21:
        raise ValueError("fixed five-chunk lifetime")
    profile = None; extra = {}; syntax_id = G.CATALOGUE[0]
    if donor == "stanza-recurrent":
        from g1_stanza_capture import bind, stable_files
        if profile_path is None:
            raise ValueError("fixed Stanza profile required")
        profile, training, extra = bind(plan_dir, plan, model, training_path, profile_path)
        syntax_id = "syntax:stanza-recurrent"
        model_sha = profile["model_sha256"]
        baseline_files = stable_files(model, training_path, profile_path, profile)
        def input_stable():
            try:
                return stable_files(model, training_path, profile_path, profile) == baseline_files
            except (OSError, ValueError):
                return False
    elif donor == "udpipe" and profile_path is None:
        training = json.loads(training_path.read_text())
        model_sha = digest(model)
        input_stable = lambda: digest(model) == model_sha and digest(training_path) == training_sha
    else:
        raise ValueError("only fixed UDPipe and Stanza donor profiles are supported")
    training_sha = digest(training_path)
    if training.get("model_sha256") != model_sha:
        raise ValueError("training manifest must bind the exact completed model")
    source_files = G.identities(syntax_id)
    source_identity = G.content_hash(source_files)
    if profile and plan.get("source_identity") != source_identity:
        raise ValueError("prospective source identity mismatch")
    worker = Path(__file__).with_name("g1_stanza_worker.py" if profile else "matched_g1_worker.py")
    scripts = [Path(__file__), worker, Path(__file__).with_name("freeze_g1_stream.py")]
    script_hashes = {str(p): digest(p) for p in scripts}
    assert script_hashes[str(scripts[2])] == plan["freeze_source_sha256"]
    output.mkdir(parents=True)
    record = {"role": "DEVELOPMENT_NATIVE_OCM_COMPARISON_NOT_HOSTED_OR_PROTECTED",
              "started_utc": datetime.now(timezone.utc).isoformat(), "plan": plan,
              "plan_sha256": digest(plan_dir / "plan.json"), "model_sha256": model_sha,
              "model_bytes": extra.get("model_bytes", model.stat().st_size), "training_manifest": training,
              "training_manifest_sha256": digest(training_path),
              "runner_sha256": digest(Path(__file__)), "worker_sha256": digest(worker), "chunks": [],
              "script_hashes": script_hashes, "assigned_ids_by_arm": {a: [i["id"] for i in items] for a in ("native", "ocm")},
              "source_files": source_files, "source_identity": source_identity,
              "cost_scope": "outer wall and reaped direct-child CPU; total tree CPU UNKNOWN; includes import/replay/archive/check/persist; installation,training,hosted and energy separate",
              "prelaunch_binding_wall_s": time.perf_counter() - capture_start,
              "prelaunch_binding_cpu_s": time.process_time() - capture_cpu,
              "capture_scope": "Function entry through seal; interpreter/import setup before entry unmeasured.",
              **extra}
    (output / "run-binding.json").write_text(json.dumps(record, indent=2) + "\n")
    for chunk in range(plan["chunks"]):
        for arm in (("native", "ocm") if chunk % 2 == 0 else ("ocm", "native")):
            if {str(p): digest(p) for p in scripts} != script_hashes or G.identities(syntax_id) != source_files or not input_stable():
                record["status"] = "CANNOT_CHECK_SOURCE_CHANGED_BEFORE_CHUNK"
                break
            prefix = output / f"{chunk:02d}-{arm}"
            rows = prefix.with_suffix(".rows.jsonl")
            config = {"arm": arm, "chunk": chunk, "items": items[chunk * 21:(chunk + 1) * 21],
                      "state": str(output / (arm + "-state")), "rows": str(rows),
                      "model": str(model), "model_sha256": model_sha, "training_manifest": training, **({"donor_profile": profile} if profile else {})}
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
                       "reaped_direct_child_cpu_s": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                       "complete_cpu_custody": False, "total_process_tree_cpu_s": None,
                       "cpu_scope": "Outer RUSAGE_CHILDREN delta only; whole process tree completeness UNKNOWN.",
                       "rows_written": len(rows.read_text().splitlines()) if rows.exists() else 0}
            if process.returncode == 0:
                try:
                    receipt["worker"] = json.loads(prefix.with_suffix(".stdout").read_text())
                    receipt["source_stable"] = (receipt["worker"]["source_files"] == source_files and
                        G.identities(syntax_id) == source_files and {str(p): digest(p) for p in scripts} == script_hashes and input_stable())
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
            record.update(capture_body_wall_s=time.perf_counter()-capture_start,
                          capture_self_cpu_s=time.process_time()-capture_cpu)
            (output / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
            return record
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["status"] = "EXECUTED_NOT_GRADED"
    record.update(capture_body_wall_s=time.perf_counter()-capture_start,
                  capture_self_cpu_s=time.process_time()-capture_cpu)
    (output / "receipt.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("plan", "model", "training", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--donor", choices=("udpipe", "stanza-recurrent"), default="udpipe")
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    receipt = run(args.plan, args.model, args.training, args.out, donor=args.donor, profile_path=args.profile)
    raise SystemExit(0 if receipt.get("status") == "EXECUTED_NOT_GRADED" else 2)
