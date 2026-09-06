"""Prepare or capture one E0 phase diagnostic; no grading, retries or option changes."""
import argparse
import json
from pathlib import Path
import subprocess

from later_consumption_capture import binding, capture_one, seal, sha, write, SUPERVISOR
from later_consumption_prepare import environment, PYTHON

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "results/explicit-phase-diagnostic-20260906"


def verify_bindings(bindings):
    for path, expected in bindings.items():
        if binding(path) != expected:
            raise ValueError("binding drift: " + path)


def required_bindings(original, baseline, request):
    additions = [baseline, request, ROOT / "explicit_phase_worker.py", Path(__file__).resolve(), SUPERVISOR,
                 ROOT / "later_consumption_capture.py", ROOT / "later_consumption_prepare.py",
                 ROOT / "later_consumption_contract.py", ROOT / "generation_clia.py",
                 ROOT / "clia_grammar.py", ROOT / "clia_tasks.py", ROOT / "clia_process.py"]
    return {**original["source_bindings"], **original["environment_bindings"], **original["request_bindings"],
            **environment(), **{str(p): binding(p) for p in additions}}


def prepare(baseline, packet):
    baseline, packet = Path(baseline).resolve(), Path(packet).resolve()
    if packet != (STUDY / "preparation").resolve():
        raise ValueError("canonical preparation path required")
    original = json.loads(baseline.read_text())
    for group in ("source_bindings", "environment_bindings", "request_bindings"):
        verify_bindings(original[group])
    if original["route_order"] != ["C", "E0", "B"] or original["native_timeout_ms"] != 5000:
        raise ValueError("unrecognized baseline assignment")
    packet.mkdir()
    request = packet / "request.json"
    request.write_bytes(Path(original["requests"]["E0"]).read_bytes())
    worker = ROOT / "explicit_phase_worker.py"
    argv = [*original["candidate_commands"]["E0"][:-1], str(worker)]
    if not original["candidate_commands"]["E0"][-1].endswith("/clia_worker.py"):
        raise ValueError("unrecognized baseline worker")
    bindings = required_bindings(original, baseline, request)
    manifest = {"schema": "ocm.explicit-phase-diagnostic.v1", "status": "PREPARED_NOT_EXECUTED",
                "baseline_manifest_sha256": sha(baseline), "baseline_manifest": str(baseline),
                "source_head": subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "assignment": ["E0"], "argv": argv, "request": str(request), "bindings": bindings,
                "watchdog_s": original["candidate_watchdog_s"], "cwd": str(ROOT),
                "output": str(packet.parent / "run-v1"),
                "event_schema": "ocm.clia.phase.v1", "semantic_assessment": "NOT_REGISTERED",
                "scope": "One instrumented diagnostic only; no B, induction, solver-option change, retry or speedup claim."}
    write(packet / "manifest.json", manifest)
    return packet / "manifest.json"


def verify(manifest):
    if manifest["schema"] != "ocm.explicit-phase-diagnostic.v1" or manifest["assignment"] != ["E0"]:
        raise ValueError("assignment drift")
    baseline_path = Path(manifest["baseline_manifest"])
    if sha(baseline_path) != manifest["baseline_manifest_sha256"]:
        raise ValueError("baseline manifest drift")
    baseline = json.loads(baseline_path.read_text())
    expected_bindings = required_bindings(baseline, baseline_path, Path(manifest["request"]))
    if manifest["bindings"] != expected_bindings:
        raise ValueError("binding inventory drift")
    verify_bindings(manifest["bindings"])
    if (manifest["cwd"] != str(ROOT) or manifest["output"] != str(STUDY / "run-v1")
            or manifest["request"] != str(STUDY / "preparation/request.json")):
        raise ValueError("canonical execution path drift")
    expected = [*baseline["candidate_commands"]["E0"][:-1], str(ROOT / "explicit_phase_worker.py")]
    if manifest["argv"] != expected or manifest["watchdog_s"] != 24:
        raise ValueError("command/envelope drift")
    if Path(manifest["request"]).read_bytes() != Path(baseline["requests"]["E0"]).read_bytes():
        raise ValueError("request drift")


def run(path, expected_sha):
    path = Path(path).resolve()
    if path != (STUDY / "preparation/manifest.json").resolve() or sha(path) != expected_sha:
        raise ValueError("registered manifest/path drift")
    manifest = json.loads(path.read_text())
    verify(manifest)
    output = Path(manifest["output"])
    output.mkdir()  # one assignment; an existing output refuses another call
    (output / "manifest.json").write_bytes(path.read_bytes())
    receipt = {"assigned": ["E0"], "manifest_sha256": sha(path), "semantic_assessment": "NOT_GRADED"}
    try:
        receipt["capture"] = capture_one(manifest["argv"], Path(manifest["request"]).read_bytes(),
                                          output / "E0", manifest["cwd"], manifest["watchdog_s"])
        verify(manifest)
        if sha(path) != expected_sha:
            raise ValueError("manifest changed during capture")
        receipt["status"] = "RAW_CAPTURE_COMPLETE"
    except (OSError, ValueError, KeyError) as exc:
        receipt.update(status="RAW_CAPTURE_INCOMPLETE", reason=type(exc).__name__ + ": " + str(exc))
    write(output / "receipt.json", receipt)
    seal(output)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--baseline", required=True); p.add_argument("--packet", required=True)
    r = sub.add_parser("run"); r.add_argument("--manifest", required=True); r.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    result = prepare(args.baseline, args.packet) if args.action == "prepare" else run(args.manifest, args.expected_sha)
    print(str(result) if isinstance(result, Path) else json.dumps(result, sort_keys=True))
