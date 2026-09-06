"""Freeze then capture the published six-process development control; never grade in actors."""
import argparse
import copy
from datetime import datetime, timezone
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from clia_reuse_study_common import (HERE, REPO, PROTOCOL_SHA, PUBLIC_SHA, digest,
                                    run_process, sha, source_files, tree_bytes, write)

MODEL_SHA = "7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9"


def bind_f1(bindings):
    if set(bindings) != {"native", "ocm"}: raise ValueError("CANNOT_CHECK_MISSING_ACQUISITION")
    for alias in ("max3", "guard2"):
        pair = [bindings[a]["programs"][alias] for a in ("native", "ocm")]
        for field in ("program_sha256", "task_id", "task_sha256", "checker_identity"):
            if pair[0][field] != pair[1][field]: raise ValueError("CANNOT_CHECK_IDENTICAL_DONOR_BINDING")
    return {"schema": "ocm.reuse.f1.v1", "arms": copy.deepcopy(bindings)}


def resolve_requests(templates, binding):
    resolved = copy.deepcopy(templates)
    for item in resolved:
        request = item["request"]
        if request["kind"] == "clia_apply":
            alias = request["program_id"]
            if alias not in ("@max3", "@guard2"): raise ValueError("UNREGISTERED_ALIAS")
            request["program_id"] = binding["programs"][alias[1:]]["descriptor_id"]
    return resolved


def dependencies():
    packages = {}
    for name in ("pytest", "sympy", "cvc5", "z3-solver", "sexpdata", "ufal.udpipe"):
        dist = metadata.distribution(name)
        files = {}
        for rel in dist.files or []:
            if str(rel).endswith((".so", ".dll", ".dylib", ".dist-info/RECORD")) or "/RECORD" in str(rel):
                path = Path(dist.locate_file(rel))
                if path.is_file(): files[str(rel)] = {"sha256": sha(path), "bytes": path.stat().st_size}
        packages[name] = {"version": dist.version, "installed_native_and_record_files": files}
    return {"python": sys.version, "executable": sys.executable,
            "executable_sha256": sha(sys.executable), "packages": packages}


def bound_tasks(protocol):
    from clia_tasks import load_task
    tasks = [load_task(item["task_id"]) for item in protocol["tasks"]]
    for task, expected in zip(tasks, protocol["tasks"]):
        if task["task_sha256"] != expected["task_sha256"] or task["source"]["sha256"] != expected["original_sha256"]: raise ValueError("TASK_CHANGED")
    return tasks


def protocol_inventory(directory):
    directory = Path(directory); inventory = directory / "SHA256SUMS"
    if sha(inventory) != "6fa6b232b84ab6b7f61c08ad30e003c10a597e83c5293c142c070b7d480b92a6":
        raise ValueError("PUBLISHED_PROTOCOL_CHANGED")
    expected = {line.split()[1]: line.split()[0] for line in inventory.read_text().splitlines()}
    expected["SHA256SUMS"] = sha(inventory)
    if set(p.name for p in directory.iterdir()) != set(expected) or any(sha(directory / name) != value for name, value in expected.items()):
        raise ValueError("PUBLISHED_PROTOCOL_CHANGED")
    return expected


def freeze(root, protocol_dir, model, cpu):
    preparation_start = time.monotonic(); preparation_cpu = time.process_time()
    root, protocol_dir, model = Path(root), Path(protocol_dir), Path(model)
    protocol_inventory(protocol_dir)
    if root.exists(): raise ValueError("F0_ROOT_MUST_BE_NEW")
    if cpu not in os.sched_getaffinity(0): raise ValueError("CPU_NOT_ALLOWED")
    if sha(protocol_dir / "protocol.json") != PROTOCOL_SHA or sha(protocol_dir / "public-requests.jsonl") != PUBLIC_SHA:
        raise ValueError("PUBLISHED_PROTOCOL_CHANGED")
    protocol = json.loads((protocol_dir / "protocol.json").read_text())
    if sha(model) != MODEL_SHA or model.stat().st_size != protocol["model"]["bytes"]: raise ValueError("MODEL_CHANGED")
    source = source_files()
    tracked = subprocess.check_output(["/usr/bin/git", "ls-files", "-z"], cwd=REPO).decode().split("\0")
    changed = subprocess.check_output(["/usr/bin/git", "diff", "HEAD", "--name-only", "-z"], cwd=REPO).decode().split("\0")
    if set(source) - set(tracked) or set(source) & set(changed): raise ValueError("F0_SOURCE_MUST_BE_COMMITTED")
    tasks = bound_tasks(protocol)
    training = REPO / protocol["model"]["manifest"]
    if sha(training) != protocol["model"]["manifest_sha256"]: raise ValueError("TRAINING_MANIFEST_CHANGED")
    root.mkdir(parents=True)
    shutil.copytree(protocol_dir, root / "protocol")
    shutil.copyfile(training, root / "training-manifest.json")
    for rel in source:
        target = root / "source" / rel; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, target)
    f0 = {"schema": "ocm.reuse.f0.v1", "status": "FROZEN_BEFORE_ACQUISITION",
          "created_utc": datetime.now(timezone.utc).isoformat(),
          "source_commit": subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"], cwd=REPO).decode().strip(),
          "source_files": source, "source_archive": {rel: "source/" + rel for rel in source},
          "protocol_path": "protocol/protocol.json", "protocol_sha256": PROTOCOL_SHA,
          "public_requests_path": "protocol/public-requests.jsonl", "public_requests_sha256": PUBLIC_SHA,
          "protocol_files": {str(p.relative_to(root)): sha(p) for p in sorted((root / "protocol").iterdir())},
          "model": {"path": str(model.resolve()), "sha256": MODEL_SHA, "bytes": model.stat().st_size,
                    "manifest_path": "training-manifest.json", "manifest_sha256": sha(training)},
          "tasks": tasks, "dependencies": dependencies(),
          "resources": {"cpu": cpu, "threads": 1, "stage_seconds": 120, "whole_seconds": 1800,
                        "address_bytes": 4294967296}}
    f0["preparation_cost"] = {"wall_s": time.monotonic() - preparation_start,
        "self_cpu_s": time.process_time() - preparation_cpu,
        "scope": "F0 preparation call; interpreter/import startup outside this measurement",
        "complete_tree_cpu_verified": False}
    write(root / "F0.json", f0)
    return f0


def validate_f0(root, f0):
    if source_files() != f0["source_files"] or dependencies() != f0["dependencies"]: raise ValueError("F0_RUNTIME_CHANGED")
    if sha(f0["model"]["path"]) != f0["model"]["sha256"]: raise ValueError("F0_MODEL_CHANGED")
    for rel, expected in f0["protocol_files"].items():
        if sha(root / rel) != expected: raise ValueError("F0_PROTOCOL_CHANGED")
    if sha(root / f0["model"]["manifest_path"]) != f0["model"]["manifest_sha256"]: raise ValueError("F0_TRAINING_CHANGED")
    for rel, archived in f0["source_archive"].items():
        if sha(root / archived) != f0["source_files"][rel]: raise ValueError("F0_ARCHIVE_CHANGED")


def capture(root):
    root = Path(root).resolve(); f0 = json.loads((root / "F0.json").read_text())
    if (root / "receipt.json").exists() or any((root / (a + "-state")).exists() for a in ("native", "ocm")):
        raise ValueError("REFUSE_CAPTURE_RESTART_OR_OVERWRITE")
    started = time.monotonic(); validate_f0(root, f0)
    protocol = json.loads((root / f0["protocol_path"]).read_text())
    templates = [json.loads(line) for line in (root / f0["public_requests_path"]).read_text().splitlines()]
    receipt = {"schema": "ocm.reuse.capture.v1", "status": "RUNNING", "capture_root": str(root), "f0_sha256": sha(root / "F0.json"),
               "started_utc": datetime.now(timezone.utc).isoformat(), "stages": []}
    bindings = {}; f1 = None; resources = f0["resources"]
    env = {**os.environ, "PYTHONPATH": str(REPO / "src") + ":" + str(HERE), "PYTHONDONTWRITEBYTECODE": "1",
           "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
    try:
        for index, phase in enumerate(protocol["phases"]):
            for arm in phase["order"]:
                remaining = resources["whole_seconds"] - (time.monotonic() - started)
                if remaining <= 0: raise ValueError("WHOLE_CAPTURE_DEADLINE")
                prefix = root / (str(index) + "-" + phase["id"] + "-" + arm)
                config = {"phase": phase["id"], "arm": arm, "state": str(root / (arm + "-state")),
                          "source_files": f0["source_files"], "f0_sha256": receipt["f0_sha256"],
                          "rows": str(prefix.with_suffix(".rows.jsonl")), "events": str(prefix.with_suffix(".events.jsonl"))}
                if phase["id"] == "acquire":
                    config.update(model=f0["model"]["path"],
                        training_manifest=json.loads((root / f0["model"]["manifest_path"]).read_text()),
                        tasks={item["alias"]: item["task_id"] for item in protocol["tasks"]})
                else:
                    config.update(f1_sha256=sha(root / "F1.json"), bindings_sha256=digest(bindings[arm]),
                                  items=[item for item in f1["resolved_requests"][arm] if item["id"].startswith(phase["id"] + ".")])
                input_path = prefix.with_suffix(".input.json"); write(input_path, config)
                process = run_process([sys.executable, str(HERE / "clia_reuse_study_worker.py"), str(input_path)],
                    prefix, seconds=min(resources["stage_seconds"], remaining), cwd=REPO, env=env,
                    cpu=resources["cpu"], address_bytes=resources["address_bytes"])
                try: worker = json.loads(prefix.with_suffix(".stdout").read_text())
                except (ValueError, OSError): worker = {"status": "CANNOT_CHECK_WORKER_OUTPUT"}
                stage = {"phase": phase["id"], "arm": arm, "process": process, "worker": worker,
                         **{k + "_path": str(prefix.with_suffix(suffix).relative_to(root)) for k, suffix in
                            (("input", ".input.json"), ("rows", ".rows.jsonl"), ("events", ".events.jsonl"),
                             ("stdout", ".stdout"), ("stderr", ".stderr"))}}
                receipt["stages"].append(stage)
                write(prefix.with_suffix(".process.json"), stage)
                if process["exit_code"] or worker["status"] != "STAGE_COMPLETED": raise ValueError("STAGE_INCOMPLETE")
                if phase["id"] == "acquire": bindings[arm] = worker["bindings"]
            if phase["id"] == "acquire":
                f1 = bind_f1(bindings)
                f1.update(f0_sha256=receipt["f0_sha256"],
                          acquisition_receipts={s["arm"]: s["process"]["stdout_sha256"] for s in receipt["stages"]},
                          resolved_requests={arm: resolve_requests(templates, bindings[arm]) for arm in bindings})
                write(root / "F1.json", f1); receipt["f1_sha256"] = sha(root / "F1.json")
        validate_f0(root, f0); receipt["status"] = "EXECUTED_NOT_GRADED"
    except Exception as exc:
        receipt["status"] = "CANNOT_CHECK_CAPTURE"; receipt["error"] = type(exc).__name__ + ":" + str(exc)
    receipt.update(finished_utc=datetime.now(timezone.utc).isoformat(), outer_wall_s=time.monotonic() - started,
                   complete_tree_cpu_verified=False, state_bytes={arm: tree_bytes(root / (arm + "-state")) for arm in ("native", "ocm")})
    write(root / "receipt.json", receipt)
    write(root / "capture-manifest.json", {"schema": "ocm.reuse.capture-seal.v1",
        "files": {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}})
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("freeze", "run")); parser.add_argument("--root", required=True)
    parser.add_argument("--protocol-dir"); parser.add_argument("--model"); parser.add_argument("--cpu", type=int)
    args = parser.parse_args()
    result = freeze(args.root, args.protocol_dir, args.model, args.cpu) if args.mode == "freeze" else capture(args.root)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] in ("FROZEN_BEFORE_ACQUISITION", "EXECUTED_NOT_GRADED") else 2)
