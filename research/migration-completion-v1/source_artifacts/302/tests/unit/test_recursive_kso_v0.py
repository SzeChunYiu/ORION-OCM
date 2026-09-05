from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "recursive_kso_v0.py"


def load():
    name = "recursive_kso_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_recursive_kso_v0_end_to_end():
    mod = load()
    r = mod.run_recursive_kso_v0()
    assert r["terminal"] == "RECURSIVE_KSO_V0_CONTROLLED_GREEN"
    assert r["non_tree"]["causal_inference_parent_count"] == 2
    assert r["revocation"] == {
        "child_evidence_kills_both_dependent_macros": True,
        "unrelated_fibre_unchanged": True,
        "bridge_revocation_local": True,
        "reinstatement_restores": True,
    }
    assert r["governance"]["dead_export_cannot_publish_macro"] is True
    assert r["governance"]["containment_cycle_rejected"] is True
    assert r["governance"]["macro_can_grant_new_authority"] is False


def test_multiple_parent_membership_is_supported_but_cycles_are_not():
    mod = load()
    r = mod.RecursiveKSO()
    r.add_scope("domain", "DOMAIN")
    r.add_scope("subject-a", "SUBJECT", ("domain",))
    r.add_scope("subject-b", "SUBJECT", ("domain",))
    r.add_scope("field", "FIELD", ("subject-a", "subject-b"))
    assert r.scopes["field"].parents == {"subject-a", "subject-b"}
    assert r.ancestors("field") == frozenset({"subject-a", "subject-b", "domain"})
    try:
        r.link_parent("domain", "field")
    except ValueError as exc:
        assert str(exc) == "containment cycle"
    else:
        raise AssertionError("containment cycle was accepted")


def test_macro_warrant_is_child_and_bridge_conjunction():
    mod = load()
    r = mod.RecursiveKSO()
    r.add_scope("parent", "SUBJECT")
    r.add_scope("child", "FIELD", ("parent",))
    r.add_local_atom("child", "fact", "claim", 11)
    macro = r.publish_macro("child", "parent", ("fact",), 12)
    assert r.macro_live(macro.macro_id)
    r.revoke(11)
    assert not r.macro_live(macro.macro_id)
    r.reinstate(11)
    assert r.macro_live(macro.macro_id)
    r.revoke(12)
    assert not r.macro_live(macro.macro_id)


def test_dead_child_export_cannot_be_promoted_to_parent_macro():
    mod = load()
    r = mod.RecursiveKSO()
    r.add_scope("parent", "SUBJECT")
    r.add_scope("child", "FIELD", ("parent",))
    r.add_local_atom("child", "fact", "claim", 21)
    r.revoke(21)
    try:
        r.publish_macro("child", "parent", ("fact",), 22)
    except mod.CannotCheck:
        pass
    else:
        raise AssertionError("dead child warrant became parent macro authority")


def test_main_returns_zero():
    mod = load()
    assert mod.main([]) == 0
