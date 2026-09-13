"""Frozen V5 source authority and strict, non-executing input helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
GRAND = HERE.parent / "gmi-grand-unification-v1"
HARNESS = "nn_nonnn_point_parity3_experiment_v5.py"
PREREG = "NN_NONNN_POINT_PARITY3_PREREG_V5.json"
PARENT = "nn_nonnn_point_parity3_experiment_v4.py"
IDS = ("N_THRESHOLD_DNF4_V1", "X_XOR2_V1", "N_SUM_THRESHOLD3_V3", "X_LOOKUP8_V3")
FAMILIES = dict(zip(IDS, ("NEURAL", "NON_NEURAL", "NEURAL", "NON_NEURAL")))
KEYS = ("python_opcode_count_per_full_domain_sweep", "wall_block_ns", "process_block_ns")
EXPECTED = [sum((a, b, c)) % 2 for a in (0, 1) for b in (0, 1) for c in (0, 1)]
INVALID = "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION"


class AuditError(ValueError):
    """Evidence contradicts the registered contract."""


class Unverifiable(AuditError):
    """Required external evidence/interpreter is unavailable, not a pass."""


def require(condition, message):
    if not condition:
        raise AuditError(message)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise AuditError("nonfinite or non-JSON value") from exc


def same(actual, expected, message):
    require(canonical(actual) == canonical(expected), message)


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def constant(value):
        raise AuditError("nonfinite JSON constant")
    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, TypeError) as exc:
        raise AuditError("invalid JSON: " + str(exc)) from exc
    canonical(result)
    return result


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()
        import os
        os.fsync(stream.fileno())


def frozen(base=GRAND):
    manifest = strict_json((HERE / "FROZEN_INPUTS_V1.json").read_bytes())
    for name in (HARNESS, PREREG, PARENT):
        require(sha((base / name).read_bytes()) == manifest["sources"][name],
                "frozen source drift: " + name)
    prereg = strict_json((base / PREREG).read_bytes())
    spec = importlib.util.spec_from_file_location("frozen_parity5", base / HARNESS)
    module = importlib.util.module_from_spec(spec)
    exec(compile((base / HARNESS).read_bytes(), str(base / HARNESS), "exec"), module.__dict__)
    # Definitions only; compile/exec also avoids creating source-tree bytecode caches.
    module.validate_preregistration(prereg)
    same(module.candidate_identity_record()["byte_identical_to_parent"], True,
         "V4/V5 candidate identity drift")
    return manifest, prereg, module


def runtime_identity():
    return {"python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "python_executable_sha256": sha(Path(sys.executable).resolve().read_bytes())}


def implementation_bindings():
    names = ("frozen_contract_v1.py", "FROZEN_INPUTS_V1.json", "attempt_custody_v1.py",
             "packet_content_v6.py", "resource_evidence_v6.py", "audit_custody_v1.py",
             "cross_envelope_v6.py", "audit_imported_v1.py",
             "raw/IMPORTED_V5_PACKET_BINDINGS_V1.json")
    return {name: sha((HERE / name).read_bytes()) for name in names}
