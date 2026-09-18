# -*- coding: utf-8 -*-
"""AG4 route A -- adjudicate all fifteen family pairs.

Ten finite specializations of the six families the AG4 section lists, each kept at
its OWN full expressive range.  Thirty directed translations, each either verified
total over the whole source range or bounded by an exact domain, a named
obstruction from a closed vocabulary, and a witness whose untranslatability is
proved by exhaustive search over the whole target range.

Definitions, ranges, the obstruction vocabulary, the gates and the falsifiers are
fixed in FREEZE_V1.md, committed before this file existed.  Rational weights are
exact `fractions.Fraction`; no float is constructed anywhere.

    python3 -I -B ag4_formalism_translations_v1.py
"""

import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

S = (0, 1)
LAB = (0, 1)
OBS = (0, 1)
W = 4
GRID = (Fraction(0), Fraction(1, 2), Fraction(1))

FAMILIES = ("A", "B", "C", "D", "E", "F")
SPECIALIZATIONS = {"A": ("A",), "B": ("B",), "C": ("Cd", "Cn", "Cp"),
                   "D": ("D",), "E": ("Er", "Ek"), "F": ("F1", "F2")}
KIND = {"A": "det", "B": "nondet", "Cd": "det", "Cn": "nondet", "Cp": "prob",
        "D": "det", "Er": "nondet", "Ek": "prob", "F1": "det", "F2": "det"}
DETERMINISTIC_TOTAL = ("A", "Cd", "D", "F1", "F2")

OBSTRUCTIONS = ("NONDETERMINISM_NOT_FUNCTIONAL", "BLOCKING_NOT_TOTAL",
                "WEIGHTS_NOT_RECOVERABLE", "NON_DIRAC_KERNEL",
                "NO_CHOSEN_GENERATING_FAMILY",
                "MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION",
                "ARITY_NOT_REPRESENTABLE", "FUNCTOR_NOT_IN_RANGE")


def words(maxlen):
    out = [()]
    cur = [()]
    for _ in range(maxlen):
        cur = [w + (l,) for w in cur for l in LAB]
        out.extend(cur)
    return tuple(out)


WORDS = words(W)
WORDS_SHORT = tuple(w for w in WORDS if len(w) <= W - 1)


# ------------------------------------------------------------ the machine view
# Every specialization is presented as (kind, states, start, step, out).
# `step(s, l)` returns a state for det, a frozenset for nondet, and a tuple of
# (state, Fraction) pairs for prob.

def dists():
    out = []
    for p in GRID:
        q = Fraction(1) - p
        if q in GRID:
            out.append(((0, p), (1, q)))
    return tuple(sorted(set(out)))


DISTS = dists()


def gen_A():
    for f0 in itertools.product(S, repeat=len(S)):
        for f1 in itertools.product(S, repeat=len(S)):
            for out in itertools.product(OBS, repeat=len(S)):
                yield ("A", (f0, f1), out)


def gen_B(tag="B"):
    masks = tuple(frozenset(t) for r in range(len(S) + 1)
                  for t in itertools.combinations(S, r))
    for r0 in itertools.product(masks, repeat=len(S)):
        for r1 in itertools.product(masks, repeat=len(S)):
            for out in itertools.product(OBS, repeat=len(S)):
                yield (tag, (r0, r1), out)


def gen_Cd():
    for o in gen_A():
        yield ("Cd",) + o[1:]


def gen_Cn():
    for o in gen_B("Cn"):
        yield o


def gen_K(tag="Ek"):
    for k0 in itertools.product(DISTS, repeat=len(S)):
        for k1 in itertools.product(DISTS, repeat=len(S)):
            for out in itertools.product(OBS, repeat=len(S)):
                yield (tag, (k0, k1), out)


def compose(f, g):
    return tuple(f[g[s]] for s in S)


ALL_MAPS = tuple(itertools.product(S, repeat=len(S)))
IDENT = tuple(S)


def submonoids():
    found = set()
    for r in range(1, len(ALL_MAPS) + 1):
        for sub in itertools.combinations(ALL_MAPS, r):
            st = set(sub)
            if IDENT not in st:
                continue
            if all(compose(a, b) in st for a in st for b in st):
                found.add(frozenset(st))
    return tuple(sorted(found, key=lambda m: (len(m), sorted(m))))


SUBMONOIDS = submonoids()


def gen_D():
    for m in SUBMONOIDS:
        for out in itertools.product(OBS, repeat=len(S)):
            yield ("D", tuple(sorted(m)), out)


def gen_F1():
    for o in gen_A():
        yield ("F1",) + o[1:]


PAIRS2 = tuple(itertools.product(S, S))


def gen_F2():
    """An arity-2 typed interface: the tensor of two arity-1 processes, observed
    through the parity of the two component observations."""
    base = tuple(gen_A())
    for p in base:
        for q in base:
            yield ("F2", (p[1], q[1]), (p[2], q[2]))


GENERATORS = {"A": gen_A, "B": gen_B, "Cd": gen_Cd, "Cn": gen_Cn, "Cp":
              (lambda: gen_K("Cp")), "D": gen_D, "Er": (lambda: gen_B("Er")),
              "Ek": (lambda: gen_K("Ek")), "F1": gen_F1, "F2": gen_F2}


def machine(obj):
    tag = obj[0]
    if tag in ("A", "Cd", "F1"):
        f, out = obj[1], obj[2]
        return ("det", S, 0, (lambda s, l: f[l][s]), (lambda s: out[s]))
    if tag in ("B", "Cn", "Er"):
        r, out = obj[1], obj[2]
        return ("nondet", S, 0, (lambda s, l: r[l][s]), (lambda s: out[s]))
    if tag in ("Cp", "Ek"):
        k, out = obj[1], obj[2]
        return ("prob", S, 0, (lambda s, l: k[l][s]), (lambda s: out[s]))
    if tag == "F2":
        (fp, fq), (op, oq) = obj[1], obj[2]
        return ("det", PAIRS2, (0, 0),
                (lambda s, l: (fp[l][s[0]], fq[l][s[1]])),
                (lambda s: (op[s[0]] + oq[s[1]]) % 2))
    raise AssertionError("no machine view for " + tag)


def behaviour(obj, wordset=WORDS):
    kind, _st, start, step, out = machine(obj)
    res = []
    if kind == "det":
        for w in wordset:
            s = start
            for l in w:
                s = step(s, l)
            res.append(out(s))
        return ("det", tuple(res))
    if kind == "nondet":
        for w in wordset:
            cur = frozenset([start])
            for l in w:
                nxt = set()
                for s in cur:
                    nxt |= set(step(s, l))
                cur = frozenset(nxt)
            res.append(frozenset(out(s) for s in cur))
        return ("nondet", tuple(res))
    for w in wordset:
        cur = {start: Fraction(1)}
        for l in w:
            nxt = {}
            for s, p in cur.items():
                for t, q in step(s, l):
                    if q:
                        nxt[t] = nxt.get(t, Fraction(0)) + p * q
            cur = nxt
        agg = {}
        for s, p in cur.items():
            agg[out(s)] = agg.get(out(s), Fraction(0)) + p
        res.append(tuple(sorted((o, str(p)) for o, p in agg.items() if p)))
    return ("prob", tuple(res))


def common_class(k1, k2):
    if k1 == k2:
        return k1
    if "det" in (k1, k2) and "nondet" in (k1, k2):
        return "nondet"
    if "det" in (k1, k2) and "prob" in (k1, k2):
        return "prob"
    return "nondet"                       # a probabilistic behaviour projects to its support


def cast(beh, target):
    k, rows = beh
    if k == target:
        return rows
    if k == "det" and target == "nondet":
        return tuple(frozenset([v]) for v in rows)
    if k == "det" and target == "prob":
        return tuple(((v, str(Fraction(1))),) for v in rows)
    if k == "prob" and target == "nondet":
        return tuple(frozenset(o for o, _p in row) for row in rows)
    raise AssertionError("no cast from %s to %s" % (k, target))


# -------------------------------------------------- the D family's behaviour set

def d_behaviours(obj, wordset=WORDS):
    """A monoid carries no label indexing, so its observable content is the SET of
    behaviours realizable by some choice of a labelled generating family."""
    mon, out = obj[1], obj[2]
    res = set()
    for f0 in mon:
        for f1 in mon:
            res.add(behaviour(("A", (f0, f1), out), wordset))
    return frozenset(res)


def behaviours_of(obj, wordset=WORDS):
    if obj[0] == "D":
        return d_behaviours(obj, wordset)
    return frozenset([behaviour(obj, wordset)])


# ----------------------------------------------------------------- the obstruction

def structural_flags(obj):
    tag = obj[0]
    f = set()
    if tag in ("B", "Cn", "Er"):
        for l in LAB:
            for s in S:
                n = len(obj[1][l][s])
                if n >= 2:
                    f.add("MULTI_SUCCESSOR")
                if n == 0:
                    f.add("BLOCKING")
    if tag in ("Cp", "Ek"):
        for l in LAB:
            for s in S:
                if not any(p == 1 for _t, p in obj[1][l][s]):
                    f.add("NON_DIRAC")
    if tag == "D":
        f.add("NO_LABELLING")
    if tag == "F2":
        f.add("ARITY_TWO")
    return f


def obstruction_for(src_tag, dst_fam, witness):
    flags = structural_flags(witness)
    dst_specs = SPECIALIZATIONS[dst_fam]
    dst_all_det = all(t in DETERMINISTIC_TOTAL for t in dst_specs)
    out = []
    if "MULTI_SUCCESSOR" in flags and dst_all_det:
        out.append("NONDETERMINISM_NOT_FUNCTIONAL")
    if "BLOCKING" in flags and dst_all_det:
        out.append("BLOCKING_NOT_TOTAL")
    if "NON_DIRAC" in flags:
        out.append("NON_DIRAC_KERNEL" if dst_all_det else "WEIGHTS_NOT_RECOVERABLE")
    if "NO_LABELLING" in flags:
        out.append("NO_CHOSEN_GENERATING_FAMILY")
    if "ARITY_TWO" in flags:
        out.append("ARITY_NOT_REPRESENTABLE")
        if dst_fam == "D":
            out.append("MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION")
    if not out and src_tag in ("Cd", "Cn", "Cp"):
        out.append("FUNCTOR_NOT_IN_RANGE")
    return sorted(set(out))


# --------------------------------------------------------------- the adjudication

def build(wordset=WORDS):
    objs, behs = {}, {}
    for tag in sorted(GENERATORS):
        items = tuple(GENERATORS[tag]())
        objs[tag] = items
        behs[tag] = [behaviours_of(o, wordset) for o in items]
    return objs, behs


def family_index(fam, objs, behs, target_class):
    """Every behaviour any member of the family can present, cast to one class."""
    idx = set()
    for tag in SPECIALIZATIONS[fam]:
        for bs in behs[tag]:
            for b in bs:
                try:
                    idx.add(cast(b, target_class))
                except AssertionError:
                    pass
    return idx


def family_kind(fam):
    ks = set(KIND[t] for t in SPECIALIZATIONS[fam])
    k = "det"
    for other in sorted(ks):
        k = common_class(k, other)
    return k


def adjudicate(objs, behs, wordset=WORDS):
    table = {}
    for src, dst in itertools.permutations(FAMILIES, 2):
        cls = common_class(family_kind(src), family_kind(dst))
        idx = family_index(dst, objs, behs, cls)
        total, dom = 0, 0
        per_token = {}
        witness, wtag = None, None
        for tag in SPECIALIZATIONS[src]:
            for i, o in enumerate(objs[tag]):
                total += 1
                ok = False
                for b in behs[tag][i]:
                    try:
                        if cast(b, cls) in idx:
                            ok = True
                            break
                    except AssertionError:
                        pass
                if ok:
                    dom += 1
                    continue
                if witness is None:
                    witness, wtag = o, tag
                for t in obstruction_for(tag, dst, o):
                    if t not in per_token:
                        per_token[t] = (tag, o)
        if dom == total:
            v = "TOTAL"
        elif dom == 0:
            v = "EMPTY"
        else:
            v = "PARTIAL"
        entry = {"source_objects": total, "translatable": dom, "verdict": v,
                 "common_class": cls,
                 "canonical": src != "D",
                 "non_canonical_because": None if src != "D"
                 else "NO_CHOSEN_GENERATING_FAMILY"}
        if witness is not None:
            entry["witness_specialization"] = wtag
            entry["witness"] = repr(witness)
            entry["obstruction"] = sorted(per_token)
            entry["witness_per_obstruction"] = dict(
                (t, {"specialization": per_token[t][0], "object": repr(per_token[t][1])})
                for t in sorted(per_token))
            entry["witness_checked_against_target_objects"] = sum(
                len(objs[t]) for t in SPECIALIZATIONS[dst])
        table["%s->%s" % (src, dst)] = entry
    return table


def canonicity(objs, behs):
    """A translation out of D is a choice, not a map.  Publish the exact fibres."""
    fib = {}
    for i, o in enumerate(objs["D"]):
        fib[repr(o)] = len(behs["D"][i])
    sizes = sorted(set(fib.values()))
    return {"D_objects": len(objs["D"]),
            "distinct_behaviour_counts_per_D_object": sizes,
            "min_fibre": min(fib.values()), "max_fibre": max(fib.values()),
            "non_canonical_because": "NO_CHOSEN_GENERATING_FAMILY"}


def kernel_fibres(objs, behs):
    """How many kernels share one relational support behaviour: the exact residual
    the WEIGHTS_NOT_RECOVERABLE obstruction names."""
    groups = {}
    for i, o in enumerate(objs["Ek"]):
        b = list(behs["Ek"][i])[0]
        groups.setdefault(cast(b, "nondet"), []).append(o)
    sizes = sorted(len(v) for v in groups.values())
    return {"kernels": len(objs["Ek"]), "distinct_support_behaviours": len(groups),
            "max_kernels_sharing_one_support": sizes[-1],
            "min_kernels_sharing_one_support": sizes[0]}


def monoidal_witness(objs):
    """Two arity-2 interfaces whose SERIAL content -- the behaviour of the wire the
    serial composites act on -- is identical while the tensor's joint behaviour is
    not.  Serial composition therefore does not determine the tensor."""
    byser = {}
    for o in objs["F2"]:
        (fp, _fq), (op, _oq) = o[1], o[2]
        key = behaviour(("A", fp, op))
        byser.setdefault(key, []).append(o)
    groups_examined = 0
    for key in sorted(byser, key=repr):
        group = byser[key]
        groups_examined += 1
        seen = {}
        for o in group:
            b = behaviour(o)
            if b in seen:
                continue
            seen[b] = o
            if len(seen) >= 2:
                vals = sorted(seen.values(), key=repr)
                return {"identical_serial_behaviour": repr(key),
                        "a": repr(vals[0]), "b": repr(vals[1]),
                        "joint_behaviours_differ": True,
                        "serial_classes_examined": groups_examined,
                        "members_of_this_serial_class": len(group),
                        "obstruction": "MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION"}
    return None


def pair_summary(table):
    pairs = {}
    for x, y in itertools.combinations(FAMILIES, 2):
        a, b = table["%s->%s" % (x, y)], table["%s->%s" % (y, x)]
        if a["verdict"] == "TOTAL" and b["verdict"] == "TOTAL":
            v = "MUTUALLY_TOTAL"
        elif a["verdict"] == "TOTAL" or b["verdict"] == "TOTAL":
            v = "TOTAL_ONE_WAY"
        else:
            v = "PARTIAL_BOTH_WAYS"
        pairs["%s-%s" % (x, y)] = {"verdict": v,
                                   "%s->%s" % (x, y): a["verdict"],
                                   "%s->%s" % (y, x): b["verdict"]}
    return pairs


# --------------------------------------------------------------- the detectors

def verify_witnesses(table, objs, behs):
    """Re-prove every published witness: no member of the target family, over its
    whole registered range, has the witness's behaviour."""
    bad = []
    for key in sorted(table):
        e = table[key]
        if "witness" not in e:
            continue
        src, dst = key.split("->")
        cls = e["common_class"]
        idx = family_index(dst, objs, behs, cls)
        tag = e["witness_specialization"]
        i = [repr(o) for o in objs[tag]].index(e["witness"])
        hit = False
        for b in behs[tag][i]:
            try:
                if cast(b, cls) in idx:
                    hit = True
            except AssertionError:
                pass
        if hit:
            bad.append(key)
    return bad


def vocabulary_check(table):
    bad = []
    for key in sorted(table):
        for t in table[key].get("obstruction", ()):
            if t not in OBSTRUCTIONS:
                bad.append([key, t])
    return bad


def class_rule_check(table):
    bad = []
    for key in sorted(table):
        src, dst = key.split("->")
        if table[key]["common_class"] != common_class(family_kind(src), family_kind(dst)):
            bad.append(key)
    return bad


def range_check(table, objs):
    bad = []
    for key in sorted(table):
        src = key.split("->")[0]
        want = sum(len(objs[t]) for t in SPECIALIZATIONS[src])
        if table[key]["source_objects"] != want:
            bad.append(key)
    return bad


def totality_pattern(table):
    return tuple(table[k]["verdict"] for k in sorted(table))


# ----------------------------------------------------------------- the hostiles

def run_hostiles(objs, behs, table, objs_s, behs_s):
    out, inapplicable = [], []
    true_total = sum(1 for k in table if table[k]["verdict"] == "TOTAL")

    # H1 -- compare in the source's own class instead of the coarsest common class
    h1 = {}
    for src, dst in itertools.permutations(FAMILIES, 2):
        cls = family_kind(src)
        idx = family_index(dst, objs, behs, cls)
        tot = dom = 0
        for tag in SPECIALIZATIONS[src]:
            for i in range(len(objs[tag])):
                tot += 1
                ok = False
                for b in behs[tag][i]:
                    try:
                        if cast(b, cls) in idx:
                            ok = True
                            break
                    except AssertionError:
                        pass
                if ok:
                    dom += 1
        h1["%s->%s" % (src, dst)] = {"common_class": cls,
                                     "verdict": "TOTAL" if dom == tot else
                                     ("EMPTY" if dom == 0 else "PARTIAL")}
    out.append({"name": "H1_behaviour_compared_in_the_source_class",
                "control_before": true_total,
                "control_after": sum(1 for k in h1 if h1[k]["verdict"] == "TOTAL"),
                "control_moved": totality_pattern(h1) != totality_pattern(table),
                "detector": "behaviour_compared_in_the_coarsest_common_class",
                "detected": bool(class_rule_check(h1)),
                "finding": len(class_rule_check(h1))})

    # H2 -- every family cut down to one common deterministic core.  This is the
    # trap gate 4 of the freeze exists to catch: a family set whose members are
    # mutually and totally interchangeable is not the six families AG4 lists.
    fobjs, fbehs = {}, {}
    for tag in sorted(objs):
        keep = [i for i, o in enumerate(objs[tag]) if _is_det_core(o)]
        fobjs[tag] = tuple(objs[tag][i] for i in keep)
        fbehs[tag] = [behs[tag][i] for i in keep]
    flat = adjudicate(fobjs, fbehs)
    flat_pairs = pair_summary(flat)
    flat_mt = sum(1 for k in flat_pairs if flat_pairs[k]["verdict"] == "MUTUALLY_TOTAL")
    out.append({"name": "H2_universe_flattened_to_one_common_deterministic_core",
                "control_before": sum(len(v) for v in objs.values()),
                "control_after": sum(len(v) for v in fobjs.values()),
                "control_moved": sum(len(v) for v in fobjs.values()) <
                                 sum(len(v) for v in objs.values()),
                "detector": "not_all_pairs_are_total",
                "detected": flat_mt == len(flat_pairs),
                "finding": {"mutually_total_pairs": flat_mt,
                            "total_directed": sum(1 for k in flat
                                                  if flat[k]["verdict"] == "TOTAL")}})

    # H3 -- a source range trimmed to its first specialization
    trimmed = {}
    for src, dst in itertools.permutations(FAMILIES, 2):
        cls = common_class(family_kind(src), family_kind(dst))
        idx = family_index(dst, objs, behs, cls)
        tag = SPECIALIZATIONS[src][0]
        tot = dom = 0
        for i in range(len(objs[tag])):
            tot += 1
            ok = any(cast(b, cls) in idx for b in behs[tag][i]
                     if _castable(b, cls))
            if ok:
                dom += 1
        trimmed["%s->%s" % (src, dst)] = {
            "source_objects": tot,
            "verdict": "TOTAL" if dom == tot else ("EMPTY" if dom == 0 else "PARTIAL")}
    out.append({"name": "H3_source_range_trimmed_to_one_specialization",
                "control_before": sum(table[k]["source_objects"] for k in table),
                "control_after": sum(trimmed[k]["source_objects"] for k in trimmed),
                "control_moved": sum(trimmed[k]["source_objects"] for k in trimmed) <
                                 sum(table[k]["source_objects"] for k in table),
                "detector": "source_range_recomputed_from_the_generators",
                "detected": bool(range_check(trimmed, objs)),
                "finding": len(range_check(trimmed, objs))})

    # H4 -- a witness that in fact translates
    forged = {}
    planted = 0
    for k in sorted(table):
        e = dict(table[k])
        if "witness" not in e:
            forged[k] = e
            continue
        src = k.split("->")[0]
        tag = SPECIALIZATIONS[src][0]
        e["witness"] = repr(objs[tag][0])
        e["witness_specialization"] = tag
        planted += 1
        forged[k] = e
    bad = verify_witnesses(forged, objs, behs)
    out.append({"name": "H4_witness_that_actually_translates",
                "control_before": 0, "control_after": planted,
                "control_moved": planted > 0,
                "detector": "every_witness_is_untranslatable",
                "detected": bool(bad), "finding": len(bad)})

    # H5 -- an obstruction outside the frozen vocabulary
    bogus = dict((k, dict(table[k])) for k in table)
    key0 = sorted(k for k in table if "obstruction" in table[k])[0]
    bogus[key0] = dict(bogus[key0])
    bogus[key0]["obstruction"] = ["REPRESENTATION_MISMATCH"]
    out.append({"name": "H5_obstruction_outside_the_frozen_vocabulary",
                "control_before": len(vocabulary_check(table)),
                "control_after": len(vocabulary_check(bogus)),
                "control_moved": len(vocabulary_check(bogus)) > len(vocabulary_check(table)),
                "detector": "obstruction_vocabulary_is_closed",
                "detected": bool(vocabulary_check(bogus)),
                "finding": vocabulary_check(bogus)})

    # H6 -- the observation window cut to one letter
    objs1, behs1 = build(words(1))
    short = adjudicate(objs1, behs1, words(1))
    out.append({"name": "H6_observation_window_cut_to_one_letter",
                "control_before": true_total,
                "control_after": sum(1 for k in short if short[k]["verdict"] == "TOTAL"),
                "control_moved": totality_pattern(short) != totality_pattern(table),
                "detector": "observation_window_is_sufficient",
                "detected": totality_pattern(short) != totality_pattern(table),
                "finding": sum(1 for k in short if short[k]["verdict"] == "TOTAL")})
    return out, inapplicable


def _is_det_core(obj):
    """Deterministic, total, arity one -- the common core every family contains."""
    tag = obj[0]
    if tag in ("A", "Cd", "F1"):
        return True
    if tag == "F2":
        return False
    if tag == "D":
        return True                      # a monoid with `out` is already deterministic
    if tag in ("B", "Cn", "Er"):
        return all(len(obj[1][l][s]) == 1 for l in LAB for s in S)
    if tag in ("Cp", "Ek"):
        return all(any(p == 1 for _t, p in obj[1][l][s]) for l in LAB for s in S)
    return False


def _castable(b, cls):
    try:
        cast(b, cls)
        return True
    except AssertionError:
        return False


def run_null(table):
    rng = random.Random(83341904)
    truth = totality_pattern(table)
    choices = ("TOTAL", "PARTIAL", "EMPTY")
    hits = 0
    for _ in range(200):
        if tuple(rng.choice(choices) for _ in truth) == truth:
            hits += 1
    return {"draws": 200, "reproduced": hits,
            "matched_on": "the verdict of all thirty directed translations"}


def main():                                                    # noqa: C901
    objs, behs = build(WORDS)
    table = adjudicate(objs, behs, WORDS)
    objs_s, behs_s = build(WORDS_SHORT)
    table_s = adjudicate(objs_s, behs_s, WORDS_SHORT)
    pairs = pair_summary(table)
    host, inapplicable = run_hostiles(objs, behs, table, objs_s, behs_s)
    null = run_null(table)

    bad_wit = verify_witnesses(table, objs, behs)
    bad_vocab = vocabulary_check(table)
    bad_cls = class_rule_check(table)
    bad_range = range_check(table, objs)
    n_total = sum(1 for k in table if table[k]["verdict"] == "TOTAL")
    n_partial = sum(1 for k in table if table[k]["verdict"] == "PARTIAL")
    n_empty = sum(1 for k in table if table[k]["verdict"] == "EMPTY")
    mutually_total = sorted(k for k in pairs if pairs[k]["verdict"] == "MUTUALLY_TOTAL")

    gates = [
        ("all_thirty_directed_translations_adjudicated", len(table) == 30),
        ("all_fifteen_pairs_adjudicated", len(pairs) == 15),
        ("every_witness_is_untranslatable", not bad_wit),
        ("obstruction_vocabulary_is_closed", not bad_vocab),
        ("behaviour_compared_in_the_coarsest_common_class", not bad_cls),
        ("source_range_recomputed_from_the_generators", not bad_range),
        ("every_partial_has_an_obstruction",
         all(table[k].get("obstruction") for k in table
             if table[k]["verdict"] in ("PARTIAL", "EMPTY"))),
        ("not_all_pairs_are_total", len(mutually_total) < 15),
        ("observation_window_is_sufficient",
         totality_pattern(table_s) == totality_pattern(table)),
        ("all_hostiles_detected", all(h["detected"] for h in host)),
        ("every_hostile_moved_its_quantity", all(h["control_moved"] for h in host)),
        ("null_clean", null["reproduced"] == 0),
        ("no_alarm_on_true_configuration",
         not bad_wit and not bad_vocab and not bad_cls and not bad_range),
    ]
    failed = [g for g, ok in gates if not ok]

    result = {
        "schema": "AG4_FORMALISM_TRANSLATION_RESULT_V1",
        "issue": 833, "section": "AG4", "row_index": 19,
        "claim_ceiling": ("AG4_ALL_FIFTEEN_FAMILY_PAIRS_ADJUDICATED_TOTAL_OR_PARTIAL_"
                          "WITH_A_NAMED_OBSTRUCTION_AT_REGISTERED_FINITE_SCOPE"),
        "results": ["AG4T-1", "AG4T-2", "AG4T-3", "AG4T-4"],
        "families": list(FAMILIES),
        "specializations": dict((f, list(SPECIALIZATIONS[f])) for f in FAMILIES),
        "registered_objects": dict((t, len(objs[t])) for t in sorted(objs)),
        "registered_objects_total": sum(len(v) for v in objs.values()),
        "observation_window": W,
        "directed_translations": table,
        "pairs": pairs,
        "directed_verdict_histogram": {"TOTAL": n_total, "PARTIAL": n_partial,
                                       "EMPTY": n_empty},
        "pair_verdict_histogram": dict(
            (v, sum(1 for k in pairs if pairs[k]["verdict"] == v))
            for v in sorted(set(pairs[k]["verdict"] for k in pairs))),
        "mutually_total_pairs": mutually_total,
        "obstruction_histogram": dict(
            (t, sum(1 for k in table if t in table[k].get("obstruction", ())))
            for t in OBSTRUCTIONS),
        "canonicity_of_translations_out_of_D": canonicity(objs, behs),
        "kernel_support_fibres": kernel_fibres(objs, behs),
        "monoidal_witness": monoidal_witness(objs),
        "hostiles": host,
        "inapplicable_perturbations": inapplicable,
        "null_random_totality_pattern": null,
        "gates": dict(gates), "failed_gates": failed,
        "status": "GREEN" if not failed else "RED",
        "forbidden_promotions": [
            "UNIQUE_LOWEST_PROCESS_FORMALISM", "ABSOLUTE_PROCESS_ONTOLOGY_PROVEN",
            "ALL_PROCESS_FORMALISMS_EQUIVALENT", "THE_SIX_FAMILIES_ARE_EXHAUSTIVE",
            "TRANSLATION_PRESERVES_COST", "TRANSLATION_PRESERVES_SEARCH_GEOMETRY",
            "FORMALISM_CHOICE_IS_FREE", "COMPLETE_GMI"],
        "scope_note": ("Thirty directed translations over ten registered finite "
                       "specializations. A TOTAL verdict is a statement about the source "
                       "family's whole registered range at this scope; it is not a claim "
                       "that the two formalisms are interchangeable in general, and it "
                       "carries nothing about cost or search geometry."),
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed,
                      "objects": result["registered_objects_total"],
                      "directed": result["directed_verdict_histogram"],
                      "pairs": result["pair_verdict_histogram"],
                      "mutually_total": mutually_total,
                      "obstructions": result["obstruction_histogram"]}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
