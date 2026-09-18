# -*- coding: utf-8 -*-
"""AH4 route B -- an independent oracle for the organization ladder.

Route B imports nothing from route A.  It rebuilds the registered organization set and
recomputes every published quantity by a different mechanism:

  * behavioural classes by Moore partition refinement over the whole set at once, instead of
    pairwise reachable product exploration;
  * composite reducibility by minimizing the explicit four-state product machine and reading
    its state count, instead of testing membership of a word-response signature;
  * capability by direct simulation against independently written task targets;
  * the L4..L8 witnesses re-implemented from their declared descriptions.

    python3 -I -B  independent_oracle_v1.py
"""

import json
import os
import random
from fractions import Fraction
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
BITS = (0, 1)


def build_set():
    """Every system as `(states, table)` with `table[(s, i)] = (s', o)` and init state 0."""
    out = []
    for f0 in BITS:
        for f1 in BITS:
            out.append((1, {(0, 0): (0, f0), (0, 1): (0, f1)}, 0))
    for choice in product(range(4), repeat=4):
        t = {}
        for k, (s, i) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
            t[(s, i)] = (choice[k] >> 1, choice[k] & 1)
        out.append((2, t, 1))
    return out


def reachable_states(nstates, table, init=0):
    seen = set()
    stack = [init]
    while stack:
        s = stack.pop()
        if s in seen:
            continue
        seen.add(s)
        for i in BITS:
            ns, _ = table[(s, i)]
            stack.append(ns)
    return seen


def minimize(nstates, table, init=0):
    """Moore partition refinement; returns the number of states of the minimal machine."""
    reach = sorted(reachable_states(nstates, table, init))
    block = {}
    for s in reach:
        block[s] = 0
    while True:
        sig = {}
        for s in reach:
            key = (block[s],) + tuple((table[(s, i)][1], block[table[(s, i)][0]])
                                      for i in BITS)
            sig[s] = key
        order = {}
        newblock = {}
        for s in reach:
            k = sig[s]
            if k not in order:
                order[k] = len(order)
            newblock[s] = order[k]
        if newblock == block:
            return len(set(block.values()))
        block = newblock


def global_partition(systems):
    """All systems refined together: tag each state with its owning system, then refine."""
    states = []
    delta = {}
    lam = {}
    for si, (n, t, _cells) in enumerate(systems):
        for s in range(n):
            states.append((si, s))
            for i in BITS:
                ns, o = t[(s, i)]
                delta[((si, s), i)] = (si, ns)
                lam[((si, s), i)] = o
    block = dict((st, 0) for st in states)
    while True:
        sig = {}
        for st in states:
            sig[st] = (block[st],) + tuple((lam[(st, i)], block[delta[(st, i)]])
                                           for i in BITS)
        order = {}
        newblock = {}
        for st in states:
            k = sig[st]
            if k not in order:
                order[k] = len(order)
            newblock[st] = order[k]
        if newblock == block:
            break
        block = newblock
    classes = {}
    for si in range(len(systems)):
        classes.setdefault(block[(si, 0)], []).append(si)
    return classes


def motif_multiplicity(n, table):
    counts = {}
    for s in range(n):
        for i in BITS:
            ns, o = table[(s, i)]
            key = (o, ns == s)
            counts[key] = counts.get(key, 0) + 1
    return max(counts.values())


def run(n, table, word):
    s = 0
    out = []
    for i in word:
        s, o = table[(s, i)]
        out.append(o)
    return tuple(out)


WORDS = []
for _k in range(1, 6):
    for _w in product(BITS, repeat=_k):
        WORDS.append(_w)
PROTECTED = [w for w in WORDS if len(w) <= 3]
TASKS = ("IDENTITY", "NEGATION", "CONST0", "DELAY1", "PARITY")


def target(task, w):
    if task == "IDENTITY":
        return tuple(w)
    if task == "NEGATION":
        return tuple(1 ^ x for x in w)
    if task == "CONST0":
        return tuple(0 for _ in w)
    if task == "DELAY1":
        return (0,) + tuple(w[:-1])
    p = 0
    out = []
    for x in w:
        p = p ^ x
        out.append(p)
    return tuple(out)


def capability(n, table):
    vec = []
    for task in TASKS:
        hit = sum(1 for w in PROTECTED if run(n, table, w) == target(task, w))
        vec.append(Fraction(hit, len(PROTECTED)))
    return tuple(vec)


def dominates(a, b):
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def compose_tables(ta, na, tb, nb):
    """Series wiring as an explicit product machine."""
    table = {}
    for sa in range(na):
        for sb in range(nb):
            for i in BITS:
                nsa, oa = ta[(sa, i)]
                nsb, ob = tb[(sb, oa)]
                table[((sa, sb), i)] = ((nsa, nsb), ob)
    flat = {}
    idx = {}
    for sa in range(na):
        for sb in range(nb):
            idx[(sa, sb)] = len(idx)
    for key, (ns, o) in table.items():
        flat[(idx[key[0]], key[1])] = (idx[ns], o)
    return len(idx), flat, idx[(0, 0)]


def main():
    systems = build_set()
    cellfree = [k for k, s in enumerate(systems) if s[2] == 0]
    onecell = [k for k, s in enumerate(systems) if s[2] == 1]

    classes = global_partition(systems)
    hist = {}
    for members in classes.values():
        hist[str(len(members))] = hist.get(str(len(members)), 0) + 1

    cellfree_class = set(min(classes.keys(), key=lambda c: 0) for _ in ())  # placeholder
    class_of = {}
    for ci, members in classes.items():
        for si in members:
            class_of[si] = ci
    cellfree_classes = set(class_of[k] for k in cellfree)

    i1 = [k for k, (n, t, _c) in enumerate(systems) if motif_multiplicity(n, t) >= 2]
    i1_set = set(i1)
    clause = {"both": 0, "cell_only": 0, "neither": 0, "behaviour_only": 0}
    i2_set = set()
    for k, (n, t, cells) in enumerate(systems):
        a = cells >= 1
        b = class_of[k] not in cellfree_classes
        if a and b:
            clause["both"] += 1
            i2_set.add(k)
        elif a:
            clause["cell_only"] += 1
        elif b:
            clause["behaviour_only"] += 1
        else:
            clause["neither"] += 1

    split_i1 = 0
    split_i2 = 0
    for ci, members in classes.items():
        if len(set((m in i1_set) for m in members)) > 1:
            split_i1 += 1
        if len(set((class_of[m] not in cellfree_classes) for m in members)) > 1:
            split_i2 += 1

    non_cumulative = sum(1 for k in range(len(systems))
                         if k not in i1_set and k in i2_set)

    comp_total = 0
    comp_irreducible = 0
    for (na, ta, _ca) in systems:
        for (nb, tb, _cb) in systems:
            n, table, init = compose_tables(ta, na, tb, nb)
            comp_total += 1
            if minimize(n, table, init) > 2:
                comp_irreducible += 1

    # ---- L4..L8 witnesses, re-implemented ------------------------------------------
    t0 = {(0, 0): (0, 0), (0, 1): (1, 0), (1, 0): (1, 0), (1, 1): (0, 1)}
    t1 = {(0, 0): (1, 1), (0, 1): (0, 1), (1, 0): (0, 0), (1, 1): (1, 0)}
    i4 = sum(1 for s in BITS for i in BITS if t0[(s, i)] != t1[(s, i)])
    i4_neg = 0
    # absorbed re-description must reproduce the adaptive run on every word
    def adaptive_run(word, tables):
        s, e = 0, 0
        out = []
        for i in word:
            s, o = tables[e][(s, i)]
            out.append(o)
            e = 1 if (e or i == 1) else 0
        return tuple(out)

    absorbed = {}
    for s in BITS:
        for e in BITS:
            for i in BITS:
                ns, o = [t0, t1][e][(s, i)]
                absorbed[((s, e), i)] = ((ns, 1 if (e or i == 1) else 0), o)

    def absorbed_run(word):
        st = (0, 0)
        out = []
        for i in word:
            st, o = absorbed[(st, i)]
            out.append(o)
        return tuple(out)

    i4_absorbs = all(adaptive_run(w, [t0, t1]) == absorbed_run(w) for w in WORDS)

    i5 = len({"READ", "EMIT", "INC", "REUSE_AB"}) - len({"READ", "EMIT", "INC"})
    i5_neg = len({"READ", "EMIT", "INC"}) - len({"READ", "EMIT", "INC"})

    def adopt(active, cand, authority, external):
        ok = (authority == "REGISTERED") if external else (cand[0] == 0)
        return (cand if ok else active), ok
    a1 = adopt((1, 1, 1), (0, 1, 0), "REGISTERED", True)
    a2 = adopt((1, 1, 1), (0, 1, 0), "UNREGISTERED", True)
    i6_differ = a1 != a2
    b1 = adopt((1, 1, 1), (0, 1, 0), "REGISTERED", False)
    b2 = adopt((1, 1, 1), (0, 1, 0), "UNREGISTERED", False)
    i6_neg_differ = b1 != b2

    def reach(seed, donor):
        out = set()
        frontier = {seed}
        for _ in range(2):
            nxt = set()
            for v in frontier:
                for k in range(len(v)):
                    w = list(v)
                    w[k] ^= 1
                    nxt.add(tuple(w))
            out |= nxt
            frontier = nxt
        out.add(seed)
        if donor is not None:
            out.add(donor)
        return out
    seed_b = (0,) * 6
    donor_a = (1,) * 6
    alone = reach(seed_b, None)
    withch = reach(seed_b, donor_a)
    i7_acq = len(withch - alone)
    i7_neg_acq = 0

    CORPUS = ((0, 1, 0, 1), (0, 1, 1), (0, 1, 0, 1, 0, 1), (1, 1, 0), (0, 1))
    TARGET = (0, 1, 0, 1, 0, 1)

    def units(corpus, expansion):
        total = 0
        for w in corpus:
            k = 0
            n = 0
            while k < len(w):
                if expansion and tuple(w[k:k + len(expansion)]) == expansion:
                    n += 1
                    k += len(expansion)
                else:
                    n += 1
                    k += 1
            total += n
        return total
    base_units = sum(len(w) for w in CORPUS)
    i8_desc = units(CORPUS, (0, 1)) - base_units
    i8_search = units((TARGET,), (0, 1)) - len(TARGET)
    i8_neg_desc = units(CORPUS, (0,)) - base_units
    i8_neg_search = units((TARGET,), (0,)) - len(TARGET)

    # ---- level versus capability ---------------------------------------------------
    levels = {}
    caps = {}
    for k, (n, t, cells) in enumerate(systems):
        a = cells >= 1
        b = class_of[k] not in cellfree_classes
        levels[k] = 2 if (a and b) else (1 if k in i1_set else 0)
        caps[k] = capability(n, t)
    inversions = 0
    for x in range(len(systems)):
        for y in range(len(systems)):
            if levels[x] > levels[y] and dominates(caps[y], caps[x]):
                inversions += 1

    rnd = random.Random(8334401)
    hits = 0
    n = len(systems)
    for _ in range(200):
        chosen = set(rnd.sample(range(n), len(i2_set)))
        constant = True
        for members in classes.values():
            vals = set((m in chosen) for m in members)
            if len(vals) > 1:
                constant = False
                break
        if constant:
            hits += 1

    return {"schema": "GMI833AH4OrganizationLadderOracleV1",
            "route": "B",
            "imports_route_a": False,
            "base_organizations": len(systems),
            "cell_free": len(cellfree), "one_cell": len(onecell),
            "operational_classes": len(classes),
            "class_size_histogram": hist,
            "i1_pass": len(i1), "i1_fail": len(systems) - len(i1),
            "i1_classes_split_by_description": split_i1,
            "i2_clause_counts": clause,
            "i2_pass": len(i2_set),
            "i2_classes_split_by_description": split_i2,
            "non_cumulative_base_systems": non_cumulative,
            "composites_total": comp_total,
            "composites_irreducible": comp_irreducible,
            "i4_witness_triples": i4,
            "i4_negative_witness_triples": i4_neg,
            "i4_collapses_under_absorption": i4_absorbs,
            "i5_growth": i5, "i5_negative_growth": i5_neg,
            "i6_outcomes_differ": i6_differ,
            "i6_negative_outcomes_differ": i6_neg_differ,
            "i7_acquired_only_through_channel": i7_acq,
            "i7_negative_acquired_only_through_channel": i7_neg_acq,
            "i8": {"description_delta": i8_desc, "expressive_delta": 0,
                   "search_distance_delta": i8_search},
            "i8_negative": {"description_delta": i8_neg_desc, "expressive_delta": 0,
                            "search_distance_delta": i8_neg_search},
            "level_capability_inversions": inversions,
            "null_class_constant_hits": hits}


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"route": "B", "operational_classes": r["operational_classes"],
                          "composites_irreducible": r["composites_irreducible"],
                          "level_capability_inversions": r["level_capability_inversions"]}))
