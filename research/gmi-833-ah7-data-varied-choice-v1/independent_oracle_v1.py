# -*- coding: utf-8 -*-
"""AH7 route B -- an independent oracle for the data axis.

Route B imports nothing from route A.  Different mechanisms throughout:

  * each member of the space gets one full response table over the fourteen registered words,
    computed once; consistency is a restriction of that table, instead of re-running the
    system for every dataset;
  * the non-domination front is computed by a sort-and-sweep skyline rather than by all-pairs
    comparison;
  * the fixed-input fingerprint is built over a different serialization, so the hash value is
    not in the agreement set -- only the fact that it is constant across datasets.

    python3 -I -B  independent_oracle_v1.py
"""

import hashlib
import json
import os
import random
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
BITS = (0, 1)
WORDS = []
for _n in (1, 2, 3):
    for _w in product(BITS, repeat=_n):
        WORDS.append(_w)
WORD_POS = dict((w, k) for k, w in enumerate(WORDS))

TARGETS = ("IDENTITY", "NEGATION", "CONST0", "DELAY1", "PARITY")
COVERAGES = ("LEN1", "UPTO2", "LEN3", "ALL")


def target_row(name):
    out = []
    for w in WORDS:
        if name == "IDENTITY":
            out.append(tuple(w))
        elif name == "NEGATION":
            out.append(tuple(1 ^ x for x in w))
        elif name == "CONST0":
            out.append(tuple(0 for _ in w))
        elif name == "DELAY1":
            out.append((0,) + tuple(w[:-1]))
        else:
            p = 0
            acc = []
            for x in w:
                p ^= x
                acc.append(p)
            out.append(tuple(acc))
    return tuple(out)


def coverage_index(name):
    if name == "LEN1":
        return tuple(k for k, w in enumerate(WORDS) if len(w) == 1)
    if name == "UPTO2":
        return tuple(k for k, w in enumerate(WORDS) if len(w) <= 2)
    if name == "LEN3":
        return tuple(k for k, w in enumerate(WORDS) if len(w) == 3)
    return tuple(range(len(WORDS)))


def space():
    out = []
    oid = 0
    for f0 in BITS:
        for f1 in BITS:
            t = {(0, 0): (0, f0), (0, 1): (0, f1)}
            out.append(("S%03d" % oid, 0, t))
            oid += 1
    for ch in product(range(4), repeat=4):
        t = {}
        for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            t[(s, i)] = (ch[k] >> 1, ch[k] & 1)
        out.append(("M%03d" % oid, 1, t))
        oid += 1
    return out


def response_table(cells, table):
    rows = []
    for w in WORDS:
        s = 0
        acc = []
        for i in w:
            s, o = table[(s, i)]
            acc.append(o)
        rows.append(tuple(acc))
    return tuple(rows)


def price(cells, table):
    sites = ((0, 0), (0, 1)) if cells == 0 else ((0, 0), (0, 1), (1, 0), (1, 1))
    flips = sum(1 for (s, i) in sites if table[(s, i)][0] != s)
    units = sum(1 for (s, i) in sites if table[(s, i)][1] == 1)
    return (cells, len(sites), flips, units)


def skyline(items):
    """Sort-and-sweep non-domination front.  `items` is a list of `(oid, price)`."""
    if not items:
        return ()
    ordered = sorted(items, key=lambda kv: (sum(kv[1]), kv[1], kv[0]))
    front = []
    for oid, p in ordered:
        dominated = False
        for _foid, fp in front:
            if all(a <= b for a, b in zip(fp, p)) and any(a < b for a, b in zip(fp, p)):
                dominated = True
                break
        if not dominated:
            front.append((oid, p))
    # the sweep keeps only front members, but a later member can still dominate an earlier
    # one of equal sum; filter once more against the kept set
    final = []
    for oid, p in front:
        if not any(all(a <= b for a, b in zip(q, p)) and any(a < b for a, b in zip(q, p))
                   for o2, q in front if o2 != oid):
            final.append(oid)
    return tuple(sorted(final))


def chosen(tables, prices, word_idx, expected):
    ok = []
    for oid, row in tables.items():
        good = True
        for k, want in zip(word_idx, expected):
            if row[k] != want:
                good = False
                break
        if good:
            ok.append((oid, prices[oid]))
    return tuple(sorted(o for o, _p in ok)), skyline(ok)


def fingerprint(tables, prices):
    h = hashlib.sha256()
    for oid in sorted(tables):
        h.update(("%s=%s;%s|" % (oid, prices[oid], tables[oid])).encode())
    h.update(b"REQ:consistent+nondominated;HOR:3")
    return h.hexdigest()


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    sp = space()
    tables = dict((oid, response_table(c, t)) for oid, c, t in sp)
    prices = dict((oid, price(c, t)) for oid, c, t in sp)
    fp = fingerprint(tables, prices)

    per = {}
    for t in TARGETS:
        row = target_row(t)
        for c in COVERAGES:
            idx = coverage_index(c)
            expected = tuple(row[k] for k in idx)
            cons, front = chosen(tables, prices, idx, expected)
            per["%s|%s" % (t, c)] = {"observations": len(idx), "consistent": len(cons),
                                     "chosen": list(front), "chosen_size": len(front)}

    sets = dict((k, tuple(v["chosen"])) for k, v in per.items())
    distinct = len(set(sets.values()))
    moves = [t for t in TARGETS
             if len(set(sets["%s|%s" % (t, c)] for c in COVERAGES)) > 1]
    keys = sorted(sets)
    disjoint = 0
    same_target_disjoint = 0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = set(sets[keys[i]]), set(sets[keys[j]])
            if a and b and not (a & b):
                disjoint += 1
                if keys[i].split("|")[0] == keys[j].split("|")[0]:
                    same_target_disjoint += 1

    mono_checks = 0
    mono_failures = 0
    for t in TARGETS:
        row = target_row(t)
        idx = coverage_index("LEN1")
        base = set(chosen(tables, prices, idx, tuple(row[k] for k in idx))[0])
        for c in ("UPTO2", "ALL"):
            idx2 = coverage_index(c)
            ext = set(chosen(tables, prices, idx2, tuple(row[k] for k in idx2))[0])
            mono_checks += 1
            if not ext <= base:
                mono_failures += 1

    rnd = random.Random(8337703)
    realizable_pairs = 0
    realizable_same = 0
    answers = set()
    for _ in range(200):
        a = sp[rnd.randrange(len(sp))]
        b = sp[rnd.randrange(len(sp))]
        wa = rnd.sample(WORDS, 4)
        wb = rnd.sample(WORDS, 4)
        ia = tuple(WORD_POS[w] for w in wa)
        ib = tuple(WORD_POS[w] for w in wb)
        ra = tables[a[0]]
        rb = tables[b[0]]
        f1 = chosen(tables, prices, ia, tuple(ra[k] for k in ia))[1]
        f2 = chosen(tables, prices, ib, tuple(rb[k] for k in ib))[1]
        realizable_pairs += 1
        answers.add(f1)
        answers.add(f2)
        if f1 == f2:
            realizable_same += 1

    return {"schema": "GMI833AH7DataVariedChoiceOracleV1",
            "route": "B",
            "imports_route_a": False,
            "possibility_space_size": len(sp),
            "fixed_input_fingerprint_route_b": fp,
            "fixed_input_fingerprint_constant_across_datasets": True,
            "registered_datasets": len(per),
            "per_dataset": per,
            "distinct_chosen_sets": distinct,
            "targets_whose_chosen_set_moves_with_coverage_alone": moves,
            "disjoint_chosen_set_pairs": disjoint,
            "disjoint_pairs_sharing_one_target": same_target_disjoint,
            "monotone_narrowing_checks": mono_checks,
            "monotone_narrowing_failures": mono_failures,
            "chosen_set_is_a_singleton_for_every_registered_dataset":
                all(v["chosen_size"] == 1 for v in per.values()),
            "null_realizable_pairs": realizable_pairs,
            "null_realizable_pairs_with_identical_answer": realizable_same,
            "null_realizable_distinct_answers": len(answers)}


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"route": "B", "distinct_chosen_sets": r["distinct_chosen_sets"],
                          "moves": r["targets_whose_chosen_set_moves_with_coverage_alone"],
                          "disjoint": r["disjoint_chosen_set_pairs"],
                          "null_same": r["null_realizable_pairs_with_identical_answer"]}))
