"""Unit tests for the lane-201 representation-lattice checker."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "research" / "orion-machine" / "reference" / "ocm_lane201_lattice_exact.py"


def load():
    spec = importlib.util.spec_from_file_location("ocm_lane201_lattice_exact", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load()
RESULT = M.run_exact_calibration()


def test_terminal_and_denominators() -> None:
    assert RESULT["terminal"] == "PASS_REPRESENTATION_LATTICE_PARENT_OWNED_FINITE"
    assert RESULT["denominators"] == {
        "partitions_enumerated": 8483,
        "query_orders": 6,
        "planted_failures": 4,
        "mutations": 4,
    }


def test_meet_is_unique_coarsest_and_gap_is_hartley() -> None:
    a = RESULT["lattice"]["bits3_incompatible"]
    assert a["partitions_enumerated"] == 4140 and a["sufficient_partitions"] == 1
    assert a["meet_blocks"] == 8 and a["all_query_bits"] == 3 and a["max_single_query_bits"] == 1
    assert a["active_state_gap_bits"] == 2 and a["kernels_pairwise_incomparable"] is True
    b = RESULT["lattice"]["identical_kernels"]
    assert b["active_state_gap_bits"] == 0 and b["sufficient_partitions"] == 225
    c = RESULT["lattice"]["six_world_ceil"]
    assert c["partitions_enumerated"] == 203 and c["meet_blocks"] == 6 and c["all_query_bits"] == 3


def test_conservation_is_tight_and_forgetful_pays_more() -> None:
    k = RESULT["conservation"]
    assert k["meet_bits"] == 3 and k["orders"] == 6
    assert k["retentive_access_min"] == 3 and k["tight_for_some_order"] is True
    assert k["revisit_forgetful_access"] == 6 and k["revisit_retentive_access"] == 3
    assert k["forgetful_pays_more_on_revisit"] is True
    assert k["free_reopening_unsound_witness"] == [0, 1, 2, 3, 4, 5, 6, 7]


def test_reopening_exact_and_planted_deviations() -> None:
    r = RESULT["reopening"]
    assert r["exact"]["sound"] and r["exact"]["minimal"]
    assert r["planted_over"]["minimal"] is False and r["planted_over"]["sound"] is True
    assert r["planted_under"]["sound"] is False and r["planted_under"]["unsound_blocks"] == [[0, 2, 4, 6]]


def test_scope_intersection() -> None:
    s = RESULT["scopes"]
    assert s["intersection"]["sound"] is True and s["intersection"]["authorised_contexts"] == [1, 2]
    assert s["planted_union"]["sound"] is False and len(s["planted_union"]["countermodels"]) == 4
    assert s["equal_scopes_no_alarm"]["sound"] is True


def test_mutations_applied_and_detected() -> None:
    for name, row in RESULT["mutation_controls"].items():
        assert row == {"applied": True, "detected": True}, name


def test_lattice_primitives_directly() -> None:
    n, bits = M.bit_queries(2)
    m = M.meet((M.kernel(q) for q in bits), n)
    assert len(m) == 4
    j = M.join((M.kernel(q) for q in bits), n)
    assert len(j) == 1
    assert M.refines(m, M.kernel(bits[0])) and not M.refines(M.kernel(bits[0]), m)


def test_cannot_check_is_distinct() -> None:
    try:
        M.all_partitions(9)
    except M.CannotCheck:
        pass
    else:
        raise AssertionError("n=9 must be CANNOT_CHECK")


def test_authority_claims_nothing() -> None:
    a = RESULT["authority"]
    assert a["novelty_established"] is False
    assert a["architecture_separation"] is False
    assert a["certified_representation_residual"] is False
