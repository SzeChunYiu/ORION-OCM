"""Rehydrate exact raw bytes and regrade with frozen source; never rerun actors."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import tarfile
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2); stream.write("\n")


def verify_files(root, records):
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if actual != set(records):
        raise ValueError("reconstruction file inventory mismatch")
    for name, record in records.items():
        path = root/name
        if path.is_symlink() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
            raise ValueError("reconstruction byte mismatch: " + name)


def extract(path, output):
    with tarfile.open(path, "r:gz") as archive:
        for item in archive:
            if not item.isfile() or Path(item.name).is_absolute() or ".." in Path(item.name).parts:
                raise ValueError("unexpected archive member")
        archive.extractall(output, filter="data")


def semantic(grade):
    result = json.loads(json.dumps(grade))
    for row in result["rows"]:
        if "external_check" in row:
            row["external_check"].pop("metrics", None)
    return result


def run(packet, output, models, gold, python):
    if output.exists():
        raise ValueError("refuse an existing replay directory")
    output.mkdir(parents=True)
    start = time.perf_counter(); cpu = time.process_time()
    rawdir = packet/"raw"; archives = read(rawdir/"ARCHIVES.json")
    try:
        for name, record in archives["archives"].items():
            if sha(rawdir/name) != record["sha256"]:
                raise ValueError("archive binding: " + name)
        for name, key in (("RAW_MANIFEST.json", "raw_manifest_sha256"),
                          ("SOURCE_MANIFEST.json", "source_manifest_sha256"),
                          ("MODEL_LOCATORS.json", "model_locators_sha256")):
            if sha(rawdir/name) != archives[key]:
                raise ValueError("manifest binding: " + name)
        records = read(rawdir/"RAW_MANIFEST.json")["files"]
        source_records = read(rawdir/"SOURCE_MANIFEST.json")["files"]
        extract(rawdir/"model-less-raw.tar.gz", output/"reconstructed")
        extract(rawdir/"frozen-source.tar.gz", output/"source")
        rehydrated = []
        for name, record in records.items():
            if record["role"] != "EXTERNAL_EXACT_MODEL":
                continue
            source = models/record["model_path"]
            if source.stat().st_size != record["bytes"] or sha(source) != record["sha256"]:
                raise ValueError("model bytes unavailable or changed: " + record["model_path"])
            target = output/"reconstructed"/name; target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(source, target); mode = "hardlink"
            except OSError:
                shutil.copyfile(source, target); mode = "copy"
            rehydrated.append({"path": name, "mode": mode, "sha256": record["sha256"]})
        verify_files(output/"reconstructed", records)
        verify_files(output/"source", source_records)
        original = output/"reconstructed"
        for name, key in (("run/receipt.json", "original_capture_receipt_sha256"),
                          ("grade.json", "original_grade_sha256"),
                          ("outer-launch-sealed.json", "original_outer_seal_sha256")):
            if sha(original/name) != archives[key]:
                raise ValueError("original seal changed: " + name)
        if sha(gold) != read(original/"grade.json")["gold_sha256"]:
            raise ValueError("external DEV custody mismatch")
        source = output/"source"; here = source/"research/ocm-prototype"
        argv = [str(python), str(here/"grade_g1_matched.py"), "--plan",
                str(here/"results/g1-stanza-matched-plan-v1"), "--run", str(original/"run"),
                "--gold", str(gold), "--out", str(output/"regrade.json")]
        write(output/"regrade-started.json", {"argv": argv, "actor_execution": False,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "source_head": read(rawdir/"SOURCE_MANIFEST.json")["source_head"]})
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with (output/"regrade.stdout").open("x") as stdout, (output/"regrade.stderr").open("x") as stderr:
            completed = subprocess.run(argv, cwd=source, stdout=stdout, stderr=stderr)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        if completed.returncode != 0:
            raise ValueError("frozen external regrade failed: exit " + str(completed.returncode))
        equal = semantic(read(output/"regrade.json")) == semantic(read(original/"grade.json"))
        verify_files(original, records)  # original raw, including weights, remains byte-identical
        if not equal:
            raise ValueError("regraded outcomes differ outside fresh checker resource/PID metrics")
        result = {"status": "EXACT_RAW_RECONSTRUCTION_AND_EXTERNAL_GRADE_REPLAY_PASS",
            "actor_execution": False, "model_inference_calls": 0,
            "completed_utc": datetime.now(timezone.utc).isoformat(), "raw_file_count": len(records),
            "raw_bytes_verified": sum(r["bytes"] for r in records.values()),
            "source_file_count": len(source_records), "model_occurrences": rehydrated,
            "semantic_equal": equal, "excluded_comparison_fields": ["rows[*].external_check.metrics"],
            "raw_manifest_sha256": sha(rawdir/"RAW_MANIFEST.json"), "source_manifest_sha256": sha(rawdir/"SOURCE_MANIFEST.json"),
            "original_grade_sha256": archives["original_grade_sha256"], "regrade_sha256": sha(output/"regrade.json"),
            "replay_script_sha256": sha(Path(__file__)),
            "reconstruction_and_regrade_wall_s": time.perf_counter()-start,
            "self_cpu_s": time.process_time()-cpu,
            "regrade_reaped_direct_child_cpu_s": after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            "total_process_tree_cpu_s": None, "complete_cpu_custody": False,
            "resource_scope": "New post-actor reconstruction/checking costs, not original actor execution."}
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        result = {"status": "CANNOT_CHECK_REPLAY", "actor_execution": False,
                  "reason": type(exc).__name__ + ": " + str(exc),
                  "wall_s": time.perf_counter()-start}
    write(output/"REPLAY_RECEIPT.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("packet", "out", "models", "gold", "python"):
        parser.add_argument("--"+name, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.packet, args.out, args.models, args.gold, args.python)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"].endswith("_PASS") else 2)
