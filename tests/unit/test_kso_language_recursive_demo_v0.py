from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_language_recursive_demo_v0.py"


def load():
    name = "kso_language_recursive_demo_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_language_is_a_real_recursive_kso_child_fibre():
    mod = load()
    r = mod.run_language_recursive_demo()
    assert r["terminal"] == "LANGUAGE_RECURSIVE_KSO_V0_CONTROLLED_GREEN"
    assert r["plan"]["sentence_sketch"] == ["S", "V", "O"]
    assert r["surface"] == "The curious robot opens the red door."
    assert r["organism"] == {
        "english_is_child_of_language": True,
        "parent_macro_live_before": True,
        "parent_macro_live_after_revoke": False,
        "child_status_after_revoke": "GAP_REVOKED_CLAUSE_TRANSITIVE_CONSTRUCTION",
        "parent_and_child_restored": True,
    }


def test_shared_revocation_state_is_same_object():
    mod = load()
    organism, english, clause, macro = mod.build_language_fibre()
    assert english.revoked is organism.revoked
    assert organism.macro_live(macro.macro_id)
    organism.revoke(clause.evidence_id)
    assert clause.evidence_id in english.revoked
    assert not organism.macro_live(macro.macro_id)
    assert english.speak(mod.lang._target_frame()).status == "GAP_REVOKED_CLAUSE_TRANSITIVE_CONSTRUCTION"


def test_demo_main_returns_zero():
    mod = load()
    assert mod.main(["--json"]) == 0
