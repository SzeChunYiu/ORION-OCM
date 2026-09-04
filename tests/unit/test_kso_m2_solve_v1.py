"""KnowledgeSpace.v1 M2 — the solve loop on ME-X1 (``kso_m2_solve_v1.py``).

Runs the frozen design on the public dev split at one instance per family (10 worlds) plus the 14
hand-authored known-answer fixtures. Pinned counts are the receipt's own denominators.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_m2_solve_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_m2_solve_v1", MODULE)
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
    return mod.run(per_family=1)


def test_design_is_frozen_and_matches(mod):
    d = mod.check_design_drift()
    assert len(d["design_sha256"]) == 64 and len(d["ids_sha256"]) == 64


def test_design_drift_is_cannot_check(mod, monkeypatch, tmp_path):
    drifted = tmp_path / "design.md"
    drifted.write_bytes(mod.DESIGN_MD.read_bytes() + b"\n<!-- post-outcome edit -->\n")
    monkeypatch.setattr(mod, "DESIGN_MD", drifted)
    with pytest.raises(mod.CannotCheck):
        mod.check_design_drift()


def test_gates_on_the_dev_split(receipt):
    assert receipt["G0_fixtures"] == {**receipt["G0_fixtures"], "n": 14, "exact": 14}
    g1 = receipt["G1_exact"]
    assert (g1["n"], g1["exact"], g1["attributions"], g1["FOUND_BY_NAVIGATION"], g1["FOUND_BY_STORE_READ"]) == (10, 10, {}, 8, 2)
    assert receipt["headline"]["NAVIGATION_EXACT"] == "8/10" and receipt["headline"]["STORE_EXACT"] == "10/10"
    assert receipt["G2_translator_invariance"] == {"n": 10, "invariant": 10, "atomizer_sources_differ": True}
    assert receipt["G3_budget"]["overruns"] == 0
    assert receipt["G5_planted_flip"]["flips"] >= 1 and receipt["G5_planted_flip"]["answers_changed"] >= 1
    assert receipt["terminal"] == "M2_EXACT_ON_DEV"
    assert receipt["request_level_atoms_added_total"] == 69


def test_every_row_has_the_agreed_shape(receipt):
    for row in receipt["instances"]:
        arm = row["arms"]["KSO_M2_SOLVE"]
        assert set(arm["answer"]) == {"action", "reopened"}
        assert arm["status"] in {"SCORED", "OBSTRUCTION", "CANNOT_CHECK"}
        assert arm["navigation_outcome"] in {"FOUND", "GAP_NOT_FOUND", "OBSTRUCTION_WITNESSED", "CANNOT_CHECK"}
        assert arm["budget"]["edge_visits"] <= arm["budget"]["edge_visits_cap"] and arm["budget"]["steps"] <= arm["budget"]["steps_cap"]
        assert arm["attribution"] == "" and arm["exact"] and arm["translator_invariant"]
        assert arm["exact_by"] in {"FOUND_BY_NAVIGATION", "FOUND_BY_STORE_READ"}
        assert len(row["graph_sha256"]) == 64 and len(arm["extraction_sha256"]) == 64


def test_informational_findings_are_recorded_not_hidden(receipt):
    f = receipt["findings_informational"]
    assert f["EXTRACT_SURPRISE_MISSES_ONE_HOP_REQUEST_ATOMS"]["instances"] == 2
    assert f["TARGET_CLAIM_DEAD_AT_REQUEST_TIME"]["instances"] == 1


def test_add_request_atoms_is_pure_and_composes_a_decision(mod):
    gen, model, oracle = mod.m1._mex1()
    inst, exp = gen.generate_split("dev", "ME-X1-DEV-20260902", {model.FAMILIES[0]: 1})[0]
    w1, pop0, pop, added = mod.prepare(inst)
    assert len(pop0.space.atoms) + len(added) == len(pop.space.atoms)
    assert "proc:transition_rule" in added and f"decision:{inst.instance_id}" in added
    dec = pop.space.atom_map()[f"decision:{inst.instance_id}"]
    live = mod.kso.profile_live(dec.profile, pop.registered_revoked | frozenset(pop.unknown))
    assert live == (exp.action == model.UPDATE)
    assert mod.graph_sha256(pop0.space) != mod.graph_sha256(pop.space)


def test_graph_digest_format_is_the_shared_one(mod):
    ks = mod.KnowledgeSpace((mod.Atom("a", "claim", mod.ONE), mod.Atom("b", "claim", mod.ONE)), (mod.Hyperedge("ab", ("a",), ("b",), "SUPPORT", profile=mod.ONE),))
    expected = hashlib.sha256("\n".join(["A|a|claim", "A|b|claim", "E|ab|a|b|SUPPORT"]).encode()).hexdigest()
    assert mod.graph_sha256(ks) == expected


def test_second_reading_of_request_atoms_matches_the_oracle_on_every_dev_world(mod):
    gen, model, oracle = mod.m1._mex1()
    for inst, exp in gen.generate_split("dev", "ME-X1-DEV-20260902", {f: 1 for f in model.FAMILIES}):
        w1, _, pop, _ = mod.prepare(inst)
        assert mod.check_against_oracle(pop, w1, inst, mod.read_request_atoms(w1, inst.request)) == []


def test_cli_exit_codes_are_three_and_distinct(mod, monkeypatch, capsys):
    monkeypatch.setattr(mod, "run", lambda per_family=5: (_ for _ in ()).throw(mod.CannotCheck("planted")))
    assert mod.main([]) == 2
    monkeypatch.setattr(mod, "run", lambda per_family=5: (_ for _ in ()).throw(AssertionError("planted")))
    assert mod.main([]) == 1
    capsys.readouterr()
