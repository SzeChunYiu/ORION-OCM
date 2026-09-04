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
    / "ocm_warranted_parity_distinct_paths_exact.py"
)
SPEC = importlib.util.spec_from_file_location(
    "ocm_warranted_parity_distinct_paths_exact", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_current_parity_is_identified_by_basis_queries() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (0,) * 6)
    queries = tuple(M.standard_basis(3, index) for index in range(3))
    assert M.current_function_transcript(world, queries) == world.theta


def test_full_current_function_is_blind_to_proof_path_profile() -> None:
    left = M.WarrantedParityWorld((1, 0, 1), 2, (0,) * 6)
    right = M.WarrantedParityWorld((1, 0, 1), 2, (1,) * 6)
    queries = tuple(itertools.product((0, 1), repeat=3))
    assert M.current_function_transcript(left, queries) == M.current_function_transcript(
        right, queries
    )


def test_backup_vector_is_distinct_from_revoked_primary() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (1,) * 6)
    for coordinate in range(3):
        primary = M.standard_basis(3, coordinate)
        for context in range(2):
            assert world.backup_vector(coordinate, context) != primary


def test_distinct_bridge_path_retains_supported_coordinate() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (1, 1, 0, 0, 0, 0))
    query = M.standard_basis(3, 0)
    for context in range(2):
        records = world.surviving_records(
            world.scope_id(0, context), frozenset({"P:0"})
        )
        result = M.warranted_prediction(records, query)
        assert result["status"] == "WARRANTED"
        assert f"B:0:{context}" in result["positive_certificate_record_ids"]
        assert f"P:{world.bridge_coordinate(0, context)}" in (
            result["positive_certificate_record_ids"]
        )
        assert M.verify_positive_certificate(
            records,
            query,
            result["label"],
            result["positive_certificate_coefficients"],
        )


def test_absent_path_forces_abstention_and_negative_witness() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (0,) * 6)
    query = M.standard_basis(3, 0)
    records = world.surviving_records(
        world.scope_id(0, 0), frozenset({"P:0"})
    )
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
    warranted = M.xor_vectors((records[0].vector, records[1].vector), 3)
    assert M.warranted_prediction(records, warranted)["status"] == "WARRANTED"
    assert M.warranted_prediction(records, (0, 1, 0))["status"] == "ABSTAIN"


def test_exact_query_complexity_formula() -> None:
    assert M.query_complexity(5, 3) == {
        "current_function_queries": 5,
        "additional_warrant_queries": 15,
        "lifecycle_queries": 20,
    }


def test_lifecycle_profile_is_injective() -> None:
    worlds = M.enumerate_worlds(2, 2)
    assert len({M.lifecycle_profile(world) for world in worlds}) == len(worlds)


def test_delete_everything_fails_useful_retention() -> None:
    world = M.WarrantedParityWorld((1, 0), 1, (1, 0))
    records = world.surviving_records(
        world.scope_id(0, 0), frozenset({"P:0"})
    )
    assert M.warranted_prediction(records, (1, 0))["status"] == "WARRANTED"


def test_retain_everything_fails_warrant() -> None:
    world = M.WarrantedParityWorld((1, 0), 1, (0, 0))
    records = world.surviving_records(
        world.scope_id(0, 0), frozenset({"P:0"})
    )
    assert M.warranted_prediction(records, (1, 0))["status"] == "ABSTAIN"


def test_other_scoped_backups_do_not_leak_into_challenge() -> None:
    world = M.WarrantedParityWorld((1, 0, 1), 2, (0, 1, 1, 1, 1, 1))
    records = world.surviving_records(
        world.scope_id(0, 0), frozenset({"P:0"})
    )
    assert all(
        record.scope in (None, world.scope_id(0, 0)) for record in records
    )
    assert M.warranted_prediction(records, (1, 0, 0))["status"] == "ABSTAIN"


def test_invalid_dimension_is_rejected() -> None:
    try:
        M.WarrantedParityWorld((1,), 1, (1,))
    except ValueError:
        pass
    else:
        raise AssertionError("dimension-one distinct-path world was accepted")


def test_full_calibration_passes() -> None:
    result = M.run_exact_calibration()
    assert result["terminal"] == "PASS_NATURAL_CLASS_DISTINCT_PROOF_PATHS"
    assert result["family"]["lifecycle_concepts"] == 512
    assert result["query_complexity"]["lifecycle_queries"] == 9
    assert result["linear_warrant_theorem"]["matrix_theta_query_checks"] == 37440
