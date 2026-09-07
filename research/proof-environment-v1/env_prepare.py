"""Evaluator-authorized inspection/preparation of a native proof environment."""
import argparse
from pathlib import Path
from env_inputs import bound_json, create_root, digest, write_bytes
from env_dispatch import OPERATIONS, invoke


def prepare(freeze_path, freeze_sha256, runtime_path, runtime_sha256, output, *,
            timeout_s=60, max_output_bytes=1048576):
    freeze = bound_json(freeze_path, freeze_sha256)
    if set(freeze) != {"schema", "operation", "inputs"} or freeze["schema"] != "ocm.proof-environment.freeze.v1":
        raise ValueError("preparation freeze schema differs")
    operation = freeze["operation"]
    if operation not in {"inspect", "prepare"} or type(freeze["inputs"]) is not dict:
        raise ValueError("preparation/inspection freeze required")
    if set(freeze["inputs"]) != OPERATIONS[operation]: raise ValueError("frozen input roles differ")
    raw = Path(freeze_path).read_bytes()
    if digest(raw) != freeze_sha256: raise ValueError("freeze changed before staging")
    root = create_root(output)
    write_bytes(root / "freeze.json", raw)
    return invoke(operation, freeze["inputs"], root, runtime_path, runtime_sha256,
                  timeout_s=timeout_s, max_output_bytes=max_output_bytes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("freeze", "freeze-sha256", "runtime", "runtime-sha256", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--timeout-s", type=float, default=60)
    parser.add_argument("--max-output-bytes", type=int, default=1048576)
    args = parser.parse_args()
    result = prepare(args.freeze, args.freeze_sha256, args.runtime, args.runtime_sha256,
                     args.output, timeout_s=args.timeout_s, max_output_bytes=args.max_output_bytes)
    print(result["terminal"])
    return 0 if result["terminal"] in {"PREPARED", "INSPECTED"} else 2


if __name__ == "__main__": raise SystemExit(main())
