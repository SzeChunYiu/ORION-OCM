"""Source-bound authored native controls. No search, learning, FLT or scaling claim."""
import argparse
from hashlib import sha256
from pathlib import Path
import sys
import time
from types import ModuleType

HERE = Path(__file__).resolve().parent
START_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()
for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check", "commission_io", "commission_contract"):
    path = HERE / (name + ".py")
    if path.resolve(strict=True) != path: raise ImportError("noncanonical recorder source")
    raw = path.read_bytes(); module = sys.modules.get(name, ModuleType(name)); module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    module.__ocm_source_sha256__ = sha256(raw).hexdigest()
import env_inputs as I
import env_check as C
from commission_io import launch, record
from commission_contract import assess, verify_matrix


def commission(path, expected_sha256, destination):
    if not sys.flags.isolated or not sys.flags.no_site: raise ValueError("Use Python -I -S")
    started = time.monotonic(); matrix = I.bound_json(path, expected_sha256)
    verify_matrix(matrix, HERE, START_SHA256)
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != expected_sha256: raise ValueError("matrix changed before staging")
    root = I.create_root(destination); I.write_bytes(root / "matrix.json", raw)
    cases_root = root / "cases"; cases_root.mkdir(); interrupted = None
    outcomes = [{"case": case["id"], "phase": phase, "passed": False, "reason": "NOT_EXECUTED"}
                for case in matrix["cases"] for phase in ["prepare", *(f"check-{i}" for i in range(len(case["checks"])))] ]
    rows = {(row["case"], row["phase"]): row for row in outcomes}; evidence = []; failure = None
    try:
        for case in matrix["cases"]:
            case_dir = cases_root / case["id"]; case_dir.mkdir()
            prepared, envelope, issued = launch("prepare", case["prepare_freeze"], case_dir / "prepare", matrix, case_dir / "prepare-process")
            passed = assess(prepared, envelope, case["prepare_expected"], "prepare")
            row = rows[(case["id"], "prepare")]; row.update(passed=passed, reason="ASSESSED")
            if issued: evidence.append(issued); row["receipt"] = issued
            if passed and prepared["terminal"] == "PREPARED":
                C.prepared_inputs(issued, prepared["environment_id"], matrix["runtime"]["sha256"])
            for index, check in enumerate(case["checks"]):
                row = rows[(case["id"], f"check-{index}")]
                if not passed or not prepared or prepared["terminal"] != "PREPARED":
                    row["reason"] = "PREPARATION_NOT_QUALIFIED"; continue
                I.verify_file(issued)  # Retain the assessed issuer; never authorize a new digest.
                freeze = {"schema": "ocm.proof-environment.freeze.v1", "operation": "check",
                          "prepared_receipt": issued, "environment_id": prepared["environment_id"],
                          **{k: check[k] for k in ("candidate_packet", "candidate_root")}}
                freeze_path = case_dir / f"check-{index}-freeze.json"; I.write_json(freeze_path, freeze)
                result, process, checked = launch("check", record(freeze_path), case_dir / f"check-{index}", matrix, case_dir / f"check-{index}-process")
                row.update(passed=assess(result, process, check["expected"], "check"), reason="ASSESSED")
                if checked: evidence.append(checked); row["receipt"] = checked
            if issued: I.verify_file(issued)
        verify_matrix(matrix, HERE, START_SHA256)
        for binding in evidence: I.verify_file(binding)
        if I.bound_json(path, expected_sha256) != matrix: raise ValueError("matrix custody changed")
    except (KeyboardInterrupt, SystemExit) as exc:
        interrupted = exc; failure = type(exc).__name__ + ": interrupted recording"
    except Exception as exc: failure = type(exc).__name__ + ": " + str(exc)
    complete = failure is None
    result = {"schema": "ocm.proof-environment.commission.v1", "scope": matrix["scope"],
              "terminal": "CONTROLS_PASSED" if complete and all(row["passed"] for row in outcomes) else "CONTROLS_FAILED",
              "evidence_complete": complete, "failure": failure, "matrix_sha256": expected_sha256,
              "controls": outcomes, "denominator": len(outcomes), "passed": sum(row["passed"] for row in outcomes),
              "wall_before_final_seal_s": time.monotonic() - started,
              "scientific_scope": "Authored transport/kernel boundary controls; not proof search or learning."}
    try: result["files"] = I.inventory(root)
    except (OSError, ValueError) as exc:
        result.update(terminal="CONTROLS_FAILED", evidence_complete=False, files=None,
                      artifact_error=type(exc).__name__ + ": " + str(exc), artifact_diagnostics=I.artifact_diagnostics(root))
    intended = result["terminal"]
    if intended == "CONTROLS_PASSED": result["terminal"] = "PROVISIONAL_PASS_REQUIRES_COMPLETE_SEAL"
    I.write_json(root / "result.json", result)
    seal_error = None
    try: files = I.inventory(root)
    except (OSError, ValueError) as exc:
        files = None; seal_error = type(exc).__name__ + ": " + str(exc)
    complete = result["evidence_complete"] and files is not None
    terminal = intended if complete else "CONTROLS_FAILED"
    seal = {"schema": "ocm.proof-environment.commission-seal.v1", "files": files,
            "terminal": terminal, "evidence_complete": complete, "error": seal_error,
            "wall_through_result_inventory_s": time.monotonic() - started,
            "scope": "Only a complete verified seal authorizes success. Outer process measures complete cost."}
    I.write_json(root / "seal.json", seal)
    if interrupted is not None: raise interrupted
    return {**result, "terminal": terminal, "evidence_complete": complete, "seal": record(root / "seal.json")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix"); parser.add_argument("matrix_sha256"); parser.add_argument("output")
    args = parser.parse_args(); result = commission(args.matrix, args.matrix_sha256, args.output)
    print(result["terminal"])
    raise SystemExit(0 if result["terminal"] == "CONTROLS_PASSED" else 2)
