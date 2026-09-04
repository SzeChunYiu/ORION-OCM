from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_warrant_blindness_exact.py"
)
SPEC = importlib.util.spec_from_file_location("ocm_warrant_blindness_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_current_function_oracle_is_warrant_blind() -> None:
    worlds = M.concepts(6)
    transcripts = {
        M.current_oracle_transcript(world, tuple(range(20)))
        for world in worlds
    }
    assert len(transcripts) == 1


def test_exact_success_formula() -> None:
    for N in range(7):
        for q in range(N + 1):
            observed = M.exhaustive_best_exact_success(N, tuple(range(q)))
            assert observed == M.exact_success_probability_uniform(N, q)


def test_hamming_error_formula() -> None:
    for N in range(7):
        for q in range(N + 1):
            for a in range(N - q + 1):
                observed = M.exhaustive_min_hamming_error(
                    N,
                    tuple(range(q)),
                    tuple(range(q, q + a)),
                )
                assert observed == M.expected_hamming_error_uniform(N, q, a)


def test_zero_error_frontier() -> None:
    for N in range(8):
        for q in range(N + 1):
            for a in range(N + 1):
                assert M.zero_error_possible(N, q, a) == (q + a >= N)


def test_registered_under_resourced_witness() -> None:
    assert M.exact_success_probability_uniform(8, 3) == 1 / 32
    assert M.expected_hamming_error_uniform(8, 3, 2) == 1.5
    assert not M.zero_error_possible(8, 3, 2)


def test_closure_record_suffices() -> None:
    concept = M.LifecycleConcept((1, 0, 1, 1, 0))
    closure_record = concept.warrant_bits
    assert tuple(
        concept.revoke_response(index) for index in range(len(closure_record))
    ) == closure_record


def test_invalid_resources_are_rejected() -> None:
    try:
        M.expected_hamming_error_uniform(3, 4)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid query budget was accepted")


def test_duplicate_query_indices_do_not_create_information() -> None:
    observed = M.exhaustive_best_exact_success(4, (0, 0, 0))
    assert observed == M.exact_success_probability_uniform(4, 1)


def test_full_sweep_passes() -> None:
    result = M.run_exact_calibration()
    assert result["terminal"] == "PASS_WARRANT_ORACLE_SEPARATION_FINITE_CHECKS"
    assert result["sweep"]["planted_false_completion_worlds"] > 0
