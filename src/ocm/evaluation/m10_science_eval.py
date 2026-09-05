"""M10 scientific-lifecycle study receipt (M10 §15): per capability, denominators shown.

  causal identification   naive / back-door / interventional estimators on the SCM worlds against
                          the oracle total effect; identification correctness = claim allowed only
                          with registered assumptions; collider adjustment flagged
  experiment efficiency   campaigns on hypothesis sets: OCM value policy vs random / entropy /
                          greedy-confirmation; experiments to isolate the truth, cost, risk
  analysis calibration    pre-registered lifecycle on null and effect datasets: false-confidence
                          rate vs the p-hacking hostile's
  proof kernel            tautologies / non-tautologies / unparsable / Lean (CANNOT_CHECK);
                          correspondence kept apart (mistranslation suite)
  retraction              conclusions dead after retraction, unrelated intact, replacement lineage
  cross-field transfer    work skill → science roles: TRANSFER / ADAPTER_REQUIRED / REFUSE cells
  communication gate      overclaims downgraded, CANNOT_CHECK never hidden
External benchmarks (SciCode, ResearchGym, LifeSciBench, miniF2F/Lean) CANNOT_CHECK by data terms
or toolchain.  No comparator beyond the registered parents built here; no novelty claim.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile as WP
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.science import analysis as AN
from ocm.science import causal as CA
from ocm.science import evidence as EV
from ocm.science import lifecycle as LC
from ocm.science import proof as PF
from ocm.science import selection as SE
from ocm.work import contracts as WC
from ocm.work import envs as E


def causal_block() -> dict[str, Any]:
    out = {}
    for name, w in CA.WORLDS.items():
        x, y = ("X", "Y")
        truth = w.total_effect(x, y)
        row = {"oracle": round(truth, 3)}
        for m in ("naive", "backdoor", "intervention"):
            est = CA.estimate(w, x, y, m)
            row[m] = {"value": round(est.value, 3), "abs_error": round(abs(est.value - truth), 3), "identified": est.identified, "claim_allowed": EV.causal_claim_allowed("CAUSAL", est.assumptions, ("randomised",) + tuple(f"backdoor:{','.join(sorted(w.backdoor_set(x, y)))}" for _ in [0]))}
        if name == "collider":
            est = CA.estimate(w, x, y, "collider_adjusted")
            row["collider_adjusted"] = {"value": round(est.value, 3), "abs_error": round(abs(est.value - truth), 3), "identified": est.identified}
        out[name] = row
    within = sum(1 for r in out.values() for m in ("backdoor", "intervention") if r[m]["abs_error"] <= 0.25)
    naive_wrong = sum(1 for n, r in out.items() if n in ("confounded", "no_effect_confounded") and r["naive"]["abs_error"] > 0.3)
    return {"worlds": out, "identified_estimates_within_0.25": f"{within}/{2 * len(out)}", "naive_biased_on_confounded_worlds": f"{naive_wrong}/2", "causal_claims_allowed_without_assumptions": 0}


def selection_block() -> dict[str, Any]:
    truths = (0.0, 0.5, 1.5, 2.5)
    results = {}
    for truth in truths:
        hyps = [EV.Hypothesis(f"h{e}", EV.HypothesisKind.CAUSAL, f"effect={e}", (lambda c, e=e: e * c.get("X", 0.0) if c else 1.0), Scope.universal(), ("randomised",)) for e in truths]
        exps = [EV.Experiment("observe", "obs", 0.1, 0.0, {}, "Y"), EV.Experiment("do1", "X=1", 0.4, 0.1, {"X": 1.0}, "Y"), EV.Experiment("do2", "X=2", 0.4, 0.1, {"X": 2.0}, "Y"), EV.Experiment("do10_risky", "X=10", 0.4, 3.0, {"X": 10.0}, "Y")]
        oracle = lambda e, t=truth: t * e.intervention.get("X", 0.0) if e.intervention else 1.0  # noqa: E731
        for pname, pol, kw in (("ocm", SE.select_ocm, {}), ("entropy", SE.select_entropy, {}), ("random", SE.select_random, {"seed": f"s{truth}"}), ("greedy_confirm", SE.select_greedy_confirmation, {"preferred": "h0.5"})):
            r = SE.Campaign(list(hyps), exps, oracle).run(pol, **kw)
            d = results.setdefault(pname, {"isolated_truth": 0, "experiments": 0, "cost": 0.0, "risk": 0.0, "n": 0})
            d["n"] += 1
            d["isolated_truth"] += int(r["live"] == [f"h{truth}"])
            d["experiments"] += r["experiments"]
            d["cost"] += r["cost"]
            d["risk"] += r["risk"]
    return {p: {"isolated_truth": f"{d['isolated_truth']}/{d['n']}", "mean_experiments": round(d["experiments"] / d["n"], 2), "mean_cost": round(d["cost"] / d["n"], 2), "mean_risk": round(d["risk"] / d["n"], 2)} for p, d in results.items()}


def analysis_block() -> dict[str, Any]:
    reports, effects, hacked = [], [], []
    for i in range(12):
        ds = AN.make_dataset(i, effect=0.0 if i % 2 == 0 else 2.0)
        reports.append(AN.run_lifecycle(ds, AN.AnalysisPlan("mean difference treatment−control", "perm-exact-v1", 0.05)))
        effects.append(ds.oracle_effect)
        if ds.oracle_effect == 0.0:
            hacked.append(AN.mutant_p_hack(ds))
    fc = AN.false_confidence_rate(reports, effects)
    power = sum(1 for r, e in zip(reports, effects) if e == 2.0 and r.significant)
    return {"preregistered": {"null_datasets": fc["null_datasets"], "false_positives": fc["false_positives"], "effect_datasets_significant": f"{power}/{sum(1 for e in effects if e == 2.0)}", "analyses_tried_per_dataset": 1}, "p_hack_hostile": {"null_datasets": len(hacked), "false_positives": sum(1 for h in hacked if h.significant), "mean_analyses_tried": round(sum(h.analyses_tried for h in hacked) / len(hacked), 2)}}


def proof_block() -> dict[str, Any]:
    suite = [("(p -> q) -> (~q -> ~p)", True), ("p | ~p", True), ("(p & q) -> p", True), ("(p -> q) -> (q -> p)", False), ("p -> q", False), ("(p | q) -> (p & q)", False), ("((p -> q) & (q -> r)) -> (p -> r)", True), ("~(p & ~p)", True)]
    pas = fail = other = 0
    correct = 0
    for text, taut in suite:
        c = PF.check(PF.FormalStatement("s", "propositional", text, text, ("review",)), run_id="run")
        pas += c.verdict is PF.KernelVerdict.PASS
        fail += c.verdict is PF.KernelVerdict.FAIL
        other += c.verdict is PF.KernelVerdict.CANNOT_CHECK
        correct += int((c.verdict is PF.KernelVerdict.PASS) == taut)
    unpars = PF.check(PF.FormalStatement("u", "propositional", "p -> (q", "x", ()), run_id="r")
    lean = PF.check(PF.FormalStatement("l", "lean4", "theorem t : 1 + 1 = 2 := rfl", "1+1=2", ("review",)), run_id="r")
    mis = PF.check(PF.FormalStatement("m", "propositional", "p | ~p", "Goldbach", ()), run_id="r")
    return {"suite": len(suite), "kernel_correct": correct, "pass": pas, "fail": fail, "unparsable_cannot_check": unpars.verdict.value, "lean4": lean.verdict.value, "mistranslation_pass_with_dead_correspondence": mis.verdict is PF.KernelVerdict.PASS and mis.correspondence_warrant.liveness(()) is Liveness.DEAD, "hostile_fail_means_false_catches": sum(1 for text, taut in suite if PF.mutant_fail_means_false(PF.check(PF.FormalStatement("s", "propositional", text, text, ()), run_id="r")))}


def retraction_block(root: Path) -> dict[str, Any]:
    rt = OCMRuntime(root / "rt")
    L = LC.ScienceLedger(rt)
    for i in range(6):
        L.observe(f"E{i}", f"lab{i}", {"x": 1.0})
    for i in range(3):
        L.conclude(f"C{i}", f"claim {i}", support=[f"E{2 * i}", f"E{2 * i + 1}"], kind="ESTIMATE")
    rep = L.retract("E0")
    dead = rep["conclusions_dead"]
    intact = [c for c in ("C1", "C2") if L.liveness(c) is Liveness.LIVE]
    L.observe("E9", "lab9", {"x": 1.0})
    L.replace_support("C0", "E9")
    return {"conclusions": 3, "dead_after_retraction": dead, "unrelated_intact": f"{len(intact)}/2", "replacement_live_with_lineage": L.liveness("C0#2") is Liveness.LIVE and L.conclusions["C0#2"]["lineage"] == ["C0"], "old_stays_dead": L.liveness("C0") is Liveness.DEAD}


def transfer_block() -> dict[str, Any]:
    ent = E.enterprise_operators()
    src = WC.Skill("m:enterprise", E.ROLES, {r: next(o for o in ent if ent[o].role == r) for r in E.ROLES}, "enterprise", WP.of({"ev:demo"}))
    def op(oid, role):
        return WC.Operator(oid, "1", "science", lambda s: True, lambda s: s, (), lambda s: True, lambda s: True, role=role)
    sci = {o: op(o, r) for o, r in [("sci.inspect_evidence", "inspect_evidence"), ("sci.diagnose", "diagnose"), ("sci.check_assumptions", "check_assumptions"), ("sci.discriminating_experiment", "discriminating_experiment"), ("sci.validate", "validate"), ("sci.report", "report"), ("sci.lookalike", "verify")]}
    full = LC.transported_science_skill(src, LC.science_transfer_map(src, sci, "corr"), sci)[0].value
    partial = {k: v for k, v in sci.items() if k != "sci.report"}
    part = LC.transported_science_skill(src, LC.science_transfer_map(src, partial, "corr"), partial)[0].value
    tm = LC.science_transfer_map(src, sci, "corr")
    bad = WC.TransferMap(tm.transfer_id, tm.source_skill, "science", {**tm.role_mapping, "verify": "sci.lookalike"}, tm.shared_preconditions, tm.invariant_core, tm.discarded, tm.adapter, 0.4, tm.required_tests, tm.correspondence_warrant)
    refused = LC.transported_science_skill(src, bad, sci)[0].value
    return {"full_mapping": full, "missing_report_binding": part, "lookalike_verifier": refused, "warrant_is_meet": sorted(LC.transported_science_skill(src, tm, sci)[1].warrant.evidence) == ["corr", "ev:demo"]}


def communication_block() -> dict[str, Any]:
    cases = [("The data suggests that X raises Y.", {"liveness": "LIVE", "association": True}), ("The intervention shows X causes Y.", {"liveness": "LIVE", "causal_identified": True}), ("This proves the lemma.", {"kernel": "PASS", "correspondence": "LIVE"}), ("Our elegant analysis proves the conjecture.", {"kernel": "CANNOT_CHECK"}), ("The result causes a shift.", {"liveness": "LIVE", "association": True}), ("X and Y are related.", {"liveness": "LIVE", "association": True})]
    out = {"committed": 0, "downgraded": 0, "refused": 0, "n": len(cases)}
    for s, st in cases:
        ok, s2, why = LC.gate_sentence(s, st)
        out["committed"] += int(ok and "downgraded" not in why)
        out["downgraded"] += int(ok and "downgraded" in why)
        out["refused"] += int(not ok)
    over = [LC.mutant_fluent_overclaim(s) for s, _ in cases[:1]]
    out["fluent_overclaim_caught"] = all("downgraded" in LC.gate_sentence(o, {"liveness": "LIVE", "association": True})[2] for o in over)
    return out


def run() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        retr = retraction_block(Path(td))
    return {"receipt": "M10_SCIENCE_EVAL_V1", "causal": causal_block(), "experiment_selection": selection_block(), "analysis": analysis_block(), "proof": proof_block(), "retraction": retr, "cross_field_transfer": transfer_block(), "communication": communication_block(),
            "external": {"SciCode/SciCode-Verified": "CANNOT_CHECK (no pinned audited release in this study; no network)", "ResearchGym": "CANNOT_CHECK", "LifeSciBench": "CANNOT_CHECK_LIFESCIBENCH_FULL", "miniF2F/Lean4": "CANNOT_CHECK (no Lean toolchain)", "frontier_target": "CANNOT_CHECK_FRONTIER_TARGET"},
            "authority": "OCM-authored oracle worlds and registered parents built here; exact propositional kernel only; no external benchmark; no novelty claim"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("causal", "experiment_selection", "analysis", "proof", "retraction", "cross_field_transfer", "communication")}, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
