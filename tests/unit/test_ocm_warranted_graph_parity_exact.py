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
    / "ocm_warranted_graph_parity_exact.py"
)
SPEC = importlib.util.spec_from_file_location(
    "ocm_warranted_graph_parity_exact", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_optional_edge_count_is_quadratic() -> None:
    for n in range(1, 8):
        assert len(M.optional_edge_universe(n)) == n * (n - 1) // 2


def test_current_function_is_blind_to_optional_graph() -> None:
    left = M.GraphParityWorld((1, 0, 1, 0), (0,) * 6)
    right = M.GraphParityWorld((1, 0, 1, 0), (1,) * 6)
    assert tuple(left.current_function(v) for v in range(1, 5)) == tuple(
        right.current_function(v) for v in range(1, 5)
    )


def test_present_optional_edge_gives_two_edge_path_certificate() -> None:
    world = M.GraphParityWorld((1, 0, 1, 0), (1, 0, 0, 0, 0, 0))
    edge = M.optional_edge_universe(4)[0]
    records, vertex = M.challenge_records(world, edge)
    result = M.warranted_vertex(records, 4, vertex)
    assert result["status"] == "WARRANTED"
    assert len(result["path_record_ids"]) == 2
    assert M.verify_path_certificate(
        records, 4, vertex, result["path_record_ids"], result["label"]
    )


def test_absent_optional_edge_gives_cut_flip_certificate() -> None:
    world = M.GraphParityWorld((1, 0, 1, 0), (0,) * 6)
    edge = M.optional_edge_universe(4)[0]
    records, vertex = M.challenge_records(world, edge)
    result = M.warranted_vertex(records, 4, vertex)
    assert result["status"] == "ABSTAIN"
    assert M.verify_flip_certificate(
        records, 4, vertex, result["negative_flip_component"]
    )


def test_graphical_warrant_is_root_connectivity() -> None:
    theta = (1, 0, 1)
    records = M.records_for_general_graph(3, theta, ((0, 1), (1, 2)))
    assert M.warranted_vertex(records, 3, 2)["status"] == "WARRANTED"
    assert M.warranted_vertex(records, 3, 3)["status"] == "ABSTAIN"


def test_lifecycle_profile_recovers_optional_graph() -> None:
    worlds = tuple(
        M.GraphParityWorld((0, 0, 0, 0), bits)
        for bits in itertools.product((0, 1), repeat=6)
    )
    assert len({M.lifecycle_profile(world) for world in worlds}) == 64


def test_exact_query_complexity() -> None:
    assert M.query_complexity(4) == {
        "current_function_queries": 4,
        "additional_warrant_queries": 6,
        "lifecycle_queries": 10,
    }


def test_zero_error_batch_frontier() -> None:
    N = 6
    for B in range(N + 1):
        for Q in range(N + 1):
            for A in range(N + 1):
                assert M.exact_batch_frontier(N, B, Q, A) == (B + Q + A >= N)


def test_randomized_summary_lower_bound_endpoints() -> None:
    assert M.summary_lower_bound_bits(6, 0.0) == 6
    assert abs(M.summary_lower_bound_bits(6, 0.5)) < 1e-12


def test_delete_everything_fails_when_path_survives() -> None:
    world = M.GraphParityWorld((1, 0, 1, 0), (1, 0, 0, 0, 0, 0))
    records, vertex = M.challenge_records(world, M.optional_edge_universe(4)[0])
    assert M.warranted_vertex(records, 4, vertex)["status"] == "WARRANTED"


def test_retain_everything_fails_without_path() -> None:
    world = M.GraphParityWorld((1, 0, 1, 0), (0,) * 6)
    records, vertex = M.challenge_records(world, M.optional_edge_universe(4)[0])
    assert M.warranted_vertex(records, 4, vertex)["status"] == "ABSTAIN"


def test_invalid_optional_profile_is_rejected() -> None:
    try:
        M.GraphParityWorld((1, 0, 1), (0, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid optional profile was accepted")


def test_full_calibration_passes() -> None:
    result = M.run_exact_calibration()
    assert result["terminal"] == "PASS_GRAPH_PARITY_QUADRATIC_WARRANT_GAP"
    assert result["family"]["warrant_lift_bits_given_exact_current_function"] == 6
    assert result["general_graphical_warrant_theorem"]["graph_theta_vertex_checks"] == 65536
