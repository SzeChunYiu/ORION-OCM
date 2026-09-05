"""M10 §2, §4–§6: evidence dependence, causal worlds (confounding, mediator, collider, intervention),
discriminating experiment selection vs comparators, analysis lifecycle and the p-hacking hostile."""
from __future__ import annotations

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness
from ocm.science import analysis as AN
from ocm.science import causal as CA
from ocm.science import evidence as EV
from ocm.science import selection as SE


def _obs(i, source, x=1.0):
    return EV.Observation(f"o{i}", source, {"x": x}, {}, "gaussian", i, "v1", Scope.universal(), (), f"ev:o{i}")


def test_evidence_dependence_and_causal_claim_gate():
    reps = [_obs(i, "labA") for i in range(5)] + [_obs(9, "labB")]
    assert EV.independent_corroboration(reps) == 2 and EV.mutant_replicates_as_corroboration(reps) == 6
    obs = {o.obs_id: o for o in reps}
    h = EV.Hypothesis("h", EV.HypothesisKind.STATISTICAL, "x>0", lambda c: 1.0, Scope.universal(), ("iid",), support=[o.obs_id for o in reps])
    assert h.liveness(obs, ()) is Liveness.LIVE
    assert h.liveness(obs, {"ev:o9"}) is Liveness.LIVE                 # labA still supports
    assert h.liveness(obs, {f"ev:o{i}" for i in range(5)} | {"ev:o9"}) is Liveness.DEAD
    h.counter.append("o9")
    assert h.liveness(obs, ()) is Liveness.DEAD                        # a live counter-observation kills it
    assert EV.causal_claim_allowed("CAUSAL", ("randomised",), ("randomised", "backdoor:Z"))
    assert not EV.causal_claim_allowed("CAUSAL", (), ("randomised",))
    assert not EV.causal_claim_allowed("CAUSAL", ("graph_structure",), ("randomised",))
    assert EV.mutant_correlation_as_causation("CAUSAL")


def test_causal_worlds_naive_vs_backdoor_vs_intervention_and_collider():
    w = CA.WORLDS["confounded"]
    truth = w.total_effect("X", "Y")
    assert abs(truth - 0.5) < 1e-9
    naive, bd, iv = CA.estimate(w, "X", "Y", "naive"), CA.estimate(w, "X", "Y", "backdoor"), CA.estimate(w, "X", "Y", "intervention")
    assert abs(naive.value - truth) > 0.4 and not naive.identified       # confounding bias ≈ +0.75
    assert abs(bd.value - truth) < 0.2 and bd.identified and bd.assumptions == ("backdoor:Z",)
    assert abs(iv.value - truth) < 0.25 and iv.identified
    w0 = CA.WORLDS["no_effect_confounded"]
    assert abs(CA.estimate(w0, "X", "Y", "naive").value) > 0.3 and abs(CA.estimate(w0, "X", "Y", "backdoor").value) < 0.2
    wc = CA.WORLDS["collider"]
    assert abs(CA.estimate(wc, "X", "Y", "naive").value) < 0.2            # X ⊥ Y marginally
    assert abs(CA.estimate(wc, "X", "Y", "collider_adjusted").value) > 0.3 and not CA.estimate(wc, "X", "Y", "collider_adjusted").identified   # adjusting on the collider induces bias
    wm = CA.WORLDS["mediator"]
    assert abs(wm.total_effect("X", "Y") - 0.8) < 1e-9 and abs(CA.estimate(wm, "X", "Y", "intervention").value - 0.8) < 0.25


def test_experiment_selection_prefers_discriminating_low_risk_and_stops():
    # three hypotheses about the effect of X on Y: 0, 0.5, 1.5; experiments: intervene at X=2 (cheap),
    # observe only (uninformative: all predict the same confounded slope), a risky high-power one
    hyps = [EV.Hypothesis(f"h{e}", EV.HypothesisKind.CAUSAL, f"effect={e}", (lambda c, e=e: e * c.get("X", 0.0) if c else 1.0), Scope.universal(), ("randomised",)) for e in (0.0, 0.5, 1.5)]
    exps = [EV.Experiment("observe", "observational", 0.1, 0.0, {}, "Y"), EV.Experiment("do2", "intervene X=2", 0.4, 0.1, {"X": 2.0}, "Y"), EV.Experiment("do10_risky", "intervene X=10", 0.4, 3.0, {"X": 10.0}, "Y")]
    ch = SE.select_ocm(hyps, exps)
    assert ch.experiment.experiment_id == "do2"                         # discriminates all three at low risk
    assert SE.select_entropy(hyps, exps).experiment.experiment_id in ("do2", "do10_risky")   # cost/risk-blind
    greedy = SE.select_greedy_confirmation(hyps, exps, preferred="h0.5")
    assert greedy.experiment.experiment_id == "observe"                # the hostile picks the non-discriminating test
    camp = SE.Campaign(hyps, exps, oracle=lambda e: 0.5 * e.intervention.get("X", 0.0) if e.intervention else 1.0)
    out = camp.run(SE.select_ocm)
    assert out["live"] == ["h0.5"] and out["experiments"] == 1 and out["risk"] <= 0.1
    outr = SE.Campaign(hyps, exps, oracle=lambda e: 0.5 * e.intervention.get("X", 0.0) if e.intervention else 1.0).run(SE.select_random, seed="s")
    assert outr["experiments"] >= 1


def test_analysis_lifecycle_and_p_hacking_hostile():
    reports, effects = [], []
    for i in range(8):
        ds = AN.make_dataset(i, effect=0.0 if i % 2 == 0 else 2.0)
        r = AN.run_lifecycle(ds, AN.AnalysisPlan("mean difference treatment−control", "perm-exact-v1", 0.05))
        assert r.analyses_tried == 1 and r.test_id == "perm-exact-v1" and "exact" in r.ci_note
        reports.append(r); effects.append(ds.oracle_effect)
    fc = AN.false_confidence_rate(reports, effects)
    assert fc["null_datasets"] == 4 and fc["false_positives"] <= 1
    assert sum(1 for r, e in zip(reports, effects) if e == 2.0 and r.significant) >= 3
    hacked = [AN.mutant_p_hack(AN.make_dataset(100 + i, effect=0.0)) for i in range(6)]
    assert any(h.significant for h in hacked) and all(h.analyses_tried >= 1 for h in hacked)   # the hostile finds "significance" on nulls
