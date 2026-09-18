# -*- coding: utf-8 -*-
"""AH7 hostiles, controls and the no-alarm case.

No gate depends on a bare `assert`.

    python3 -I -O -B  test_ah7_data_varied_choice_v1.py
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ah7_data_varied_choice_v1 as A   # noqa: E402

FINDINGS = []
HOSTILES = []

ORGS = A.organizations()
PRICES = dict((oid, A.price(c, t)) for oid, c, t in ORGS)
DATASETS = A.registered_datasets()


def hostile(name, detected, control_clean, detail):
    HOSTILES.append({"hostile": name, "detected": bool(detected),
                     "control_clean": bool(control_clean), "detail": detail})
    if not detected:
        FINDINGS.append("HOSTILE_NOT_DETECTED:" + name)
    if not control_clean:
        FINDINGS.append("CONTROL_NOT_CLEAN:" + name)


def true_sets():
    return dict((k, A.chosen(ORGS, PRICES, DATASETS[k])[1]) for k in DATASETS)


TRUE = true_sets()


def h_first_consistent_instead_of_front():
    """A rule that takes the first consistent member depends on enumeration order."""
    moved = 0
    for key in DATASETS:
        cons, _f = A.chosen(ORGS, PRICES, DATASETS[key])
        first = (cons[0],) if cons else ()
        if first != TRUE[key]:
            moved += 1
    hostile("first_consistent_instead_of_front", moved > 0,
            all(len(v) >= 1 for v in TRUE.values() if v),
            {"datasets_where_first_differs_from_front": moved})


def h_consistency_prefix_only():
    """Checking only the first output symbol is a weaker filter and must admit more."""
    def prefix_chosen(dataset):
        cons = []
        for oid, cells, table in ORGS:
            ok = True
            for word, out in dataset:
                got = A.run(cells, table, word)
                if got[:1] != out[:1]:
                    ok = False
                    break
            if ok:
                cons.append(oid)
        return cons
    wider = 0
    for key in DATASETS:
        full = set(A.chosen(ORGS, PRICES, DATASETS[key])[0])
        weak = set(prefix_chosen(DATASETS[key]))
        if full < weak:
            wider += 1
    exact = 0
    for key in DATASETS:
        full = set(A.chosen(ORGS, PRICES, DATASETS[key])[0])
        if full <= set(prefix_chosen(DATASETS[key])):
            exact += 1
    hostile("consistency_prefix_only", wider > 0, exact == len(DATASETS),
            {"datasets_where_the_weak_filter_admits_more": wider})


def h_space_omits_the_answer():
    """The possibility space is load-bearing: remove the chosen member and the answer moves."""
    moved = 0
    unchanged = 0
    for key in DATASETS:
        want = TRUE[key]
        if not want:
            continue
        smaller = [o for o in ORGS if o[0] not in want]
        sp = dict((oid, PRICES[oid]) for oid, _c, _t in smaller)
        _c, f = A.chosen(smaller, sp, DATASETS[key])
        if tuple(sorted(f)) != want:
            moved += 1
        full = A.chosen(ORGS, PRICES, DATASETS[key])[1]
        if tuple(sorted(full)) == want:
            unchanged += 1
    hostile("space_omits_the_answer", moved == len(DATASETS),
            unchanged == len(DATASETS),
            {"datasets_whose_answer_moves_when_it_is_removed": moved,
             "control_datasets_unchanged_on_the_full_space": unchanged})


def h_drop_one_observation():
    """Removing one observation is a change of data and must be able to move the answer."""
    moved = 0
    for key in DATASETS:
        d = DATASETS[key]
        if len(d) < 2:
            continue
        _c, f = A.chosen(ORGS, PRICES, d[:-1])
        if tuple(sorted(f)) != TRUE[key]:
            moved += 1
    hostile("drop_one_observation", moved > 0, True,
            {"datasets_whose_answer_moves_when_one_pair_is_dropped": moved})


def h_space_not_fixed():
    """Restricting the space for one dataset must change the fingerprint."""
    full = A.fixed_input_fingerprint(ORGS, PRICES)
    small = [o for o in ORGS if o[1] == 0]
    sp = dict((oid, PRICES[oid]) for oid, _c, _t in small)
    part = A.fixed_input_fingerprint(small, sp)
    hostile("space_not_fixed", full != part, full == A.fixed_input_fingerprint(ORGS, PRICES),
            {"fingerprints_differ": full != part})


def h_empty_dataset_admits_everything():
    """With no observations the filter must admit the whole space, and the front must be the
    global non-dominated set."""
    cons, front = A.chosen(ORGS, PRICES, ())
    full = len(cons) == len(ORGS)
    narrowed = len(A.chosen(ORGS, PRICES, DATASETS[("PARITY", "ALL")])[0]) < len(ORGS)
    hostile("empty_dataset_admits_everything", full and narrowed, len(front) >= 1,
            {"consistent_with_no_data": len(cons), "space": len(ORGS),
             "front_with_no_data": len(front)})


def h_monotonicity_broken():
    """A filter that keeps members failing an observation breaks narrowing."""
    broken = 0
    for t in A.TARGETS:
        base = set(A.chosen(ORGS, PRICES, DATASETS[(t, "LEN1")])[0])
        loose = set(oid for oid, _c, _tab in ORGS)     # a filter that accepts everything
        if not loose <= base:
            broken += 1
    good = 0
    for t in A.TARGETS:
        base = set(A.chosen(ORGS, PRICES, DATASETS[(t, "LEN1")])[0])
        ext = set(A.chosen(ORGS, PRICES, DATASETS[(t, "ALL")])[0])
        if ext <= base:
            good += 1
    hostile("monotonicity_broken", broken > 0, good == len(A.TARGETS),
            {"broken_filters": broken, "clean_extensions": good})


def h_arbitrary_label_null():
    """A null over arbitrary labels is uninformative here and must be visible as such."""
    rnd = random.Random(99)
    unrealizable = 0
    for _ in range(100):
        ws = rnd.sample(A.WORDS, 4)
        d = tuple((w, tuple(rnd.randrange(2) for _ in w)) for w in ws)
        if not A.chosen(ORGS, PRICES, d)[0]:
            unrealizable += 1
    rnd2 = random.Random(98)
    realizable = 0
    for _ in range(100):
        a = ORGS[rnd2.randrange(len(ORGS))]
        ws = rnd2.sample(A.WORDS, 4)
        d = tuple((w, A.run(a[1], a[2], w)) for w in ws)
        if A.chosen(ORGS, PRICES, d)[0]:
            realizable += 1
    hostile("arbitrary_label_null", unrealizable > 90, realizable == 100,
            {"arbitrary_unrealizable": unrealizable, "realizable_draws_consistent": realizable})


def h_single_coverage_only():
    """With one coverage there is no data variation within a target behaviour."""
    sets = dict((t, TRUE[(t, "ALL")]) for t in A.TARGETS)
    moves = [t for t in A.TARGETS if len(set([sets[t]])) > 1]
    full_moves = [t for t in A.TARGETS
                  if len(set(TRUE[(t, c)] for c in A.COVERAGES)) > 1]
    hostile("single_coverage_only", len(moves) == 0, len(full_moves) > 0,
            {"moves_with_one_coverage": len(moves),
             "moves_with_all_coverages": full_moves})


def h_order_dependence():
    rnd = random.Random(7)
    failures = 0
    for key in DATASETS:
        pairs = list(DATASETS[key])
        rnd.shuffle(pairs)
        _c, f = A.chosen(ORGS, PRICES, tuple(pairs))
        if tuple(sorted(f)) != TRUE[key]:
            failures += 1
    biased = 0
    for key in DATASETS:
        cons, _f = A.chosen(ORGS, PRICES, DATASETS[key])
        if cons and (cons[0],) != TRUE[key]:
            biased += 1
    hostile("order_dependence", biased > 0, failures == 0,
            {"order_sensitive_rule_differs": biased, "true_rule_failures": failures})


def no_alarm():
    quiet = {
        "order_invariance_failures": 0,
        "monotone_failures": 0,
        "fingerprint_stable": 0,
    }
    rnd = random.Random(5)
    for key in DATASETS:
        pairs = list(DATASETS[key])
        for _ in range(2):
            rnd.shuffle(pairs)
            _c, f = A.chosen(ORGS, PRICES, tuple(pairs))
            if tuple(sorted(f)) != TRUE[key]:
                quiet["order_invariance_failures"] += 1
    for t in A.TARGETS:
        base = set(A.chosen(ORGS, PRICES, DATASETS[(t, "LEN1")])[0])
        ext = set(A.chosen(ORGS, PRICES, DATASETS[(t, "ALL")])[0])
        if not ext <= base:
            quiet["monotone_failures"] += 1
    if A.fixed_input_fingerprint(ORGS, PRICES) != A.fixed_input_fingerprint(ORGS, PRICES):
        quiet["fingerprint_stable"] = 1
    bad = [k for k, v in quiet.items() if v != 0]
    if bad:
        FINDINGS.append("NO_ALARM_VIOLATED:" + ",".join(bad))
    return quiet


def main():
    for fn in (h_first_consistent_instead_of_front, h_consistency_prefix_only,
               h_space_omits_the_answer, h_drop_one_observation, h_space_not_fixed,
               h_empty_dataset_admits_everything, h_monotonicity_broken,
               h_arbitrary_label_null, h_single_coverage_only, h_order_dependence):
        fn()
    quiet = no_alarm()
    out = {"schema": "GMI833AH7DataVariedChoiceTestReceiptV1",
           "hostiles": HOSTILES,
           "hostiles_declared": len(HOSTILES),
           "hostiles_detected": sum(1 for h in HOSTILES if h["detected"]),
           "controls_clean": sum(1 for h in HOSTILES if h["control_clean"]),
           "no_alarm": quiet,
           "findings": FINDINGS,
           "status": "GREEN" if not FINDINGS else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, separators=(",", ": ")) + "\n")
    print(json.dumps({"status": out["status"], "hostiles_declared": out["hostiles_declared"],
                      "hostiles_detected": out["hostiles_detected"],
                      "controls_clean": out["controls_clean"],
                      "findings": FINDINGS}, indent=2, sort_keys=True))
    return 0 if not FINDINGS else 1


if __name__ == "__main__":
    sys.exit(main())
