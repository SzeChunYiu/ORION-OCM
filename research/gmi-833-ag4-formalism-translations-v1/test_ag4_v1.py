# -*- coding: utf-8 -*-
"""AG4 tests.  Runs under `python3 -I -B` and `python3 -I -O -B`.

No bare `assert` is used: under -O an assert is removed and the test would pass
vacuously.  Every check calls `check()` explicitly.
"""

import importlib.util
import json
import os
import sys
from fractions import Fraction

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


M = load("ag4_route_a", "ag4_formalism_translations_v1.py")


def test_ranges_are_not_flattened():
    objs, _ = M.build(M.words(1))
    check("A is the deterministic range", len(objs["A"]) == 64)
    check("B carries the relational range", len(objs["B"]) == 1024)
    check("kernels use the frozen weight grid", len(objs["Ek"]) == 324)
    check("D is the submonoid range", len(objs["D"]) == 24)
    check("F carries an arity-two range", len(objs["F2"]) == 4096)
    check("a blocking relation is registered",
          any(any(len(o[1][l][s]) == 0 for l in M.LAB for s in M.S) for o in objs["B"]))
    check("a two-successor relation is registered",
          any(any(len(o[1][l][s]) == 2 for l in M.LAB for s in M.S) for o in objs["B"]))
    check("a non-point-mass kernel is registered",
          any(any(all(p != 1 for _t, p in o[1][l][s]) for l in M.LAB for s in M.S)
              for o in objs["Ek"]))


def test_behaviour_is_exact_and_rational():
    half = Fraction(1, 2)
    fair = ((0, half), (1, half))
    obj = ("Ek", ((fair, fair), (fair, fair)), (0, 1))
    k, rows = M.behaviour(obj, M.words(1))
    check("a kernel behaviour is probabilistic", k == "prob")
    check("the fair kernel splits exactly in half",
          rows[1] == ((0, str(half)), (1, str(half))))
    det = ("A", ((1, 0), (0, 1)), (0, 1))
    k2, rows2 = M.behaviour(det, M.words(1))
    check("a function behaviour is deterministic", k2 == "det")
    check("swap then observe", rows2[0] == 0 and rows2[1] == 1)


def test_class_lifting():
    check("det lifts to nondet",
          M.cast(("det", (0, 1)), "nondet") == (frozenset([0]), frozenset([1])))
    check("prob projects to its support",
          M.cast(("prob", (((0, "1/2"), (1, "1/2")),)), "nondet") == (frozenset([0, 1]),))
    check("the coarsest class of det and nondet is nondet",
          M.common_class("det", "nondet") == "nondet")
    check("the coarsest class of nondet and prob is nondet",
          M.common_class("nondet", "prob") == "nondet")


def test_obstruction_vocabulary_is_closed():
    for t in M.OBSTRUCTIONS:
        check("%s is a declared obstruction" % t, isinstance(t, str))
    blocking = ("B", ((frozenset(), frozenset()), (frozenset(), frozenset())), (0, 1))
    check("a blocking relation obstructs a total-function target",
          "BLOCKING_NOT_TOTAL" in M.obstruction_for("B", "A", blocking))
    multi = ("B", ((frozenset([0, 1]), frozenset([0])),
                   (frozenset([0]), frozenset([0]))), (0, 1))
    check("a two-successor relation obstructs a total-function target",
          "NONDETERMINISM_NOT_FUNCTIONAL" in M.obstruction_for("B", "A", multi))
    check("no obstruction outside the vocabulary is produced",
          all(t in M.OBSTRUCTIONS for t in M.obstruction_for("B", "A", multi)))


def test_receipts_agree():
    ra = os.path.join(HERE, "RESULT_V1.json")
    rb = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not (os.path.exists(ra) and os.path.exists(rb)):
        FAILURES.append("receipts missing -- run both routes first")
        return
    a, b = json.load(open(ra)), json.load(open(rb))
    check("route A is GREEN", a["status"] == "GREEN" and a["failed_gates"] == [])
    check("thirty directed translations", len(a["directed_translations"]) == 30)
    check("fifteen pairs", len(a["pairs"]) == 15)
    for k in ("registered_objects", "registered_objects_total",
              "directed_verdict_histogram", "pair_verdict_histogram",
              "mutually_total_pairs", "obstruction_histogram"):
        check("routes agree on %s" % k, a[k] == b[k])
    for k in sorted(b["directed_translations"]):
        for f in ("verdict", "source_objects", "translatable", "common_class"):
            check("routes agree on %s.%s" % (k, f),
                  a["directed_translations"][k][f] == b["directed_translations"][k][f])
        check("routes agree on %s obstruction" % k,
              sorted(a["directed_translations"][k].get("obstruction", [])) ==
              sorted(b["directed_translations"][k]["obstruction"]))
    check("not every pair is mutually total", len(a["mutually_total_pairs"]) < 15)
    check("some pair is partial in both directions",
          a["pair_verdict_histogram"].get("PARTIAL_BOTH_WAYS", 0) > 0)
    check("every partial translation names an obstruction",
          all(a["directed_translations"][k].get("obstruction")
              for k in a["directed_translations"]
              if a["directed_translations"][k]["verdict"] != "TOTAL"))
    check("translations out of D are marked non-canonical",
          all(a["directed_translations"][k]["canonical"] is False
              for k in a["directed_translations"] if k.startswith("D->")))
    check("the monoidal witness exists", a["monoidal_witness"] is not None)
    check("the kernel support fibre is larger than one",
          a["kernel_support_fibres"]["max_kernels_sharing_one_support"] > 1)
    check("every hostile was detected", all(h["detected"] for h in a["hostiles"]))
    check("every hostile moved its quantity",
          all(h["control_moved"] for h in a["hostiles"]))
    check("the flattening hostile makes every pair total",
          any(h["name"].startswith("H2") and
              h["finding"]["mutually_total_pairs"] == 15 for h in a["hostiles"]))
    check("the null never reproduced the pattern",
          a["null_random_totality_pattern"]["reproduced"] == 0)


def main():
    for fn in sorted(k for k in globals() if k.startswith("test_")):
        globals()[fn]()
    out = {"schema": "AG4_TEST_RESULT_V1", "optimized": not __debug__,
           "failures": FAILURES, "status": "GREEN" if not FAILURES else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
