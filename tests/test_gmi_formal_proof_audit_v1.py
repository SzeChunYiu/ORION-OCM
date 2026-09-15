from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-formal-proof-audit-v1"
SPEC = importlib.util.spec_from_file_location("formal_proof_audit_v1", BUNDLE / "formal_proof_audit_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_canonical_theorem_corpus_is_fail_closed_and_typed():
    result = MODULE.validate_audit()
    assert result["theorems"] == 39
    assert sum(result["tag_counts"].values()) >= 39
    assert result["ledger_rows"] == 9
