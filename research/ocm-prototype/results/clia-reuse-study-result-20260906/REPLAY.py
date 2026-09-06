"""Exact raw reconstruction and external regrading; ADAPT of the Stanza result replay."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import tarfile
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write("\n")


def verify_one(path, record):
    if path.is_symlink() or path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
        raise ValueError("reconstruction byte mismatch: " + str(path))


def verify_files(root, records):
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if actual != set(records): raise ValueError("reconstruction file inventory mismatch")
    for name, record in records.items(): verify_one(root / name, record)


def extract(path, output):
    with tarfile.open(path, "r:gz") as archive:
        for item in archive:
            if not item.isfile() or Path(item.name).is_absolute() or ".." in Path(item.name).parts:
                raise ValueError("unexpected archive member")
        archive.extractall(output, filter="data")


def run(packet, output, model, python):
    if output.exists(): raise ValueError("refuse an existing replay directory")
    output.mkdir(parents=True)
    start = time.perf_counter(); cpu = time.process_time()
    try:
        rawdir = packet / "raw"; binding = read(rawdir / "ARCHIVES.json")
        verify_one(rawdir / binding["archive"]["file"], binding["archive"])
        if sha(rawdir / "RAW_MANIFEST.json") != binding["raw_manifest_sha256"]: raise ValueError("raw manifest changed")
        if sha(rawdir / "MODEL_LOCATORS.json") != binding["model_locators_sha256"]: raise ValueError("model locator changed")
        manifest = read(rawdir / "RAW_MANIFEST.json"); records = manifest["files"]
        verify_one(model, read(rawdir / "MODEL_LOCATORS.json"))
        original = output / "reconstructed"
        extract(rawdir / binding["archive"]["file"], original)
        model_copies = []
        for name, record in records.items():
            if record["role"] != "EXTERNAL_EXACT_MODEL": continue
            verify_one(model, record)
            target = original / name; target.parent.mkdir(parents=True, exist_ok=True)
            try: os.link(model, target); mode = "hardlink"
            except OSError: shutil.copyfile(model, target); mode = "copy"
            model_copies.append({"path": name, "mode": mode, "sha256": record["sha256"]})
        verify_files(original, records)
        outcomes = {}; child_cpu = 0
        for attempt in ("v1", "v2", "v3"):
            expected = binding["attempts"][attempt]; capture = original / attempt / "run"
            for name, key in (("receipt.json", "capture_receipt_sha256"),
                              ("capture-manifest.json", "capture_manifest_sha256"), ("F0.json", "f0_sha256")):
                if sha(capture / name) != expected[key]: raise ValueError("original attempt binding changed")
            if sha(original / attempt / "grade.json") != expected["grade_sha256"]: raise ValueError("original grade changed")
            seal = read(capture / "capture-manifest.json")
            for name, digest in seal["files"].items():
                if sha(capture / name) != digest: raise ValueError("original capture seal mismatch")
            source = capture / "source"; here = source / "research/ocm-prototype"
            argv = [str(python), str(here / "grade_clia_reuse.py"), str(capture),
                    "--output", str(output / (attempt + "-regrade.json"))]
            write(output / (attempt + "-regrade-started.json"),
                  {"argv": argv, "actor_execution": False, "source_commit": expected["source_commit"]})
            env = {**os.environ, "PYTHONPATH": os.pathsep.join((str(source / "src"), str(here))),
                   "PYTHONDONTWRITEBYTECODE": "1"}
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            with (output / (attempt + "-regrade.stdout")).open("x") as out, (output / (attempt + "-regrade.stderr")).open("x") as err:
                completed = subprocess.run(argv, cwd=source, env=env, stdout=out, stderr=err, timeout=60)
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            child_cpu += after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
            # The frozen CLI returns 2 for the preserved incomplete v1/v2 outcomes.
            if completed.returncode != (0 if attempt == "v3" else 2): raise ValueError("unexpected external grade exit")
            actual = read(output / (attempt + "-regrade.json")); prior = read(original / attempt / "grade.json")
            if actual != prior: raise ValueError("external regrade differs from original")
            outcomes[attempt] = {"equal_all_fields": True, "exit_code": completed.returncode,
                "function": actual["function"], "parent": actual["parent"],
                "regrade_sha256": sha(output / (attempt + "-regrade.json"))}
        # Same verifier used above, on a real unmodified grade and a separate altered copy.
        actual_grade = original / "v3/grade.json"; expected = records["v3/grade.json"]
        verify_one(actual_grade, expected)
        mutant = output / "changed-raw-control.json"; mutant.write_bytes(actual_grade.read_bytes() + b"\n")
        try: verify_one(mutant, expected)
        except ValueError as exc: refusal = str(exc)
        else: raise ValueError("changed raw control was accepted")
        write(output / "CUSTODY_CONTROL.json", {"actual_no_alarm": "PASS", "changed_raw": "EXPECTED_REFUSAL",
            "reason": refusal, "original_sha256": sha(actual_grade), "changed_sha256": sha(mutant)})
        verify_files(original, records)
        result = {"status": "EXACT_RAW_RECONSTRUCTION_AND_EXTERNAL_GRADE_REPLAY_PASS",
            "actor_execution": False, "model_inference_calls": 0, "outcomes": outcomes,
            "raw_files": len(records), "logical_bytes_verified": sum(r["bytes"] for r in records.values()),
            "model_occurrences": model_copies, "wall_s": time.perf_counter() - start,
            "self_cpu_s": time.process_time() - cpu, "regrade_reaped_child_cpu_s": child_cpu,
            "total_process_tree_cpu_s": None, "complete_cpu_custody": False,
            "resource_scope": "New post-study reconstruction/regrading cost; no original runtime cost replacement.",
            "script_sha256": sha(Path(__file__)), "archive_sha256": binding["archive"]["sha256"]}
    except (OSError, ValueError, KeyError, tarfile.TarError, subprocess.TimeoutExpired) as exc:
        result = {"status": "CANNOT_CHECK_REPLAY", "reason": type(exc).__name__ + ": " + str(exc),
                  "actor_execution": False, "wall_s": time.perf_counter() - start}
    write(output / "REPLAY_RECEIPT.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("packet", "out", "model", "python"): parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = run(args.packet, args.out, args.model, args.python)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"].endswith("_PASS") else 2)
