"""Execute frozen #203 without altering its source, allocation, or limits.

This wrapper supplies only the transport described in PROTOCOL.md. It is a
post-exposure repeat, not an independent or protected scientific replication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import zipfile

PIN = "29c0ec40bb377152e24b5e9cd5ad133daae6fa36"
TASK_SHA = "11aa5ae4f887dda9606b4f2def3aa3432811977027fd4a52bc709e7ed8d5a92d"

def checked(test: bool, why: str):
    if not test:
        raise ValueError(why)

def run_logged(command: list[str], path: Path, timeout: float) -> None:
    with path.open("xb") as stream:
        result = subprocess.run(command, stdin=subprocess.DEVNULL,
                                stdout=stream, stderr=subprocess.STDOUT, timeout=timeout)
    checked(result.returncode == 0, f"command failed; retained log {path.name}; exit {result.returncode}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    checked(not out.exists(), "new evidence directory required")
    out.mkdir(parents=True)
    started = time.perf_counter()
    source = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    checked(source == PIN, "frozen experiment source mismatch")
    subprocess.run(["git", "-C", str(repo), "diff", "--exit-code", "HEAD"], check=True)
    engine = repo / "research/goal-only-lifecycle-v1"
    bundle = out / "bundle"
    bundle.mkdir()
    with zipfile.ZipFile(repo / "research/ordinary-goal-cohort-result-v1/RAW.zip") as z:
        base = z.read("base/PREFIX.mm")
        suffix = z.read("caller/qualification-01/TRANSPORTED-SUFFIX.mm")
        files = {"base.mm": base, "joined.mm": base + b"\n" + suffix,
                 "manifest.json": z.read("caller/qualification-01/LIBRARY-MANIFEST.json"),
                 "receipt.json": z.read("caller/qualification-01/native-01/result.json")}
    for name, raw in files.items():
        (bundle / name).write_bytes(raw)
    manifest = json.loads(files["manifest.json"])
    for name, key in (("base.mm", "base_prefix"), ("joined.mm", "joined_prefix")):
        raw = files[name]
        checked({"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()} == manifest[key], "transport identity: " + name)
    provenance = {"schema": "ocm.programme-execution.repeat.v1", "experiment_commit": PIN,
                  "wrapper": {"bytes": Path(__file__).stat().st_size, "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                  "python": sys.version, "platform": platform.platform(), "hard_wall_per_arm_seconds": 150,
                  "expected_tasks_sha256": TASK_SHA, "interpretation": "Post-exposure unchanged-source repeat; no protected or independent claim."}
    (out / "REPEAT-PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    run_logged([sys.executable, str(engine / "allocation.py"), "--repo", str(repo),
                "--manifest", str(bundle / "manifest.json"), "--prefix", str(bundle / "joined.mm"),
                "--out", str(out / "allocation")], out / "allocation.log", 600)
    tasks = out / "allocation/TASKS.json"
    checked(hashlib.sha256(tasks.read_bytes()).hexdigest() == TASK_SHA, "frozen population mismatch; do not run")
    run_logged([sys.executable, str(engine / "lifecycle.py"), "--repo", str(repo),
                "--bundle", str(bundle), "--tasks", str(tasks), "--output", str(out / "run"),
                "--hard-wall", "150"], out / "execution.log", 600)
    subprocess.run(["git", "-C", str(repo), "diff", "--exit-code", "HEAD"], check=True)
    result = json.loads((out / "run/RESULT.json").read_text())
    report = {"source": PIN, "tasks_sha256": TASK_SHA, "terminal": result["terminal"],
              "comparison": result["comparison"], "experiment_wall_seconds": result["wall_seconds"],
              "wrapper_wall_seconds": time.perf_counter() - started,
              "boundary": "Nested walls are not additive; no acquisition payback or scientific closure follows."}
    (out / "REPEAT-RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
