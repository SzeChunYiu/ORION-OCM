"""Unit tests for the lane-200 rectangularity / direct-product decomposition checker."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "research" / "orion-machine" / "reference" / "ocm_lane200_decomposition_exact.py"


def load():
    spec = importlib.util.spec_from_file_location("ocm_lane200_decomposition_exact", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load()
RESULT = M.run_exact_calibration()


def test_terminal_and_denominators() -> None:
    assert RESULT["terminal"] == "PASS_EVERY_REGISTERED_CLASS_IS_A_DIRECT_PRODUCT_OF_PARENT_PROBLEMS"
    d = RESULT["denominators"]
    assert d == {
        "registered_classes": 3,
        "registered_worlds": 2048,
        "planted_classes": 3,
        "planted_worlds": 648,
        "mutations_planted": 4,
    }


def test_every_registered_class_is_rectangular_blind_and_additive() -> None:
    rows = {r["name"]: r for r in RESULT["registered_classes"]}
    assert set(rows) == {"WPL_V1_p3_h2", "WPL_V2_p3_h2", "WGPL_n4"}
    for name, r in rows.items():
        assert r["rectangularity"]["rectangular"] is True
        assert r["rectangularity"]["pairs"] == r["rectangularity"]["product"]
        assert r["blindness"]["blind"] is True
        assert r["blindness"]["leaked_warrant_coordinates"] == []
        assert r["warrant_lift"]["warrant_lift_bits"] == 6.0
        assert r["additivity"]["registered_is_additive"] is True
        assert r["additivity"]["registered_meets_lower_bound"] is True
        assert r["product_learner"]["all_exact"] is True
        assert r["disposition"] == "DIRECT_PRODUCT_OF_PARENT_PROBLEMS"
    assert rows["WPL_V2_p3_h2"]["additivity"]["registered_lifecycle"] == 9
    assert rows["WGPL_n4"]["additivity"]["registered_lifecycle"] == 10
    assert rows["WGPL_n4"]["product_learner"]["current_queries"] == [4]
    assert rows["WGPL_n4"]["product_learner"]["warrant_queries"] == [6]


def test_planted_coupled_classes_fire() -> None:
    rows = {r["name"]: r for r in RESULT["planted_coupled_classes"]}
    assert rows["COUPLED_FULL"]["rectangularity"]["rectangular"] is False
    assert rows["COUPLED_FULL"]["blindness"]["leaked_warrant_coordinates"] == [0, 1, 2, 3, 4, 5]
    assert rows["COUPLED_FULL"]["warrant_lift"]["warrant_lift_bits"] == 0.0
    assert rows["COUPLED_HALF"]["blindness"]["leaked_warrant_coordinates"] == [0]
    assert rows["COUPLED_HALF"]["warrant_lift"]["warrant_lift_bits"] == 5.0
    assert rows["COUPLED_FORCED"]["warrant_lift"]["fibres_equal_size"] is False
    assert rows["COUPLED_FORCED"]["warrant_lift"]["max_fibre"] == 64
    assert rows["COUPLED_FORCED"]["warrant_lift"]["min_fibre"] == 32
    assert all(r["fired"] for r in rows.values())


def test_mutations_applied_and_detected() -> None:
    for name, row in RESULT["mutation_controls"].items():
        assert row["applied"] is True, name
        assert row["detected"] is True, name


def test_registered_classes_are_the_committed_modules() -> None:
    for name in (
        "ocm_warranted_parity_exact",
        "ocm_warranted_parity_distinct_paths_exact",
        "ocm_warranted_graph_parity_exact",
    ):
        assert name in sys.modules
        assert Path(sys.modules[name].__file__).parent == MODULE_PATH.parent


def test_authority_claims_nothing() -> None:
    assert RESULT["authority"]["novelty_established"] is False
    assert RESULT["authority"]["architecture_separation"] is False
    assert RESULT["authority"]["finite_enumeration_only"] is True
