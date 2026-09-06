"""The query and uniform background must use the same navigation channel."""
from fractions import Fraction as F
import math

import pytest

from ocm.kso import navigation as N
from ocm.kso import space as S
from ocm.kso import surprise as SP
from ocm.kso.types import Authority
from ocm.kso.warrant import CannotCheck, WarrantProfile as WP
from ocm.runtime import solve as SV
from test_solve_loop import _cfg, _op, _space, _task


@pytest.mark.parametrize("model", list(SP.SurpriseModel))
@pytest.mark.parametrize("warrant", [WP.of({1}), WP.partial([{1}])], ids=["dead", "unknown"])
def test_channel_backgrounds_match_independent_three_atom_solution(model, warrant):
    # One edge q->d and isolated u, alpha=1/3. Removing d's warrant removes
    # only the warranted transition/restart. Exploratory P and seed stay intact.
    ks = S.KnowledgeSpace(
        (S.Atom("q", "query_seed"), S.Atom("d", "claim", warrant), S.Atom("u", "claim")),
        (S.Hyperedge("qd", ("q",), ("d",), "SUPPORT"),),
    )
    task = SV.Task("channels", (SV.QueryPart("q", "claim", ("q",)),))
    cfg = SV.SolveConfig(surprise_model=model)
    seed = N.seed_vector(ks, {"q": F(1)})
    stage, nav = SV.navigate_stage(ks, seed, task, cfg, {1})
    assert nav["act_w"] == {"q": F(1, 3), "d": F(0), "u": F(0)}
    assert nav["act_x"] == {"q": F(1, 3), "d": F(2, 9), "u": F(0)}
    assert nav["background"] == {"q": F(1, 9), "d": F(0), "u": F(1, 9)}
    assert nav["background_x"] == {"q": F(1, 9), "d": F(5, 27), "u": F(1, 9)}
    assert stage.resources.navigation_work == 4 * 3 * 3

    background_mass = SP.propagated_mass(ks, nav["background_x"], N.uniform_seed(ks),
                                        cfg.alpha, revoked={1}, mode=N.NavigationMode.EXPLORATORY)
    assert background_mass == {"q": F(0), "d": F(2, 27), "u": F(0)}
    rho = SP.surprise(ks, nav["act_x"], nav["background_x"], seed, cfg.alpha, model,
                      revoked={1}, mode=N.NavigationMode.EXPLORATORY)
    ratio = 3 if model is SP.SurpriseModel.PROPAGATED else F(6, 5)
    assert rho["d"] == pytest.approx(float(F(2, 9)) * math.log(float(ratio)), abs=1e-10)
    stage, extracted = SV.extract_stage(ks, seed, nav, cfg, {1})
    assert "d" not in extracted["g_w"].atoms
    assert "d" in extracted["g_x"].atoms
    assert all(math.isfinite(value) for value in rho.values())


@pytest.mark.parametrize("model", list(SP.SurpriseModel))
@pytest.mark.parametrize("revoked", [(), (1,), (2,), (3,)])
def test_existing_solve_fixture_preserves_refusal_and_unrelated_capability(model, revoked):
    out = SV.solve(_space(), _task(), [_op()], revoked=revoked,
                   config=SV.SolveConfig(surprise_model=model),
                   commit_authority=Authority.of(src=3))
    assert out.trace.stages[-1].stage is SV.Stage.COMMITMENT
    if 1 in revoked or 2 in revoked:
        assert out.answer is None
        assert not SV.committed(out)
        assert out.trace.stages[-1].reason.startswith("REFUSED")
    elif model is SP.SurpriseModel.PROPAGATED:
        assert out.decision is SV.Decision.ANSWER
        assert out.answer["result"] == 42
        assert SV.committed(out)


def test_unavailable_exploratory_background_remains_cannot_check(monkeypatch):
    fixed_point = N.fixed_point

    def unavailable(ks, seed, alpha, **kwargs):
        if kwargs.get("mode") is N.NavigationMode.EXPLORATORY and seed == N.uniform_seed(ks):
            raise CannotCheck("exploratory background unavailable")
        return fixed_point(ks, seed, alpha, **kwargs)

    monkeypatch.setattr(N, "fixed_point", unavailable)
    out = SV.solve(_space(), _task(), [_op()], config=_cfg(), commit_authority=Authority.of(src=3))
    assert out.decision is SV.Decision.CANNOT_CHECK
    assert out.answer is None and not SV.committed(out)
    nav = next(stage for stage in out.trace.stages if stage.stage is SV.Stage.NAVIGATION)
    assert nav.status is SV.Status.CANNOT_CHECK
    assert nav.reason == "exploratory background unavailable"
