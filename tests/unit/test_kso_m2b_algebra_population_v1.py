"""KSO M2b — algebra population through the instruction channel and the quadratic solve (``kso_m2b_algebra_population_v1.py``)."""

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_m2b_algebra_population_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_m2b_algebra_population_v1", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def receipt(mod):
    return mod.run(per_family=5)


def test_population_is_through_the_instruction_channel_and_dense(receipt):
    p = receipt["population"]
    assert p["atoms"] == 24 and p["hyperedges"] == 60
    assert p["P1_dense"]["isolated"] == 0 and p["meter"]["admit"] == 24
    assert all(p["genome"].values())


def test_solve_is_exact_on_every_dev_instance_and_gated_by_labels(receipt):
    g = receipt["G1_exact_vs_oracle"]
    assert g == {"n": 30, "exact": 30, "attributions": {}}
    fired = {(r["family"], tuple(r["fired_procedures"])) for r in receipt["instances"]}
    assert ("COMPLEX_PAIR", ("proc:quadratic_formula", "proc:complete_square")) in fired
    assert ("RATIONAL_DISTINCT", ("proc:quadratic_formula", "proc:complete_square", "proc:factor")) in fired
    assert ("NO_EQUATION", ()) in fired
    assert all(r["navigation_outcome"] == "GAP_NOT_FOUND" for r in receipt["instances"] if r["family"] == "NO_EQUATION")
    assert all(r["warrant"] == "UNWARRANTED_PENDING_EXACT_CHECKER" for r in receipt["instances"])
    assert receipt["terminal"] == "M2B_POPULATED_AND_SOLVED_ON_DEV"


def test_retraction_both_directions_on_the_algebra_graph(receipt):
    r = receipt["retraction_both_directions"]
    assert r["revocations"] == 12 and r["dead_zero"] == r["unreachable_unchanged"] == r["restored"] == 12
    assert r["parent_raised"] >= 1


def test_planted_constraint_revocation_blocks_procedures(mod):
    pop, _ = mod.populate_from_source()
    pairs, _ = mod.alg.generate_split("dev", "ALGEBRA-DEV-20260904", 1)
    inst, ans = next((i, a) for i, a in pairs if i.family == "RATIONAL_DISTINCT")
    row = mod.solve_instance(pop, inst, ans)
    assert set(row["fired_procedures"]) == {"proc:quadratic_formula", "proc:complete_square", "proc:factor"} and row["exact"]
    plant = mod.m1.Population(pop.space, pop.governed, pop.base_index, pop.base_status, {}, {}, frozenset({pop.base_index["con:a_nonzero"]}), ())
    assert mod.solve_instance(plant, inst, ans)["fired_procedures"] == []


def test_root_claims_follow_the_registered_schema(receipt):
    for r in receipt["instances"]:
        for rc in r["root_claims"]:
            assert set(rc) == {"atom_id", "kind", "variable", "expr", "root", "domain", "label_channel", "produced_by"}
            assert rc["kind"] == "ROOT_CLAIM" and rc["label_channel"] == "INSTRUCTION" and rc["domain"] in {"Q", "C"}
