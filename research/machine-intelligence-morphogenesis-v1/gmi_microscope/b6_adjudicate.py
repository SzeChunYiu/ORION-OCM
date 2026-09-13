"""RV-377-180 -- mechanical scoring of the frozen B6 predictions D1a..D5.

Reads the arm receipts written by b6_development.run_arm and scores each frozen
prediction exactly as GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md states it.
No threshold, quantifier or falsifier is introduced here that is not in that table.

    python3 -m gmi_microscope.b6_adjudicate <host> [seeds]

Readings fixed here (stated so they are auditable, not silently chosen):
  * DISJ has no RESET arm of its own; the freeze shares CROSS's RESET as the baseline
    (same E_b, same seed), exactly as b6_development.summary does.
  * "RESET's seed spread" = max - min of the RESET arm's value over the three seeds,
    computed on B_morph for D3a and on B_dense for D2d.
  * D2d compares DISJ-CONTINUED's B_dense against the RESET B_dense of the SAME seed.
  * A prediction of the form "X on >= 2/3 seeds" is HELD iff it holds on >= 2 of the
    seeds that are scoreable; seeds that are UNDETERMINED are excluded from the
    denominator only where the freeze says so (D2b, D2d), never elsewhere.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
REVIVAL = "RV-377-180"
MEMORY_CLASSES = {"TABLE", "KVSTORE", "PROGRAM"}
SMOOTH1_OCCUPANTS = {"KVSTORE", "PROGRAM", "TABLE"}


def path(pair, arm, seed, host):
    if pair == "DISJ" and arm == "RESET":
        pair = "CROSS"          # shared baseline, same E_b and seed
    return os.path.join(RES, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_{host}.json")


def load(pair, arm, seed, host):
    p = path(pair, arm, seed, host)
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    fa = d.get("first_admissible") or {}
    fd = d.get("first_dense_admissible") or {}
    return {
        "B_morph": fa.get("B_morph") if fa.get("found") else None,
        "found": bool(fa.get("found")),
        "class": fa.get("carrier_atrophied"),
        "origin": fa.get("origin"),
        "B_dense": fd.get("B_morph") if fd.get("found") else None,
        "dense_found": bool(fd.get("found")),
        "final_best": d.get("final_best_capability_standard"),
        "final_best_dense": (d.get("final_best_by_carrier") or {}).get("DENSE"),
    }


def spread(vals):
    v = [x for x in vals if x is not None]
    return (max(v) - min(v)) if len(v) >= 2 else None


def _tally(per_seed):
    """per_seed: seed -> True / False / None(undetermined)."""
    det = {s: v for s, v in per_seed.items() if v is not None}
    return sum(1 for v in det.values() if v), len(det), per_seed


def adjudicate(host, seeds=(0, 1, 2), validation_only=False):
    """validation_only=True runs the scorer on a partial seed set to check the
    instrument against real receipts. The frozen quantifier is ">= 2 of 3 seeds",
    so a run on fewer than three seeds can never be an adjudication: it is written
    to a separate file and stamped, never to the adjudication receipt."""
    if len(seeds) != 3 and not validation_only:
        raise SystemExit("REFUSED: the freeze quantifies over exactly 3 seeds; "
                         "pass validation_only=True to inspect a partial set")
    R = {(p, a, s): load(p, a, s, host) for p in ("SAME", "CROSS", "DISJ")
         for a in ("RESET", "CONTINUED", "TWIN") for s in seeds}
    missing = sorted(f"{p}|{a}|S{s}" for (p, a, s), v in R.items() if v is None)
    out = {"schema": "StageB6AdjudicationV1",
           "validation_only": bool(validation_only), "revival_record": REVIVAL, "host": host,
           "seeds": list(seeds), "missing_units": missing,
           "complete": not missing, "rows": {f"{p}|{a}|S{s}": v for (p, a, s), v in R.items() if v},
           "predictions": {}}

    def lt(pair, a, b, s):
        x, y = R[(pair, a, s)], R[(pair, b, s)]
        if not x or not y or x["B_morph"] is None or y["B_morph"] is None:
            return None
        return x["B_morph"] < y["B_morph"]

    def rec(pid, per_seed, rule, detail=None):
        """A ">= 2 of 3" prediction is decidable early in one direction only:
        two hits settle it HELD whatever the third seed does, and it is FAILED only
        once two or more seeds are known NOT to satisfy it. Anything in between is
        PENDING, never FAILED -- a missing unit is not a refutation."""
        ok, n, _ = _tally(per_seed)
        n_false = sum(1 for v in per_seed.values() if v is False)
        if validation_only:
            verdict = "NOT_SCORED__PARTIAL_SEED_SET"
        elif ok >= 2:
            verdict = "HELD"
        elif len(per_seed) - n_false < 2:
            verdict = "FAILED"
        elif n < len(per_seed):
            verdict = "PENDING_MORE_UNITS"
        else:
            verdict = "UNDETERMINED" if n == 0 else "FAILED"
        out["predictions"][pid] = {"per_seed": {str(s): per_seed[s] for s in per_seed},
                                   "n_true": ok, "n_determined": n, "verdict": verdict,
                                   "rule": rule}
        if detail:
            out["predictions"][pid]["detail"] = detail

    # D1a / D1b / D1s -- SAME
    rec("D1a", {s: lt("SAME", "CONTINUED", "RESET", s) for s in seeds},
        "SAME: B_morph(CONTINUED) < B_morph(RESET) on >= 2/3 seeds")
    rec("D1b", {s: lt("SAME", "CONTINUED", "TWIN", s) for s in seeds},
        "SAME residual: B_morph(CONTINUED) < B_morph(TWIN) on >= 2/3 seeds [LOAD-BEARING]")
    rec("D1s", {s: (None if lt("SAME", "TWIN", "RESET", s) is None else not lt("SAME", "TWIN", "RESET", s))
                for s in seeds},
        "SAME strong form (reported, predicted to FAIL): TWIN does NOT beat RESET on >= 2/3 seeds")

    # D2a -- CROSS: earlier AND memory class
    d2a = {}
    for s in seeds:
        e = lt("CROSS", "CONTINUED", "RESET", s)
        c = R[("CROSS", "CONTINUED", s)]
        k = None if not c or c["class"] is None else (c["class"] in MEMORY_CLASSES)
        d2a[s] = None if (e is None or k is None) else (e and k)
    rec("D2a", d2a, "CROSS: CONTINUED earlier than RESET AND first atrophied class is memory, each on >= 2/3 seeds",
        {"classes": {str(s): (R[("CROSS", "CONTINUED", s)] or {}).get("class") for s in seeds}})

    # D2b -- committed sign, determined seeds only
    d2b = {}
    for s in seeds:
        c, r = R[("CROSS", "CONTINUED", s)], R[("CROSS", "RESET", s)]
        if not c or not r or not c["dense_found"] or not r["dense_found"]:
            d2b[s] = None
        else:
            d2b[s] = c["B_dense"] > r["B_dense"]
    ok, n, _ = _tally(d2b)
    out["predictions"]["D2b"] = {
        "per_seed": {str(s): d2b[s] for s in seeds}, "n_true": ok, "n_determined": n,
        "verdict": "NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                   ("FAILED" if (n and ok < n) else
                    ("PENDING_MORE_UNITS" if any(R[("CROSS", a, s)] is None for a in ("CONTINUED", "RESET") for s in seeds)
                     else ("UNDETERMINED__NO_DETERMINED_SEED" if n == 0 else "HELD"))),
        "rule": "CROSS: B_dense(CONTINUED) > B_dense(RESET) on EVERY determined seed; undetermined seeds excluded"}

    # D2c -- continuous form, always determined
    d2c = {}
    for s in seeds:
        c, r = R[("CROSS", "CONTINUED", s)], R[("CROSS", "RESET", s)]
        d2c[s] = None if not c or not r or c["final_best_dense"] is None or r["final_best_dense"] is None \
            else c["final_best_dense"] <= r["final_best_dense"]
    rec("D2c", d2c, "CROSS: CONTINUED final best DENSE-cell capability <= RESET's on >= 2/3 seeds",
        {"continued": {str(s): (R[("CROSS", "CONTINUED", s)] or {}).get("final_best_dense") for s in seeds},
         "reset": {str(s): (R[("CROSS", "RESET", s)] or {}).get("final_best_dense") for s in seeds}})

    # D2d -- class-conditioned, uses RESET's B_dense spread
    sp_dense = spread([(R[("CROSS", "RESET", s)] or {}).get("B_dense") for s in seeds])
    d2d = {}
    for s in seeds:
        c, r = R[("DISJ", "CONTINUED", s)], R[("CROSS", "RESET", s)]
        if not c or not r or c["B_dense"] is None or r["B_dense"] is None or sp_dense is None:
            d2d[s] = None
        else:
            d2d[s] = abs(c["B_dense"] - r["B_dense"]) <= sp_dense
    ok, n, _ = _tally(d2d)
    out["predictions"]["D2d"] = {
        "per_seed": {str(s): d2d[s] for s in seeds}, "n_true": ok, "n_determined": n,
        "verdict": ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                    ("HELD" if ok >= 2 else
                     ("PENDING_MORE_UNITS" if any(R[(pp, aa, ss)] is None for pp, aa in
                                                  (("DISJ", "CONTINUED"), ("CROSS", "RESET")) for ss in seeds)
                      else ("HELD_VACUOUSLY__NO_DETERMINED_SEED" if n == 0 else "FAILED")))),
        "reset_B_dense_spread": sp_dense,
        "rule": "DISJ-CONTINUED B_dense within RESET seed spread, or UNDETERMINED, on >= 2/3 seeds"}

    # D3a / D3b -- DISJ
    sp_morph = spread([(R[("CROSS", "RESET", s)] or {}).get("B_morph") for s in seeds])
    d3a = {}
    for s in seeds:
        c, t = R[("DISJ", "CONTINUED", s)], R[("DISJ", "TWIN", s)]
        if not c or not t or c["B_morph"] is None or t["B_morph"] is None or sp_morph is None:
            d3a[s] = None
        else:
            d3a[s] = abs(c["B_morph"] - t["B_morph"]) <= sp_morph
    rec("D3a", d3a, "DISJ: |B_morph(CONTINUED) - B_morph(TWIN)| <= RESET seed spread on >= 2/3 seeds",
        {"reset_B_morph_spread": sp_morph})
    rec("D3b", {s: lt("DISJ", "CONTINUED", "RESET", s) for s in seeds},
        "DISJ: B_morph(CONTINUED) < B_morph(RESET) on >= 2/3 seeds (parent's prediction)")

    # D4 -- quality preserved, every pair
    d4pairs = {}
    for p in ("SAME", "CROSS", "DISJ"):
        per = {}
        for s in seeds:
            c, r = R[(p, "CONTINUED", s)], R[(p, "RESET", s)]
            per[s] = None if not c or not r or c["final_best"] is None or r["final_best"] is None \
                else c["final_best"] >= r["final_best"]
        ok, n, _ = _tally(per)
        nf = sum(1 for v in per.values() if v is False)
        if validation_only:
            pv = "NOT_SCORED__PARTIAL_SEED_SET"
        elif ok >= 2:
            pv = "HELD"
        elif len(seeds) - nf < 2:
            pv = "FAILED"
        elif n < len(seeds):
            pv = "PENDING_MORE_UNITS"
        else:
            pv = "UNDETERMINED" if n == 0 else "FAILED"
        d4pairs[p] = {"per_seed": {str(s): per[s] for s in seeds}, "n_true": ok, "n_determined": n,
                      "verdict": pv}
    vs = [v["verdict"] for v in d4pairs.values()]
    # every pair must be HELD; anything else (FAILED, UNDETERMINED, NOT_SCORED) must not roll up to HELD
    if validation_only:
        d4v = "NOT_SCORED__PARTIAL_SEED_SET"
    elif "FAILED" in vs:
        d4v = "FAILED"
    elif "PENDING_MORE_UNITS" in vs:
        d4v = "PENDING_MORE_UNITS"
    elif all(v == "HELD" for v in vs):
        d4v = "HELD"
    else:
        d4v = "UNDETERMINED"
    out["predictions"]["D4"] = {"per_pair": d4pairs, "verdict": d4v,
                                "rule": "CONTINUED final best >= RESET's on >= 2/3 seeds on EVERY pair"}

    # D5 -- SAME: occupant class and lineage root is a seed elite
    d5 = {}
    for s in seeds:
        c = R[("SAME", "CONTINUED", s)]
        if not c or c["class"] is None or c["origin"] is None:
            d5[s] = None
        else:
            root_is_seed = isinstance(c["origin"], (list, tuple)) and len(c["origin"]) >= 1 and c["origin"][0] == "seed"
            d5[s] = (c["class"] in SMOOTH1_OCCUPANTS) and root_is_seed
    rec("D5", d5, "SAME: CONTINUED first admissible class in {KVSTORE,PROGRAM,TABLE} and lineage root is a seed elite, on >= 2/3 seeds",
        {"class_origin": {str(s): [(R[("SAME", "CONTINUED", s)] or {}).get("class"),
                                   (R[("SAME", "CONTINUED", s)] or {}).get("origin")] for s in seeds}})

    # ---- RV-377-180-Z: separate registration on coefficient-carrier reachability.
    # Scored apart from D1a..D5; a Z outcome cannot change any D verdict or the D terminal.
    def dense_hits(pair, arm):
        per = {}
        for s in seeds:
            r = R[(pair, arm, s)]
            per[s] = None if not r else bool(r["dense_found"])
        return per

    Z = {}
    z1, z2, z3 = dense_hits("SAME", "CONTINUED"), dense_hits("SAME", "RESET"), dense_hits("SAME", "TWIN")

    def zrec(zid, per, ok_fn, rule):
        n = sum(1 for v in per.values() if v is not None)
        hits = sum(1 for v in per.values() if v)
        unknown = len(seeds) - n
        # settled early iff the verdict is the same for every way the missing seeds could land
        outcomes = {ok_fn(hits + extra) for extra in range(unknown + 1)}
        verdict = ("NOT_SCORED__PARTIAL_SEED_SET" if validation_only else
                   ("HELD" if outcomes == {True} else
                    ("FAILED" if outcomes == {False} else "PENDING_MORE_UNITS")))
        Z[zid] = {"per_seed": {str(s): per[s] for s in per}, "n_hits": hits,
                  "n_determined": n, "verdict": verdict, "rule": rule}

    zrec("Z1", z1, lambda h: h >= 2, "SAME/CONTINUED reaches atrophied-DENSE on >= 2/3 seeds")
    zrec("Z2", z2, lambda h: h == 0, "SAME/RESET reaches it on 0/3 seeds (within-lane control for the 0-of-43 invariant)")
    zrec("Z3", z3, lambda h: h <= 1, "SAME/TWIN reaches it on <= 1/3 seeds (residual over 'any warm start helps')")
    Z["Z4_reported_only"] = {"note": "CROSS target E_sym5 lists DENSE as a registered occupant; a DENSE "
                                     "recovery there is expected under any arm and is reported, not scored",
                             "cross": {a: {str(s): v for s, v in dense_hits("CROSS", a).items()}
                                       for a in ("RESET", "CONTINUED", "TWIN")}}
    if validation_only:
        Z["terminal"] = "NOT_SCORED__PARTIAL_SEED_SET"
    elif any(Z[k]["verdict"] in ("UNDETERMINED", "PENDING_MORE_UNITS") for k in ("Z1", "Z2", "Z3")):
        Z["terminal"] = "Z_UNDETERMINED__UNITS_MISSING"
    elif Z["Z2"]["verdict"] == "FAILED":
        # F-Z2: the cell is reachable cold, so this is about speed, not reachability
        Z["terminal"] = "COEFFICIENT_CELL_REACHABLE_COLD__NO_CLAIM_ON_THE_INVARIANT"
    elif Z["Z1"]["verdict"] == "HELD" and Z["Z3"]["verdict"] == "FAILED":
        # F-Z3: any developed archive suffices -> the warm-start parents own it
        Z["terminal"] = "COEFFICIENT_LIFT_PARENT_SUFFICIENT_OOPS"
    elif Z["Z1"]["verdict"] == "HELD" and Z["Z3"]["verdict"] == "HELD":
        Z["terminal"] = "COEFFICIENT_CELL_REACHABLE_ONLY_FROM_STRUCTURED_HISTORY_AT_REGISTERED_SCOPE"
    else:
        Z["terminal"] = "COEFFICIENT_LIFT_NOT_OBSERVED"
    out["Z_registration"] = Z

    # terminal
    P = out["predictions"]
    if not out["complete"]:
        out["terminal"] = "ADJUDICATION_INCOMPLETE__UNITS_MISSING"
    elif P["D1a"]["verdict"] == "FAILED" and P["D1a"]["n_true"] == 0:
        out["terminal"] = "DEVELOPMENTAL_MORPHOGENESIS_NOT_OBSERVED_AT_SCOPE"
    elif P["D1b"]["verdict"] != "HELD" and not (P["D2b"]["verdict"] == "HELD" and P["D2d"]["verdict"] == "HELD"):
        # a vacuous D2d ("no determined seed") is not support: it cannot rescue a failed D1b
        out["terminal"] = "PARENT_SUFFICIENT_OOPS"
    else:
        out["terminal"] = "DEVELOPMENTAL_MORPHOGENESIS_OBSERVED_AT_REGISTERED_SCOPE"
    out["residual_over_parents"] = {
        "D1b_load_bearing": P["D1b"]["verdict"],
        "D2b_class_conditioned_sign": P["D2b"]["verdict"],
        "D2d_class_conditioned_control": P["D2d"]["verdict"],
    }
    if validation_only:
        out["terminal"] = "VALIDATION_ONLY__NOT_AN_ADJUDICATION"
        out["note"] = ("scored on %d of 3 seeds; every '>= 2/3' verdict below is therefore "
                       "not the frozen verdict, only an instrument check" % len(seeds))
    p = os.path.join(RES, ("STAGE_B6_DEV_ADJ_VALIDATION_%s.json" % host) if validation_only
                     else ("STAGE_B6_DEV_ADJUDICATION_%s.json" % host))
    json.dump(out, open(p, "w"), indent=1, sort_keys=True, default=str)
    for k in sorted(Z):
        if isinstance(Z[k], dict) and "verdict" in Z[k]:
            print(f"{k:5s} {Z[k]['verdict']:38s} {Z[k]['per_seed']}")
    print("Z terminal:", Z["terminal"])
    for k in sorted(P):
        v = P[k]
        print(f"{k:5s} {v['verdict']:38s} {v.get('per_seed', v.get('per_pair'))}")
    print("terminal:", out["terminal"], "| missing:", len(missing))
    print("receipt", p)
    return out


if __name__ == "__main__":
    _seeds = tuple(int(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else (0, 1, 2)
    adjudicate(sys.argv[1] if len(sys.argv) > 1 else "billy", _seeds,
               validation_only=(len(sys.argv) > 3 and sys.argv[3] == "validate"))
