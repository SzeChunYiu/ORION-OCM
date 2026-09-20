"""Freshly replay immutable V11 proof evidence for original R1-010."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research/gmi-1068-typed-foundation-v11"
RECEIPT_SHA = "598a325e75a7005ca906dd0d21f2feea1aab9de561b0a83219b475f944c59d65"


class CannotCheck(RuntimeError):
    pass


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def evaluate():
    raw = (PACKAGE / "RESULT_V11.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != RECEIPT_SHA:
        raise ValueError("inherited V11 receipt drift")
    receipt = json.loads(raw)
    for name in ("proof_contract_v11.py", "check_lean_v11.py"):
        actual = hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        if actual != receipt["inputs"][name]:
            raise ValueError("inherited V11 proof checker/contract drift")
    load("proof_contract_v11", PACKAGE / "proof_contract_v11.py")
    kernel = load("bound_v11_kernel", PACKAGE / "check_lean_v11.py")
    try:
        result = kernel.evaluate()
    except kernel.CannotCheck as exc:
        raise CannotCheck(str(exc)) from exc
    if result != receipt["kernel"]:
        raise ValueError("inherited V11 kernel evidence drift")
    return result
