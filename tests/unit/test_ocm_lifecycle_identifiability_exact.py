from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "orion-machine"
    / "reference"
    / "ocm_lifecycle_identifiability_exact.py"
)
SPEC = importlib.util.spec_from_file_location(
    "ocm_lifecycle_identifiability_exact", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def test_rank_and_basis_completion() -> None:
    rows = ((1, 1, 0, 0), (0, 1, 1, 0))
    complement = M.complement_rows(rows, 4)
    assert M.gf2_rank(rows, 4) == 2
    assert len(complement) == 2
    assert M.gf2_rank((*rows, *complement), 4) == 4


def test_exact_lifecycle_profile_is_injective() -> None:
    result = M.run_exact_calibration()
    counts = result["exact_counts"]
    assert counts["latent_lifecycle_worlds"] == 1024
    assert counts["distinct_full_future_profiles"] == 1024
    assert counts["full_profile_collisions"] == 0


def test_planted_coordinate_drop_creates_real_collisions() -> None:
    result = M.run_exact_calibration()
    counts = result["exact_counts"]
    assert counts["distinct_profiles_after_planted_coordinate_drop"] == 512
    assert counts["planted_collision_groups"] == 512
    assert counts["worlds_per_planted_collision_group"] == 2


def test_candidate_information_frontier_is_tight_on_instance() -> None:
    result = M.run_exact_calibration()
    theorem = result["theorem_instance"]
    assert theorem["M"] == 1024
    assert theorem["ceil_log2_M"] == 10
    assert theorem["instantiated_bound"].endswith(">= 10")


def test_one_witness_retention_trilemma_is_live() -> None:
    trilemma = M.one_witness_retention_trilemma()
    assert trilemma["training_transcripts_identical"] is True
    assert trilemma["always_retain_is_unsound"] is True
    assert trilemma["always_retract_is_destructive"] is True
    assert len(trilemma["resolution_requires_one_of"]) == 3


def test_negative_resources_are_rejected() -> None:
    try:
        M.lifecycle_capacity_bits(-1, 0, 0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative resource value was accepted")


def test_small_parameter_grid_obeys_profile_formula() -> None:
    families = (
        M.LifecycleFamily(
            module_count=2,
            endpoint_matrix=((1, 1),),
            endpoint_rhs=(0,),
            alternate_scopes_per_module=1,
        ),
        M.LifecycleFamily(
            module_count=3,
            endpoint_matrix=((1, 1, 0),),
            endpoint_rhs=(0,),
            alternate_scopes_per_module=2,
        ),
        M.LifecycleFamily(
            module_count=4,
            endpoint_matrix=((1, 0, 1, 0), (0, 1, 0, 1)),
            endpoint_rhs=(0, 1),
            alternate_scopes_per_module=1,
        ),
    )
    for family in families:
        groups = M.profile_groups(family)
        assert len(groups) == 2 ** family.lifecycle_dimension
        assert all(len(group) == 1 for group in groups.values())
