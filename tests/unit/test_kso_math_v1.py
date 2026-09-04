"""KnowledgeSpace.v1 M0 mathematics.

These tests distinguish all-size proofs in the contract from finite implementation checks.
Every finite checker has a planted negative or mutation where appropriate; CANNOT_CHECK is a
distinct exit status and never a pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_math_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_math_v1", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def result(mod):
    return mod.run_all()


def test_warrant_semiring_exhaustive_counts(result):
    w = result["warrant_semiring"]
    assert w == {"profiles": 20, "pair_checks": 400, "triple_checks": 8000}


def test_navigation_exact_share_revocation_and_fixed_point(result):
    n = result["navigation"]
    assert n["matrix_equalities"] == 2
    assert n["planted_renormalization_detected"] == 1
    assert n["fixed_point_checks"] == 1
    assert n["contraction_checks"] == 200
    assert n["firing_revocation_checks"] == 2


def test_live_conjunctive_hyperedge_stops_after_required_tail_revocation(mod):
    one = (frozenset(),)
    ks = mod.KnowledgeSpace(
        (
            mod.Atom("a", "claim", one),
            mod.Atom("b", "claim", (frozenset({0}),)),
            mod.Atom("c", "claim", one),
        ),
        (mod.Hyperedge("abc", ("a", "b"), ("c",), "compose", profile=one),),
    )
    activation = {"a": Fraction(1), "b": Fraction(1), "c": Fraction(0)}
    assert mod.enabled_hyperedges(ks, activation, Fraction(1, 2)) == ("abc",)
    assert mod.enabled_hyperedges(ks, activation, Fraction(1, 2), revoked={0}) == ()


def test_restart_map_is_contractive_on_substochastic_navigation(mod):
    p = [
        [Fraction(0), Fraction(1, 2)],
        [Fraction(0), Fraction(0)],
    ]
    seed = [Fraction(1), Fraction(0)]
    alpha = Fraction(1, 4)
    x = [Fraction(3, 2), Fraction(-1, 3)]
    y = [Fraction(-2, 5), Fraction(7, 4)]
    fx = mod.restart_step(p, seed, x, alpha)
    fy = mod.restart_step(p, seed, y, alpha)
    lhs = mod.l1([a - b for a, b in zip(fx, fy, strict=True)])
    rhs = (1 - alpha) * mod.l1([a - b for a, b in zip(x, y, strict=True)])
    assert lhs <= rhs


def test_lumpability_commutes_and_negative_control_fires(result):
    q = result["lumpability"]
    assert q == {"pushforward_commutation_checks": 80, "nonlumpable_control": 1}


def test_semantic_connectivity_and_dependency_impact(result):
    c = result["connectivity_rewrite"]
    assert c == {"connectivity_checks": 5, "impact_cone_checks": 1}


def test_reaction_is_surprise_not_raw_hub_popularity(mod):
    assert mod.reaction_surprise(Fraction(1, 3), Fraction(1, 3)) == 0.0
    specific = mod.reaction_surprise(Fraction(1, 2), Fraction(1, 10))
    generic = mod.reaction_surprise(Fraction(1, 2), Fraction(49, 100))
    assert specific > generic >= 0.0


def test_exit_contract_has_distinct_cannot_check_and_fail(mod, monkeypatch, capsys):
    assert mod.main([]) == 0
    capsys.readouterr()

    def cannot():
        raise mod.CannotCheck("planted")

    monkeypatch.setattr(mod, "run_all", cannot)
    assert mod.main([]) == 2
    assert json.loads(capsys.readouterr().out) == {"status": "CANNOT_CHECK", "reason": "planted"}

    def fail():
        raise AssertionError("planted")

    monkeypatch.setattr(mod, "run_all", fail)
    assert mod.main([]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "FAIL" and "AssertionError: planted" in payload["reason"]


def test_m0_does_not_launder_later_milestones_into_results(result):
    t = result["terminals"]
    assert t["M0_FINITE_MATH_CORE"] == "GREEN"
    assert t["GENERAL_NOVELTY"] == "NOT_ESTABLISHED"
    assert [t[f"M{i}_{name}"] for i, name in ((1, "KSO_INSTANCE"), (2, "SOLVE_LOOP"), (3, "GAP_LEARNING"), (4, "JUMP_LOOP"), (5, "CHAT"), (6, "FRONTIER_MATH"))] == ["NOT_RUN"] * 6
