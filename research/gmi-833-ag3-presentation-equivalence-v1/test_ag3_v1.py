# -*- coding: utf-8 -*-
"""AG3 tests.  Runs under `python3 -I -B` and `python3 -I -O -B`.

No bare `assert` is used anywhere: under -O an assert is removed and the test
would pass vacuously.  Every check calls `fail()` explicitly.
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


M = load("ag3_route_a", "ag3_presentation_equivalence_v1.py")


def test_state_algebra():
    check("identity is neutral", M.compose(M.ident(3), (1, 2, 0)) == (1, 2, 0))
    # apply t1 first then t2:  succ then pred is the identity
    succ, pred = (1, 2, 0), (2, 0, 1)
    check("succ then pred is identity", M.compose(pred, succ) == M.ident(3))
    check("const0 absorbs", M.compose((0, 0, 0), succ) == (0, 0, 0))
    check("basis(3) has five distinct maps", len(M.basis(3)) == 5)
    check("basis(2) has three distinct maps", len(M.basis(2)) == 3)


def test_monoid_and_realizability():
    sig = ((1, 2, 0), (0, 1, 2))
    mon = M.monoid(sig, 3)
    check("succ generates a 3-element monoid", len(mon) == 3)
    real = M.realizable_by_len(sig, 3, 4)
    check("length 0 realizes only the identity", real[0] == frozenset({M.ident(3)}))
    check("pred needs two succ steps", ((2, 0, 1) in real[2]) and ((2, 0, 1) not in real[1]))


def test_levels_on_the_registered_witnesses():
    specs = M.witness_specs()
    order = {}
    for a in M.LEVEL_NAMES:
        for b in M.LEVEL_NAMES:
            order["%s<=%s" % (a, b)] = (a == b)
    # W-RENAME: definitional extension, so L2 but not L1
    p, q, _ = specs["W-RENAME"]
    v = M.level_vector(M.derive(p), M.derive(q))
    check("W-RENAME is not a renaming", v["L1"] is False)
    check("W-RENAME is term equivalent", v["L2"] is True)
    check("W-RENAME presents one object", v["L4"] is True)
    # W-STATESPACE: state-space change, so L3(1) but not L2
    p, q, _ = specs["W-STATESPACE"]
    v = M.level_vector(M.derive(p), M.derive(q))
    check("W-STATESPACE is not term equivalent", v["L2"] is False)
    check("W-STATESPACE compiles at overhead 1", v["L3(1)"] is True)
    # W-OVERHEAD: term equivalent but overhead 1 is not enough
    p, q, _ = specs["W-OVERHEAD"]
    v = M.level_vector(M.derive(p), M.derive(q))
    check("W-OVERHEAD is term equivalent", v["L2"] is True)
    check("W-OVERHEAD does not compile at overhead 1", v["L3(1)"] is False)
    check("W-OVERHEAD compiles at overhead 2", v["L3(2)"] is True)
    # PW-RELABEL: the parent relabeling kind is a pure renaming
    p, q, _ = specs["PW-RELABEL"]
    v = M.level_vector(M.derive(p), M.derive(q))
    check("PW-RELABEL is a renaming", v["L1"] is True)


def test_certificate_verifier_rejects_damage():
    specs = M.witness_specs()
    p, q, _ = specs["W-STATESPACE"]
    d1, d2 = M.derive(p), M.derive(q)
    cert = M.certificate(d1, d2, 1)
    check("a certificate exists", cert is not None)
    check("the true certificate verifies", M.verify_certificate(d1, d2, cert, 1))
    if cert is not None:
        bad = {"encoding": dict(cert["encoding"]),
               "compiled_lengths": dict(cert["compiled_lengths"])}
        bad["compiled_lengths"]["0"] = 99
        check("an over-long compile is rejected",
              not M.verify_certificate(d1, d2, bad, 1))
        bad2 = {"encoding": dict((k, 0) for k in cert["encoding"]),
                "compiled_lengths": dict(cert["compiled_lengths"])}
        check("a collapsing encoding is rejected",
              not M.verify_certificate(d1, d2, bad2, 1))
    check("no certificate is invented when none exists",
          M.certificate(d1, d2, 0) is None or
          M.verify_certificate(d1, d2, M.certificate(d1, d2, 0), 0))


def test_partition_algebra():
    p = (0, 0, 1, 1)
    q = (0, 1, 0, 1)
    check("meet refines both", M.refines(M.meet(p, q), p) and M.refines(M.meet(p, q), q))
    check("join coarsens both", M.refines(p, M.join(p, q)) and M.refines(q, M.join(p, q)))
    check("join of these two is total", len(set(M.join(p, q))) == 1)
    check("meet of these two is discrete", len(set(M.meet(p, q))) == 4)
    check("pair count", M.pair_count((0, 0, 0, 1)) == 3)


def test_receipts_agree():
    ra = os.path.join(HERE, "RESULT_V1.json")
    rb = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not (os.path.exists(ra) and os.path.exists(rb)):
        FAILURES.append("receipts missing -- run both routes first")
        return
    a = json.load(open(ra))
    b = json.load(open(rb))
    check("route A is GREEN", a["status"] == "GREEN")
    check("route A failed no gate", a["failed_gates"] == [])
    shared = ["universe_size", "comparable_pairs", "level_classes", "level_related_pairs",
              "k_star_l2_inside_l3", "l3_tolerance_edges", "generated_sublattice_size",
              "l3_raw_clause_cross_object_pairs", "level_equalities_on_this_universe"]
    for k in shared:
        check("routes agree on %s" % k, a[k] == b[k])
    check("routes agree on the incomparable pair",
          sorted(a["incomparable_pairs"]) == sorted(b["incomparable_pairs"]))
    check("the tolerance is exhibited", a["l3_nontransitive_triple"]["1"] is not None)
    check("every hostile was detected", all(h["detected"] for h in a["hostiles"]))
    check("every hostile moved its quantity", all(h["control_moved"] for h in a["hostiles"]))
    check("no inapplicable perturbation is counted as a hostile",
          all(not p["control_moved"] for p in a["inapplicable_perturbations"]))
    check("the null never reproduced the placement",
          a["null_random_level_assignment"]["reproduced"] == 0 and
          a["null_scrambled_interpretation"]["reproduced"] == 0)
    check("the raw section-2 clause is not semantics preserving",
          a["l3_raw_clause_cross_object_pairs"] > 0 and
          a["l3_raw_clause_counterexample"] is not None)
    check("L1 is strictly below L2", a["order"]["L1<=L2"] and
          a["level_related_pairs"]["L1"] < a["level_related_pairs"]["L2"])
    check("L2 and L3*(1) are incomparable", "L2~L3*(1)" in a["incomparable_pairs"])
    check("the lattice adds exactly one new element",
          a["generated_sublattice_new_elements"] == 1)
    for nm, v in a["anti_vacuity"].items():
        check("%s is not vacuous" % nm,
              v["strictly_above_identity"] and v["strictly_below_total"])


def main():
    for fn in sorted(k for k in globals() if k.startswith("test_")):
        globals()[fn]()
    out = {"schema": "AG3_TEST_RESULT_V1",
           "optimized": not __debug__,
           "failures": FAILURES,
           "status": "GREEN" if not FAILURES else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
