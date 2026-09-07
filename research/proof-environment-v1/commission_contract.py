"""Fixed control attribution and final nested custody validation."""
import base64
import sys
import env_inputs as I
import env_runtime as R


def expectation(value, phase):
    if type(value) is not dict or set(value) != {"terminal", "stage", "reason_contains"}:
        raise ValueError("exact expected native terminal/stage/reason condition required")
    if any(type(v) is not str for v in value.values()): raise ValueError("string expectations required")
    allowed = {"PREPARED" if phase == "prepare" else "KERNEL_PASS", "REJECTED", "CANNOT_CHECK"}
    if value["terminal"] not in allowed: raise ValueError("unregistered expected terminal")
    if value["terminal"] in {"REJECTED", "CANNOT_CHECK"} and not value["reason_contains"]:
        raise ValueError("negative native control requires an intended refusal reason")


def verify_matrix(matrix, here, start_sha256):
    required = {"schema", "scope", "recorder", "recorder_dependencies", "runtime", "cases", "timeout_s", "max_output_bytes"}
    if set(matrix) != required or matrix["schema"] != "ocm.proof-environment.controls.v1":
        raise ValueError("control matrix schema differs")
    if matrix["scope"] != "AUTHORED_NATIVE_ENVIRONMENT_CONTROLS": raise ValueError("control scope differs")
    if I.verify_file(matrix["recorder"]) != here / "commission.py" or matrix["recorder"]["sha256"] != start_sha256:
        raise ValueError("recorder differs")
    if set(matrix["recorder_dependencies"]) != {"commission_io.py", "commission_contract.py"}:
        raise ValueError("recorder source closure differs")
    for name, binding in matrix["recorder_dependencies"].items():
        if I.verify_file(binding) != here / name: raise ValueError("recorder dependency path differs")
        if getattr(sys.modules[name[:-3]], "__ocm_source_sha256__", None) != binding["sha256"]:
            raise ValueError("loaded recorder dependency bytes differ")
    runtime = matrix["runtime"]; I.verify_file(runtime); R.verify_runtime(runtime["path"], runtime["sha256"])
    if type(matrix["timeout_s"]) is not int or matrix["timeout_s"] <= 0:
        raise ValueError("positive whole-second native timeout required")
    if type(matrix["max_output_bytes"]) is not int or matrix["max_output_bytes"] <= 0:
        raise ValueError("positive output envelope required")
    cases = matrix["cases"]
    if type(cases) is not list or not cases: raise ValueError("nonempty fixed control matrix required")
    ids = set()
    for case in cases:
        if type(case) is not dict or set(case) != {"id", "purpose", "prepare_freeze", "prepare_expected", "checks"}:
            raise ValueError("exact control case required")
        name = I.relative_name(case["id"])
        if "/" in name or name in ids: raise ValueError("unique basename case ID required")
        ids.add(name)
        if type(case["purpose"]) is not str or not case["purpose"]: raise ValueError("control purpose required")
        binding = case["prepare_freeze"]; I.verify_file(binding); freeze = I.bound_json(binding["path"], binding["sha256"])
        if (set(freeze) != {"schema", "operation", "inputs"} or freeze["schema"] != "ocm.proof-environment.freeze.v1" or
                freeze["operation"] != "prepare" or set(freeze["inputs"]) != {"source_packet", "policy", "primitive_packet", "registered_target_packet"}):
            raise ValueError("preparation control requires an actual prepare freeze")
        for item in freeze["inputs"].values(): I.verify_file(item)
        expectation(case["prepare_expected"], "prepare")
        if type(case["checks"]) is not list: raise ValueError("check list required")
        if case["checks"] and case["prepare_expected"]["terminal"] != "PREPARED":
            raise ValueError("check requires expected successful preparation")
        for check in case["checks"]:
            if type(check) is not dict or set(check) != {"candidate_packet", "candidate_root", "expected"}:
                raise ValueError("exact registered candidate check required")
            I.verify_file(check["candidate_packet"]); expectation(check["expected"], "check")
            if type(check["candidate_root"]) is not int or check["candidate_root"] < 0:
                raise ValueError("candidate expression root must be a natural number")


def assess(result, envelope, expected, operation):
    if type(result) is not dict or type(result.get("native")) is not dict: return False
    native = result["native"]; wanted = expected["terminal"]
    try:
        return (result["operation"] == native["operation"] == operation and
                result["terminal"] == native["terminal"] == wanted and result["stage"] == native["stage"] == expected["stage"] and
                result.get("evidence_complete", True) is True and type(result["files"]) is dict and
                "artifact_error" not in result and result["reason"] == native["reason"] and
                expected["reason_contains"] in native["reason"] and
                not envelope.get("error") and envelope.get("interrupted") is False and
                envelope["cleanup"] == {"reaped": True, "group_absent": True} and
                envelope["returncode"] == (0 if wanted in {"PREPARED", "KERNEL_PASS"} else 2) and
                base64.b64decode(envelope["stderr_base64"], validate=True) == b"")
    except (ValueError, TypeError, KeyError): return False
