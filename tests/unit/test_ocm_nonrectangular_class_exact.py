"""Unit tests for the lane-200 revival checker: rectangularity criterion,
decomposability, and the version-space warrant class."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "research" / "orion-machine" / "reference" / "ocm_nonrectangular_class_exact.py"


def load():
    spec = importlib.util.spec_from_file_location("ocm_nonrectangular_class_exact", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load()
RESULT = M.run_exact_calibration()


def test_terminal_and_denominators() -> None:
    assert RESULT["terminal"] == "NATURAL_NONRECTANGULAR_CLASSES_EXIST__ONE_NATURAL_NONDECOMPOSABLE_INSTANCE_REGISTERED__PARENT_OWNED"
    d = RESULT["denominators"]
    assert d["registered_worlds_R0"] == 2048
    assert d["planted_worlds_non_R0"] == 648
    assert d["affinity_classes_enumerated"] == 15 + 255 + 65535
    assert d["named_families"] == 4
    assert d["mutations_planted"] == 4
    assert d["atms_label_cells_checked"] > 0


def test_R0_first_pass_claim_reverified_with_firing_control() -> None:
    r0 = RESULT["A_coordinate_rectangularity"]
    assert {r["name"] for r in r0["registered"]} == {"WPL_V1_p3_h2", "WPL_V2_p3_h2", "WGPL_n4"}
    assert all(r["rectangular"] for r in r0["registered"])
    assert {r["name"] for r in r0["planted_non_rectangular"]} == {"COUPLED_FULL", "COUPLED_HALF", "COUPLED_FORCED"}
    assert r0["control_fired"] is True


def test_planted_non_rectangular_classes_are_decomposable() -> None:
    rows = {r["name"]: r for r in RESULT["B_decomposability"]["first_pass_planted_classes"]}
    for name, r in rows.items():
        assert r["R0_rectangular"] is False, name
        assert r["interaction_term"] == 0, name
        assert r["certified"]["decomposability_certified"] is True, name
        assert r["D_joint"] == r["joint_lower_bound_counting"], name
    assert rows["COUPLED_HALF"]["D_joint"] == 8
    assert rows["COUPLED_FORCED"]["D_joint"] == 9


def test_pointer_control_fires_and_rectangular_control_does_not() -> None:
    p = RESULT["B_decomposability"]["pointer_chasing_control"]
    assert p["D_joint"] == 3 and p["B_first"]["cost"] == 4 and p["Z_first"]["cost"] == 4
    assert p["interaction_term"] == 1
    assert p["certified"]["nondecomposability_certified"] is True
    assert p["witness"] == {"tree_of_depth_D_joint_exists": True, "tree_of_depth_D_joint_minus_1_exists": False}
    r = RESULT["B_decomposability"]["rectangular_control"]
    assert r["interaction_term"] == 0 and r["certified"]["decomposability_certified"] is True


def test_affinity_census_equivalence() -> None:
    census = RESULT["C_version_space_warrant_class"]["affinity_census"]
    assert census["points_2"]["classes"] == 15 and census["points_3"]["classes"] == 255 and census["points_4"]["classes"] == 65535
    for c in census.values():
        assert c["affine_label_dependent"] == 0
        assert c["nonaffine_label_independent"] == 0
        assert c["affine_label_independent"] > 0 and c["nonaffine_label_dependent"] > 0
    assert census["points_3"]["affine_label_independent"] == 51
    assert census["points_4"]["affine_label_independent"] == 307


def test_named_families_rectangular_iff_affine() -> None:
    fams = {f["name"]: f for f in RESULT["C_version_space_warrant_class"]["named_families_4_points"]}
    assert set(fams) == {"LINEAR_F2^2", "MONO_CONJ_2", "LTF_2", "SINGLETONS_4"}
    assert fams["LINEAR_F2^2"]["affine"] is True and fams["LINEAR_F2^2"]["rectangular"] is True
    for name in ("MONO_CONJ_2", "LTF_2", "SINGLETONS_4"):
        assert fams[name]["affine"] is False and fams[name]["rectangular"] is False, name
        assert fams[name]["interaction_term"] == 0, name
    for f in fams.values():
        assert f["atms_label_mismatches"] == 0
        assert f["D_joint_simulated"] == f["D_joint"]


def test_singletons_5_is_natural_nonrectangular_and_nondecomposable() -> None:
    s5 = RESULT["D_registered_natural_nondecomposable_instance"]["SINGLETONS_5"]
    assert s5["affine"] is False and s5["rectangular"] is False
    assert s5["worlds_quotient"] == 160 and s5["behaviour_values"] == 5 and s5["warrant_values"] == 111
    assert s5["D_joint"] == 8 and s5["joint_lower_bound_counting"] == 8
    assert s5["B_first"]["cost"] == 9 and s5["B_first"]["D_first"] == 4 and s5["B_first"]["worst_fibre"] == 5
    assert s5["Z_first"]["cost"] == 9
    assert s5["B_first"]["cost_solver_b"] == 9 and s5["Z_first"]["cost_solver_b"] == 9
    assert s5["B_first"]["cost_simulated"] == 9 and s5["Z_first"]["cost_simulated"] == 9
    assert s5["interaction_term"] == 1
    assert s5["certified"]["interaction_lower_bound"] == 1 and s5["certified"]["nondecomposability_certified"] is True
    assert s5["atms_label_mismatches"] == 0
    s5e = RESULT["D_registered_natural_nondecomposable_instance"]["SINGLETONS_EMPTY_5"]
    assert s5e["interaction_term"] == 0
    ident = RESULT["D_registered_natural_nondecomposable_instance"]["subset_query_identity"]
    assert ident["points_5"]["identity_holds_on"] == ident["points_5"]["cells"] == 400
    assert ident["points_5"]["elimination_cells"] == 25


def test_mutations_applied_and_detected() -> None:
    for name, row in RESULT["mutation_controls"].items():
        assert row["applied"] is True, name
        assert row["detected"] is True, name


def test_solvers_agree_where_both_run() -> None:
    qc = M.pointer_chasing_class()
    allq = list(qc.b_queries) + list(qc.z_queries)
    a, tree = M.solve_weighted(qc.n, allq, tuple(range(qc.n)))
    b = M.solve_weighted_b(qc.n, allq, tuple(range(qc.n)))
    assert a == b == 3
    assert M.simulate_tree(tree, allq, tuple(range(qc.n)), range(qc.n)) == 3


def test_authority_claims_nothing() -> None:
    assert RESULT["authority"]["novelty_established"] is False
    assert RESULT["authority"]["separation_established"] is False
    assert RESULT["authority"]["architecture_separation"] is False
