"""D27 campaign — continued vs reset vs knockout across sampled forms.

For each sampled legal form that is T2-feasible, run all six lineage arms, run
the three parent arms, attribute the continued-over-reset advantage to a single
inherited object by knockout, and test the B_future_cognition signature against
its unrelated and harmful controls.

Nothing here chooses which forms count after seeing their results: the sample
is a seeded draw from the legality-bounded vocabulary, and every drawn form
that clears the frozen T2 feasibility gate is kept.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from typing import Any, Dict, List, Optional

from oracle.burden import RejectLedger, b_own
from oracle.d27_lineage import (ARMS, INHERITED_OBJECTS, first_useful_epoch,
                                knockout_attribution, run_arm,
                                signature_with_controls)


def _parent_arms(genome: Any, t2: Dict[str, Any]) -> Dict[str, Any]:
    """The three #277 sec 7 parent arms, at matched information and budget.

    TASK_SPECIFIC_OCM is the per-family specialist upper bound: for each frozen
    family, the best solve rate any arm of THIS form achieves on that family
    alone, with no credit for transfer between families. It is deliberately a
    strong parent -- a specialist per task is exactly what a developmental
    claim has to beat.
    """
    from evaluation.evaluate import evaluate_genome
    out: Dict[str, Any] = {}

    per_family_best: Dict[str, float] = {}
    for arm in ("CONTINUED_OCM", "RESET_OCM"):
        r = run_arm(genome, arm)
        if r.get("status") != "OK":
            continue
        for fam, v in (r.get("per_family") or {}).items():
            tot = float(v.get("total", 0) or 0)
            frac = (float(v.get("solved", 0)) / tot) if tot else 0.0
            per_family_best[fam] = max(per_family_best.get(fam, 0.0), frac)
    out["TASK_SPECIFIC_OCM"] = {
        "status": "OK" if per_family_best else "CANNOT_CHECK_NO_FAMILIES",
        "capability": (round(statistics.fmean(per_family_best.values()), 6)
                       if per_family_best else None),
        "per_family_best": {k: round(v, 6)
                            for k, v in sorted(per_family_best.items())},
        "note": "per-family specialist upper bound; no transfer credit",
    }

    g = genome
    persistent = (getattr(g, "L", None) != "none"
                  or getattr(g, "K", None) in ("episodic_store",
                                               "procedural_store"))
    approximate = (getattr(g, "F_arch", None) == "approx_projection_vsa"
                   or "assoc_similarity" in {u.unit_type
                                             for u in getattr(g, "U", [])})
    cont = run_arm(genome, "CONTINUED_OCM")
    out["STRONG_PERSISTENT_NON_NEURAL_PARENT"] = {
        "status": "OK" if (persistent and not approximate) else
                  "CANNOT_CHECK_FORM_NOT_IN_PARENT_CLASS",
        "capability": cont.get("capability") if persistent and not approximate
                      else None,
        "B_own": cont.get("B_own") if persistent and not approximate else None,
        "class_test": {"persistent": persistent, "approximate": approximate},
    }
    out["STRONG_ADAPTIVE_APPROXIMATE_PARENT"] = {
        "status": "OK" if approximate else
                  "CANNOT_CHECK_FORM_NOT_IN_PARENT_CLASS",
        "capability": cont.get("capability") if approximate else None,
        "B_own": cont.get("B_own") if approximate else None,
        "class_test": {"approximate": approximate},
        "deviation": ("#277 sec 7 names STRONG_ADAPTIVE_NEURAL_PARENT; no "
                      "learned neural parent exists in this stack"),
    }
    return out


def run_campaign(seed: int, n_forms: int, max_draws: int = 4000,
                 with_signature: bool = True) -> Dict[str, Any]:
    from evaluation.evaluate import evaluate_genome
    from morphology.gs_bound import gs_uniform_sample

    t0 = time.time()
    rng = random.Random(seed)
    ledger = RejectLedger()
    forms: List[Dict[str, Any]] = []
    n_drawn = 0
    n_infeasible = 0

    while len(forms) < n_forms and n_drawn < max_draws:
        n_drawn += 1
        g = gs_uniform_sample(rng)
        try:
            r = evaluate_genome(g, tier="T2")
        except Exception:  # noqa: BLE001
            ledger.charge_crash("T2")
            continue
        ledger.charge_eval("T2", r.get("evaluation"))
        if not r.get("feasible"):
            n_infeasible += 1
            continue

        by_arm = {a: run_arm(g, a) for a in ARMS}
        for a, rec in by_arm.items():
            if rec.get("status") == "OK":
                ledger.charge_eval("D27_%s" % a,
                                   {"work_total": rec.get("work_total", 0.0)})
        att = knockout_attribution(by_arm)

        entry: Dict[str, Any] = {
            "seed": seed,
            "genotype_digest": r.get("genotype_digest"),
            "phenotype_digest": r.get("phenotype_digest"),
            "F_arch": getattr(g, "F_arch", None),
            "Pi_arch": getattr(g, "Pi_arch", None),
            "L": getattr(g, "L", None), "R": getattr(g, "R", None),
            "K": getattr(g, "K", None), "T_family": getattr(g, "T", None),
            "n_units": len(getattr(g, "U", []) or []),
            "arms": {a: {k: v for k, v in rec.items()
                         if k not in ("per_family", "inherited_store_by_epoch")}
                     for a, rec in by_arm.items()},
            "first_useful_epoch": {a: first_useful_epoch(rec)
                                   for a, rec in by_arm.items()},
            "attribution": att,
            "parents": _parent_arms(g, r),
        }
        if with_signature:
            try:
                entry["signature"] = signature_with_controls(
                    g, by_arm["CONTINUED_OCM"])
            except Exception as e:  # noqa: BLE001
                entry["signature"] = {"status": "CANNOT_CHECK_EXCEPTION",
                                      "error": repr(e)[:200]}
        forms.append(entry)

    ledger.n_retained = len(forms)
    ledger.settle()
    return {
        "study": "FO_D27_LINEAGE_V1",
        "seed": seed, "n_forms": len(forms), "n_drawn": n_drawn,
        "n_infeasible": n_infeasible,
        "arms": list(ARMS),
        "inherited_objects": list(INHERITED_OBJECTS),
        "ledger": ledger.report(),
        "elapsed_s": round(time.time() - t0, 3),
        "forms": forms,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n-forms", type=int, default=40)
    ap.add_argument("--no-signature", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = run_campaign(a.seed, a.n_forms, with_signature=not a.no_signature)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(res, fh, sort_keys=True, separators=(",", ":"), default=str)
    os.replace(tmp, a.out)
    with open(a.out + ".status", "w") as fh:
        fh.write("OK\n")
    sys.stderr.write("D27 seed=%d forms=%d drawn=%d elapsed=%.1fs\n"
                     % (a.seed, res["n_forms"], res["n_drawn"],
                        res["elapsed_s"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
