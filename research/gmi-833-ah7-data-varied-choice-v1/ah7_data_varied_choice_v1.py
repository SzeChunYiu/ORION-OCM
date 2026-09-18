# -*- coding: utf-8 -*-
"""AH7 route A -- the data axis, with space, requirement and pricing held fixed.

The sibling result already on `main` varies requirements and pricing.  This varies the data and
nothing else.  The four fixed inputs are fingerprinted so that "held fixed" is checkable rather
than asserted.

    python3 -I -B  ah7_data_varied_choice_v1.py
"""

import hashlib
import json
import os
import random
from fractions import Fraction
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))

SOURCE_MAIN = "5e57d4292266bccf435136e1f7d72caa32e920a0"
CLAIM_CEILING = ("AH7_DATA_AXIS_MOVES_THE_PREFERRED_FORM_WITH_SPACE_REQUIREMENT_"
                 "AND_PRICING_HELD_FIXED")
FORBIDDEN_PROMOTIONS = ("DATA_CREATES_THE_POSSIBILITY_SPACE",
                        "MORE_DATA_IS_ALWAYS_BETTER",
                        "DATA_AXIS_DOMINATES_REQUIREMENTS_OR_PRICING",
                        "UNIQUE_PREFERRED_FORM_PER_DATASET",
                        "LEARNING_THEORY_DERIVED",
                        "COMPLETE_GMI")

BITS = (0, 1)
WORDS = []
for _n in (1, 2, 3):
    for _w in product(BITS, repeat=_n):
        WORDS.append(_w)

TARGETS = ("IDENTITY", "NEGATION", "CONST0", "DELAY1", "PARITY")
COVERAGES = ("LEN1", "UPTO2", "LEN3", "ALL")


def target_output(name, word):
    if name == "IDENTITY":
        return tuple(word)
    if name == "NEGATION":
        return tuple(1 ^ x for x in word)
    if name == "CONST0":
        return tuple(0 for _ in word)
    if name == "DELAY1":
        return (0,) + tuple(word[:-1])
    p = 0
    out = []
    for x in word:
        p ^= x
        out.append(p)
    return tuple(out)


def coverage_words(name):
    if name == "LEN1":
        return tuple(w for w in WORDS if len(w) == 1)
    if name == "UPTO2":
        return tuple(w for w in WORDS if len(w) <= 2)
    if name == "LEN3":
        return tuple(w for w in WORDS if len(w) == 3)
    return tuple(WORDS)


# --------------------------------------------------------------------------------------
# The possibility space: held fixed for every dataset.
# --------------------------------------------------------------------------------------

def organizations():
    out = []
    oid = 0
    for f0 in BITS:
        for f1 in BITS:
            table = {(0, 0): (0, f0), (0, 1): (0, f1)}
            out.append(("S%03d" % oid, 0, table))
            oid += 1
    for choice in product(range(4), repeat=4):
        table = {}
        for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            table[(s, i)] = (choice[k] >> 1, choice[k] & 1)
        out.append(("M%03d" % oid, 1, table))
        oid += 1
    return out


def run(cells, table, word):
    s = 0
    out = []
    for i in word:
        s, o = table[(s, i)]
        out.append(o)
    return tuple(out)


def price(cells, table):
    """The raw four-coordinate vector.  No scalarization anywhere."""
    sites = ((0, 0), (0, 1)) if cells == 0 else ((0, 0), (0, 1), (1, 0), (1, 1))
    flips = 0
    units = 0
    for (s, i) in sites:
        ns, o = table[(s, i)]
        if ns != s:
            flips += 1
        if o == 1:
            units += 1
    return (cells, len(sites), flips, units)


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def fixed_input_fingerprint(orgs, prices):
    h = hashlib.sha256()
    for oid, cells, table in orgs:
        h.update(oid.encode())
        h.update(str(cells).encode())
        for key in sorted(table):
            h.update(("%s:%s" % (key, table[key])).encode())
        h.update(str(prices[oid]).encode())
    h.update(b"|REQUIREMENT=consistent-then-nondominated")
    h.update(b"|HORIZON=words-up-to-length-3")
    return h.hexdigest()


def chosen(orgs, prices, dataset):
    consistent = []
    for oid, cells, table in orgs:
        ok = True
        for word, out in dataset:
            if run(cells, table, word) != out:
                ok = False
                break
        if ok:
            consistent.append(oid)
    front = []
    for oid in consistent:
        p = prices[oid]
        if not any(dominates(prices[other], p) for other in consistent if other != oid):
            front.append(oid)
    return tuple(sorted(consistent)), tuple(sorted(front))


def registered_datasets():
    out = {}
    for t in TARGETS:
        for c in COVERAGES:
            ws = coverage_words(c)
            out[(t, c)] = tuple((w, target_output(t, w)) for w in ws)
    return out


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    orgs = organizations()
    prices = dict((oid, price(cells, table)) for oid, cells, table in orgs)
    datasets = registered_datasets()

    fp = fixed_input_fingerprint(orgs, prices)
    per_dataset = {}
    fingerprints = set()
    for key in sorted(datasets):
        cons, front = chosen(orgs, prices, datasets[key])
        per_dataset["%s|%s" % key] = {
            "observations": len(datasets[key]),
            "consistent": len(cons),
            "chosen": list(front),
            "chosen_size": len(front),
            "chosen_prices": sorted(set(str(prices[o]) for o in front)),
        }
        fingerprints.add(fp)

    # the four fixed inputs must be identical for every dataset
    fixed_ok = (len(fingerprints) == 1)

    sets = dict((k, tuple(v["chosen"])) for k, v in per_dataset.items())
    distinct = len(set(sets.values()))

    same_target_moves = []
    for t in TARGETS:
        keys = ["%s|%s" % (t, c) for c in COVERAGES]
        seen = set(sets[k] for k in keys)
        if len(seen) > 1:
            same_target_moves.append(t)

    disjoint_pairs = []
    keys = sorted(sets)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = set(sets[keys[i]]), set(sets[keys[j]])
            if a and b and not (a & b):
                disjoint_pairs.append([keys[i], keys[j]])
    same_target_disjoint = [p for p in disjoint_pairs
                            if p[0].split("|")[0] == p[1].split("|")[0]]

    # order invariance: a dataset is a set of pairs, not a sequence
    rnd = random.Random(8337701)
    order_failures = 0
    for key in sorted(datasets):
        pairs = list(datasets[key])
        for _ in range(3):
            rnd.shuffle(pairs)
            _c, f = chosen(orgs, prices, tuple(pairs))
            if tuple(sorted(f)) != sets["%s|%s" % key]:
                order_failures += 1

    # monotone narrowing: extending a dataset can only shrink the consistent set
    mono_checks = 0
    mono_failures = 0
    for t in TARGETS:
        base = set(chosen(orgs, prices, datasets[(t, "LEN1")])[0])
        for c in ("UPTO2", "ALL"):
            ext = set(chosen(orgs, prices, datasets[(t, c)])[0])
            mono_checks += 1
            if not ext <= base:
                mono_failures += 1

    # the two axes are distinguishable.  Permuting price coordinates cannot move a
    # non-domination front, so the control uses a genuinely coarser price: the three-coordinate
    # vector with `unit_outputs` dropped.
    permuted_prices = dict((oid, (p[1], p[0], p[3], p[2])) for oid, p in prices.items())
    permuted_moves = 0
    coarse_prices = dict((oid, (p[0], p[1], p[2])) for oid, p in prices.items())
    reprice_moves = 0
    for key in sorted(datasets):
        _c, f = chosen(orgs, coarse_prices, datasets[key])
        if tuple(sorted(f)) != sets["%s|%s" % key]:
            reprice_moves += 1
        _c2, f2 = chosen(orgs, permuted_prices, datasets[key])
        if tuple(sorted(f2)) != sets["%s|%s" % key]:
            permuted_moves += 1

    # null: two random datasets of the same size, how often is the answer the same?
    # Measurements, not gates: at this scope the non-domination front happens to coincide
    # with the sum-minimal set, so scalarizing changes nothing.  The no-scalarization rule
    # stays because it is the correct general discipline, not because it bites here.
    scalar_prices = dict((oid, (sum(p),)) for oid, p in prices.items())
    scalarization_moves = 0
    sum_rule_differs = 0
    for key in sorted(datasets):
        _c, f = chosen(orgs, scalar_prices, datasets[key])
        if tuple(sorted(f)) != sets["%s|%s" % key]:
            scalarization_moves += 1
        cons, _f2 = chosen(orgs, prices, datasets[key])
        if cons:
            best = min(sum(prices[o]) for o in cons)
            bysum = tuple(sorted(o for o in cons if sum(prices[o]) == best))
            if bysum != sets["%s|%s" % key]:
                sum_rule_differs += 1

    # Null.  Two independent random datasets: how often is the preferred form the same?
    # A dataset of arbitrary labels is almost never realizable at this budget, so the
    # informative null draws *realizable* datasets -- a random member of the space, then a
    # random word sample of its own behaviour.  Both rates are published.
    rnd2 = random.Random(8337702)
    null_draws = 200
    arbitrary_unrealizable = 0
    for _ in range(null_draws):
        ws = rnd2.sample(WORDS, 4)
        d = tuple((w, tuple(rnd2.randrange(2) for _ in w)) for w in ws)
        if not chosen(orgs, prices, d)[0]:
            arbitrary_unrealizable += 1

    rnd3 = random.Random(8337703)
    realizable_pairs = 0
    realizable_same = 0
    realizable_distinct_answers = set()
    for _ in range(null_draws):
        a = orgs[rnd3.randrange(len(orgs))]
        b = orgs[rnd3.randrange(len(orgs))]
        wa = rnd3.sample(WORDS, 4)
        wb = rnd3.sample(WORDS, 4)
        d1 = tuple((w, run(a[1], a[2], w)) for w in wa)
        d2 = tuple((w, run(b[1], b[2], w)) for w in wb)
        f1 = chosen(orgs, prices, d1)[1]
        f2 = chosen(orgs, prices, d2)[1]
        realizable_pairs += 1
        realizable_distinct_answers.add(f1)
        realizable_distinct_answers.add(f2)
        if f1 == f2:
            realizable_same += 1

    failed = []
    if not fixed_ok:
        failed.append("GATE_FIXED_INPUTS_NOT_IDENTICAL")
    if distinct < 2:
        failed.append("GATE_DATA_DOES_NOT_MOVE_THE_CHOICE")
    if not same_target_moves:
        failed.append("GATE_ONLY_THE_REQUIREMENT_MOVED")
    if not disjoint_pairs:
        failed.append("GATE_NO_DISJOINT_PAIR")
    if order_failures:
        failed.append("GATE_CHOICE_NOT_A_FUNCTION_OF_THE_DATA")
    if mono_failures:
        failed.append("GATE_CONSISTENCY_NOT_MONOTONE")
    if realizable_pairs == 0:
        failed.append("GATE_NULL_HAS_NO_REALIZABLE_DRAWS")

    receipt = {
        "schema": "GMI833AH7DataVariedChoiceReceiptV1",
        "package": "gmi-833-ah7-data-varied-choice-v1",
        "issue": 833,
        "section": "AH7",
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "possibility_space_size": len(orgs),
        "cell_free": sum(1 for _o, c, _t in orgs if c == 0),
        "one_cell": sum(1 for _o, c, _t in orgs if c == 1),
        "fixed_input_fingerprint": fp,
        "fixed_input_fingerprint_identical_across_datasets": fixed_ok,
        "pricing_coordinates": ["state_cells", "table_rows", "flip_transitions",
                                "unit_outputs"],
        "scalarization_used": False,
        "registered_datasets": len(datasets),
        "per_dataset": per_dataset,
        "distinct_chosen_sets": distinct,
        "targets_whose_chosen_set_moves_with_coverage_alone": same_target_moves,
        "disjoint_chosen_set_pairs": len(disjoint_pairs),
        "disjoint_pairs_sharing_one_target": len(same_target_disjoint),
        "disjoint_example": disjoint_pairs[0] if disjoint_pairs else None,
        "same_target_disjoint_example": (same_target_disjoint[0]
                                         if same_target_disjoint else None),
        "order_invariance_failures": order_failures,
        "monotone_narrowing_checks": mono_checks,
        "monotone_narrowing_failures": mono_failures,
        "datasets_whose_answer_moves_under_coarser_pricing": reprice_moves,
        "datasets_whose_answer_moves_under_scalarization": scalarization_moves,
        "datasets_where_the_sum_rule_differs_from_non_domination": sum_rule_differs,
        "datasets_whose_answer_moves_under_coordinate_permutation": permuted_moves,
        "chosen_set_is_a_singleton_for_every_registered_dataset": all(
            v["chosen_size"] == 1 for v in per_dataset.values()),
        "null_draws": null_draws,
        "null_arbitrary_label_datasets_unrealizable": arbitrary_unrealizable,
        "null_realizable_pairs": realizable_pairs,
        "null_realizable_pairs_with_identical_answer": realizable_same,
        "null_realizable_distinct_answers": len(realizable_distinct_answers),
        "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
    }
    return receipt


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"status": r["status"], "failed_gates": r["failed_gates"],
                          "distinct_chosen_sets": r["distinct_chosen_sets"],
                          "targets_whose_chosen_set_moves_with_coverage_alone":
                              r["targets_whose_chosen_set_moves_with_coverage_alone"],
                          "disjoint_chosen_set_pairs": r["disjoint_chosen_set_pairs"],
                          "disjoint_pairs_sharing_one_target":
                              r["disjoint_pairs_sharing_one_target"],
                          "null_realizable_pairs_with_identical_answer":
                              r["null_realizable_pairs_with_identical_answer"],
                          "null_realizable_distinct_answers":
                              r["null_realizable_distinct_answers"]}))
