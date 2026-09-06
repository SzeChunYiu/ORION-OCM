"""Create-only development capture; no model calls, timing comparison, or runtime integration."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import representation_donor as D
from representation_donor_grade import wire, grade_archive
from representation_donor_imports import DONORS, load

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "research/ocm-prototype"
SCENARIOS = ("base", "incoming", "mixed_warrant", "missing_state", "alternative",
             "withdraw_one", "withdraw_backup", "withdraw_both", "withdraw_rule",
             "withdraw_partial", "irrelevant", "reinstate", "changed_query",
             "changed_config", "changed_state", "unregistered", "mutated_task",
             "mutated_config", "mutated_family")
ARMS = ("full", "informed_parent", "ocm")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wire(value), indent=2, sort_keys=True, allow_nan=False) + "\n")


def source_inventory():
    tracked = subprocess.check_output(["/usr/bin/git", "-C", str(ROOT), "ls-files", "-z", "src"]).split(b"\0")
    files = [ROOT / path.decode() for path in tracked if path]
    files += [ROOT / "tests/m2/test_solve_loop.py", ROOT / "pyproject.toml"]
    files += sorted(PROTO.glob("representation_donor*.py"))
    files += sorted((PROTO / "representation_donor_tests").glob("*.py"))
    files += sorted(p for p in DONORS.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return {str(p.relative_to(ROOT)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in files}


def scenario(name, arm):
    alternative = {"alternative", "withdraw_one", "withdraw_backup", "withdraw_both", "withdraw_rule", "withdraw_partial", "irrelevant", "reinstate"}
    f = D.fixture("alternative" if name in alternative else name if name in ("incoming", "mixed_warrant") else "base")
    policy = D.prepare(f, available_states=(frozenset(),) if name == "missing_state" else None)
    revisions = {"withdraw_one": (1,), "withdraw_backup": ("backup",), "withdraw_both": (1,"backup"),
                 "withdraw_rule": (2,), "withdraw_partial": (3,), "irrelevant": ("irrelevant",),
                 "unregistered": ("unregistered",)}
    args = {"revoked": revisions.get(name, ())}
    if name == "changed_query":
        args["task"] = replace(f["task"], parts=(replace(f["task"].parts[0], refs=("background_0",)),))
    elif name == "changed_config":
        args["config"] = replace(f["config"], alpha=Fraction(1,2))
    elif name == "changed_state":
        args["ks"] = D.fixture("incoming")["ks"]
    elif name == "mutated_task":
        f["task"] = replace(f["task"], targets=("island",))
    elif name == "mutated_config":
        f["config"] = replace(f["config"], threshold=Fraction(1,2))
    elif name == "mutated_family":
        args["revoked"] = ("newly_appended",)
        f["revocations"] = (*f["revocations"], frozenset(args["revoked"]))
    return D.evaluate(policy, arm=arm, **args)


def capture(output, *, scenarios=SCENARIOS):
    if sys.flags.optimize:
        raise ValueError("CANNOT_CHECK_OPTIMIZED_PYTHON")
    output = Path(output)
    if not scenarios or len(set(scenarios)) != len(scenarios) or not set(scenarios) <= set(SCENARIOS):
        raise ValueError("UNREGISTERED_SCENARIOS")
    output.mkdir(parents=True, exist_ok=False)
    before = source_inventory()
    write(output / "SOURCE.json", before)
    write(output / "PLAN.json", {"scenarios": scenarios, "arms": ARMS, "background_added": 8,
          "base": subprocess.check_output(["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
          "registration": "https://github.com/SzeChunYiu/ORION-OCM/issues/72#issuecomment-5558162066",
          "mode": "REGISTERED_FUNCTIONAL_INTEGRATION" if tuple(scenarios) == SCENARIOS else "DEVELOPMENT_FIXTURE_SUBSET",
          "lifecycle": "independent finite snapshots; no runtime persistence claim"})
    started = datetime.now(timezone.utc).isoformat()
    wall = time.monotonic(); cpu = resource.getrusage(resource.RUSAGE_SELF)
    for name in scenarios:
        for arm in ARMS:
            write(output / "records" / f"{name}-{arm}.json", scenario(name, arm))
    revision = load()["revision"]
    write(output / "revision-checker.json", {"scope": "existing finite-map controls only; no OCM revision authority",
          "identity": revision.revision_commutes((0,1,2), ((0,1),(2,)), (0,1)),
          "split_fibre": revision.revision_commutes((0,2,2), ((0,1),(2,)), (0,1))})
    after = source_inventory()
    if before != after:
        raise ValueError("EXECUTED_SOURCE_DRIFT")
    end_cpu = resource.getrusage(resource.RUSAGE_SELF)
    write(output / "RECEIPT.json", {"status": "SEALED", "started_utc": started,
          "finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic()-wall,
          "python": platform.python_version(), "executable": sys.executable, "pytest_fixture_dependency": version("pytest"),
          "self_cpu_user_seconds": end_cpu.ru_utime-cpu.ru_utime,
          "self_cpu_system_seconds": end_cpu.ru_stime-cpu.ru_stime,
          "maxrss_kib_process_high_water": end_cpu.ru_maxrss,
          "resource_scope": "whole Python fixture capture, including preparation/checks/all arms; child CPU uncounted; other host activity not excluded; no timing comparison",
          "source_unchanged": True, "assigned_records": len(scenarios)*len(ARMS)})
    files = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob("*")) if p.is_file()}
    write(output / "SHA256.json", files)
    return output


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grade-only", action="store_true"); args = parser.parse_args()
    if not args.grade_only:
        capture(args.output)
    grade = grade_archive(args.output)
    target = args.output.with_name(args.output.name + "-grade.json")
    if target.exists():
        raise FileExistsError(target)
    write(target, grade); print(json.dumps(grade["summary"], sort_keys=True))
    return 1 if grade["functional_mismatch_comparisons"] else 2 if grade["consumer_failed_comparisons"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
