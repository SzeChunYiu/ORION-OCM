"""Check only against an independently authorized, successfully issued environment."""
import argparse
from pathlib import Path
from env_inputs import (bound_json, create_root, digest, file_record, inventory, valid_hash,
                        verify_file, write_bytes, write_json)
from env_dispatch import invoke


def prepared_inputs(record, environment_id, runtime_sha256):
    path = verify_file(record)
    receipt = bound_json(path, record["sha256"])
    if (receipt.get("schema") != "ocm.proof-environment.receipt.v1" or
            receipt.get("operation") != "prepare" or receipt.get("terminal") != "PREPARED" or
            receipt.get("environment_id") != valid_hash(environment_id) or
            receipt.get("runtime_sha256") != runtime_sha256):
        raise ValueError("not the independently authorized prepared environment")
    actual = inventory(path.parent); actual.pop(path.name)
    if actual != receipt["files"]: raise ValueError("prepared environment custody differs")
    names = {"permitted_packet": "execution/native/permitted.ndjson",
             "target_packet": "execution/native/target.ndjson",
             "registration": "execution/native/registration.json",
             "primitive_packet": "inputs/primitive_packet.ndjson"}
    return {role: {"path": str(path.parent / name), **file_record(path.parent / name)}
            for role, name in names.items()}


def check(freeze_path, freeze_sha256, runtime_path, runtime_sha256, output, *,
          timeout_s=60, max_output_bytes=1048576):
    freeze = bound_json(freeze_path, freeze_sha256)
    required = {"schema", "operation", "prepared_receipt", "environment_id", "candidate_packet", "candidate_root"}
    if set(freeze) != required or freeze["schema"] != "ocm.proof-environment.freeze.v1" or freeze["operation"] != "check":
        raise ValueError("check freeze schema differs")
    if type(freeze["candidate_root"]) is not int or freeze["candidate_root"] < 0:
        raise ValueError("candidate root must be a natural number")
    raw = Path(freeze_path).read_bytes()
    if digest(raw) != freeze_sha256: raise ValueError("freeze changed before staging")
    root = create_root(output)
    write_bytes(root / "freeze.json", raw)
    try:
        records = prepared_inputs(freeze["prepared_receipt"], freeze["environment_id"], runtime_sha256)
        records["candidate_packet"] = freeze["candidate_packet"]
        verify_issuer = lambda: prepared_inputs(freeze["prepared_receipt"], freeze["environment_id"], runtime_sha256)
        result = invoke("check", records, root, runtime_path, runtime_sha256,
                        candidate_root=freeze["candidate_root"], timeout_s=timeout_s,
                        max_output_bytes=max_output_bytes, verify_issuer=verify_issuer)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        result = {"schema": "ocm.proof-environment.check.v1", "terminal": "CANNOT_CHECK",
                  "stage": "issuer_custody", "reason": type(exc).__name__ + ": " + str(exc)}
    issuer = freeze["prepared_receipt"]
    result = {**result, "prepared_receipt_sha256": issuer.get("sha256") if type(issuer) is dict else None,
              "environment_id": freeze["environment_id"]}
    write_json(root / "check.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("freeze", "freeze-sha256", "runtime", "runtime-sha256", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--timeout-s", type=float, default=60)
    parser.add_argument("--max-output-bytes", type=int, default=1048576)
    args = parser.parse_args()
    result = check(args.freeze, args.freeze_sha256, args.runtime, args.runtime_sha256,
                   args.output, timeout_s=args.timeout_s, max_output_bytes=args.max_output_bytes)
    print(result["terminal"])
    return 0 if result["terminal"] == "KERNEL_PASS" else 2


if __name__ == "__main__": raise SystemExit(main())
