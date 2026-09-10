"""Aggregate the Form Oracle arms into the deliverable: the Pareto front.

The front is the deliverable, not a champion. Every front is reported against
the frozen parents at matched information, resources and checker access, and
the regions a parent owns are labelled PARENT_SUFFICIENT rather than engineered
past.

Also runs the two frozen falsifiers on evolvability (F1 shuffle-equal-n null
within capability bins, F2 redundancy against capability) and the dedup
lever's yield-versus-price accounting.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import statistics
import sys
from typing import Any, Dict, List, Optional

from oracle import evolvability as EV
from oracle import objectives4 as OB

# Frozen parents, cited from results/GS_R2_AGGREGATE.json on main (b434c55c).
PARENTS = {
    "GSA2_hetero": {"distinct_t2_viable_per_seed": 5062.7,
                    "morphologies_per_cpu_hour": 354046.0,
                    "cpu_seconds_per_seed": 51.258},
    "GSA5_surrogate": {"distinct_t2_viable_per_seed": 2233.3,
                       "morphologies_per_cpu_hour": 72150.0,
                       "cpu_seconds_per_seed": 111.257},
    "GSA6_DP": {"mean_distinct_per_seed": 5802.0,
                "morphologies_per_cpu_hour": 190526.55},
}
GS_R2_T3 = {"fail": 85025, "hold": 15668, "total": 100693}


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def load(results_dir: str) -> List[Dict[str, Any]]:
    out = []
    for f in sorted(glob.glob(os.path.join(results_dir, "FO_FO_*.json"))):
        if f.endswith(".status"):
            continue
        try:
            out.append(json.load(open(f)))
        except Exception as e:  # noqa: BLE001
            sys.stderr.write("unreadable %s: %r\n" % (f, e))
    return out


def aggregate(results_dir: str) -> Dict[str, Any]:
    runs = load(results_dir)
    if not runs:
        return {"status": "CANNOT_CHECK_NO_ARM_RESULTS"}

    all_records: List[Dict[str, Any]] = []
    per_arm: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for r in runs:
        tag = "%s|%s" % (r["arm"], r["lane"])
        for rec in r["records"]:
            rec = dict(rec)
            rec["arm_tag"] = tag
            rec["arm"] = r["arm"]
            all_records.append(rec)
            per_arm[tag].append(rec)

    # ---- the deliverable fronts
    front_report = OB.pareto_front_k(all_records, "report_objectives",
                                     OB.REPORT_MAXIMIZE)
    front_cov = OB.pareto_front_k(all_records, "coverage_objectives",
                                  OB.COVERAGE_MAXIMIZE)

    def _front_rows(fr):
        return [{k: all_records[i].get(k)
                 for k in ("arm_tag", "capability", "burden", "t3_gen",
                           "evolvability", "cap_bin", "phenotype_digest")}
                for i in fr["front_indices"]]

    # ---- throughput against the parents, on the parents' own unit
    thr = {}
    for r in runs:
        tag = "%s|%s" % (r["arm"], r["lane"])
        thr.setdefault(tag, {"morph_per_cpu_hour": [], "distinct_phenotypes": [],
                             "distinct_behaviours": [], "search_s": []})
        t = thr[tag]
        if _num(r.get("morphologies_per_cpu_hour")):
            t["morph_per_cpu_hour"].append(r["morphologies_per_cpu_hour"])
        t["distinct_phenotypes"].append(r.get("distinct_t2_viable_phenotypes"))
        t["distinct_behaviours"].append(r.get("distinct_t2_viable_behaviours"))
        if _num(r.get("search_elapsed_s")):
            t["search_s"].append(r["search_elapsed_s"])
    throughput = {}
    for tag, t in sorted(thr.items()):
        mp = [x for x in t["morph_per_cpu_hour"] if _num(x)]
        dp = [x for x in t["distinct_phenotypes"] if _num(x)]
        db = [x for x in t["distinct_behaviours"] if _num(x)]
        throughput[tag] = {
            "n_seeds": len(t["distinct_phenotypes"]),
            "mean_morphologies_per_cpu_hour": (round(statistics.fmean(mp), 2)
                                               if mp else None),
            "mean_distinct_t2_viable_phenotypes_per_seed": (
                round(statistics.fmean(dp), 2) if dp else None),
            "mean_distinct_behaviours_per_seed": (round(statistics.fmean(db), 2)
                                                  if db else None),
            "mean_search_seconds_per_seed": (round(statistics.fmean(t["search_s"]), 3)
                                             if t["search_s"] else None),
        }

    # ---- who owns the front, arm by arm, and where a parent owns it
    owners = collections.Counter(all_records[i]["arm_tag"]
                                 for i in front_report["front_indices"])
    cov_owners = collections.Counter(all_records[i]["arm_tag"]
                                     for i in front_cov["front_indices"])

    parent_verdict = {}
    for name, p in PARENTS.items():
        pv = p.get("morphologies_per_cpu_hour")
        beaten_by = [tag for tag, t in throughput.items()
                     if _num(t.get("mean_morphologies_per_cpu_hour"))
                     and t["mean_morphologies_per_cpu_hour"] > pv]
        parent_verdict[name] = {
            "parent_morphologies_per_cpu_hour": pv,
            "arms_exceeding_on_throughput": beaten_by,
            "verdict": ("PARENT_SUFFICIENT_ON_THROUGHPUT" if not beaten_by
                        else "EXCEEDED_ON_THROUGHPUT"),
            "caveat": ("throughput only. The parents were never scored on "
                       "burden, T3 or evolvability, so this comparison covers "
                       "one axis of four and is not a front comparison."),
        }

    # ---- falsifiers
    null = EV.shuffle_null([r for r in all_records
                            if _num(r.get("evolvability"))],
                           seed=20260910, n_perm=1000)
    redundancy = EV.redundancy_check(all_records)

    # The discriminating diagnostic for any evolvability null: if the gate
    # accepts the first proposal every time it is not gating, and the null is
    # attributable to the MUTATION OPERATOR being near-neutral on the future
    # family -- a single-stage attribution, not "evolvability does not exist".
    det = [r["evolvability_detail"] for r in all_records
           if isinstance(r.get("evolvability_detail"), dict)]
    gate_diag: Dict[str, Any] = {"n_measured": len(det)}
    if det:
        gate_diag.update({
            "n_accepted_distribution": dict(collections.Counter(
                d.get("n_accepted") for d in det)),
            "total_proposals_distribution": dict(collections.Counter(
                d.get("total_proposals") for d in det)),
            "delta_cap_fof_zero": sum(1 for d in det
                                      if abs(d.get("delta_cap_fof", 0.0)) < 1e-9),
            "delta_cap_fof_positive": sum(1 for d in det
                                          if d.get("delta_cap_fof", 0.0) > 1e-9),
            "delta_cap_fof_negative": sum(1 for d in det
                                          if d.get("delta_cap_fof", 0.0) < -1e-9),
            "mean_cap_fof_before": round(statistics.fmean(
                [d["cap_fof_before"] for d in det
                 if _num(d.get("cap_fof_before"))]), 6),
        })
        always_first = all(d.get("total_proposals") == 3 for d in det
                           if d.get("total_proposals") is not None)
        allzero = gate_diag["delta_cap_fof_zero"] == len(det)
        gate_diag["gate_is_gating"] = not always_first
        gate_diag["attribution"] = (
            "MUTATION_OPERATOR_NEUTRAL_ON_FUTURE_FAMILY"
            if (always_first and allzero) else
            ("GOVERNANCE_SELECTIVE" if not always_first else "MIXED"))

    # ---- dedup lever: yield against price
    dedup = {}
    for r in runs:
        tag = "%s|%s" % (r["arm"], r["lane"])
        d = r.get("dedup_cost") or {}
        e = dedup.setdefault(tag, {"calls": 0, "distinct": 0, "dups": 0,
                                   "seconds": 0.0, "n": 0})
        e["calls"] += d.get("n_signature_calls", 0)
        e["distinct"] += d.get("n_distinct_behaviours", 0)
        e["dups"] += d.get("n_duplicates_suppressed", 0)
        e["seconds"] += d.get("dedup_seconds", 0.0)
        e["n"] += 1
    for tag, e in dedup.items():
        e["duplicate_fraction"] = (round(e["dups"] / e["calls"], 6)
                                   if e["calls"] else None)
        e["seconds_per_call"] = (round(e["seconds"] / e["calls"], 9)
                                 if e["calls"] else None)

    # ---- burden decomposition and the honesty term
    reject = [r["reject_share_per_retained"] for r in runs
              if _num(r.get("reject_share_per_retained"))]
    bown = [r["B_own"] for r in all_records if _num(r.get("B_own"))]
    ledger_search = [r["ledger"]["search_charged_work"] for r in runs]
    ledger_meas = [r["ledger"]["measurement_charged_work"] for r in runs]

    # ---- T3, against the GS-R2 boundary
    # GS-R2's SURVIVOR_T3_GENERALIZATION_{HOLD,FAIL} verdict is r3["feasible"]
    # -- the full frozen hard-gate report on the T3 evaluation (see
    # hpc/aggregate_gs_r2.py:175). It is NOT solved_fraction >= floor. Scoring
    # solved_fraction and putting it beside GS-R2's 84.4% would compare two
    # different quantities, so the verdict-comparable count uses t3_feasible
    # and the solved-fraction summary is reported separately and labelled.
    t3 = [r["t3_gen"] for r in all_records if _num(r.get("t3_gen"))]
    t3_feas = [r for r in all_records if isinstance(r.get("t3_feasible"), bool)]
    t3_hold = sum(1 for r in t3_feas if r["t3_feasible"])

    # ---- equal-n control for the dedup comparison
    # Behavioural dedup shrinks the archive by roughly an order of magnitude, so
    # asking which arm owns the JOINT front rewards the larger archive
    # mechanically: more draws, more front members. Selectivity is not edge.
    # This subsamples the no-dedup records down to the dedup arm's record count
    # and recomputes ownership, repeatedly.
    import random as _random
    dedup_recs = [r for r in all_records if r["arm"] == "FO_DEDUP"]
    nodedup_recs = [r for r in all_records if r["arm"] == "FO_NODEDUP"]
    equal_n: Dict[str, Any] = {
        "n_dedup_records": len(dedup_recs),
        "n_nodedup_records": len(nodedup_recs),
        "note": ("joint-front ownership is confounded by archive size; this "
                 "control equalises n before comparing"),
    }
    if dedup_recs and len(nodedup_recs) > len(dedup_recs):
        rr = _random.Random(20260910)
        n = len(dedup_recs)
        wins = {"FO_DEDUP": 0, "FO_NODEDUP": 0, "tie": 0}
        trials = 200
        for _ in range(trials):
            sub = rr.sample(nodedup_recs, n)
            merged = dedup_recs + sub
            fr = OB.pareto_front_k(merged, "coverage_objectives",
                                   OB.COVERAGE_MAXIMIZE)
            cnt = collections.Counter(merged[i]["arm"]
                                      for i in fr["front_indices"])
            d, nd = cnt.get("FO_DEDUP", 0), cnt.get("FO_NODEDUP", 0)
            if d > nd:
                wins["FO_DEDUP"] += 1
            elif nd > d:
                wins["FO_NODEDUP"] += 1
            else:
                wins["tie"] += 1
        equal_n.update({
            "status": "OK", "trials": trials, "n_per_arm": n,
            "front_ownership_wins": wins,
            "verdict": ("NO_DEDUP_ADVANTAGE_AT_EQUAL_N"
                        if wins["FO_NODEDUP"] <= wins["FO_DEDUP"]
                        else "NODEDUP_OWNS_MORE_FRONT_AT_EQUAL_N"),
        })
    else:
        equal_n["status"] = "CANNOT_CHECK_INSUFFICIENT_RECORDS"

    # ---- WHY dedup loses: is the retained representative arbitrary?
    # Behavioural dedup keeps the FIRST member of each behaviour class it meets.
    # If members of a class differ in burden, "first" is arbitrary with respect
    # to the objective and the class's cheapest member is discarded whenever it
    # is not seen first. That would be an implementation choice, not a property
    # of behavioural dedup, and it has a concrete fix: keep the argmin-burden
    # member instead.
    classes: Dict[str, List[float]] = collections.defaultdict(list)
    for r in all_records:
        sig = r.get("behaviour_signature")
        if sig and _num(r.get("burden")):
            classes[sig].append(r["burden"])
    multi = {k: v for k, v in classes.items() if len(v) > 1}
    spreads = [max(v) - min(v) for v in multi.values()]
    rel = [(max(v) - min(v)) / max(v) for v in multi.values() if max(v) > 0]
    dedup_mechanism = {
        "n_behaviour_classes": len(classes),
        "n_classes_with_multiple_members": len(multi),
        "n_classes_with_burden_spread": sum(1 for x in spreads if x > 1e-9),
        "fraction_of_multi_classes_with_spread": (
            round(sum(1 for x in spreads if x > 1e-9) / len(multi), 6)
            if multi else None),
        "mean_absolute_burden_spread_within_class": (
            round(statistics.fmean(spreads), 4) if spreads else None),
        "mean_relative_burden_spread_within_class": (
            round(statistics.fmean(rel), 6) if rel else None),
        "interpretation": (
            "a class whose members differ in burden loses its cheapest member "
            "whenever that member is not encountered first; if the spread is "
            "widespread this is an implementation choice with a concrete fix "
            "(retain argmin-burden per class), not a property of behavioural "
            "dedup itself"),
    }

    # ---- why records could not be checked
    # A record outside the evolvability subsample is a different thing from a
    # record where evolvability was attempted and came out undefined. Collapsing
    # both into one CANNOT_CHECK bucket makes the front's coverage illegible.
    reasons = collections.Counter()
    for r in all_records:
        if not _num(r.get("evolvability")):
            det = r.get("evolvability_detail")
            if det is None and "evolvability_error" not in r:
                reasons["evolvability:NOT_SAMPLED"] += 1
            elif "evolvability_error" in r:
                reasons["evolvability:EXCEPTION"] += 1
            else:
                reasons["evolvability:" + str(det.get("status"))] += 1
        if not _num(r.get("t3_gen")):
            reasons["t3:missing"] += 1

    # ---- the region map: where each form wins and loses
    # Front membership alone names a champion. The deliverable is a map, so
    # every structural axis is tabulated with the rate at which its levels
    # reach the front and their burden and T3 behaviour. A level that never
    # reaches the front is as informative as one that dominates it.
    region_map: Dict[str, Any] = {}
    front_ids = set(front_cov["front_indices"])
    for axis in ("F_arch", "Pi_arch", "L", "R", "K", "T_family", "n_units"):
        tab: Dict[Any, Dict[str, Any]] = {}
        for i, r in enumerate(all_records):
            lvl = r.get(axis)
            if lvl is None:
                continue
            e = tab.setdefault(str(lvl), {"n": 0, "n_front": 0,
                                          "burden": [], "t3": [], "cap": []})
            e["n"] += 1
            if i in front_ids:
                e["n_front"] += 1
            if _num(r.get("burden")):
                e["burden"].append(r["burden"])
            if _num(r.get("t3_gen")):
                e["t3"].append(r["t3_gen"])
            if _num(r.get("capability")):
                e["cap"].append(r["capability"])
        region_map[axis] = {
            lvl: {
                "n": e["n"], "n_on_front": e["n_front"],
                "front_rate": round(e["n_front"] / e["n"], 6) if e["n"] else None,
                "mean_burden": (round(statistics.fmean(e["burden"]), 3)
                                if e["burden"] else None),
                "mean_capability": (round(statistics.fmean(e["cap"]), 6)
                                    if e["cap"] else None),
                "mean_t3": (round(statistics.fmean(e["t3"]), 6)
                            if e["t3"] else None),
            }
            for lvl, e in sorted(tab.items())
        }

    # Per capability bin: the cheapest form and its structural signature.
    by_bin: Dict[Any, List[int]] = collections.defaultdict(list)
    for i, r in enumerate(all_records):
        if r.get("cap_bin") is not None and _num(r.get("burden")):
            by_bin[int(r["cap_bin"])].append(i)
    bin_map = {}
    for b, idxs in sorted(by_bin.items()):
        best = min(idxs, key=lambda i: all_records[i]["burden"])
        r = all_records[best]
        bin_map[str(b)] = {
            "n": len(idxs),
            "cheapest": {k: r.get(k) for k in
                         ("arm_tag", "capability", "burden", "t3_gen",
                          "F_arch", "Pi_arch", "L", "R", "K", "n_units")},
            "mean_burden": round(statistics.fmean(
                [all_records[i]["burden"] for i in idxs]), 3),
        }

    c_viol = sum(r["c_immutability"]["n_violations"] for r in runs)

    return {
        "study": "FO_ARMS_AGGREGATE_V1",
        "protocol": "FORM_ORACLE_PROTOCOL_V1",
        "protocol_sha256": ("3c956d336793b04c98c8dce19af2137e"
                            "7365c3ef971bd70aefaeed889ecbf833"),
        "n_arm_runs": len(runs),
        "n_records": len(all_records),
        "arms": sorted(per_arm),
        "front_report": {**{k: v for k, v in front_report.items()
                            if k != "cannot_check_indices"},
                         "members": _front_rows(front_report),
                         "owners": dict(owners)},
        "front_coverage": {**{k: v for k, v in front_cov.items()
                              if k != "cannot_check_indices"},
                           "members": _front_rows(front_cov)[:200],
                           "owners": dict(cov_owners)},
        "throughput_vs_parents": {"arms": throughput, "parents": PARENTS,
                                  "verdict": parent_verdict},
        "falsifier_F1_shuffle_null": null,
        "falsifier_F2_redundancy": redundancy,
        "evolvability_gate_diagnostic": gate_diag,
        "dedup_lever": dedup,
        "burden": {
            "mean_reject_share_per_retained": (round(statistics.fmean(reject), 4)
                                               if reject else None),
            "mean_B_own": (round(statistics.fmean(bown), 4) if bown else None),
            "mean_search_charged_work": round(statistics.fmean(ledger_search), 2),
            "mean_measurement_charged_work": round(statistics.fmean(ledger_meas), 2),
            "note": ("reject share is SEARCH work per retained member; "
                     "measurement work is excluded so burden and evolvability "
                     "are not entangled through the ledger"),
        },
        "t3": {
            "verdict_comparable": {
                "criterion": ("t3_feasible == the frozen hard-gate report on "
                              "the T3 evaluation; identical to GS-R2's "
                              "SURVIVOR_T3_GENERALIZATION_HOLD/FAIL rule"),
                "n_scored": len(t3_feas),
                "n_hold": t3_hold,
                "n_fail": len(t3_feas) - t3_hold,
                "fail_fraction": (round((len(t3_feas) - t3_hold) / len(t3_feas), 6)
                                  if t3_feas else None),
            },
            "solved_fraction_summary_NOT_A_VERDICT": {
                "n_scored": len(t3),
                "mean": round(statistics.fmean(t3), 6) if t3 else None,
            },
            "gs_r2_reference": {**GS_R2_T3,
                                "fail_fraction": round(GS_R2_T3["fail"]
                                                       / GS_R2_T3["total"], 6),
                                "criterion": "r3['feasible'] (same rule)"},
        },
        "equal_n_dedup_control": equal_n,
        "dedup_mechanism": dedup_mechanism,
        "region_map": region_map,
        "capability_bin_map": bin_map,
        "cannot_check_reasons": dict(reasons),
        "c_immutability": {"total_violations": c_viol,
                           "verdict": ("NO_CONFIGURATION_ALTERED_C"
                                       if c_viol == 0 else "C_ALTERABLE_BUG")},
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="fo/results")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = aggregate(a.results)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(res, fh, sort_keys=True, separators=(",", ":"), default=str)
    os.replace(tmp, a.out)
    sys.stderr.write("front aggregate: %s\n"
                     % json.dumps({k: v for k, v in res.items()
                                   if not isinstance(v, (dict, list))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
