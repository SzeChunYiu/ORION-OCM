# -*- coding: utf-8 -*-
"""Emergence tests.  Runs under `python3 -I -B` and `python3 -I -O -B`.

No bare `assert` is used: under -O an assert is removed and the test would pass
vacuously.  Every check calls `check()` explicitly.
"""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FAILURES = []


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(label, ok):
    if not ok:
        FAILURES.append(label)


M = load("emergence_route_a", "emergence_conditions_v1.py")


def test_machine_semantics():
    ops = M.OPS_B0
    idx = dict((o, i) for i, o in enumerate(ops))
    r = M.run((idx["OBS0"], idx["EMIT0"]), (2,), 8, ops)
    check("read then emit echoes the input", r["out"] == (2,))
    check("running off the end terminates", r["terminated"])
    r = M.run((idx["INC0"], idx["INC0"], idx["EMIT0"]), (), 8, ops)
    check("two increments from zero give two", r["out"] == (2,))
    r = M.run((idx["OBS0"],), (), 8, ops)
    check("an exhausted input stalls", r["stalled"] and not r["terminated"])
    r = M.run((idx["SKZ0"], idx["INC0"], idx["EMIT0"]), (), 8, ops)
    check("skip-if-zero skips the next instruction", r["out"] == (0,))
    r = M.run((idx["INC0"], idx["BNZ0"]), (), 6, ops)
    check("an unguarded backward jump exhausts the budget", not r["terminated"])
    r = M.run((idx["HLT"], idx["EMIT0"]), (), 8, ops)
    check("halt stops before the next instruction", r["out"] == () and r["terminated"])


def test_cost_is_dynamic_and_integral():
    ops = M.OPS_B0
    idx = dict((o, i) for i, o in enumerate(ops))
    price = M.prices(ops, 1)
    check("halt is free", price[idx["HLT"]] == 0)
    check("every price is an integer", all(isinstance(p, int) for p in price))
    price3 = M.prices(ops, 3)
    check("the observation price is the swept parameter", price3[idx["OBS0"]] == 3)
    r = M.run((idx["INC0"], idx["INC0"], idx["EMIT0"]), (), 8, ops)
    check("cost counts executed operations", M.cost_of(r["counts"], price) == 3)
    r2 = M.run((idx["SKZ0"], idx["INC0"], idx["EMIT0"]), (), 8, ops)
    check("a skipped operation is not charged", M.cost_of(r2["counts"], price) == 2)


def test_substrate_is_neutral():
    n = M.neutrality(M.OPS_B0)
    check("no operation names a behaviour", n["operation_name_collisions"] == [])
    check("the semantics mentions no behaviour", n["semantics_body_collisions"] == [])
    bad = M.neutrality(M.OPS_B0 + ("METAREASON",))
    check("the neutrality detector fires on a planted name", not bad["clean"])
    check("the neutrality detector is silent on the true substrate", n["clean"])


def test_predicates_are_functions_of_the_trace():
    for name in M.BEHAVIOURS:
        check("%s has a predicate" % name, name in M.PREDICATES)
    ops = M.OPS_B0
    idx = dict((o, i) for i, o in enumerate(ops))
    price = M.prices(ops, 1)
    recs = []
    for w in ((0,), (1,)):
        r = dict(M.run((idx["OBS0"], idx["EMIT0"]), w, 8, ops))
        r["word"] = w
        recs.append(r)
    check("echoing adapts", M.PREDICATES["ADAPTATION"](recs, price, ops))
    recs2 = []
    for w in ((0,), (1,)):
        r = dict(M.run((idx["EMIT0"],), w, 8, ops))
        r["word"] = w
        recs2.append(r)
    check("a blind emitter does not adapt",
          not M.PREDICATES["ADAPTATION"](recs2, price, ops))
    check("a deterministic run is not probabilistic",
          not M.PREDICATES["PROBABILISTIC_STATE"](recs2, price, ops))
    check("an unmodified program does not self-modify",
          not M.PREDICATES["SELF_MODIFICATION"](recs2, price, ops))


def test_verdict_algebra():
    sols = [((0,), ()), ((1,), ())]
    check("no holder gives NOT_EXPRESSIBLE",
          M.verdict_from(sols, [False, False], [1, 2])["verdict"] == "NOT_EXPRESSIBLE")
    check("no avoider gives FORCED_BY_REQUIREMENT",
          M.verdict_from(sols, [True, True], [1, 2])["verdict"] == "FORCED_BY_REQUIREMENT")
    e = M.verdict_from(sols, [True, False], [1, 4])
    check("a cheaper holder emerges by price", e["verdict"] == "EMERGES_BY_PRICE")
    check("the margin is exact", e["delta"] == 3)
    e = M.verdict_from(sols, [True, False], [4, 1])
    check("a dearer holder does not emerge", e["verdict"] == "DOES_NOT_EMERGE")
    check("a tie is not emergence",
          M.verdict_from(sols, [True, False], [2, 2])["verdict"] == "DOES_NOT_EMERGE")


def test_receipts_agree():
    ra, rb = os.path.join(HERE, "RESULT_V1.json"), os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not (os.path.exists(ra) and os.path.exists(rb)):
        FAILURES.append("receipts missing -- run both routes first")
        return
    a, b = json.load(open(ra)), json.load(open(rb))
    check("route A is GREEN", a["status"] == "GREEN" and a["failed_gates"] == [])
    check("all thirteen behaviours carry a verdict", len(a["behaviours"]) == 13)
    for k in sorted(b["behaviours"]):
        for f in ("verdict", "delta", "c_star_M", "c_star_notM", "solutions",
                  "blind_solutions"):
            check("routes agree on %s.%s" % (k, f),
                  a["behaviours"][k][f] == b["behaviours"][k][f])
    for k in sorted(b["revivals"]):
        for f in ("verdict", "delta", "c_star_M", "c_star_notM", "solutions"):
            check("routes agree on revival %s.%s" % (k, f),
                  a["revivals"][k][f] == b["revivals"][k][f])
    check("routes agree on the histogram",
          a["verdict_histogram"] == b["verdict_histogram"])
    check("routes agree that no behaviour emerges by price",
          a["emerges_by_price"] == b["emerges_by_price"])
    check("the two uncovered boundaries are decided",
          a["behaviours"]["METAREASONING"]["verdict"] != "NOT_EXPRESSIBLE" and
          a["behaviours"]["ENDOGENOUS_EXPERIMENT_CHOICE"]["verdict"] != "NOT_EXPRESSIBLE")
    check("a forced verdict has no predicate-free blind cover",
          all(a["behaviours"][k]["blind_and_predicate_free"] == 0
              for k in a["behaviours"]
              if a["behaviours"][k]["verdict"] == "FORCED_BY_REQUIREMENT"))

    # EM-5 rests on the four headline families surviving the entails-control, so the
    # control must be present for each of them and must not have been silently skipped.
    strip = a["stripped_requirements"]
    for k in ("ADAPTATION", "ROUTING", "METAREASONING",
              "ENDOGENOUS_EXPERIMENT_CHOICE"):
        check("%s is entered into the entails-control" % k, k in strip)
        if k not in strip:
            continue
        check("%s does not have its predicate entailed by its requirement" % k,
              strip[k]["requirement_entails_predicate"] is False)
        # Where the stripped requirement IS the frozen one, the control run must
        # reproduce the published, two-route-agreed figures exactly. This is what ties
        # the single-route control back to the cross-checked result.
        if strip[k]["stripped_is_frozen"]:
            check("control reproduces the published verdict for %s" % k,
                  strip[k]["stripped_verdict"] == a["behaviours"][k]["verdict"])
            check("control reproduces the published solution count for %s" % k,
                  strip[k]["stripped_solutions"] == a["behaviours"][k]["solutions"])
    if "ENDOGENOUS_EXPERIMENT_CHOICE" in strip:
        e = strip["ENDOGENOUS_EXPERIMENT_CHOICE"]
        check("the experiment-choice clause is genuinely stripped",
              e["stripped_is_frozen"] is False)
        check("the experiment-choice clause is inert on this universe",
              e["stripped_solutions"]
              == a["behaviours"]["ENDOGENOUS_EXPERIMENT_CHOICE"]["solutions"]
              and e["stripped_verdict"]
              == a["behaviours"]["ENDOGENOUS_EXPERIMENT_CHOICE"]["verdict"])
    check("exactly five frozen requirements entail their own predicate",
          sum(1 for v in strip.values()
              if v["requirement_entails_predicate"]) == 5)
    check("every predicate is extensional",
          all(e["extensionality"]["groups_with_split_verdict"] == 0
              for e in a["behaviours"].values()))
    check("the static prefilter changes no solution set",
          all(v["identical"] for v in a["prefilter_validation"].values()))
    check("every hostile was detected", all(h["detected"] for h in a["hostiles"]))
    check("every hostile moved its quantity",
          all(h["control_moved"] for h in a["hostiles"]))
    check("no inapplicable perturbation is shipped as a hostile",
          all(not p["control_moved"] for p in a["inapplicable_perturbations"]))
    check("the predicate null never reproduced the verdicts",
          a["null_random_predicates"]["reproduced"] == 0)
    check("every declared revival was run",
          all(k in a["revivals"] for k in a["not_expressible"] if k in ("PROBABILISTIC_STATE",
                                                                       "SELF_MODIFICATION")))
    check("EC-3 is declared unexercised when no behaviour emerges by price",
          a["ec3_exercised"] == bool(a["emerges_by_price"]))


def main():
    for fn in sorted(k for k in globals() if k.startswith("test_")):
        globals()[fn]()
    out = {"schema": "EMERGENCE_TEST_RESULT_V1", "optimized": not __debug__,
           "failures": FAILURES, "status": "GREEN" if not FAILURES else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
