"""R8 — cost-bounded multi-fidelity triage with a MEASURED soundness audit of its screen.

WHICH R8 THIS IS. `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1` section 20 lists R8 as the "distributed search runner"; the
working brief asks R8 for the scaling document's cost-bounded triage. They are the same layer: the runner is only a
runner because it does not pay full fidelity for every candidate, and `GMI_BIOSPHERE_SCALING_AND_TRIAGE_V1` is the
document that says how it is allowed to do that. This module implements the fidelity ladder of that document (F0 static
validity, F2 cheap proxy, F5 exact confirmation) with diversity-preserving promotion (section 5) and the triage-bias
audit (section 11), and refuses to run at all until its screen has an audit receipt.

PROTOCOL RULE 18 IS A PRECONDITION, NOT A REPORT. The gap ledger's rule 18 was added after a functional-equivalence
cache assigned candidates a fitness they had not earned and mis-scored 34.65 per cent of them
(`gmi_microscope/fec_audit.py`, `microscopes/results/STAGE_F_FEC_AUDIT_V1.json`, RV-377-061). So the screen here is
audited BEFORE it is used and its audit receipt hash is cited in the run receipt; `main` raises if the audit is missing
or RED. Two error rates are measured separately because they are not interchangeable:

  FALSE PROMOTION  the screen promotes a candidate the exact confirmation then rejects. Costs exact budget. Bounded by
                   the promotion budget, and it cannot hide a species.
  FALSE REJECTION  the screen rejects a candidate that the exact confirmation would have called admissible. This is the
                   scientific error: it removes a form from the reachable set and no later stage can recover it. It is
                   measured per mechanism family, because a screen that is 5 per cent wrong overall but 60 per cent
                   wrong on one carrier is a biased instrument, not a cheap one (scaling document section 11).

The threshold tau is frozen on a CALIBRATION sample against a false-rejection BUDGET declared before calibration, and
the rates are measured on a DISJOINT AUDIT sample, so the reported rates are not the rates the threshold was fitted to.
If the audit rate exceeds the declared budget the screen fails its audit and the run refuses to start; that refusal is
the falsifiable content of the calibration, and it is why the budget is declared first and measured second.

THE CACHE THIS LANE IS ALLOWED TO USE. The FEC keyed candidates by a behavioural PROBE, a strict coarsening of the
fitness — two candidates could share a key and differ in score. The only cache used here is keyed by the exact CANONICAL
FORM (`morph.canonical`), i.e. by isomorphism of the typed port graph. Two genotypes with the same key are the same
machine up to the nuisance group, so the reuse is sound by construction — but "by construction" is what the FEC also
claimed, so the audit MEASURES it: every canonical-form group in the audit sample is exactly scored and the receipt
reports the maximum score spread within a group, which must be 0.0.

CLAIM CEILING. One ecology, one grammar, one screen (development truncated from 16 events to 4). The measured rates are
rates of THIS screen on the DECLARED audit population (see `PARENT_FRACTION`); a different population gives different
rates — the same caveat the FEC audit carries. A screen with a bounded false-rejection rate makes the search cheap, not
complete: the missed-species bound is the rate, and it is not zero.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from . import b1, ecology, morph, morphgen, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
FEC_AUDIT = os.path.join(RES, "STAGE_F_FEC_AUDIT_V1.json")
SCREEN_EVENTS = 4          # F2 cheap proxy: development truncated from the registered 16 events to 4
EXACT_EVENTS = 16          # F5 exact confirmation: the registered protocol
THETA = b1.THETA
AUDIT_SAMPLE_RATE = 0.15   # scaling document section 11: promote this fraction of the REJECTED anyway, and measure


def _draw(rng, steps_lo=3, steps_hi=12):
    """one candidate from the registered grammar, in canonical genotype form; None when the draw is too wide."""
    from .lineage import canon_geno
    g = morphgen.random_genotype(rng, steps=rng.randrange(steps_lo, steps_hi))
    try:
        return canon_geno(g)
    except morph.MorphError:
        return None


def f0_static(g):
    """F0 STATIC VALIDITY: type/interface validity and servability. Architecture-neutral by construction — F0 knows only
    the type system, so it cannot eliminate a candidate for lacking a familiar pattern (scaling document section 3)."""
    try:
        morph.typecheck(g); morphgen._check_servable(g); return True
    except (morph.MorphError, ValueError, KeyError, IndexError):
        return False


def screen(g, target, seed=0):
    """F2 cheap proxy: the registered protocol truncated to SCREEN_EVENTS events, scored on all inputs."""
    r = b1.evaluate(g, target, n_events=SCREEN_EVENTS, criterion="all", seed=seed)
    return (None, None, 0) if r is None else (r[0], r[1], sum(r[2].values()))


def confirm(g, target, seed=0):
    """F5 exact confirmation: the registered 16-event protocol scored on the unseen inputs."""
    r = b1.evaluate(g, target, n_events=EXACT_EVENTS, criterion="unseen", seed=seed)
    return (None, None, 0) if r is None else (r[0], r[1], sum(r[2].values()))


def _draw_neighbour(rng, target=None):
    """a 1-3 step mutational neighbour of a registered R4 known parent."""
    from .lineage import canon_geno, propose
    from . import zoo
    name = rng.choice(sorted(zoo.ZOO))
    g = canon_geno(zoo.ZOO[name]())
    for _ in range(rng.randrange(1, 4)):
        try:
            g, _, _ = propose(g, rng.randrange(2 ** 31))
        except morph.MorphError:
            return None
    return g


# The DECLARED AUDIT POPULATION. Uniform draws from the grammar are almost never admissible (about 1 per cent at
# theta = 0.85 on this ecology), so an audit sample of uniform draws alone cannot measure a false-REJECTION rate: the
# denominator is empty. Under selection the screen does not see uniform draws either — it sees the neighbourhood of
# whatever the archive already holds. The audit population is therefore declared as a half-and-half mixture of uniform
# grammar draws and 1-3 step mutational neighbours of the R4 known parents, and the receipt reports the two rates
# separately as well as jointly, so neither is hidden inside the other.
PARENT_FRACTION = 0.5


def sample(rng, n, target, seed=0, parent_fraction=PARENT_FRACTION):
    """n drawn candidates with BOTH fidelities measured, plus the carrier (mechanism family) and the sub-population."""
    out = []
    while len(out) < n:
        neighbour = rng.random() < parent_fraction
        g = _draw_neighbour(rng) if neighbour else _draw(rng)
        if g is None or not f0_static(g): continue
        s, sdesc, scost = screen(g, target, seed)
        if s is None: continue
        c, cdesc, ccost = confirm(g, target, seed)
        if c is None: continue
        out.append({"fp": morph.fingerprint(g), "carrier": b1.carrier_of(g), "screen": s, "screen_charge": scost,
                    "exact": c, "exact_charge": ccost, "desc": cdesc, "g": g,
                    "population": "parent_neighbour" if neighbour else "uniform_grammar_draw"})
    return out


# ------------------------------------------------------------------------------------------------- the screen audit
FALSE_REJECTION_BUDGET = 0.05   # declared BEFORE calibration: the bias the triage is allowed to buy its saving with


def calibrate(cal, budget=FALSE_REJECTION_BUDGET):
    """freeze tau on the calibration sample as the largest threshold whose CALIBRATION false-rejection rate is within
    the declared budget: the `budget` quantile of the screen scores of the calibration candidates the exact
    confirmation calls admissible.

    Setting the budget to 0 (tau = the minimum admissible screen score) is the safe choice and buys almost no saving,
    because the screen's score distribution for admissible and inadmissible candidates overlaps at the bottom. A triage
    is a declared trade of completeness for cost, so the budget is declared in advance and the audit sample then
    measures whether the realized rate honours it. If the audit rate exceeds the budget, the screen fails the audit and
    `main` refuses to run — that is the falsifiable content of this calibration."""
    adm = sorted(c["screen"] for c in cal if c["exact"] >= THETA)
    if not adm: return 0.0
    return round(adm[min(int(budget * len(adm)), len(adm) - 1)], 4)


def audit_screen(tau, aud):
    """measure the two rates on the disjoint audit sample, overall and per mechanism family."""
    promoted = [c for c in aud if c["screen"] >= tau]
    rejected = [c for c in aud if c["screen"] < tau]
    admissible = [c for c in aud if c["exact"] >= THETA]
    false_prom = [c for c in promoted if c["exact"] < THETA]
    false_rej = [c for c in rejected if c["exact"] >= THETA]
    by_family = {}
    for fam in sorted({c["carrier"] for c in aud}):
        fam_c = [c for c in aud if c["carrier"] == fam]; fam_adm = [c for c in fam_c if c["exact"] >= THETA]
        fam_fr = [c for c in fam_adm if c["screen"] < tau]
        by_family[fam] = {"n": len(fam_c), "n_admissible": len(fam_adm), "n_false_rejection": len(fam_fr),
                          "false_rejection_rate": round(len(fam_fr) / len(fam_adm), 4) if fam_adm else None,
                          "mechanism": b1.MECHANISM_OF_CARRIER[fam]}
    # the canonical-form cache: exact scores of every group sharing a canonical fingerprint (contrast with the FEC)
    groups = {}
    for c in aud: groups.setdefault(c["fp"], []).append(c["exact"])
    shared = {k: v for k, v in groups.items() if len(v) > 1}
    spread = max([max(v) - min(v) for v in shared.values()] or [0.0])
    by_population = {}
    for pop in sorted({c["population"] for c in aud}):
        pc = [c for c in aud if c["population"] == pop]; padm = [c for c in pc if c["exact"] >= THETA]
        pprom = [c for c in pc if c["screen"] >= tau]
        by_population[pop] = {"n": len(pc), "n_admissible": len(padm), "n_promoted": len(pprom),
                              "false_rejection_rate": round(sum(1 for c in padm if c["screen"] < tau) / len(padm), 4) if padm else None,
                              "false_promotion_rate": round(sum(1 for c in pprom if c["exact"] < THETA) / len(pprom), 4) if pprom else None}
    return {"tau": tau, "n_audit": len(aud), "n_promoted": len(promoted), "n_rejected": len(rejected), "n_admissible_exact": len(admissible),
            "by_declared_population": by_population,
            "n_false_promotion": len(false_prom), "n_false_rejection": len(false_rej),
            "false_promotion_rate": round(len(false_prom) / len(promoted), 4) if promoted else None,
            "false_rejection_rate": round(len(false_rej) / len(admissible), 4) if admissible else None,
            "screen_recall_on_admissible": round(1 - len(false_rej) / len(admissible), 4) if admissible else None,
            "false_rejection_by_mechanism_family": by_family,
            "mean_screen_charge": round(sum(c["screen_charge"] for c in aud) / len(aud), 1),
            "mean_exact_charge": round(sum(c["exact_charge"] for c in aud) / len(aud), 1),
            "screen_cost_fraction_of_exact": round(sum(c["screen_charge"] for c in aud) / sum(c["exact_charge"] for c in aud), 4),
            "canonical_cache": {"n_groups": len(groups), "n_shared_canonical_forms": len(shared),
                                "max_exact_score_spread_within_a_canonical_form": round(spread, 6),
                                "sound": spread == 0.0}}


def main_audit(cal_seed=101, aud_seed=202, n_cal=250, n_aud=400, tag="V1", eco_name="E_smooth3"):
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4}[eco_name]
    target = smooth.make_target(coeffs); t0 = time.time()
    cal = sample(random.Random(cal_seed), n_cal, target)
    tau = calibrate(cal)
    aud = sample(random.Random(aud_seed), n_aud, target)
    a = audit_screen(tau, aud)
    # the cost/bias trade-off, measured rather than asserted: each budget's tau is fitted on the CALIBRATION sample and
    # its rates are then measured on the AUDIT sample. This is a diagnostic curve, not a menu to pick from after seeing
    # it — the operating point is the budget declared before calibration.
    sweep = []
    for b in (0.0, 0.05, 0.10, 0.20, 0.40):
        tb = calibrate(cal, b); ab = audit_screen(tb, aud)
        promoted_frac = ab["n_promoted"] / ab["n_audit"]
        cost_frac = a["screen_cost_fraction_of_exact"] + promoted_frac        # screen on all + exact on the promoted
        sweep.append({"declared_budget": b, "tau": tb, "promoted_fraction": round(promoted_frac, 4),
                      "measured_false_rejection_rate": ab["false_rejection_rate"],
                      "measured_false_promotion_rate": ab["false_promotion_rate"],
                      "cost_fraction_of_full_fidelity": round(cost_frac, 4),
                      "pays_for_itself": cost_frac < 1.0})
    # remint invariance: both fidelities are unchanged by morph.remint on a sample of the audit draws
    bad = 0
    for c in aud[:40]:
        gr = morph.remint(c["g"], 7)
        if screen(gr, target)[0] != c["screen"] or confirm(gr, target)[0] != c["exact"]: bad += 1
    within_budget = a["false_rejection_rate"] is not None and a["false_rejection_rate"] <= FALSE_REJECTION_BUDGET
    ok = within_budget and a["canonical_cache"]["sound"] and bad == 0
    out = {"schema": "StageR8ScreenSoundnessAuditV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R8",
           "protocol_rule": "18 — any cache or surrogate that assigns a fitness a candidate did not itself earn must be audited for soundness on the registered grammar BEFORE the run, and the audit receipt cited in the run receipt",
           "prior_failure_that_created_the_rule": {"record": "RV-377-061", "receipt": "STAGE_F_FEC_AUDIT_V1.json",
                                                   "functional_equivalence_cache_wrong_score_fraction_probe10": 0.3465},
           "run_tag": tag, "ecology": eco_name, "ecology_spec_id": ecology.spec_id(ecology.REGISTRY[eco_name]),
           "screen": f"F2 cheap proxy: the registered development protocol truncated from {EXACT_EVENTS} events to {SCREEN_EVENTS}, capability scored on all 16 inputs",
           "exact": f"F5 exact confirmation: the registered {EXACT_EVENTS}-event protocol, capability scored on the unseen inputs, theta = {THETA}",
           "declared_audit_population": f"{int(PARENT_FRACTION * 100)} per cent uniform draws from the registered grammar, {int((1 - PARENT_FRACTION) * 100)} per cent 1-3 step mutational neighbours of the R4 known parents; rates are reported for the mixture and for each sub-population separately (see the module docstring for why uniform draws alone cannot measure a false-rejection rate)",
           "theta": THETA, "calibration_seed": cal_seed, "audit_seed": aud_seed, "n_calibration": n_cal,
           "declared_false_rejection_budget": FALSE_REJECTION_BUDGET,
           "tau_frozen_on_calibration": tau, "calibration_admissible": sum(1 for c in cal if c["exact"] >= THETA),
           "audit_rate_within_declared_budget": within_budget,
           "audit": a, "budget_sweep": sweep,
           "budget_sweep_note": "each row's tau is fitted on the calibration sample and measured on the audit sample. A row with pays_for_itself false means the ladder costs MORE than confirming everything exactly at that budget, because the screen promotes nearly everything; the operating row is the budget declared before calibration, not the cheapest row in this table",
           "remint_invariance": {"n_checked": 40, "n_changed": bad,
                                             "assertion": "morph.remint changes neither fidelity's score on any checked draw"},
           "seconds": round(time.time() - t0, 1),
           "status_verdict": "SCREEN_AUDITED_GREEN" if ok else "SCREEN_AUDIT_RED",
           "claim_ceiling": "rates of this screen on RANDOM draws of the registered grammar on one ecology; under selection the population is not random and the rates may differ (the same caveat as RV-377-061). A bounded false-rejection rate makes the search cheap, not complete"}
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_R8_SCREEN_AUDIT_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"R8 audit {out['status_verdict']}: tau {tau}, false promotion {a['false_promotion_rate']}, "
          f"false rejection {a['false_rejection_rate']}, screen costs {a['screen_cost_fraction_of_exact']} of exact")
    return out


# ------------------------------------------------------------------------------------------------------- the run
def triage_run(target, seed=303, n_raw=600, tau=None, audit_rate=AUDIT_SAMPLE_RATE):
    """F0 -> F2 -> F5 with diversity-preserving promotion and a random audit of the rejected."""
    rng = random.Random(seed); raw = 0; f0_fail = 0; dup = 0; seen = set(); pool = []
    while len(pool) < n_raw:
        raw += 1; g = _draw(rng)
        if g is None: f0_fail += 1; continue
        if not f0_static(g): f0_fail += 1; continue
        fp = morph.fingerprint(g)
        if fp in seen: dup += 1; continue                 # F0 exact duplicate collapse under canonicalization
        seen.add(fp); pool.append({"fp": fp, "g": g, "carrier": b1.carrier_of(g)})
    screen_charge = 0
    for c in pool:
        s, d, sc = screen(c["g"], target); c["screen"] = s; c["screen_desc"] = d; screen_charge += sc
    live = [c for c in pool if c["screen"] is not None]
    # promotion strata (scaling document section 5): best per behavioural cell, everything over tau, and a random audit
    best_per_cell = {}
    for c in live:
        cur = best_per_cell.get(c["screen_desc"])
        if cur is None or c["screen"] > cur["screen"]: best_per_cell[c["screen_desc"]] = c
    promoted = {id(c): c for c in best_per_cell.values()}
    for c in live:
        if tau is not None and c["screen"] >= tau: promoted[id(c)] = c
    rejected = [c for c in live if id(c) not in promoted]
    audit_extra = [c for c in rejected if rng.random() < audit_rate]
    exact_charge = 0
    for c in list(promoted.values()) + audit_extra:
        e, d, ec = confirm(c["g"], target); c["exact"] = e; c["exact_desc"] = d; c["exact_charge"] = ec; exact_charge += ec
    return {"n_raw_drawn": raw, "n_f0_eliminated": f0_fail, "n_duplicates_collapsed": dup, "n_pool": len(pool),
            "n_screened": len(live), "n_promoted": len(promoted), "n_rejected": len(rejected),
            "n_rejected_audited_anyway": len(audit_extra), "screen_charge": screen_charge, "exact_charge": exact_charge,
            "promoted": list(promoted.values()), "audit_extra": audit_extra, "rejected": rejected, "live": live}


def main(tag="V1", eco_name="E_smooth3", seed=303, n_raw=600, audit_tag="V1"):
    audit_path = os.path.join(RES, f"STAGE_R8_SCREEN_AUDIT_{audit_tag}.json")
    if not os.path.exists(audit_path):
        raise RuntimeError(f"protocol rule 18: the screen has no audit receipt at {audit_path}; run triage.main_audit first")
    aud = json.load(open(audit_path))
    if aud["status_verdict"] != "SCREEN_AUDITED_GREEN":
        raise RuntimeError(f"protocol rule 18: the screen audit is {aud['status_verdict']}; the screen may not be used")
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4}[eco_name]
    target = smooth.make_target(coeffs); tau = aud["tau_frozen_on_calibration"]; t0 = time.time()
    r = triage_run(target, seed, n_raw, tau)
    conf_adm = [c for c in r["promoted"] if c["exact"] is not None and c["exact"] >= THETA]
    missed = [c for c in r["audit_extra"] if c["exact"] is not None and c["exact"] >= THETA]
    # What full fidelity on everything would have cost, MEASURED on this run's own population rather than extrapolated
    # from the audit sample's mean. (The first version of this receipt did extrapolate, and it was wrong by two orders
    # of magnitude: the audit population is half parent-neighbours, whose exact confirmation is far more expensive than
    # a uniform grammar draw's, so the audit's mean exact charge does not describe this population at all. The reference
    # pass below is a MEASUREMENT taken for the receipt; its charge is not part of the triage.)
    full_cost = 0
    n_reference = 0
    for c in r["live"]:
        if "exact_charge" in c:
            full_cost += c["exact_charge"]
        else:
            e, d, ec = confirm(c["g"], target); c["exact"] = e; c["reference_only"] = True
            full_cost += ec; n_reference += 1
    spent = r["screen_charge"] + r["exact_charge"]
    by_carrier = {}
    for c in r["promoted"] + r["audit_extra"]:
        b = by_carrier.setdefault(c["carrier"], {"n_confirmed": 0, "n_admissible": 0, "best_exact": None})
        b["n_confirmed"] += 1
        if c["exact"] is not None:
            b["n_admissible"] += int(c["exact"] >= THETA)
            if b["best_exact"] is None or c["exact"] > b["best_exact"]: b["best_exact"] = c["exact"]
    out = {"schema": "StageR8TriageRunV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422], "layer": "R8",
           "layer_reading": "the scaling document's cost-bounded triage, which is also the protocol's distributed search runner; see the module docstring",
           "run_tag": tag, "seed": seed, "ecology": eco_name, "ecology_spec_id": ecology.spec_id(ecology.REGISTRY[eco_name]),
           "screen_audit_receipt": f"STAGE_R8_SCREEN_AUDIT_{audit_tag}.json",
           "screen_audit_receipt_sha256": aud["receipt_sha256"],          # protocol rule 18: cited, not assumed
           "screen_audit_false_promotion_rate": aud["audit"]["false_promotion_rate"],
           "screen_audit_false_rejection_rate": aud["audit"]["false_rejection_rate"],
           "tau": tau, "theta": THETA,
           "fidelity_ladder": {"F0_static_validity": {"n_drawn": r["n_raw_drawn"], "n_eliminated": r["n_f0_eliminated"],
                                                      "n_duplicates_collapsed_by_canonical_form": r["n_duplicates_collapsed"],
                                                      "elimination_reasons": ["invalid type/interface", "OUTPUT unbound (not servable)", "exact duplicate under canonicalization", "canonical form wider than the declared search bound"]},
                               "F2_cheap_screen": {"n_screened": r["n_screened"], "charge": r["screen_charge"]},
                               "F5_exact_confirmation": {"n_confirmed": r["n_promoted"] + r["n_rejected_audited_anyway"], "charge": r["exact_charge"]}},
           "promotion_strata": {"best_screen_score_per_behavioural_cell": True, "all_above_tau": True,
                                "random_audit_of_the_rejected_rate": AUDIT_SAMPLE_RATE,
                                "naive_top_k_used": False},
           "n_promoted": r["n_promoted"], "n_rejected": r["n_rejected"], "n_confirmed_admissible": len(conf_adm),
           "triage_bias_audit": {"n_rejected_promoted_anyway": r["n_rejected_audited_anyway"],
                                 "n_of_those_that_were_admissible": len(missed),
                                 "measured_in_run_false_rejection_rate": round(len(missed) / r["n_rejected_audited_anyway"], 4) if r["n_rejected_audited_anyway"] else None,
                                 "note": "measured on this run's own rejected set, which is drawn from the same grammar but filtered by F0; the pre-run rate on the disjoint audit sample is the citable one"},
           "charge": {"screen_charge": r["screen_charge"], "exact_charge": r["exact_charge"], "total_charged": spent,
                      "full_fidelity_on_all_screened_measured": full_cost,
                      "measured_saving_fraction": round(1 - spent / full_cost, 4) if full_cost else None,
                      "triage_pays_for_itself": bool(full_cost and spent < full_cost),
                      "n_extra_confirmations_for_the_reference_measurement": n_reference,
                      "note": "the full-fidelity reference is MEASURED by exactly confirming every screened candidate, not extrapolated from the audit sample's mean exact charge (that extrapolation is invalid here: the audit population is half parent-neighbours, whose confirmations are far more expensive than a uniform grammar draw's). A NEGATIVE saving is a real result and is reported as one: at a tight false-rejection budget this screen promotes nearly everything, so the ladder costs MORE than confirming everything exactly. A saving is available only by declaring a larger budget, i.e. by buying it with completeness — see budget_sweep in the audit receipt"},
           "by_mechanism_family": by_carrier,
           "best_confirmed": sorted([{"carrier": c["carrier"], "screen": c["screen"], "exact": c["exact"], "fingerprint": c["fp"],
                                      "genotype": morph.to_json(c["g"])} for c in r["promoted"] + r["audit_extra"] if c["exact"] is not None],
                                    key=lambda d: -d["exact"])[:8],
           "seconds": round(time.time() - t0, 1),
           "terminal": "R8_TRIAGE_EXECUTED_WITH_AUDITED_SCREEN",
           "cost_verdict": None,
           "claim_ceiling": "one ecology, one grammar, one screen, one seed. The saving is measured against a measured mean exact charge, not against a full exhaustive run; the completeness of the triaged search is bounded by the screen's audited false-rejection rate and is not zero"}
    out["cost_verdict"] = ("TRIAGE_SAVES_CHARGE_AT_THE_DECLARED_BUDGET" if out["charge"]["triage_pays_for_itself"]
                           else "TRIAGE_COSTS_MORE_THAN_FULL_FIDELITY_AT_THE_DECLARED_BUDGET — the screen's admissible-score distribution has a long lower tail, so a 5 per cent false-rejection budget puts tau near the floor and nearly everything is promoted; the saving is available only by declaring a larger budget, which buys it with completeness")
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_R8_TRIAGE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(f"R8 triage: {r['n_raw_drawn']} drawn -> {r['n_screened']} screened -> {r['n_promoted']} promoted -> "
          f"{len(conf_adm)} admissible; saving {out['charge']['measured_saving_fraction']}; "
          f"in-run false rejection {out['triage_bias_audit']['measured_in_run_false_rejection_rate']}")
    return out


if __name__ == "__main__":
    if "--audit" in sys.argv: main_audit(tag=sys.argv[sys.argv.index("--audit") + 1] if len(sys.argv) > sys.argv.index("--audit") + 1 else "V1")
    else: main()
