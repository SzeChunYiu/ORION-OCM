from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_wisdom_methods_v0.py"


def load():
    name = "kso_wisdom_methods_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_wisdom_method_end_to_end():
    mod = load()
    r = mod.run_wisdom_methods_v0()
    assert r["terminal"] == "WISDOM_METHOD_KSO_V0_CONTROLLED_GREEN"
    assert r["productive_search"]["selected_method"] == "safe-probe"
    assert set(r["productive_search"]["active_principles"]) == {
        "epistemic-humility",
        "perseverance",
    }
    assert r["high_risk_low_value"]["selected_method"] == "report-unknown"
    assert set(r["high_risk_low_value"]["active_principles"]) == {
        "epistemic-humility",
        "restraint",
    }
    assert all(r["revocation"].values())
    assert all(r["hostile"].values())


def test_interpretation_revocation_does_not_delete_historical_artifact():
    mod = load()
    w = mod.build_demo_space()
    assert w.artifact_live("analects-known-unknown")
    assert w.principle_live("epistemic-humility")
    w.revoke(1101)
    assert w.artifact_live("analects-known-unknown")
    assert not w.interpretation_live("analects-epistemic-humility")
    assert not w.principle_live("epistemic-humility")


def test_context_not_popularity_selects_between_perseverance_and_restraint():
    mod = load()
    w = mod.build_demo_space()
    open_task = mod.TaskContext(
        "open",
        frozenset({"uncertain", "search-open", "valuable-next-step"}),
        0.8,
        0.9,
        0.1,
        1,
    )
    risky_task = mod.TaskContext(
        "risky",
        frozenset({"uncertain", "high-risk"}),
        0.8,
        0.0,
        1.0,
        0,
    )
    assert w.select_method(open_task).selected_method == "safe-probe"
    assert w.select_method(risky_task).selected_method == "report-unknown"


def test_unsupported_guess_is_suppressed_under_uncertainty():
    mod = load()
    w = mod.build_demo_space()
    task = mod.TaskContext(
        "unknown",
        frozenset({"uncertain"}),
        1.0,
        0.0,
        0.5,
        0,
    )
    assert w.select_method(task).selected_method != "guess"


def test_main_returns_zero():
    mod = load()
    assert mod.main([]) == 0
