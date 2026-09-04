"""Lane #202 exact checker: the toy core-memory-time frontier must be exact, must be
able to fail for each registered reason, and must report CANNOT_CHECK distinctly."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "ocm_lane202_core_frontier_exact.py"


def _load():
    spec = importlib.util.spec_from_file_location("ocm_lane202_core_frontier_exact", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def result(mod):
    return mod.run_exact_calibration()


def test_exhaustive_enumeration_denominators_are_real(result):
    m = result["model"]
    assert m["programs_per_length"] == {1: 28, 2: 784, 3: 21952, 4: 614656}
    assert m["programs_enumerated"] == 28 + 784 + 21952 + 614656 == 637420
    assert m["bits_per_instruction"] == 5 and m["distinct_instructions"] == 28
    assert m["runs_executed"] == 637420 * 4


def test_registered_frontier_and_subadditivity_witnesses(result):
    t = result["tables"]
    assert t["IDENTITY_ENDPOINTS"]["C_bits"] == [None, 10, 10, 5, 5, 5, 5, 5]
    assert t["IS_ZERO"]["C_bits"] == [None] + [15] * 7
    assert t["PARITY"]["C_bits"] == [None] * 8  # unsolvable within the cap, never 0
    assert result["frontier"]["qualifying_families"] == ["IDENTITY_ENDPOINTS"]
    w = result["subadditivity"]["failure_witness"]
    assert (w["F1"], w["F2"], w["t"], w["C_F1"], w["C_F2"], w["C_union"]) == (
        "IS_ZERO_NONZERO",
        "IS_ZERO_ZERO",
        2,
        5,
        5,
        15,
    )
    assert result["frontier_census"] == {
        "examples": [],
        "families_scanned": 6560,
        "with_two_finite_strict_decreases": 0,
    }


def test_monotonicity_and_infeasibility_are_measured_not_assumed(result):
    assert result["monotone_in_time"] == {"comparisons": 98, "holds": True, "violations": []}
    assert result["monotone_in_family"]["holds"] and result["monotone_in_family"]["comparisons"] == 72
    u = result["unsolvable"]
    assert (u["count"], u["denominator"]) == (32, 112)
    assert all(v is None or v > 0 for row in result["tables"].values() for v in row["C_bits"])


def test_no_alarm_two_independent_computations_agree(result):
    agreement = result["controls"]["no_alarm_independent_agreement"]
    assert agreement == {"agree": 112, "denominator": 112, "disagreements": [], "holds": True}


def test_planted_failures_fire(result):
    p = result["controls"]["planted_failures"]
    assert p["P1_wrong_claimed_table_rejected"]["fired"] is True
    assert p["P1_wrong_claimed_table_rejected"]["comparison"]["mismatches"] == [{"claimed": 10, "enumerated": 5, "t": 4}]
    assert p["P2_inconsistent_family_refused"]["fired"] is True
    assert p["P2_inconsistent_family_refused"]["error_type"] == "InconsistentFamily"


def test_mutations_asserted_applied_and_detected(result):
    mc = result["controls"]["mutation_controls"]
    assert set(mc) == {"M1_simulator_ignores_time_bound", "M2_enumerator_skips_length_2", "M3_bits_function_returns_len"}
    for name, case in mc.items():
        assert case["applied"] is True, name
        assert case["detected"] is True, name
    assert mc["M2_enumerator_skips_length_2"]["agreement"]["agree"] < mc["M2_enumerator_skips_length_2"]["agreement"]["denominator"]
    assert result["controls"]["M0_unmutated"] == {"applied": True, "all_checks_pass": True}


def test_inconsistent_family_is_a_distinct_error_not_unsolvable(mod):
    with pytest.raises(mod.InconsistentFamily):
        mod.TaskFamily("BAD", [(1, 0), (1, 1)])


def test_exit_code_contract(mod, monkeypatch, capsys):
    assert mod.main([]) == 0
    capsys.readouterr()

    def boom_cannot(*a, **k):
        raise mod.CannotCheck("planted")

    monkeypatch.setattr(mod, "run_exact_calibration", boom_cannot)
    assert mod.main([]) == 2
    assert json.loads(capsys.readouterr().out)["terminal"] == "CANNOT_CHECK"

    def boom_fail(*a, **k):
        raise AssertionError("planted")

    monkeypatch.setattr(mod, "run_exact_calibration", boom_fail)
    assert mod.main([]) == 1
    assert json.loads(capsys.readouterr().out)["terminal"] == "FAIL"


def test_authority_fields_claim_nothing(result):
    a = result["authority"]
    assert a["finite_toy_model_only"] is True
    assert a["novelty_established"] is False
    assert a["architecture_separation"] is False
    assert a["transformer_equivalence_proved_here"] is False
