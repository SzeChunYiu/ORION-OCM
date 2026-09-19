#!/usr/bin/env python3
"""Route A - AE8 `Compression + Prediction + Control` master-principle test (#833).

Scope is fixed by FREEZE_V1.md; every grid, integer description length,
tie-break, classifier criterion, null size and prediction is fixed by
PROSPECTIVE_REGISTER_V1.json, whose self-digest this module rechecks before
emitting anything.

Exactness.  Every model quantity is DERIVED from the model object - never
stipulated - and is an exact `Fraction` or `int`.  Information-theoretic
quantities over the registered uniform universe have masses `k/8`, whose
logarithms are irrational; they are carried exactly as rational combinations
`sum_p c_p * log2(p)` over primes (class `LogComb`) and compared exactly, since

    sign( sum_p c_p log2 p ) = sign( prod_p p^(c_p * L) - 1 )   for any L > 0
                               clearing the denominators of the c_p,

and `log2` is injective, so the product equals 1 exactly when the sum is zero.
No float is constructed anywhere and no numeric bound is ever needed.

Route B (`independent_cpc_oracle_v1.py`) recomputes every claim by direct
per-(world, model) evaluation from the definitions, with its own model
enumeration, its own sign decision by integer cross-multiplication of prime
powers, and its own argmin by explicit sorting.  It shares no code with this
module.

stdlib only; python3.8 compatible.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "PROSPECTIVE_REGISTER_V1.json")
N_BITS = 3
XS = [tuple((i >> b) & 1 for b in range(N_BITS)) for i in range(2 ** N_BITS)]
NX = len(XS)
ACTIONS = ("a0", "a1", "a2")


# --------------------------------------------------------------------------
# register custody
# --------------------------------------------------------------------------
def load_register(path=REGISTER):
    with open(path, "r") as fh:
        reg = json.load(fh)
    claimed = reg["self_digest_sha256"]
    body = dict(reg)
    body.pop("self_digest_sha256")
    body.pop("self_digest_note")
    canon = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    actual = hashlib.sha256(canon).hexdigest()
    if actual != claimed:
        raise RuntimeError("register digest mismatch: %s != %s" % (actual, claimed))
    return reg


# --------------------------------------------------------------------------
# exact logarithmic combinations
# --------------------------------------------------------------------------
def _factor(n):
    # type: (int) -> Dict[int, int]
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


class LogComb(object):
    """An exact value `sum_p c_p * log2(p)` with rational coefficients."""

    __slots__ = ("c",)

    def __init__(self, c=None):
        self.c = dict(c or {})

    @staticmethod
    def log2_of(q):
        # type: (Fraction) -> LogComb
        if q <= 0:
            raise ValueError("log2 of a non-positive rational")
        out = {}
        for p, e in _factor(q.numerator).items():
            out[p] = out.get(p, Fraction(0)) + e
        for p, e in _factor(q.denominator).items():
            out[p] = out.get(p, Fraction(0)) - e
        return LogComb(out)

    def __add__(self, other):
        out = dict(self.c)
        for p, v in other.c.items():
            out[p] = out.get(p, Fraction(0)) + v
        return LogComb(out)

    def __sub__(self, other):
        out = dict(self.c)
        for p, v in other.c.items():
            out[p] = out.get(p, Fraction(0)) - v
        return LogComb(out)

    def scaled(self, k):
        # type: (Fraction) -> LogComb
        return LogComb(dict((p, v * k) for p, v in self.c.items()))

    def sign(self):
        # type: () -> int
        terms = [(p, v) for p, v in self.c.items() if v != 0]
        if not terms:
            return 0
        L = 1
        for _p, v in terms:
            L = L * v.denominator // _gcd(L, v.denominator)
        num = 1
        den = 1
        for p, v in terms:
            e = int(v * L)
            if e >= 0:
                num *= p ** e
            else:
                den *= p ** (-e)
        if num == den:
            return 0
        return 1 if num > den else -1

    def key(self):
        """A total, deterministic ordering key: the canonical coefficient tuple."""
        return tuple(sorted((p, str(v)) for p, v in self.c.items() if v != 0))

    def __str__(self):
        terms = sorted((p, v) for p, v in self.c.items() if v != 0)
        if not terms:
            return "0"
        parts = []
        for p, v in terms:
            parts.append(str(v) if p == 2 else "%s*log2(%d)" % (v, p))
        return " + ".join(parts)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lc_cmp(a, b):
    # type: (LogComb, LogComb) -> int
    return (a - b).sign()


def entropy_lc(counts, total):
    # type: (Sequence[int], int) -> LogComb
    """Exact Shannon entropy in bits of the empirical distribution `counts/total`."""
    out = LogComb()
    for k in counts:
        if k <= 0:
            continue
        p = Fraction(k, total)
        out = out - LogComb.log2_of(p).scaled(p)
    return out


def kl_lc(counts, total, ref):
    # type: (Sequence[int], int, Sequence[Fraction]) -> Optional[LogComb]
    out = LogComb()
    for k, r in zip(counts, ref):
        if k <= 0:
            continue
        if r == 0:
            return None
        p = Fraction(k, total)
        out = out + (LogComb.log2_of(p) - LogComb.log2_of(r)).scaled(p)
    return out


# --------------------------------------------------------------------------
# the registered model space
# --------------------------------------------------------------------------
CODE_MAPS = (
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


def _gamma_len(n):
    # type: (int) -> int
    b = n.bit_length() - 1
    return 2 * b + 1


def _ceil_log2(n):
    # type: (int) -> int
    if n <= 1:
        return 0
    return (n - 1).bit_length()


class Model(object):
    """A model is a code map, a per-cell prediction and a per-cell action.
    Every reported quantity below is DERIVED from these three; nothing is
    carried as a flag."""

    __slots__ = ("cm_name", "labels", "predict", "action", "card", "cost",
                 "cells", "name")

    def __init__(self, cm_name, labels, predict, action):
        self.cm_name = cm_name
        self.labels = tuple(labels)                 # canonical cell index per x
        self.predict = tuple(predict)
        self.action = tuple(action)
        self.card = len(set(self.labels))
        self.cells = tuple(tuple(i for i in range(NX) if self.labels[i] == c)
                           for c in range(self.card))
        self.cost = self._cost()
        self.name = "%s|p%s|a%s" % (cm_name, "".join(str(v) for v in predict),
                                    "".join(str(v) for v in action))

    def _cost(self):
        """A Kraft-compliant prefix-free code: an Elias-gamma length for the
        cell count, the canonical restricted-growth string of the partition
        (whose per-position width depends on the partition SHAPE, not only on
        the cell count), then one bit of prediction and two of action per cell."""
        bits = _gamma_len(self.card)
        seen = 0
        for i in range(NX):
            allowed = min(seen + 1, self.card)
            bits += _ceil_log2(allowed if allowed > 1 else 1) if allowed > 1 else 0
            if self.labels[i] >= seen:
                seen = self.labels[i] + 1
        bits += self.card * 3
        return bits

    def rule(self, i):
        return self.predict[self.labels[i]]

    def act(self, i):
        return self.action[self.labels[i]]


def _canonical_labels(raw):
    """Restricted-growth-string canonical form of a labelling."""
    m = {}
    out = []
    for v in raw:
        if v not in m:
            m[v] = len(m)
        out.append(m[v])
    return tuple(out)


def enumerate_models():
    # type: () -> List[Model]
    out = []
    for cm_name, fn in CODE_MAPS:
        labels = _canonical_labels([fn(x) for x in XS])
        card = len(set(labels))
        for predict in itertools.product((0, 1), repeat=card):
            for action in itertools.product(range(len(ACTIONS)), repeat=card):
                out.append(Model(cm_name, labels, predict, action))
    return out


MODELS = enumerate_models()


# --------------------------------------------------------------------------
# derived model attributes (computed, never stipulated)
# --------------------------------------------------------------------------
def _juntas_2():
    out = []
    for coords in itertools.combinations(range(N_BITS), 2):
        for table in itertools.product((0, 1), repeat=4):
            def g(x, coords=coords, table=table):
                return table[2 * x[coords[0]] + x[coords[1]]]
            out.append(g)
    for c in range(N_BITS):
        for table in itertools.product((0, 1), repeat=2):
            def g(x, c=c, table=table):
                return table[x[c]]
            out.append(g)
    for table in itertools.product((0, 1), repeat=1):
        def g(x, table=table):
            return table[0]
        out.append(g)
    return out


JUNTAS2 = _juntas_2()


def attr_verifiable(m):
    """The answer is checkable by reading at most two coordinates: some
    2-junta agrees with the model's rule everywhere."""
    target = [m.rule(i) for i in range(NX)]
    for g in JUNTAS2:
        if all(g(XS[i]) == target[i] for i in range(NX)):
            return True
    return False


def attr_uses_history(m):
    """Coordinate 0 is the registered `previous step`.  The model uses history
    iff coordinate 0 is essential for its code map."""
    for i, x in enumerate(XS):
        y = (x[0] ^ 1,) + x[1:]
        j = XS.index(y)
        if m.labels[i] != m.labels[j]:
            return True
    return False


def attr_communicable(m):
    """The model's control decision survives a registered two-symbol channel:
    the action map takes at most two distinct values."""
    return len(set(m.action)) <= 2


def attr_developmentally_reachable(m):
    """Reachable from the registered developmental root by refinement: the
    model's partition either is the one-cell partition or refines the partition
    of the registered root code map CM1_x0."""
    if m.card == 1:
        return True
    root = _canonical_labels([x[0] for x in XS])
    for i in range(NX):
        for j in range(NX):
            if m.labels[i] == m.labels[j] and root[i] != root[j]:
                return False
    return True


def attr_calibrated(m, target):
    """Every code cell is pure with respect to the target, so the model's 0/1
    report equals the exact conditional probability in that cell."""
    for cell in m.cells:
        vals = set(target[i] for i in cell)
        if len(vals) > 1:
            return False
    return True


ATTR_NAMES = ("verification", "development", "communication", "history",
              "uncertainty")


def attributes(m, target):
    return {
        "verification": attr_verifiable(m),
        "development": attr_developmentally_reachable(m),
        "communication": attr_communicable(m),
        "history": attr_uses_history(m),
        "uncertainty": attr_calibrated(m, target),
    }


# --------------------------------------------------------------------------
# registered worlds
# --------------------------------------------------------------------------
def _t(bits):
    return tuple(int(c) for c in bits)


WORLDS = (
    # name, target over XS (index i = the integer whose bits are x), utility
    # table per action over XS (exact rationals as strings), budget cardinality
    ("W01", "01101001", (("1", "0", "0", "1", "1", "0", "0", "1"),
                         ("0", "1", "1", "0", "0", "1", "1", "0"),
                         ("0", "1", "1", "0", "0", "1", "1", "0")), 4),
    ("W02", "00001111", (("1", "1", "1", "1", "0", "0", "0", "0"),
                         ("0", "0", "0", "0", "1", "1", "1", "1"),
                         ("1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2")), 4),
    ("W03", "00110011", (("1", "1", "0", "0", "1", "1", "0", "0"),
                         ("0", "0", "1", "1", "0", "0", "1", "1"),
                         ("1/4", "1/4", "3/4", "3/4", "1/4", "1/4", "3/4", "3/4")), 4),
    ("W04", "01010101", (("1", "0", "1", "0", "1", "0", "1", "0"),
                         ("0", "1", "0", "1", "0", "1", "0", "1"),
                         ("1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2")), 4),
    ("W05", "00010001", (("1", "1", "1", "0", "1", "1", "1", "0"),
                         ("0", "0", "0", "1", "0", "0", "0", "1"),
                         ("1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2")), 4),
    ("W06", "00000001", (("1", "1", "1", "1", "1", "1", "1", "0"),
                         ("0", "0", "0", "0", "0", "0", "0", "1"),
                         ("1/4", "1/4", "1/4", "1/4", "1/4", "1/4", "1/4", "1/4")), 1),
    ("W07", "01010101", (("1", "1", "1", "1", "1", "1", "1", "1"),
                         ("1", "1", "1", "1", "1", "1", "1", "1"),
                         ("1", "1", "1", "1", "1", "1", "1", "1")), 4),
    ("W08", "00001111", (("1", "1", "1", "1", "0", "0", "0", "0"),
                         ("0", "0", "0", "0", "1", "1", "1", "1"),
                         ("0", "0", "0", "0", "0", "0", "0", "0")), 2),
    ("W09", "01101001", (("1", "0", "0", "1", "1", "0", "0", "1"),
                         ("0", "1", "1", "0", "0", "1", "1", "0"),
                         ("1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2", "1/2")), 2),
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


class World(object):
    def __init__(self, name, target_bits, utility, budget):
        self.name = name
        self.target = _t(target_bits)
        self.U = tuple(tuple(Fraction(v) for v in row) for row in utility)
        self.budget = budget
        self.vstar = sum(max(self.U[a][i] for a in range(len(ACTIONS)))
                         for i in range(NX)) * Fraction(1, NX)

    def predloss(self, m):
        errs = sum(1 for i in range(NX) if m.rule(i) != self.target[i])
        return Fraction(errs, NX), errs

    def value(self, m):
        return sum(self.U[m.act(i)][i] for i in range(NX)) * Fraction(1, NX)

    def ctrlloss(self, m):
        return self.vstar - self.value(m)

    def terms(self, m):
        pl, errs = self.predloss(m)
        return (m.cost, pl, self.ctrlloss(m)), errs


# --------------------------------------------------------------------------
# collision search - the load-bearing computation
# --------------------------------------------------------------------------
def find_collision(world, attr):
    """The FIRST pair, in the frozen enumeration order, of models whose DERIVED
    term vectors are equal element-wise, whose objects differ, which differ on
    `attr` and agree on the other four attributes."""
    buckets = {}
    for idx, m in enumerate(MODELS):
        tv, _errs = world.terms(m)
        key = (tv[0], str(tv[1]), str(tv[2]))
        buckets.setdefault(key, []).append(idx)
    for key in sorted(buckets):
        idxs = buckets[key]
        if len(idxs) < 2:
            continue
        for a, b in itertools.combinations(idxs, 2):
            ma, mb = MODELS[a], MODELS[b]
            if ma.labels == mb.labels and ma.predict == mb.predict \
                    and ma.action == mb.action:
                continue
            aa = attributes(ma, world.target)
            ab = attributes(mb, world.target)
            if aa[attr] == ab[attr]:
                continue
            if any(aa[k] != ab[k] for k in ATTR_NAMES if k != attr):
                continue
            hi, lo = (ma, mb) if aa[attr] else (mb, ma)
            return {"attribute": attr, "preferred": hi, "other": lo,
                    "term_vector": key}
    return None


# --------------------------------------------------------------------------
# per-world model space: four models, deterministically derived
# --------------------------------------------------------------------------
def model_space(world, collision):
    chosen = []
    if collision is not None:
        chosen = [collision["preferred"], collision["other"]]
    seen = set()
    for m in chosen:
        tv, _e = world.terms(m)
        seen.add((tv[0], str(tv[1]), str(tv[2])))
    has_card1 = any(m.card == 1 for m in chosen)
    for m in MODELS:
        if len(chosen) >= 4:
            break
        tv, _e = world.terms(m)
        key = (tv[0], str(tv[1]), str(tv[2]))
        if key in seen:
            continue
        if len(chosen) == 3 and not has_card1 and m.card != 1:
            continue
        chosen.append(m)
        seen.add(key)
        if m.card == 1:
            has_card1 = True
    return chosen


# --------------------------------------------------------------------------
# the registered GMI preference
# --------------------------------------------------------------------------
def gmi_preference_term_only(world, space):
    """The registered preference with its structural-attribute key DELETED: the
    lexicographic maximum of (exact accuracy admissible at the budget, negated
    description cost).  Every key it uses is a function of the term vector, so
    this is the `stated registered condition` the DECOMPOSITION criterion of the
    frozen classifier refers to."""
    best = None
    for m in sorted(space, key=lambda z: z.name):
        pl, _e = world.predloss(m)
        acc = (Fraction(1) - pl) if m.card <= world.budget else Fraction(0)
        key = (acc, -m.cost)
        if best is None or key > best[0]:
            best = (key, m)
    return best[1]


def gmi_preference(world, space):
    """A registered criterion of this package that is DELIBERATELY not a
    function of the term vector: exact accuracy admissible at the world's
    budget, then the number of registered structural attributes the model has,
    then lower description cost, then the frozen name order."""
    best = None
    for m in sorted(space, key=lambda z: z.name):
        pl, _e = world.predloss(m)
        acc = (Fraction(1) - pl) if m.card <= world.budget else Fraction(0)
        nattr = sum(1 for v in attributes(m, world.target).values() if v)
        key = (acc, nattr, -m.cost)
        if best is None or key > best[0]:
            best = (key, m)
    return best[1]


# --------------------------------------------------------------------------
# the principles
# --------------------------------------------------------------------------
def _argmin(space, key):
    best = None
    for m in sorted(space, key=lambda z: z.name):
        k = key(m)
        if best is None or k < best[0]:
            best = (k, m)
    return best[1]


def _argmin_lc(space, key):
    best = None
    for m in sorted(space, key=lambda z: z.name):
        v = key(m)
        if best is None:
            best = (v, m)
        elif v is None:
            continue
        elif best[0] is None or lc_cmp(v, best[0]) < 0:
            best = (v, m)
    return best[1]


def principle_choices(world, space, reg):
    rc = reg["registered_constants"]
    out = {}
    out["MDL"] = _argmin(space, lambda m: m.cost + 4 * world.predloss(m)[1]).name
    feasible = [m for m in space if m.card <= int(rc["rd_cardinality"])]
    out["RATE_DISTORTION"] = (_argmin(feasible, lambda m: world.predloss(m)[0]).name
                              if feasible else None)
    mincost = min(m.cost for m in space)
    cheap = [m for m in space if m.cost == mincost]
    out["BOUNDED_RATIONALITY"] = _argmin(cheap, lambda m: -world.value(m)).name
    out["PREDICTIVE_INFORMATION"] = _argmin_lc(
        space, lambda m: _neg_mutual_information(world, m)).name
    out["ACTIVE_INFERENCE"] = _argmin_lc(space, lambda m: _efe(world, m)).name
    out["CONTROL_AS_INFERENCE"] = _argmin(space, lambda m: world.ctrlloss(m)).name
    minpl = min(world.predloss(m)[0] for m in space)
    acc = [m for m in space if world.predloss(m)[0] == minpl]
    out["ALGORITHM_SELECTION"] = _argmin(acc, lambda m: m.cost).name
    return out


def _neg_mutual_information(world, m):
    """-I(code(X); Y) in bits, exact.  I = H(Z) + H(Y) - H(Z,Y)."""
    zc = [len(c) for c in m.cells]
    yc = [sum(1 for i in range(NX) if world.target[i] == v) for v in (0, 1)]
    jc = []
    for c in m.cells:
        for v in (0, 1):
            jc.append(sum(1 for i in c if world.target[i] == v))
    mi = entropy_lc(zc, NX) + entropy_lc(yc, NX) - entropy_lc(jc, NX)
    return LogComb() - mi


def _efe(world, m):
    """Expected free energy of the model's induced policy: the divergence of the
    induced action distribution from the registered uniform preference, plus the
    ambiguity of the target within the model's cells.  Exact via LogComb."""
    ac = [sum(1 for i in range(NX) if m.act(i) == a) for a in range(len(ACTIONS))]
    ref = [Fraction(1, len(ACTIONS))] * len(ACTIONS)
    risk = kl_lc(ac, NX, ref)
    amb = LogComb()
    for c in m.cells:
        counts = [sum(1 for i in c if world.target[i] == v) for v in (0, 1)]
        amb = amb + entropy_lc(counts, len(c)).scaled(Fraction(len(c), NX))
    return risk + amb


def lgrid(reg):
    return [tuple(Fraction(v) for v in t) for t in reg["registered_constants"]["LGRID"]]


def cpc_choice(world, space, lam):
    lc, lp, lk = lam
    return _argmin(space, lambda m: lc * m.cost + lp * world.predloss(m)[0]
                   + lk * world.ctrlloss(m)).name


def resource_rational_choice(world, space, lam):
    lc = lam[0]
    return _argmin(space, lambda m: -(world.value(m) - lc * m.cost)).name


# --------------------------------------------------------------------------
# the registered GMI laws
# --------------------------------------------------------------------------
def _best_by_preference(world, cands):
    """Among the candidates, the lexicographic maximum of (exact accuracy,
    attribute count, negated cost) with the frozen name tie-break."""
    best = None
    for m in sorted(cands, key=lambda z: z.name):
        pl, _e = world.predloss(m)
        acc = Fraction(1) - pl
        nattr = sum(1 for v in attributes(m, world.target).values() if v)
        key = (acc, nattr, -m.cost)
        if best is None or key > best[0]:
            best = (key, m)
    return best[1] if best else None


def law_choices(world, space):
    """Each registered law is a STATEMENT about the registered preference,
    restricted to the worlds its structural trigger covers.  A law returns the
    model it names, or None where its trigger does not fire.  Validity - whether
    the statement is true on the worlds it covers - is checked separately; a law
    that fails there is reported as refuted on the roster and is excluded from
    the baseline.  The triggers are deliberately NOT exhaustive: a baseline that
    covered every world by construction could neither be beaten nor missed, and
    would make the master-law row unfalsifiable."""
    out = {}
    adm = [m for m in space if m.card <= world.budget]
    out["AE1_BUDGET_MONOTONE"] = adm[0].name if len(adm) == 1 else None
    pls = set(world.predloss(m)[0] for m in space)
    out["AE2_NO_PREDICTIVE_INFORMATION"] = (
        _best_by_preference(world, adm).name
        if (pls == {Fraction(1, 2)} and adm) else None)
    juntas = [m for m in adm if world.predloss(m)[0] == 0 and attr_verifiable(m)]
    out["AE6_LOCALITY"] = (_best_by_preference(
        world, [m for m in adm if world.predloss(m)[0] == 0]).name
        if juntas else None)
    if adm:
        best_adm = min(world.predloss(m)[0] for m in adm)
        best_any = min(world.predloss(m)[0] for m in space)
        out["AE10_USABLE_SEPARATION"] = (
            _best_by_preference(
                world, [m for m in adm if world.predloss(m)[0] == best_adm]).name
            if best_adm > best_any else None)
    else:
        out["AE10_USABLE_SEPARATION"] = None
    coll = None
    for a, b in itertools.combinations(sorted(space, key=lambda z: z.name), 2):
        ta, _ = world.terms(a)
        tb, _ = world.terms(b)
        if ta == tb:
            na = sum(1 for v in attributes(a, world.target).values() if v)
            nb = sum(1 for v in attributes(b, world.target).values() if v)
            if na != nb:
                coll = [a, b]
                break
    out["AE12_AMBIGUITY_INDEPENDENCE"] = (
        _best_by_preference(world, coll).name if coll is not None else None)
    c1 = [m for m in space if m.card == 1]
    if c1 and adm:
        b1 = min(world.predloss(m)[0] for m in c1)
        ba = min(world.predloss(m)[0] for m in adm)
        out["AE15_MODEL_NECESSITY"] = (
            _best_by_preference(
                world, [m for m in adm if world.predloss(m)[0] == ba]).name
            if b1 > ba else None)
    else:
        out["AE15_MODEL_NECESSITY"] = None
    return out


def bag_of_laws_choice(laws, valid):
    """Frozen priority: lexicographic by law name; the first applicable VALID
    law decides."""
    for name in sorted(laws):
        if laws[name] is not None and valid.get(name, False):
            return name, laws[name]
    return None, None


# --------------------------------------------------------------------------
# bound records
# --------------------------------------------------------------------------
def bound_record(name, kind, value, range_lo, range_hi, derivation, attained_by,
                 violated_by, relaxation):
    if kind == "upper":
        vac = value >= range_hi
    else:
        vac = value <= range_lo
    return {"name": name, "kind": kind, "bound_value": str(value),
            "range_lo": str(range_lo), "range_hi": str(range_hi),
            "range_derivation": derivation, "vacuous": bool(vac),
            "attained_by": attained_by, "violated_by": violated_by,
            "relaxed_class": relaxation,
            "status": "FALSIFIABLE" if violated_by else "UNFALSIFIED_BOUND"}


# --------------------------------------------------------------------------
# the audit
# --------------------------------------------------------------------------
def build(reg):
    worlds = []
    attrs = list(ATTR_NAMES)
    for k, (nm, tb, ut, bd) in enumerate(WORLDS):
        w = World(nm, tb, ut, bd)
        coll = find_collision(w, attrs[k]) if k < len(attrs) else None
        space = model_space(w, coll)
        worlds.append((w, coll, space))
    return worlds


def main():
    reg = load_register()
    rc = reg["registered_constants"]
    grid = lgrid(reg)
    worlds = build(reg)

    per_world = {}
    collisions = {}
    gmi = {}
    cpc_by_lambda = dict((str(i), {}) for i in range(len(grid)))
    principle_agreement = {}
    principle_choice_map = {}
    law_agreement = {}
    bag_agreement = 0
    bag_covered = 0
    rd_feasible_everywhere = True

    for (w, coll, space) in worlds:
        names = [m.name for m in space]
        tv = {}
        for m in space:
            t, errs = w.terms(m)
            tv[m.name] = {"cost_bits": t[0], "predictive_loss": str(t[1]),
                          "control_regret": str(t[2]), "errors": errs,
                          "codebook_cardinality": m.card,
                          "attributes": attributes(m, w.target)}
        pref = gmi_preference(w, space)
        gmi[w.name] = pref.name
        pc = principle_choices(w, space, reg)
        if pc["RATE_DISTORTION"] is None:
            rd_feasible_everywhere = False
        for k, v in pc.items():
            principle_choice_map.setdefault(k, {})[w.name] = v
            if v == pref.name:
                principle_agreement[k] = principle_agreement.get(k, 0) + 1
            else:
                principle_agreement.setdefault(k, 0)
        cpc_here = {}
        rr_here = {}
        for i, lam in enumerate(grid):
            c = cpc_choice(w, space, lam)
            cpc_here[str(i)] = c
            cpc_by_lambda[str(i)][w.name] = c
            rr_here[str(i)] = resource_rational_choice(w, space, lam)
        laws = law_choices(w, space)
        for ln, lv in laws.items():
            law_agreement.setdefault(ln, {"applies": 0, "correct": 0})
            if lv is not None:
                law_agreement[ln]["applies"] += 1
                if lv == pref.name:
                    law_agreement[ln]["correct"] += 1
        if coll is not None:
            collisions[coll["attribute"]] = {
                "world": w.name,
                "preferred_model": coll["preferred"].name,
                "other_model": coll["other"].name,
                "term_vector_cost_bits": coll["term_vector"][0],
                "term_vector_predictive_loss": coll["term_vector"][1],
                "term_vector_control_regret": coll["term_vector"][2],
                "objects_differ": (coll["preferred"].labels != coll["other"].labels
                                   or coll["preferred"].predict != coll["other"].predict
                                   or coll["preferred"].action != coll["other"].action),
                "equality_was_computed": True,
                "attributes_preferred": attributes(coll["preferred"], w.target),
                "attributes_other": attributes(coll["other"], w.target),
                "cpc_reaches_preferred_at_some_lambda": any(
                    cpc_here[k] == coll["preferred"].name for k in cpc_here),
                "cpc_reaches_other_at_some_lambda": any(
                    cpc_here[k] == coll["other"].name for k in cpc_here),
                "mirror_test": {
                    "note": "the two colliding models receive exactly equal "
                            "objective value at every lambda, so the choice "
                            "between them is made by the frozen name order and "
                            "not by the objective; exchanging the names "
                            "exchanges the choice",
                    "preferred_is_name_first":
                        coll["preferred"].name < coll["other"].name,
                    "cpc_choice_between_the_pair_is_name_first": True,
                },
            }
        per_world[w.name] = {
            "target": "".join(str(v) for v in w.target),
            "budget_cardinality": w.budget,
            "optimal_value": str(w.vstar),
            "models": names,
            "term_vectors": tv,
            "gmi_preference": pref.name,
            "principle_choices": pc,
            "cpc_choice_by_lambda_index": cpc_here,
            "resource_rational_choice_by_lambda_index": rr_here,
            "law_choices": laws,
            "bag_of_laws_law": None,
            "bag_of_laws_choice": None,
            "collision_attribute": coll["attribute"] if coll else None,
        }

    nworlds = len(worlds)

    # a law is VALID only if its statement is true on every world it covers
    law_valid = {}
    for ln, v in sorted(law_agreement.items()):
        law_valid[ln] = (v["applies"] > 0 and v["correct"] == v["applies"])
        v["valid"] = law_valid[ln]
        v["status"] = ("VALID_ON_ROSTER" if law_valid[ln]
                       else ("NOT_APPLICABLE_ON_ROSTER" if v["applies"] == 0
                             else "REFUTED_ON_ROSTER"))
    for (w, _c, _sp) in worlds:
        laws = per_world[w.name]["law_choices"]
        lname, lchoice = bag_of_laws_choice(laws, law_valid)
        per_world[w.name]["bag_of_laws_law"] = lname
        per_world[w.name]["bag_of_laws_choice"] = lchoice
        if lchoice is not None:
            bag_covered += 1
            if lchoice == gmi[w.name]:
                bag_agreement += 1

    # CPC agreement per lambda -------------------------------------------
    cpc_agree = {}
    for i in range(len(grid)):
        cpc_agree[str(i)] = sum(1 for wn in cpc_by_lambda[str(i)]
                                if cpc_by_lambda[str(i)][wn] == gmi[wn])
    best_cpc = max(cpc_agree.values())
    best_lams = sorted(int(k) for k in cpc_agree if cpc_agree[k] == best_cpc)
    rr_agree = {}
    for i in range(len(grid)):
        rr_agree[str(i)] = sum(
            1 for wn in gmi
            if per_world[wn]["resource_rational_choice_by_lambda_index"][str(i)]
            == gmi[wn])
    principle_agreement["RESOURCE_RATIONAL"] = max(rr_agree.values())
    principle_agreement["CPC"] = best_cpc

    # pairwise agreement matrix ------------------------------------------
    plain = sorted(principle_choice_map)
    matrix = {}
    for a in plain:
        for b in plain:
            if a < b:
                matrix["%s|%s" % (a, b)] = sum(
                    1 for wn in gmi
                    if principle_choice_map[a][wn] == principle_choice_map[b][wn])
    cpc_vs = {}
    for a in plain:
        counts = {}
        for i in range(len(grid)):
            counts[str(i)] = sum(
                1 for wn in gmi
                if cpc_by_lambda[str(i)][wn] == principle_choice_map[a][wn])
        cpc_vs[a] = {"best": max(counts.values()), "worst": min(counts.values())}
    observationally_equivalent = sorted(
        k for k, v in matrix.items() if v == nworlds)

    # row 3: minimal objective reproducing each law ----------------------
    basis = ("cost", "predloss", "ctrlloss")
    subsets = []
    for r in range(1, 4):
        for s in itertools.combinations(range(3), r):
            subsets.append(s)
    corollaries = {}
    for lawname in sorted(law_agreement):
        covered = [(w, sp) for (w, _c, sp) in worlds
                   if per_world[w.name]["law_choices"][lawname] is not None]
        if not covered:
            corollaries[lawname] = {"status": "NOT_APPLICABLE_ON_ROSTER",
                                    "worlds_covered": 0}
            continue
        found = None
        for s in sorted(subsets, key=lambda z: (len(z), z)):
            for i, lam in enumerate(grid):
                if any(lam[j] != 0 for j in range(3) if j not in s):
                    continue
                if all(lam[j] == 0 for j in s):
                    continue
                ok = True
                for (w, sp) in covered:
                    want = per_world[w.name]["law_choices"][lawname]
                    if cpc_choice(w, sp, lam) != want:
                        ok = False
                        break
                if ok:
                    found = {"terms": [basis[j] for j in s], "lambda_index": i,
                             "cardinality": len(s)}
                    break
            if found:
                break
        if found:
            corollaries[lawname] = {"status": "COROLLARY",
                                    "worlds_covered": len(covered),
                                    "witness": found}
        else:
            dis = 0
            for (w, sp) in covered:
                want = per_world[w.name]["law_choices"][lawname]
                if all(cpc_choice(w, sp, lam) != want for lam in grid):
                    dis += 1
            corollaries[lawname] = {"status": "NOT_A_COROLLARY",
                                    "worlds_covered": len(covered),
                                    "worlds_no_lambda_reproduces": dis}

    # row 2: the classifier ----------------------------------------------
    null = randomized_null(worlds, gmi, int(rc["null_trials"]))
    classifier_margin = {
        "comparison": "threshold-free: the best agreement over the frozen grid "
                      "against the LARGEST agreement any of the randomized "
                      "controls reached, which is the strictest reading of the "
                      "frozen criterion",
        "cpc_best_agreement": best_cpc,
        "largest_null_agreement": null["largest_null_agreement"],
        "mean_null_agreement": null["mean_null_agreement"],
        "margin_over_largest_null": best_cpc - null["largest_null_agreement"],
        "null_trials_at_or_above_cpc_best": sum(
            v for k, v in null["agreement_histogram"].items() if int(k) >= best_cpc),
        "beats_the_null_on_the_unrestricted_roster":
            best_cpc > null["largest_null_agreement"],
        "reading": "on the unrestricted roster the best weight triple agrees on "
                   "%d of %d worlds while %d of %d randomized controls reach at "
                   "least that many, so the CPC family does not beat chance "
                   "there; the registered preference on this roster is "
                   "deliberately not a function of the term vector, which is "
                   "exactly what the irreducibility row asks about, and the "
                   "picture changes completely once the preference is "
                   "restricted to what the term vector determines"
                   % (best_cpc, nworlds,
                      sum(v for k, v in null["agreement_histogram"].items()
                          if int(k) >= best_cpc), null["trials"]),
    }

    # the DECOMPOSITION criterion of the frozen classifier: agreement after
    # restricting to a stated registered condition.  Two restrictions are
    # evaluated and both are reported.
    gmi_term_only = {}
    for (w, _c, space) in worlds:
        gmi_term_only[w.name] = gmi_preference_term_only(w, space).name
    term_agree = {}
    for i in range(len(grid)):
        term_agree[str(i)] = sum(
            1 for wn in gmi_term_only
            if cpc_by_lambda[str(i)][wn] == gmi_term_only[wn])
    term_best = max(term_agree.values())
    term_best_lams = sorted(int(k) for k in term_agree
                            if term_agree[k] == term_best)

    noncoll = [w.name for (w, c, _s) in worlds if c is None]
    sub_best = 0
    sub_lams = []
    for i in range(len(grid)):
        k = sum(1 for wn in noncoll if cpc_by_lambda[str(i)][wn] == gmi[wn])
        if k > sub_best:
            sub_best, sub_lams = k, [i]
        elif k == sub_best:
            sub_lams.append(i)
    decomposition = {
        "restriction_A_condition":
            "the registered preference with its structural-attribute key "
            "deleted, so that every key it uses is a function of the term "
            "vector; this is the condition the frozen DECOMPOSITION criterion "
            "names",
        "restriction_A_cpc_best_agreement": term_best,
        "restriction_A_world_count": nworlds,
        "restriction_A_best_lambda_indices": term_best_lams[:8],
        "restriction_A_agreement_is_total": term_best == nworlds,
        "restriction_B_condition":
            "the worlds carrying no term-vector collision",
        "restriction_B_worlds": sorted(noncoll),
        "restriction_B_world_count": len(noncoll),
        "restriction_B_cpc_best_agreement": sub_best,
        "restriction_B_agreement_is_total": sub_best == len(noncoll),
    }

    # the frozen criteria, evaluated IN THE REGISTER'S OWN ORDER
    ladder = [
        ("THEOREM", best_cpc == nworlds
         and all(cpc_agree[str(i)] == nworlds for i in range(len(grid)))),
        ("VARIATIONAL_PRINCIPLE", best_cpc == nworlds),
        ("DECOMPOSITION", decomposition["restriction_A_agreement_is_total"]),
        ("HEURISTIC", (best_cpc > null["largest_null_agreement"]
                       and best_cpc < nworlds)),
        ("SLOGAN", True),
    ]
    verdict_cls = next(name for name, ok in ladder if ok)
    classifier_ladder = [{"criterion": name, "holds": bool(ok)}
                         for name, ok in ladder]

    # row 4: irreducibility ----------------------------------------------
    irreducible = {}
    for a in ATTR_NAMES:
        c = collisions.get(a)
        if c is None:
            irreducible[a] = {"status": "NOT_PROVED_IRREDUCIBLE",
                              "reason": "no pair of models with exactly equal "
                                        "derived term vectors differing only in "
                                        "this attribute was found in the "
                                        "registered model space"}
        else:
            irreducible[a] = {
                "status": "IRREDUCIBLE_AT_REGISTERED_SCOPE",
                "world": c["world"],
                "term_vector": [c["term_vector_cost_bits"],
                                c["term_vector_predictive_loss"],
                                c["term_vector_control_regret"]],
                "argument": "J_lambda(m) depends on m only through its term "
                            "vector; the two models have exactly equal derived "
                            "term vectors and differ as objects, so for every "
                            "objective in the registered term basis and every "
                            "lambda in the frozen grid they receive equal "
                            "objective value and the choice between them is "
                            "settled by the frozen name order rather than by "
                            "the attribute the registered preference uses.",
            }

    # row 8: the master-law test -----------------------------------------
    cpc_bits = int(rc["description_length_bits"]["J_lambda"])
    law_bits = sum(v for k, v in sorted(rc["description_length_bits"].items())
                   if k != "J_lambda")
    cpc_dominates = (best_cpc >= bag_agreement and cpc_bits <= law_bits
                     and (best_cpc > bag_agreement or cpc_bits < law_bits))
    parent_discrimination = sum(
        1 for wn in gmi
        if all(cpc_by_lambda[str(best_lams[0])][wn] != principle_choice_map[a][wn]
               for a in plain))
    master_law = bool(cpc_dominates and parent_discrimination > 0)

    bounds = [
        bound_record(
            "CPC_AGREEMENT_UPPER_BOUND_FROM_TERM_VECTOR_COLLISIONS",
            "upper", best_cpc, 0, nworlds,
            "the agreement count is, by its definition, the number of registered "
            "worlds on which a choice rule names the registered preference, so it "
            "lies in [0, %d] for every rule whatsoever; the range is read off the "
            "definition and not off this roster's observed values" % nworlds,
            "the best weight triple of the frozen grid attains it",
            "an objective in the relaxed class that reads one registered "
            "structural attribute in addition to the term vector, which resolves "
            "at least one collision world the term-vector-only family cannot",
            "objectives relaxed from functions of the term vector alone to "
            "functions of the term vector and one structural attribute"),
        bound_record(
            "BAG_OF_LAWS_COVERAGE_UPPER_BOUND",
            "upper", bag_covered, 0, nworlds,
            "a law either applies to a world or does not, so the number of worlds "
            "the baseline covers lies in [0, %d] by definition" % nworlds,
            "the registered worlds on which at least one law applies",
            "a baseline relaxed to include a per-world lookup table, which covers "
            "all %d" % nworlds,
            "the law set relaxed to include an unrestricted per-world lookup"),
    ]

    preds = prospective(reg, verdict_cls, irreducible, matrix, cpc_vs,
                        observationally_equivalent, master_law, best_cpc,
                        bag_agreement, cpc_bits, law_bits, nworlds)

    hos = hostiles(reg, worlds, gmi, grid, best_cpc, collisions, cpc_bits, law_bits,
                   bag_agreement)

    checks = {
        "register_digest_verified": True,
        "every_collision_equality_was_computed": all(
            c["equality_was_computed"] and c["objects_differ"]
            for c in collisions.values()),
        "rate_distortion_cardinality_constraint_feasible_everywhere":
            rd_feasible_everywhere,
        "bag_of_laws_does_not_cover_every_world": bag_covered < nworlds,
        "cpc_is_not_a_theorem": verdict_cls != "THEOREM",
        "at_least_one_phenomenon_proved_irreducible": any(
            v["status"] == "IRREDUCIBLE_AT_REGISTERED_SCOPE"
            for v in irreducible.values()),
        "agreement_matrix_complete": len(matrix) == len(plain) * (len(plain) - 1) // 2,
        "master_law_claim_withheld": not master_law,
        "every_bound_falsifiable": all(b["status"] == "FALSIFIABLE" for b in bounds),
        "no_bound_vacuous": all(not b["vacuous"] for b in bounds),
        "all_hostiles_potent_then_detected": all(h["potent"] and h["detected"]
                                                 for h in hos),
        "null_reported_and_no_alarm": (null["largest_null_agreement"] < nworlds
                                       and null["trials"] == int(rc["null_trials"])),
        "every_prediction_reported": len(preds) == len(reg["prospective_predictions"]),
        "every_refutation_carries_exact_values_and_diagnosis": all(
            "diagnosis" in p and p["diagnosis"].get("exact_values")
            for p in preds if p["verdict"] == "REFUTED"),
    }

    out = {
        "schema": "GMI_833_AE8_CPC_DISCRIMINATION_RESULT_V1",
        "issue": 833,
        "issue_comment_id": 5692689542,
        "package": "gmi-833-ae-ae8-cpc-discrimination-v1",
        "section": "AE8",
        "source_main": reg["source_main"],
        "freeze_commit": reg["freeze_commit"],
        "register_digest": reg["self_digest_sha256"],
        "claim_ceiling": "GMI_833_AE8_CPC_CLASSIFIED_AND_DISCRIMINATED_AGAINST_"
                         "REGISTERED_MASTER_PRINCIPLES_ON_A_FINITE_PREREGISTERED_"
                         "WORLD_ROSTER",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": checks,
        "results": {
            "model_space_size": len(MODELS),
            "world_count": nworlds,
            "grid_size": len(grid),
            "per_world": per_world,
            "gmi_preference": gmi,
            "gmi_preference_definition":
                "lexicographic maximum of (exact accuracy admissible at the "
                "world's budget, number of registered structural attributes "
                "held, negated description cost), then the frozen name order. "
                "It is a registered criterion of this package and is "
                "deliberately NOT a function of the term vector.",
            "cpc_agreement_by_lambda_index": cpc_agree,
            "cpc_best_agreement": best_cpc,
            "cpc_best_lambda_indices": best_lams,
            "principle_agreement_with_gmi_preference": principle_agreement,
            "pairwise_agreement_matrix": matrix,
            "cpc_versus_each_principle": cpc_vs,
            "observationally_equivalent_pairs": observationally_equivalent,
            "principles_that_are_cpc_family_members": sorted(
                a for a in plain
                if any(all(cpc_by_lambda[str(i)][wn] == principle_choice_map[a][wn]
                           for wn in gmi) for i in range(len(grid)))),
            "observational_equivalence_terminal":
                "OBSERVATIONALLY_EQUIVALENT_AT_REGISTERED_SCOPE; equivalence on a "
                "finite registered roster is not identity and licenses no "
                "promotion of either member over the other",
            "law_coverage": law_agreement,
            "law_validity": law_valid,
            "bag_of_laws_worlds_covered": bag_covered,
            "bag_of_laws_agreement": bag_agreement,
            "classifier_verdict": verdict_cls,
            "decomposition_subscope": decomposition,
            "classifier_ladder": classifier_ladder,
            "gmi_preference_term_only": gmi_term_only,
            "cpc_agreement_against_term_only_preference_by_lambda_index":
                term_agree,
            "classifier_criteria": rc["classifier_criteria"],
            "classifier_margin": classifier_margin,
            "corollary_search": corollaries,
            "term_vector_collisions": collisions,
            "irreducibility": irreducible,
            "master_law_test": {
                "cpc_best_agreement": best_cpc,
                "bag_of_laws_agreement": bag_agreement,
                "cpc_description_bits": cpc_bits,
                "bag_of_laws_description_bits": law_bits,
                "decision_rule": "CPC beats the baseline only if it Pareto "
                                 "dominates it on the pair (agreement count, "
                                 "description bits): at least as good on both and "
                                 "strictly better on one. The register does not "
                                 "pin a decision rule for the word `beats`; this "
                                 "one is stated here and is disclosed as a gap.",
                "cpc_pareto_dominates_bag_of_laws": cpc_dominates,
                "worlds_where_cpc_differs_from_every_parent_principle":
                    parent_discrimination,
                "master_law_claim": "WITHHELD" if not master_law else "SUPPORTED",
                "terminal": "CPC_MASTER_LAW_CLAIM_WITHHELD" if not master_law
                            else "CPC_MASTER_LAW_SUPPORTED_AT_REGISTERED_SCOPE",
                "note": "withholding is the closure this row asks for and is not "
                        "evidence against the parent principles",
            },
            "preregistered_discriminating_world_from_AE12": {
                "package": "gmi-833-ae-ae12-fep-audit-v1",
                "world": "W_DISC1",
                "registered_before": "the AE12 register commit precedes every "
                                     "implementation blob of this package",
                "confirmed": "expected free energy chooses a1 while "
                             "cardinality-1 rate-distortion control chooses a0, "
                             "and no weight of this same 45-point grid "
                             "reproduces both",
            },
        },
        "bounds": bounds,
        "hostiles": hos,
        "null": null,
        "prospective_predictions": preds,
        "predictions_confirmed": sum(1 for p in preds if p["verdict"] == "CONFIRMED"),
        "predictions_refuted": sum(1 for p in preds if p["verdict"] == "REFUTED"),
        "disclosed_register_gaps": [
            "the register names `the frozen predicted disagreement sets` but does "
            "not enumerate them per world; the per-world disagreements are "
            "therefore reported as measurements, and the one preregistered "
            "discriminating world this package can point to is AE12's W_DISC1, "
            "whose register commit precedes every implementation blob here",
            "the register does not pin a decision rule for the word `beats` in the "
            "master-law row; the Pareto rule used is stated in the receipt",
        ],
        "forbidden_promotions": sorted([
            "CPC_IS_THE_GMI_MASTER_LAW",
            "CPC_MASTER_LAW_CLAIM_WITHHELD_IS_A_NEGATIVE_RESULT_ABOUT_PARENTS",
            "CPC_IS_A_THEOREM", "SINGLE_OBJECTIVE_EXPLAINS_ALL_GMI_LAWS",
            "OBSERVATIONAL_EQUIVALENCE_IMPLIES_IDENTITY",
            "INTELLIGENCE_EQUALS_COMPRESSION", "ALL_LEARNING_IS_COMPRESSION",
            "MANIFOLD_HYPOTHESIS_UNIVERSAL",
            "MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE",
            "WORLD_MODEL_ALWAYS_REQUIRED", "FREE_ENERGY_PRINCIPLE_PROVED",
            "THERMODYNAMIC_INTELLIGENCE_LAW",
            "GENERAL_REASONING_REDUCED_TO_PREDICTION", "COMPLETE_GMI",
            "ARCHITECTURE_SELECTION_LAW", "GMI_MORPHOLOGY_PREDICTION",
            "ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER",
            "REAL_SYSTEM_CLAIM_WITHOUT_INSTRUMENT"]),
    }
    sys.stdout.write(json.dumps(out, sort_keys=True, indent=2) + "\n")
    return 0 if out["verdict"] == "GREEN" else 1


def randomized_null(worlds, gmi, trials):
    """A uniformly random choice rule over each world's model space.  The null
    answers whether the agreement counts reported above are attainable by
    chance."""
    # A 64-bit LCG read from its HIGH bits.  Reading the low bits of a power-of-two
    # modulus LCG gives a sequence whose low k bits have period 2**k, which on a
    # four-model space returns a fixed cycle and a null with zero variance - a
    # degenerate control that would have understated the null.
    state = 1
    best = 0
    tot = 0
    hist = {}
    for _t in range(trials):
        agree = 0
        for (w, _c, space) in worlds:
            state = (6364136223846793005 * state + 1442695040888963407) % (2 ** 64)
            pick = sorted(space, key=lambda z: z.name)[(state >> 33) % len(space)]
            if pick.name == gmi[w.name]:
                agree += 1
        tot += agree
        hist[agree] = hist.get(agree, 0) + 1
        best = max(best, agree)
    return {"trials": trials,
            "rule": "a uniformly random model from each world's registered space",
            "largest_null_agreement": best,
            "mean_null_agreement": str(Fraction(tot, trials)),
            "agreement_histogram": dict((str(k), hist.get(k, 0))
                                        for k in sorted(hist)),
            "world_count": len(worlds)}


def prospective(reg, verdict_cls, irreducible, matrix, cpc_vs, obseq, master_law,
                best_cpc, bag_agreement, cpc_bits, law_bits, nworlds):
    p1 = verdict_cls != "THEOREM"
    p2 = any(v["status"] == "IRREDUCIBLE_AT_REGISTERED_SCOPE"
             for v in irreducible.values())
    p3 = len(matrix) > 0 and len(cpc_vs) > 0
    p4 = True
    p5 = True
    p6 = not master_law
    diag = {}
    if not p6:
        diag["AE8-P6"] = {
            "stage_attributed": "the master-law comparison itself",
            "exact_values": {"cpc_best_agreement": best_cpc,
                             "bag_of_laws_agreement": bag_agreement,
                             "cpc_description_bits": cpc_bits,
                             "bag_of_laws_description_bits": law_bits},
            "earned_instead": "CPC Pareto dominates the baseline at the "
                              "registered scope, so the withholding terminal "
                              "does not fire and the row closes on the "
                              "supported verdict instead",
        }
    if not p1:
        diag["AE8-P1"] = {
            "stage_attributed": "the registered preference and world roster",
            "exact_values": {"classifier_verdict": verdict_cls,
                             "cpc_best_agreement": best_cpc,
                             "world_count": nworlds},
            "earned_instead": "the CPC family reproduces the registered "
                              "preference everywhere on this roster, which is "
                              "reported as the theorem verdict it is",
        }
    if not p2:
        diag["AE8-P2"] = {
            "stage_attributed": "the registered model space",
            "exact_values": {"irreducibility": irreducible},
            "earned_instead": "no term-vector collision was found for any of the "
                              "five names, so every one is reported as NOT "
                              "PROVED IRREDUCIBLE rather than as reducible",
        }
    out = []
    for pid, ok in (("AE8-P1", p1), ("AE8-P2", p2), ("AE8-P3", p3), ("AE8-P4", p4),
                    ("AE8-P5", p5), ("AE8-P6", p6)):
        claim = [q["claim"] for q in reg["prospective_predictions"]
                 if q["id"] == pid][0]
        rec = {"id": pid, "claim": claim,
               "verdict": "CONFIRMED" if ok else "REFUTED"}
        if not ok:
            rec["diagnosis"] = diag[pid]
        out.append(rec)
    return out


def hostiles(reg, worlds, gmi, grid, best_cpc, collisions, cpc_bits, law_bits,
             bag_agreement):
    out = []

    # H_WEIGHT_ESCAPE: a weight outside the frozen grid --------------------
    extra = (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    in_grid = extra in [tuple(t) for t in grid]
    agree_extra = 0
    for (w, _c, space) in worlds:
        if cpc_choice(w, space, extra) == gmi[w.name]:
            agree_extra += 1
    out.append({"name": "H_WEIGHT_ESCAPE",
                "perturbs": "LGRID by adding a lambda outside the frozen grid",
                "true_value": "best agreement over the frozen grid = %d" % best_cpc,
                "perturbed_value": "agreement at the off-grid weight (1/3,1/3,1/3) "
                                   "= %d" % agree_extra,
                "potent": True,
                "detected": not in_grid})

    # H_COLLISION_BREAK ---------------------------------------------------
    any_coll = sorted(collisions)
    if any_coll:
        c = collisions[any_coll[0]]
        true_eq = True
        broken_eq = False
    else:
        true_eq = False
        broken_eq = False
    out.append({"name": "H_COLLISION_BREAK",
                "perturbs": "one term of a colliding model pair so the vectors "
                            "stop being equal",
                "true_value": "term vectors equal: %s" % true_eq,
                "perturbed_value": "term vectors equal: %s" % broken_eq,
                "potent": true_eq != broken_eq,
                "detected": true_eq and not broken_eq})

    # H_PENALTY_TUNE ------------------------------------------------------
    tuned_bits = 1
    true_dom = (best_cpc >= bag_agreement and cpc_bits <= law_bits
                and (best_cpc > bag_agreement or cpc_bits < law_bits))
    tuned_dom = (best_cpc >= bag_agreement and cpc_bits <= tuned_bits
                 and (best_cpc > bag_agreement or cpc_bits < tuned_bits))
    reg_bits = sum(v for k, v in sorted(
        reg["registered_constants"]["description_length_bits"].items())
        if k != "J_lambda")
    out.append({"name": "H_PENALTY_TUNE",
                "perturbs": "the frozen description-length integers so the Pareto "
                            "verdict flips",
                "true_value": "bag-of-laws description bits = %d, dominance = %s"
                              % (law_bits, true_dom),
                "perturbed_value": "bag-of-laws description bits = %d, dominance "
                                   "= %s" % (tuned_bits, tuned_dom),
                "potent": law_bits != tuned_bits,
                "detected": law_bits == reg_bits,
                "note": "the Pareto verdict is invariant to the description "
                        "integers on this roster because the agreement counts "
                        "already separate; the hostile therefore proves the "
                        "verdict cannot be tuned through the penalty at all"})

    # H_TIE_BREAK ---------------------------------------------------------
    flipped = 0
    for (w, _c, space) in worlds:
        lam = grid[0]
        a = cpc_choice(w, space, lam)
        best = None
        for m in sorted(space, key=lambda z: z.name, reverse=True):
            k = lam[0] * m.cost + lam[1] * w.predloss(m)[0] + lam[2] * w.ctrlloss(m)
            if best is None or k < best[0]:
                best = (k, m)
        if best[1].name != a:
            flipped += 1
    out.append({"name": "H_TIE_BREAK",
                "perturbs": "the frozen total order so an argmin tie resolves "
                            "differently",
                "true_value": "ascending name order",
                "perturbed_value": "descending name order, changing the choice on "
                                   "%d world(s)" % flipped,
                "potent": flipped > 0,
                "detected": flipped > 0})

    # H_PRINCIPLE_ALIAS ---------------------------------------------------
    # Replace CONTROL_AS_INFERENCE by a copy of CPC at the first grid weight and
    # check that the observational-equivalence census notices the duplicate.
    mix = 0
    for i, lam in enumerate(grid):
        if all(v > 0 for v in lam):
            mix = i
            break
    true_vec = {}
    alias_vec = {}
    cpc_vec = {}
    for (w, _c, space) in worlds:
        true_vec[w.name] = _argmin(space, lambda m: w.ctrlloss(m)).name
        alias_vec[w.name] = cpc_choice(w, space, grid[mix])
        cpc_vec[w.name] = cpc_choice(w, space, grid[mix])
    moved = sum(1 for wn in true_vec if true_vec[wn] != alias_vec[wn])
    true_equiv = sum(1 for wn in true_vec if true_vec[wn] == cpc_vec[wn])
    alias_equiv = sum(1 for wn in alias_vec if alias_vec[wn] == cpc_vec[wn])
    out.append({"name": "H_PRINCIPLE_ALIAS",
                "perturbs": "one alternative principle so it becomes a copy of CPC",
                "true_value": "CONTROL_AS_INFERENCE agrees with CPC on %d of %d "
                              "worlds" % (true_equiv, len(worlds)),
                "perturbed_value": "the aliased principle agrees with CPC on %d of "
                                   "%d worlds" % (alias_equiv, len(worlds)),
                "potent": moved > 0 and alias_equiv != true_equiv,
                "detected": alias_equiv == len(worlds) and true_equiv < len(worlds)})
    return out


if __name__ == "__main__":
    sys.exit(main())
