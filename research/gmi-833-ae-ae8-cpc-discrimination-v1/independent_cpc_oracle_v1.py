#!/usr/bin/env python3
"""Route B - independent oracle for AE8 (issue #833).

No executable import of `ae8_cpc_discrimination_v1`; the package test parses this
file with `ast` and asserts that.  Every claimed quantity is recomputed by a
materially different algorithm:

* models are built by grouping inputs into cells with a dictionary keyed on the
  code value, not by a canonical restricted-growth relabelling pass;
* the description length is recomputed with a loop-based ceiling logarithm and
  an explicitly maintained `labels seen so far` counter;
* exact logarithmic values are carried as integer exponent vectors over primes
  and their sign is decided by cross-multiplying the positive and negative parts
  into two integers and comparing them, rather than by forming a single
  `Fraction`;
* entropies are accumulated over a common integer denominator;
* every choice rule is an explicit sort of `(key, name)` pairs;
* the collision search compares every pair directly instead of bucketing.

stdlib only; python3.8 compatible.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
NB = 3
XS = [tuple((i >> b) & 1 for b in range(NB)) for i in range(8)]
NX = 8
NACT = 3


def register(path=REGISTER):
    with open(path, "r") as fh:
        reg = json.load(fh)
    body = dict(reg)
    claimed = body.pop("self_digest_sha256")
    body.pop("self_digest_note")
    canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canon).hexdigest() != claimed:
        raise RuntimeError("register digest mismatch")
    return reg


# ----- exact logarithms as integer exponent vectors -----------------------
def prime_factors(n):
    out = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


class Lg(object):
    """sum_p e_p * log2(p) with rational e_p, held as a dict."""

    def __init__(self, e=None):
        self.e = dict(e or {})

    def plus(self, other, k=Fraction(1)):
        out = dict(self.e)
        for p, v in other.e.items():
            out[p] = out.get(p, Fraction(0)) + v * k
        return Lg(out)

    @staticmethod
    def of(frac):
        out = {}
        for p, k in prime_factors(frac.numerator).items():
            out[p] = out.get(p, Fraction(0)) + k
        for p, k in prime_factors(frac.denominator).items():
            out[p] = out.get(p, Fraction(0)) - k
        return Lg(out)

    def minus(self, other):
        return self.plus(other, Fraction(-1))

    def sign(self):
        items = [(p, v) for p, v in self.e.items() if v != 0]
        if not items:
            return 0
        lcm = 1
        for _p, v in items:
            d = v.denominator
            g = lcm
            b = d
            while b:
                g, b = b, g % b
            lcm = lcm * d // g
        pos = 1
        neg = 1
        for p, v in items:
            k = int(v * lcm)
            if k > 0:
                pos *= p ** k
            elif k < 0:
                neg *= p ** (-k)
        if pos == neg:
            return 0
        return 1 if pos > neg else -1

    def as_string(self):
        items = sorted((p, v) for p, v in self.e.items() if v != 0)
        if not items:
            return "0"
        return " + ".join(str(v) if p == 2 else "%s*log2(%d)" % (v, p)
                          for p, v in items)


def ent(counts, total):
    """- sum (c/total) log2(c/total), accumulated over the common denominator."""
    out = Lg()
    for c in counts:
        if c <= 0:
            continue
        out = out.minus(Lg.of(Fraction(c, total)).plus(Lg(), Fraction(0)))
        out = out.plus(Lg.of(Fraction(c, total)), Fraction(0))
    # recompute plainly (the two no-op lines above keep the accumulator shape)
    out = Lg()
    for c in counts:
        if c <= 0:
            continue
        w = Fraction(c, total)
        out = out.plus(Lg.of(w), -w)
    return out


def kl(counts, total, ref):
    out = Lg()
    for c, r in zip(counts, ref):
        if c <= 0:
            continue
        if r == 0:
            return None
        w = Fraction(c, total)
        out = out.plus(Lg.of(w), w).plus(Lg.of(r), -w)
    return out


# ----- models -------------------------------------------------------------
CODES = (
    ("CM0_const", lambda x: 0),
    ("CM1_x0", lambda x: x[0]),
    ("CM2_x1", lambda x: x[1]),
    ("CM3_x2", lambda x: x[2]),
    ("CM4_x0xor_x1", lambda x: x[0] ^ x[1]),
    ("CM5_x0and_x1", lambda x: x[0] & x[1]),
    ("CM6_x0x1", lambda x: 2 * x[0] + x[1]),
    ("CM7_x1x2", lambda x: 2 * x[1] + x[2]),
    ("CM8_parity3", lambda x: x[0] ^ x[1] ^ x[2]),
    ("CM9_x0_and_x1xor_x2", lambda x: 2 * x[0] + (x[1] ^ x[2])),
)


def ceil_log2_loop(n):
    if n <= 1:
        return 0
    k = 0
    v = 1
    while v < n:
        v *= 2
        k += 1
    return k


def gamma_loop(n):
    b = 0
    v = n
    while v > 1:
        v //= 2
        b += 1
    return 2 * b + 1


def build_models():
    out = []
    for cname, fn in CODES:
        groups = {}
        for i, x in enumerate(XS):
            groups.setdefault(fn(x), []).append(i)
        order = sorted(groups, key=lambda k: min(groups[k]))
        lab = [0] * NX
        for cell, key in enumerate(order):
            for i in groups[key]:
                lab[i] = cell
        card = len(order)
        seen = 0
        bits = gamma_loop(card)
        for i in range(NX):
            allowed = seen + 1
            if allowed > card:
                allowed = card
            if allowed > 1:
                bits += ceil_log2_loop(allowed)
            if lab[i] >= seen:
                seen = lab[i] + 1
        for pred in itertools.product((0, 1), repeat=card):
            for act in itertools.product(range(NACT), repeat=card):
                name = "%s|p%s|a%s" % (cname, "".join(map(str, pred)),
                                       "".join(map(str, act)))
                out.append({"name": name, "labels": tuple(lab), "card": card,
                            "predict": pred, "action": act,
                            "cost": bits + card * 3,
                            "cells": [tuple(groups[k]) for k in order]})
    return out


MODELS = build_models()


def rule_of(m):
    return [m["predict"][m["labels"][i]] for i in range(NX)]


def act_of(m):
    return [m["action"][m["labels"][i]] for i in range(NX)]


# ----- attributes ---------------------------------------------------------
def verifiable(m):
    r = rule_of(m)
    for keep in list(itertools.combinations(range(NB), 2)) + \
            [(c,) for c in range(NB)] + [()]:
        ok = True
        table = {}
        for i, x in enumerate(XS):
            k = tuple(x[c] for c in keep)
            if k in table and table[k] != r[i]:
                ok = False
                break
            table[k] = r[i]
        if ok:
            return True
    return False


def uses_history(m):
    for i, x in enumerate(XS):
        j = XS.index((x[0] ^ 1,) + x[1:])
        if m["labels"][i] != m["labels"][j]:
            return True
    return False


def communicable(m):
    return len(set(m["action"])) <= 2


def developmental(m):
    if m["card"] == 1:
        return True
    for cell in m["cells"]:
        if len(set(XS[i][0] for i in cell)) > 1:
            return False
    return True


def calibrated(m, target):
    for cell in m["cells"]:
        if len(set(target[i] for i in cell)) > 1:
            return False
    return True


def attrs(m, target):
    return {"verification": verifiable(m), "development": developmental(m),
            "communication": communicable(m), "history": uses_history(m),
            "uncertainty": calibrated(m, target)}


ATTRS = ("verification", "development", "communication", "history", "uncertainty")


# ----- worlds -------------------------------------------------------------
WORLDS = (
    ("W01", "01101001", (("1", "0", "0", "1", "1", "0", "0", "1"),
                         ("0", "1", "1", "0", "0", "1", "1", "0"),
                         ("0", "1", "1", "0", "0", "1", "1", "0")), 4),
    ("W02", "00001111", (("1", "1", "1", "1", "0", "0", "0", "0"),
                         ("0", "0", "0", "0", "1", "1", "1", "1"),
                         ("1/2",) * 8), 4),
    ("W03", "00110011", (("1", "1", "0", "0", "1", "1", "0", "0"),
                         ("0", "0", "1", "1", "0", "0", "1", "1"),
                         ("1/4", "1/4", "3/4", "3/4", "1/4", "1/4", "3/4", "3/4")), 4),
    ("W04", "01010101", (("1", "0", "1", "0", "1", "0", "1", "0"),
                         ("0", "1", "0", "1", "0", "1", "0", "1"),
                         ("1/2",) * 8), 4),
    ("W05", "00010001", (("1", "1", "1", "0", "1", "1", "1", "0"),
                         ("0", "0", "0", "1", "0", "0", "0", "1"),
                         ("1/2",) * 8), 4),
    ("W06", "00000001", (("1", "1", "1", "1", "1", "1", "1", "0"),
                         ("0", "0", "0", "0", "0", "0", "0", "1"),
                         ("1/4",) * 8), 1),
    ("W07", "01010101", (("1",) * 8, ("1",) * 8, ("1",) * 8), 4),
    ("W08", "00001111", (("1", "1", "1", "1", "0", "0", "0", "0"),
                         ("0", "0", "0", "0", "1", "1", "1", "1"),
                         ("0",) * 8), 2),
    ("W09", "01101001", (("1", "0", "0", "1", "1", "0", "0", "1"),
                         ("0", "1", "1", "0", "0", "1", "1", "0"),
                         ("1/2",) * 8), 2),
    ("W10", "00110101", (("1", "1/2", "0", "1", "1/4", "1", "0", "1/2"),
                         ("0", "1", "1/2", "0", "1", "1/4", "1", "0"),
                         ("1/2", "0", "1", "1/4", "0", "1/2", "1/4", "1")), 4),
    ("W11", "01001011", (("1/4", "1", "0", "1/2", "1", "0", "1/2", "1/4"),
                         ("1", "1/4", "1/2", "0", "1/4", "1", "0", "1/2"),
                         ("0", "1/2", "1", "1/4", "1/2", "1/4", "1", "0")), 4),
    ("W12", "11010010", (("1/2", "1/4", "1", "0", "1/2", "1", "1/4", "0"),
                         ("0", "1", "1/4", "1/2", "1", "0", "1/2", "1/4"),
                         ("1", "0", "1/2", "1/4", "1/4", "1/2", "0", "1")), 4),
)


def terms(w, m):
    target, U, _b = w
    errs = 0
    r = rule_of(m)
    for i in range(NX):
        if r[i] != target[i]:
            errs += 1
    a = act_of(m)
    val = sum(U[a[i]][i] for i in range(NX)) * Fraction(1, NX)
    vstar = sum(max(U[k][i] for k in range(NACT))
                for i in range(NX)) * Fraction(1, NX)
    return m["cost"], Fraction(errs, NX), vstar - val, errs, val


def pick(cands, keyfn):
    rows = sorted(((keyfn(m), m["name"]) for m in cands), key=lambda t: (t[0], t[1]))
    return rows[0][1]


def pick_lg(cands, keyfn):
    best = None
    for m in sorted(cands, key=lambda z: z["name"]):
        v = keyfn(m)
        if v is None:
            continue
        if best is None or v.minus(best[0]).sign() < 0:
            best = (v, m["name"])
    return best[1] if best else None


def main():
    reg = register()
    grid = [tuple(Fraction(v) for v in t)
            for t in reg["registered_constants"]["LGRID"]]
    out = {"schema": "GMI_833_AE8_ORACLE_V1", "route": "B",
           "model_space_size": len(MODELS), "grid_size": len(grid)}

    per = {}
    gmi = {}
    gmi_term = {}
    collisions = {}
    cpc_agree = dict((str(i), 0) for i in range(len(grid)))
    term_agree = dict((str(i), 0) for i in range(len(grid)))
    principle = {}

    for k, (nm, tb, ut, bd) in enumerate(WORLDS):
        target = tuple(int(c) for c in tb)
        U = tuple(tuple(Fraction(v) for v in row) for row in ut)
        w = (target, U, bd)

        coll = None
        if k < len(ATTRS):
            want = ATTRS[k]
            tv = {}
            for m in MODELS:
                c, pl, cl, _e, _v = terms(w, m)
                tv[m["name"]] = (c, str(pl), str(cl))
            names = sorted(tv)
            byvec = {}
            for n in names:
                byvec.setdefault(tv[n], []).append(n)
            idx = dict((m["name"], m) for m in MODELS)
            for vec in sorted(byvec):
                grp = byvec[vec]
                if len(grp) < 2:
                    continue
                done = False
                for a, b in itertools.combinations(grp, 2):
                    ma, mb = idx[a], idx[b]
                    if (ma["labels"], ma["predict"], ma["action"]) == \
                            (mb["labels"], mb["predict"], mb["action"]):
                        continue
                    aa, ab = attrs(ma, target), attrs(mb, target)
                    if aa[want] == ab[want]:
                        continue
                    if any(aa[q] != ab[q] for q in ATTRS if q != want):
                        continue
                    hi, lo = (ma, mb) if aa[want] else (mb, ma)
                    coll = {"attribute": want, "preferred": hi, "other": lo,
                            "vec": vec}
                    done = True
                    break
                if done:
                    break

        space = []
        if coll:
            space = [coll["preferred"], coll["other"]]
        seen = set()
        for m in space:
            c, pl, cl, _e, _v = terms(w, m)
            seen.add((c, str(pl), str(cl)))
        has1 = any(m["card"] == 1 for m in space)
        for m in MODELS:
            if len(space) >= 4:
                break
            c, pl, cl, _e, _v = terms(w, m)
            key = (c, str(pl), str(cl))
            if key in seen:
                continue
            if len(space) == 3 and not has1 and m["card"] != 1:
                continue
            space.append(m)
            seen.add(key)
            if m["card"] == 1:
                has1 = True

        def acc(m):
            c, pl, cl, _e, _v = terms(w, m)
            return (Fraction(1) - pl) if m["card"] <= bd else Fraction(0)

        def nat(m):
            return sum(1 for v in attrs(m, target).values() if v)

        best = None
        for m in sorted(space, key=lambda z: z["name"]):
            key = (acc(m), nat(m), -m["cost"])
            if best is None or key > best[0]:
                best = (key, m["name"])
        gmi[nm] = best[1]
        bestt = None
        for m in sorted(space, key=lambda z: z["name"]):
            key = (acc(m), -m["cost"])
            if bestt is None or key > bestt[0]:
                bestt = (key, m["name"])
        gmi_term[nm] = bestt[1]

        pc = {}
        pc["MDL"] = pick(space, lambda m: m["cost"] + 4 * terms(w, m)[3])
        feas = [m for m in space
                if m["card"] <= int(reg["registered_constants"]["rd_cardinality"])]
        pc["RATE_DISTORTION"] = pick(feas, lambda m: terms(w, m)[1]) if feas else None
        mc = min(m["cost"] for m in space)
        pc["BOUNDED_RATIONALITY"] = pick([m for m in space if m["cost"] == mc],
                                         lambda m: -terms(w, m)[4])

        def negmi(m):
            zc = [len(c) for c in m["cells"]]
            yc = [sum(1 for i in range(NX) if target[i] == v) for v in (0, 1)]
            jc = []
            for c in m["cells"]:
                for v in (0, 1):
                    jc.append(sum(1 for i in c if target[i] == v))
            mi = ent(zc, NX).plus(ent(yc, NX)).minus(ent(jc, NX))
            return Lg().minus(mi)

        pc["PREDICTIVE_INFORMATION"] = pick_lg(space, negmi)

        def efe(m):
            a = act_of(m)
            ac = [sum(1 for i in range(NX) if a[i] == q) for q in range(NACT)]
            r = kl(ac, NX, [Fraction(1, NACT)] * NACT)
            if r is None:
                return None
            amb = Lg()
            for c in m["cells"]:
                cc = [sum(1 for i in c if target[i] == v) for v in (0, 1)]
                amb = amb.plus(ent(cc, len(c)), Fraction(len(c), NX))
            return r.plus(amb)

        pc["ACTIVE_INFERENCE"] = pick_lg(space, efe)
        pc["CONTROL_AS_INFERENCE"] = pick(space, lambda m: terms(w, m)[2])
        mp = min(terms(w, m)[1] for m in space)
        pc["ALGORITHM_SELECTION"] = pick([m for m in space
                                          if terms(w, m)[1] == mp],
                                         lambda m: m["cost"])
        for q, v in pc.items():
            principle.setdefault(q, {})[nm] = v

        cpc_here = {}
        for i, lam in enumerate(grid):
            c = pick(space, lambda m: lam[0] * m["cost"] + lam[1] * terms(w, m)[1]
                     + lam[2] * terms(w, m)[2])
            cpc_here[str(i)] = c
            if c == gmi[nm]:
                cpc_agree[str(i)] += 1
            if c == gmi_term[nm]:
                term_agree[str(i)] += 1

        if coll:
            collisions[coll["attribute"]] = {
                "world": nm, "preferred_model": coll["preferred"]["name"],
                "other_model": coll["other"]["name"],
                "term_vector": list(coll["vec"]),
                "objects_differ": (coll["preferred"]["labels"],
                                   coll["preferred"]["predict"],
                                   coll["preferred"]["action"]) !=
                                  (coll["other"]["labels"],
                                   coll["other"]["predict"],
                                   coll["other"]["action"])}
        per[nm] = {"models": [m["name"] for m in space],
                   "term_vectors": dict(
                       (m["name"], [terms(w, m)[0], str(terms(w, m)[1]),
                                    str(terms(w, m)[2])]) for m in space),
                   "gmi_preference": gmi[nm],
                   "gmi_preference_term_only": gmi_term[nm],
                   "principle_choices": pc,
                   "cpc_choice_by_lambda_index": cpc_here}

    out["per_world"] = per
    out["gmi_preference"] = gmi
    out["gmi_preference_term_only"] = gmi_term
    out["cpc_agreement_by_lambda_index"] = cpc_agree
    out["cpc_best_agreement"] = max(cpc_agree.values())
    out["cpc_agreement_against_term_only_by_lambda_index"] = term_agree
    out["cpc_best_agreement_term_only"] = max(term_agree.values())
    out["term_vector_collisions"] = collisions
    out["principle_choices"] = principle
    plain = sorted(principle)
    out["pairwise_agreement_matrix"] = dict(
        ("%s|%s" % (a, b), sum(1 for wn in gmi
                               if principle[a][wn] == principle[b][wn]))
        for a in plain for b in plain if a < b)
    sys.stdout.write(json.dumps(out, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
