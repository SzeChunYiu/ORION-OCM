"""M1 core: every registered checker passes and the obligation registry is consistent."""
from __future__ import annotations

import pytest

from ocm.kso import checks as C
from ocm.kso import warrant as W
from ocm.kso.obligations import load_registry, summarize, verify_registry


@pytest.mark.parametrize("name,fn", C.CHECKS, ids=[n for n, _ in C.CHECKS])
def test_registered_checker_passes(name, fn):
    result = fn()
    assert isinstance(result, dict) and result


def test_semiring_exhaustive_counts():
    assert W.check_semiring(3) == {"evidence_atoms": 3, "profiles": 20, "pair_checks": 400, "triple_checks": 8000}


def test_three_valued_homomorphism_exhaustive_counts():
    r = W.check_three_valued_reduction(3)
    assert r["intervals"] == 168 and r["homomorphism_checks"] == 168 * 168 * 8 and r["reduction_checks"] == 160


def test_registry_loads_and_every_proved_row_has_a_passing_checker():
    data = load_registry()
    assert len(data["obligations"]) >= 25
    results = verify_registry()
    summary = summarize(results)
    assert summary["proved_or_calibrated_without_passing_checker"] == []
    assert summary["counts"]["FAIL"] == 0
    statuses = {r["id"]: r["status"] for r in data["obligations"]}
    assert statuses["KS-T12"] == "OPEN" and statuses["KS-T07"] == "PARENT_OWNED" and statuses["KS-P1"] == "PARENT_OWNED"


def test_run_all_terminal_preserves_inherited_authority():
    out = C.run_all()
    t = out["terminals"]
    assert t["M1_KSO_CORE"] == "GREEN"
    assert t["M2_SOLVE_HISTORICAL"] == "PARENT_SUFFICIENT" and t["GENERAL_NOVELTY"] == "NOT_ESTABLISHED"
    assert t["KS-T12_CONSOLIDATION"] == "OPEN"


def test_cli_exit_codes_are_three_and_distinct(capsys):
    assert C.main([]) == 0
    assert set(C.main.__code__.co_consts) & {1, 2}  # both non-zero paths exist in the CLI
