from __future__ import annotations

import importlib.util
import itertools
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_warranted_parity_exact.py"
)
SPEC = importlib.util.spec_from_file_location("ocm_warranted_parity_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_standard_basis_learns_parity() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (0, 0, 0, 0, 0, 0))
    queries = tuple(M.standard_basis(3, i) for i in range(3))
    assert M.current_function_transcript(world, queries) == world.theta


def test_full_current_oracle_cannot_see_backup_provenance() -> None:
    left = M.WarrantedParityWorld((1, 0, 1), 2, (0, 0, 0, 0, 0, 0))
    right = M.WarrantedParityWorld((1, 0, 1), 2, (1, 1, 1, 1, 1, 1))
    queries = tuple(itertools.product((0, 1), repeat=3))
    assert M.current_function_transcript(left, queries) == M.current_function_transcript(
        right, queries
    )


def test_backup_preserves_warrant_after_primary_revocation() -> None:
    world = M.WarrantedParityWorld((1, 0), 1, (1, 0))
    query = M.standard_basis(2, 0)
    records = world.surviving_records(0, frozenset({"P:0"}))
    result = M.warranted_prediction(records, query)
    assert result["status"] == "WARRANTED"
    assert result["label"] == 1
    assert M.verify_positive_certificate(
        records,
        query,
        result["label"],
        result["positive_certificate_coefficients"],
    )


def test_no_backup_forces_abstention_with_disagreement_witness() -> None:
    world = M.WarrantedParityWorld((1, 0), 1, (0, 0))
    query = M.standard_basis(2, 0)
    records = world.surviving_records(0, frozenset({"P:0"}))
    result = M.warranted_prediction(records, query)
    assert result["status"] == "ABSTAIN"
    assert M.verify_disagreement_witness(
        records, query, result["negative_disagreement_witness"]
    )


def test_row_span_is_exact_warrant_criterion() -> None:
    theta = (1, 0, 1)
    records = (
        M.CertifiedEquation("a", (1, 1, 0), M.dot((1, 1, 0), theta), None, False),
        M.CertifiedEquation("b", (0, 1, 1), M.dot((0, 1, 1), theta), None, False),
    )
    warranted_query = M.xor_vectors((records[0].vector, records[1].vector), 3)
    assert M.warranted_prediction(records, warranted_query)["status"] == "WARRANTED"
    assert M.warranted_prediction(records, (0, 1, 0))["status"] == "ABSTAIN"


def test_query_complexity_formula() -> None:
    assert M.deterministic_query_complexity(5, 3) == {
        "exact_current_parity_membership_queries": 5,
        "additional_warrant_queries": 15,
        "exact_lifecycle_queries_total": 20,
    }


def test_lifecycle_profile_is_injective() -> None:
    worlds = M.enumerate_worlds(2, 2)
    profiles = {M.lifecycle_profile(world) for world in worlds}
    assert len(profiles) == len(worlds) == 64


def test_delete_everything_is_caught_by_useful_retention_control() -> None:
    world = M.WarrantedParityWorld((1,), 1, (1,))
    records = world.surviving_records(0, frozenset({"P:0"}))
    assert M.warranted_prediction(records, (1,))["status"] == "WARRANTED"


def test_retain_without_support_is_caught() -> None:
    world = M.WarrantedParityWorld((1,), 1, (0,))
    records = world.surviving_records(0, frozenset({"P:0"}))
    assert M.warranted_prediction(records, (1,))["status"] == "ABSTAIN"


def test_invalid_backup_width_is_rejected() -> None:
    try:
        M.WarrantedParityWorld((1, 0), 2, (1, 0, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid backup width was accepted")


def test_full_calibration_passes() -> None:
    result = M.run_exact_calibration()
    assert result["terminal"] == "PASS_NATURAL_CLASS_WARRANTED_PARITY_CALIBRATION"
    assert result["family"]["lifecycle_concepts"] == 512
    assert result["query_complexity"]["exact_lifecycle_queries_total"] == 9
