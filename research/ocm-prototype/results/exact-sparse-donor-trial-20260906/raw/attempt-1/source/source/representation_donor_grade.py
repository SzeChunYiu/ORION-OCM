"""External exact grading against recorded original SV calls; never import the router/checker."""
from dataclasses import asdict, is_dataclass
from enum import Enum
from fractions import Fraction
import hashlib
import json
import math


def wire(value):
    if type(value) is float and not math.isfinite(value):
        return {"nonfinite_float": repr(value)}  # explicit unbounded Scope epochs; never a kernel rational
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return wire(asdict(value))
    if isinstance(value, dict):
        return {str(k): wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [wire(v) for v in sorted(value, key=repr)]
    if value is None or type(value) in (str, int, bool, float):
        return value
    raise TypeError(f"Unsupported explicit record type: {type(value).__name__}")


def digest(value):
    return hashlib.sha256(json.dumps(wire(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def compare(reference, candidate):
    differences = []
    failed = any(row["consumer"].get("status") != "COMPLETED" for row in (reference, candidate))
    for key in ("request", "vectors", "consumer", "surprise"):
        if reference[key] != candidate[key]:
            differences.append(key)
    mismatch = any(k in differences for k in ("request", "vectors", "surprise")) or (not failed and bool(differences))
    return {"functional_parity": not differences and not failed, "differences": differences, "consumer_failed": failed,
            "terminal": "FUNCTIONAL_MISMATCH" if mismatch else "CANNOT_CHECK_CONSUMER_FAILURE" if failed else "EXACT_FUNCTIONAL_PARITY",
            "reference_digest": digest({k: reference[k] for k in ("request", "vectors", "consumer", "surprise")}),
            "candidate_digest": digest({k: candidate[k] for k in ("request", "vectors", "consumer", "surprise")}),
            "performance_authority": "NOT_TESTED"}


def grade_archive(root):
    from pathlib import Path
    root = Path(root)
    inventory = json.loads((root / "SHA256.json").read_text())
    for path, expected in inventory.items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError("CAPTURE_DRIFT:" + path)
    def read(path):
        if path not in inventory:
            raise ValueError("UNBOUND_CAPTURE_FILE:" + path)
        return json.loads((root / path).read_text())
    plan, receipt = read("PLAN.json"), read("RECEIPT.json")
    if plan["arms"] != ["full", "informed_parent", "ocm"] or receipt["status"] != "SEALED":
        raise ValueError("INVALID_CAPTURE_CONTRACT")
    rows = []
    statuses = {"EXACT_FUNCTIONAL_PARITY": 0, "CANNOT_CHECK_CONSUMER_FAILURE": 0, "FUNCTIONAL_MISMATCH": 0}
    completed_scenarios = completed_records = error_records = failed_comparisons = 0
    for name in plan["scenarios"]:
        reference = read(f"records/{name}-full.json")
        if reference["arm"] != "full":
            raise ValueError("ARM_BINDING_MISMATCH")
        completed = reference["consumer"].get("status") == "COMPLETED"
        completed_records += int(completed); error_records += int(not completed)
        for arm in plan["arms"][1:]:
            candidate = read(f"records/{name}-{arm}.json")
            if candidate["arm"] != arm:
                raise ValueError("ARM_BINDING_MISMATCH")
            done = candidate["consumer"].get("status") == "COMPLETED"
            completed_records += int(done); error_records += int(not done)
            completed = completed and done
            result = compare(reference, candidate)
            failed_comparisons += int(result["consumer_failed"])
            statuses[result["terminal"]] += 1
            rows.append({"scenario": name, "arm": arm, **result})
        completed_scenarios += int(completed)
    expected = len(plan["scenarios"]) * len(plan["arms"])
    recorded = sum(path.startswith("records/") for path in inventory)
    if recorded != expected or receipt["assigned_records"] != expected or not receipt["source_unchanged"]:
        raise ValueError("INCOMPLETE_CAPTURE_DENOMINATOR")
    equal, failed, mismatch = (statuses[k] for k in ("EXACT_FUNCTIONAL_PARITY", "CANNOT_CHECK_CONSUMER_FAILURE", "FUNCTIONAL_MISMATCH"))
    summary = {"assigned_scenarios": len(plan["scenarios"]), "recorded_scenarios": len(plan["scenarios"]), "completed_scenarios": completed_scenarios,
               "assigned_arm_records": expected, "recorded_arm_records": recorded,
               "completed_arm_records": completed_records, "consumer_error_arm_records": error_records,
               "functionally_equal_comparisons": equal, "consumer_failed_comparisons": failed_comparisons, "uncheckable_function_comparisons": failed,
               "functional_mismatch_comparisons": mismatch,
               "terminal": "FUNCTIONAL_MISMATCH" if mismatch else "PARTIAL_PARITY__CANNOT_CHECK_CONSUMER_REVISION" if failed else "EXACT_FUNCTIONAL_PARITY",
               "parent_disposition": "PARENT_SUFFICIENT_ON_COMPLETED_CASES" if not mismatch else "NOT_ESTABLISHED",
               "performance_authority": "NOT_TESTED"}
    return {**summary, "summary": summary, "comparisons": rows,
            "seal_sha256": hashlib.sha256((root / "SHA256.json").read_bytes()).hexdigest()}
