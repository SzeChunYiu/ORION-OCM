"""Same current ten-stage consumer, four channels and withdrawal/authority controls."""
from dataclasses import replace
import importlib
import importlib.util
import pytest
from ocm.kso import navigation as N
from ocm.kso import surprise as SP
from ocm.kso.types import Authority
from representation_donor_fixture import fixture


@pytest.mark.parametrize("model", list(SP.SurpriseModel))
@pytest.mark.parametrize("revoked", [(), (1,), ("backup",), (1,"backup"), (2,), (3,)])
def test_real_consumer_and_all_four_channels_match(model, revoked):
    assert importlib.util.find_spec("exact_sparse_donor_consumer"), "missing donor consumer adapter"
    C = importlib.import_module("exact_sparse_donor_consumer")
    f = fixture("alternative")
    args = (f["ks"], f["task"], f["operators"])
    kwargs = dict(revoked=revoked, config=replace(f["config"], surprise_model=model),
                  commit_authority=f["authority"])
    original_function = N.fixed_point
    reference = C.evaluate(*args, arm="reference", **kwargs)
    candidate = C.evaluate(*args, arm="sympy", **kwargs)
    assert candidate["consumer"] == reference["consumer"]
    assert candidate["vectors"] == reference["vectors"]
    assert candidate["surprise"] == reference["surprise"]
    assert len(candidate["vectors"]) == 4
    assert sum(r["donor_solve_calls"] for r in candidate["checks"]) == 4
    assert N.fixed_point is original_function


def test_authority_refusal_is_unchanged():
    assert importlib.util.find_spec("exact_sparse_donor_consumer"), "missing donor consumer adapter"
    C = importlib.import_module("exact_sparse_donor_consumer")
    f = fixture()
    task = replace(f["task"], required_authority=Authority.of(src=5))
    reference = C.evaluate(f["ks"], task, f["operators"], arm="reference",
                           config=f["config"], commit_authority=f["authority"])
    candidate = C.evaluate(f["ks"], task, f["operators"], arm="sympy",
                           config=f["config"], commit_authority=f["authority"])
    assert candidate["consumer"] == reference["consumer"]
    assert not candidate["consumer"]["committed"]

@pytest.mark.parametrize("model", list(SP.SurpriseModel))
def test_three_atom_channels_match_independent_known_values(model, monkeypatch):
    from fractions import Fraction as F
    from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
    from ocm.kso.warrant import WarrantProfile as WP
    from ocm.runtime import solve as SV
    import exact_sparse_donor as D
    ks = KnowledgeSpace((Atom("q", "query_seed"), Atom("d", "claim", WP.of({1})),
                         Atom("u", "claim")),
                        (Hyperedge("qd", ("q",), ("d",), "SUPPORT"),))
    task = SV.Task("channels", (SV.QueryPart("q", "claim", ("q",)),))
    config = SV.SolveConfig(surprise_model=model)
    monkeypatch.setattr(N, "fixed_point", D.fixed_point)
    _, nav = SV.navigate_stage(ks, [F(1), F(0), F(0)], task, config, {1})
    assert nav["act_w"] == {"q": F(1,3), "d": F(0), "u": F(0)}
    assert nav["act_x"] == {"q": F(1,3), "d": F(2,9), "u": F(0)}
    assert nav["background"] == {"q": F(1,9), "d": F(0), "u": F(1,9)}
    assert nav["background_x"] == {"q": F(1,9), "d": F(5,27), "u": F(1,9)}
    _, extracted = SV.extract_stage(ks, [F(1), F(0), F(0)], nav, config, {1})
    assert "d" not in extracted["g_w"].atoms and "d" in extracted["g_x"].atoms
