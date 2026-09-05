"""Missing data and small samples must not become scientific support."""
from dataclasses import replace

import pytest

from ocm.evaluation import stats as ST
from ocm.evaluation import m7_comparison as M7
from ocm.evaluation import m12_lifetime_eval as M12


@pytest.mark.parametrize("paired", [M7.paired, M12.paired])
def test_pairing_refuses_truncation_and_non_boolean_observations(paired):
    for a, b in [([True], [True, False]), (["CANNOT_CHECK"], [True]), ([1], [True])]:
        with pytest.raises(ValueError):
            paired(a, b)


def test_one_agreement_does_not_prove_population_equivalence():
    result = ST.tost_equivalence(ST.PairedComparison(1, 1, 1, 0, 0))
    assert result["verdict"] == "INCONCLUSIVE"
    assert result["ci_90"][0] < 0 < result["ci_90"][1]


@pytest.mark.parametrize("values", [(1, 2, 1, 0, 0), (10, 5, 5, 4, 2), (1, 1, 0, 0, 0), (True, 1, 1, 0, 0)])
def test_paired_contingency_table_must_exist(values):
    with pytest.raises(ValueError):
        ST.PairedComparison(*values)


def test_empty_run_inventory_never_passes_operational_gate():
    assert M12.kill_gates({})["hits"] > 0


def test_truthy_replication_flag_never_promotes_science():
    assert M12.exit_gate({"tier6_broad": {"holds": True}}, {}, True) != "FULL_OCM_RESIDUAL_SUPPORTED"


def test_equal_length_transfer_vectors_do_not_override_different_case_identities():
    left = {"phases": {"E": {"cells": {"a": {"expected": "TRANSFER", "result": "TRANSFER"}}}}}
    right = {"phases": {"E": {"cells": {"b": {"expected": "TRANSFER", "result": "TRANSFER"}}}}}
    with pytest.raises(ValueError, match="case identities"):
        M12.paired_family(left, right, "E_transfer")


def test_invalid_lifetime_data_cannot_pass_through_caller_gate_summary():
    result = M12.claim_tiers({"ocm": {}, "whole_system_parent": {}}, {"hits": 0}, {})
    assert all(x["holds"] is False for x in result.values())


def test_output_is_explicit_and_exclusive(tmp_path):
    from ocm.evaluation.output import new_output_path, write_result
    with pytest.raises(SystemExit):
        new_output_path([], "test")
    path = new_output_path(["--out", str(tmp_path / "fresh.json")], "test")
    write_result(path, {"scope": "engineering"})
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        write_result(path, {"scope": "protected"})
    with pytest.raises(SystemExit):
        new_output_path(["--out", str(path)], "test")
    assert path.read_bytes() == before


def test_unconditional_paired_interval_has_nominal_coverage_on_exact_small_multinomial_grid():
    from fractions import Fraction
    from math import factorial
    for n in range(1, 9):
        intervals = {(a, b): ST.tost_equivalence(ST.PairedComparison(n, a, b, a, b))["ci_90"]
                     for a in range(n + 1) for b in range(n - a + 1)}
        for ia in range(6):
            for ib in range(6 - ia):
                pa, pb = Fraction(ia, 5), Fraction(ib, 5)
                difference = pa - pb
                coverage = Fraction(0)
                for (a, b), (lo, hi) in intervals.items():
                    c = n - a - b
                    if Fraction(lo) <= difference <= Fraction(hi):
                        coverage += (Fraction(factorial(n), factorial(a) * factorial(b) * factorial(c))
                                     * pa**a * pb**b * (1 - pa - pb)**c)
                assert coverage >= Fraction(9, 10), (n, pa, pb, coverage)


def test_transfer_precision_uses_each_ordering_instead_of_repeating_the_first(monkeypatch):
    from ocm.evaluation import m9_transfer_eval as M9
    monkeypatch.setattr(M9, "ORDERINGS", {"first": ("good",), "second": ("bad",)})
    def lifetime(arm, order):
        success = int(order == ("good",))
        first = {"success": 1, "tasks": 1, "route": "LEARN", "unauthorized_attempts": 0}
        later = {"success": success, "tasks": 1, "route": "TRANSFER", "unauthorized_attempts": 0}
        return {"later_domain_costs": [1], "domains": [first, later]}
    monkeypatch.setattr(M9, "lifetime", lifetime)
    result = M9.run()
    assert result["transfer_precision"] == {"attempted": 2, "beneficial": 1, "precision": 0.5}
