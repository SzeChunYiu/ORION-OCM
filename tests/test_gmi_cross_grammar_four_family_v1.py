from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BUNDLE = Path(__file__).resolve().parents[1] / "research" / "gmi-cross-grammar-four-family-v1"
SPEC = importlib.util.spec_from_file_location("cross_grammar_four_family_v1", BUNDLE / "cross_grammar_four_family_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_four_postclassified_families_replicate_across_grammars():
    result = MODULE.validate_closure()
    assert result["families"] == 4
    assert result["grammars"] == 2
    assert result["positive_twin_flips"] == 8
