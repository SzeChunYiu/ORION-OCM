"""Route B for gmi-833-h-revival-v1: a source-separated oracle.

This file imports NOTHING from grammar_s_v1, grammar_h_v1, ecologies_v1,
search_engine_v1, certify_v1, run_real_scale_v1, successor_revival_v1 or
revival_v1. It re-implements, from FREEZE_V1.md alone, every part whose
result is claimed, by materially different means:

  * expressions are enumerated as reverse-polish token sequences with arity
    bookkeeping and then parsed, rather than assembled by recursive node tiers;
  * expressions are evaluated by a recursive interpreter over a dictionary
    environment, rather than by compiled positional closures;
  * the ascending-cost search filters candidates on the LAST search row, where
    route A filters on the rarest response and on the first row;
  * every ecology response is recomputed in closed form with a different
    accumulation shape;
  * the logarithm is bracketed by an inverse-hyperbolic-tangent series in
    exact rational interval arithmetic, where route A uses the decimal
    module's correctly rounded logarithm. Two independent bracketings of the
    same logarithm must intersect.

Non-import is enforced structurally by test_revival_v1.py via an `ast` scan
and a `sys.modules` assertion, not by this comment.

    python3 -I -B  independent_oracle_v1.py
"""
from fractions import Fraction as F
import itertools
import json
import os
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.join(WHERE, "REAL_RUNS")
DERIV = os.path.join(WHERE, "DERIVATION_RUNS")

REAL_KEYS = ("V02", "V03")
EXPECT_SIGMA = {"V02": "SIGMA_V02", "V03": "SIGMA_V03"}
DERIV_SCOPES = ("SIGMA_E17", "SIGMA_E20", "SIGMA_E22", "SIGMA_E32", "SIGMA_E34")
GRID = (F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2))
LINE = (F(-2), F(-1), F(0), F(1), F(2))
RAT_DEN = 10 ** 9


def fetch(folder, fname):
    full = os.path.join(folder, fname)
    if not os.path.isfile(full):
        raise SystemExit("MISSING ARTIFACT: " + full)
    with open(full) as handle:
        return json.load(handle)


# ------------------------------------------------- expression semantics -----

def read_expr(text, at=0):
    stop = at
    while stop < len(text) and (text[stop].isalnum() or text[stop] == "_"):
        stop += 1
    tag = text[at:stop]
    if stop < len(text) and text[stop] == "(":
        kids = []
        cursor = stop + 1
        while True:
            kid, cursor = read_expr(text, cursor)
            kids.append(kid)
            if text[cursor] == ",":
                cursor += 1
                continue
            cursor += 1
            break
        return (tag, tuple(kids)), cursor
    return (tag, None), stop


def parse(text):
    tree, _ = read_expr(text, 0)
    return tree


def count_nodes(tree):
    tag, kids = tree
    if kids is None:
        return 1
    return 1 + sum(count_nodes(k) for k in kids)


CONSTANTS = {"C0": F(0), "C1": F(1)}


def evaluate(tree, binding):
    tag, kids = tree
    if kids is None:
        if tag in CONSTANTS:
            return CONSTANTS[tag]
        return binding[tag]
    if tag == "NEG":
        return F(0) - evaluate(kids[0], binding)
    if tag == "ABS":
        got = evaluate(kids[0], binding)
        return got if got >= 0 else F(0) - got
    if tag == "STEP":
        return F(1) if evaluate(kids[0], binding) > 0 else F(0)
    if tag == "RECIP":
        got = evaluate(kids[0], binding)
        return F(0) if got == 0 else F(1) / got
    if tag == "ADD":
        return evaluate(kids[0], binding) + evaluate(kids[1], binding)
    if tag == "MUL":
        return evaluate(kids[0], binding) * evaluate(kids[1], binding)
    raise ValueError("operation outside the frozen grammar: " + tag)


def float_eval(tree, binding):
    tag, kids = tree
    if kids is None:
        if tag == "C0":
            return 0.0
        if tag == "C1":
            return 1.0
        return binding[tag]
    if tag == "NEG":
        return -float_eval(kids[0], binding)
    if tag == "ABS":
        return abs(float_eval(kids[0], binding))
    if tag == "STEP":
        return 1.0 if float_eval(kids[0], binding) > 0.0 else 0.0
    if tag == "RECIP":
        got = float_eval(kids[0], binding)
        return 0.0 if got == 0.0 else 1.0 / got
    if tag == "ADD":
        return float_eval(kids[0], binding) + float_eval(kids[1], binding)
    if tag == "MUL":
        return float_eval(kids[0], binding) * float_eval(kids[1], binding)
    raise ValueError(tag)


_LV = {}


def leaves_of(t):
    hit = _LV.get(t)
    if hit is not None:
        return hit
    if t[1] is None:
        hit = set([t[0]])
    else:
        hit = set()
        for k in t[1]:
            hit = hit | leaves_of(k)
    _LV[t] = hit
    return hit


def _assignments(names):
    for combo in itertools.product(GRID, repeat=len(names)):
        yield dict(zip(names, combo))


def varies_with(tree, moving, universe):
    if moving not in leaves_of(tree):
        return False
    others = sorted((leaves_of(tree) & set(universe)) - set([moving]) - set(CONSTANTS))
    for base in _assignments(others):
        got = set()
        for v in GRID:
            base[moving] = v
            got.add(evaluate(tree, base))
        if len(got) > 1:
            return True
    return False


def straight_in(tree, moving, universe):
    if moving not in leaves_of(tree):
        return True
    others = sorted((leaves_of(tree) & set(universe)) - set([moving]) - set(CONSTANTS))
    for base in _assignments(others):
        seq = []
        for v in LINE:
            base[moving] = v
            seq.append(evaluate(tree, base))
        for k in range(len(seq) - 2):
            if seq[k] - seq[k + 1] - seq[k + 1] + seq[k + 2] != 0:
                return False
    return True


def gs_class(body_text, head_text):
    """FREEZE_V1.md section 6.1 priority, re-implemented independently."""
    body = parse(body_text)
    head = parse(head_text)
    if varies_with(head, "STATE", ["S", "BIAS", "STATE"]):
        return "PERSISTENT_STATE"
    if not straight_in(body, "ARG", ["ARG", "PARAM"]):
        return "LIFTED_BASIS"
    if not straight_in(head, "S", ["S", "BIAS", "STATE"]):
        return "NONLINEAR_LINK"
    return "AFFINE_SCORE"


# ------------------------------------------- certified logarithm, route B ---
# ln(x) via 2*atanh((x-1)/(x+1)) in exact rational interval arithmetic with an
# explicit geometric tail bound. No decimal module, no float.

SCALE = 2 ** 192
TERMS = 64


def _snap(lo, hi):
    """Widen an interval outward to denominator SCALE, bounding the growth of
    the rationals without ever losing containment."""
    lo_n = (F(lo) * SCALE).numerator // (F(lo) * SCALE).denominator
    hi_f = F(hi) * SCALE
    hi_n = -((-hi_f.numerator) // hi_f.denominator)
    return F(lo_n, SCALE), F(hi_n, SCALE)


def _atanh_interval(z):
    """[lo, hi] containing atanh(z) for exact rational 0 <= z < 1/3."""
    z = F(z)
    if z < 0 or z >= F(1, 2):
        raise ValueError("series is registered for 0 <= z < 1/2")
    lo = F(0)
    hi = F(0)
    p = z                       # z^(2i+1)
    zz = z * z
    for i in range(TERMS):
        term = p / (2 * i + 1)
        lo += term
        hi += term
        lo, hi = _snap(lo, hi)
        p = p * zz
    # tail: sum_{i>=TERMS} z^(2i+1)/(2i+1) <= p / (1 - z^2)
    tail = p / (1 - zz) if zz < 1 else F(1)
    return _snap(lo, hi + tail)


_LN2 = None


def ln2_interval():
    global _LN2
    if _LN2 is None:
        a_lo, a_hi = _atanh_interval(F(1, 3))
        _LN2 = (2 * a_lo, 2 * a_hi)
    return _LN2


def ln_interval(x):
    """[lo, hi] containing ln(x) for exact rational x > 0."""
    x = F(x)
    if x <= 0:
        raise ValueError("ln_interval needs x > 0")
    k = 0
    while x >= 2:
        x = x / 2
        k += 1
    while x < 1:
        x = x * 2
        k -= 1
    z = (x - 1) / (x + 1)
    a_lo, a_hi = _atanh_interval(z)
    l2_lo, l2_hi = ln2_interval()
    if k >= 0:
        lo = k * l2_lo + 2 * a_lo
        hi = k * l2_hi + 2 * a_hi
    else:
        lo = k * l2_hi + 2 * a_lo
        hi = k * l2_lo + 2 * a_hi
    return lo, hi


def deviance_difference(ys, mu_a, mu_b):
    """D(mu_a) - D(mu_b) as a rational interval, route B's own bracketing."""
    bad_a = any(F(m) <= 0 for m in mu_a)
    bad_b = any(F(m) <= 0 for m in mu_b)
    if bad_a and bad_b:
        return {"status": "BOTH_INADMISSIBLE"}
    if bad_a:
        return {"status": "DECIDED", "sign": +1, "reason": "A_INADMISSIBLE"}
    if bad_b:
        return {"status": "DECIDED", "sign": -1, "reason": "B_INADMISSIBLE"}
    lo = F(0)
    hi = F(0)
    lin = F(0)
    for y, a, b in zip(ys, mu_a, mu_b):
        y = F(y)
        a = F(a)
        b = F(b)
        lin += a - b
        if y == 0:
            continue
        la_lo, la_hi = ln_interval(a)
        lb_lo, lb_hi = ln_interval(b)
        lo += y * (lb_lo - la_hi)
        hi += y * (lb_hi - la_lo)
    lo = 2 * (lo + lin)
    hi = 2 * (hi + lin)
    if hi < 0:
        return {"status": "DECIDED", "sign": -1, "lo": str(lo), "hi": str(hi)}
    if lo > 0:
        return {"status": "DECIDED", "sign": +1, "lo": str(lo), "hi": str(hi)}
    return {"status": "UNDECIDED", "sign": 0, "lo": str(lo), "hi": str(hi)}


def nonpositive(mu):
    return sum(1 for m in mu if F(m) <= 0)


# --------------------------------------------------------- exact replay -----

def replay_real(rec):
    body = parse(rec["chosen"]["body"])
    head = parse(rec["chosen"]["head"])
    stateful = bool(rec["chosen"]["attributes"]["reads_state"])
    params = [F(v) for v in rec["chosen"]["params"]]
    bias = F(rec["chosen"]["bias"])
    xden = rec["xden"]
    yden = rec["yden"]
    block = rec["replay"]
    preds = []
    carried = F(0)
    for raw in block["X"]:
        fold = F(0)
        for j, cell in enumerate(raw):
            fold = fold + evaluate(body, {"ARG": F(int(cell), xden[j]),
                                          "PARAM": params[j]})
        got = evaluate(head, {"S": fold, "BIAS": bias, "STATE": carried})
        if stateful:
            carried = got
        preds.append(got)
    ys = [F(int(v), yden) for v in block["y"]]
    return preds, ys


def replay_squared(rec):
    preds, ys = replay_real(rec)
    total = F(0)
    wrong = 0
    for got, want in zip(preds, ys):
        gap = got - want
        total = total + gap * gap
        if (1 if got > 0 else 0) != (1 if want > 0 else 0):
            wrong += 1
    return total, wrong


# --------------------------------------------- independent survivor rank ----

def solve_normal(A, rhs):
    """Gaussian elimination with partial pivoting, written here."""
    n = len(rhs)
    M = [row[:] + [rhs[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-14:
            return None
        M[col], M[piv] = M[piv], M[col]
        inv = 1.0 / M[col][col]
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col] * inv
            if factor == 0.0:
                continue
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def fold_values(body, rows, params):
    out = []
    for raw in rows:
        acc = 0.0
        for j, cell in enumerate(raw):
            acc += float_eval(body, {"ARG": cell, "PARAM": params[j]})
        out.append(acc)
    return out


def head_values(head, folds, bias, stateful):
    out = []
    carried = 0.0
    for fold in folds:
        got = float_eval(head, {"S": fold, "BIAS": bias, "STATE": carried})
        if stateful:
            carried = got
        out.append(got)
    return out


def squared(pred, ys):
    total = 0.0
    for a, b in zip(pred, ys):
        total += (a - b) * (a - b)
    return total


def deviance(pred, ys):
    import math
    total = 0.0
    for m, y in zip(pred, ys):
        if not (m > 0.0) or m != m:
            return float("inf")
        if y > 0:
            total += y * math.log(y / m)
        total -= (y - m)
    return 2.0 * total


def fit_and_score(body_text, head_text, stateful, rows, ys, d, kind,
                  score_rows, score_ys):
    body = parse(body_text)
    head = parse(head_text)

    def predict(rws, params, bias):
        return head_values(head, fold_values(body, rws, params), bias, stateful)

    def loss(pred, yy):
        return squared(pred, yy) if kind == "squared" else deviance(pred, yy)

    zero = [0.0] * d
    base = predict(rows, zero, 0.0)
    cols = []
    for j in range(d):
        p = [0.0] * d
        p[j] = 1.0
        cols.append([a - b for a, b in zip(predict(rows, p, 0.0), base)])
    cols.append([a - b for a, b in zip(predict(rows, zero, 1.0), base)])
    probe = [1.0 if (j % 3) == 0 else -1.0 for j in range(d + 1)]
    got = predict(rows, probe[:d], probe[d])
    want = [base[i] + sum(cols[j][i] * probe[j] for j in range(d + 1))
            for i in range(len(rows))]
    jointly_affine = all(abs(a - b) <= 1e-7 * (1.0 + abs(a))
                         for a, b in zip(got, want))
    params = [0.0] * d
    bias = 0.0
    if jointly_affine and kind == "squared":
        A = [[sum(cols[a][i] * cols[b][i] for i in range(len(rows)))
              + (1e-8 if a == b else 0.0) for b in range(d + 1)]
             for a in range(d + 1)]
        rhs = [sum(cols[a][i] * (ys[i] - base[i]) for i in range(len(rows)))
               for a in range(d + 1)]
        sol = solve_normal(A, rhs)
        if sol is None:
            return None
        params, bias = sol[:d], sol[d]
    else:
        starts = [[0.0] * (d + 1)]
        if jointly_affine:
            A = [[sum(cols[a][i] * cols[b][i] for i in range(len(rows)))
                  + (1e-8 if a == b else 0.0) for b in range(d + 1)]
                 for a in range(d + 1)]
            rhs = [sum(cols[a][i] * (ys[i] - base[i]) for i in range(len(rows)))
                   for a in range(d + 1)]
            sol = solve_normal(A, rhs)
            if sol is not None:
                starts.append(list(sol))
        best = None
        for s in starts:
            v = loss(predict(rows, s[:d], s[d]), ys)
            if v == v and v != float("inf") and (best is None or v < best[1]):
                best = (s, v)
        if best is None:
            return None
        theta = list(best[0])
        cur = best[1]
        step = 1.0
        for _ in range(60):
            improved = False
            for j in range(d + 1):
                for sgn in (1.0, -1.0):
                    trial = list(theta)
                    trial[j] += sgn * step
                    v = loss(predict(rows, trial[:d], trial[d]), ys)
                    if v == v and v < cur - 1e-12:
                        theta = trial
                        cur = v
                        improved = True
            if not improved:
                step *= 0.5
                if step < 1e-6:
                    break
        params, bias = theta[:d], theta[d]
    sc = loss(predict(score_rows, params, bias), score_ys)
    return sc


def rerank(rec):
    block = rec["search_sample"]
    xden = block["xden"]
    yden = block["yden"]
    d = block["d"]
    kind = block["loss"]
    rows = [[float(cell) / float(xden[j]) for j, cell in enumerate(raw)]
            for raw in block["X"]]
    ys = [float(v) / float(yden) for v in block["y"]]
    srows = [[float(cell) / float(xden[j]) for j, cell in enumerate(raw)]
             for raw in block["Xs"]]
    sys_ = [float(v) / float(yden) for v in block["ys"]]
    table = []
    for entry in block["survivors"]:
        stateful = varies_with(parse(entry["head"]), "STATE", ["S", "BIAS", "STATE"])
        sc = fit_and_score(entry["body"], entry["head"], stateful, rows, ys, d,
                           kind, srows, sys_)
        if sc is None or sc != sc:
            continue
        bad = 0 if sc != float("inf") else 1
        q = int(round(sc * RAT_DEN)) if sc != float("inf") else 0
        table.append((bad, q, count_nodes(parse(entry["body"]))
                      + count_nodes(parse(entry["head"])),
                      entry["body"], entry["head"]))
    table.sort()
    return table


# -------------------------------------------------- derivational grammar ----

UN = ("NEG", "ABS", "STEP", "RECIP")
BI = ("ADD", "MUL")
BODY_L = ("ARG", "PARAM", "C0", "C1")
BODY2_L = ("U", "PARAM2", "C0", "C1")
HEAD_L = ("S1", "S2", "BIAS", "STATE", "RESP", "C0", "C1")
GSHEAD_L = ("S1", "BIAS", "STATE", "C0", "C1")
NIDX = 12
WST = 4
MODULI = (1, 2, 3, 4, 6, 12)
YSET = (F(-6), F(-4), F(0), F(4), F(6))
IDENT = {"ADD": F(0), "MUL": F(1)}
BMAX = 10
CHANNEL_SEED = 20260919
CANDIDATE_SEED = 20260921


def rpn_sequences(n, leaves):
    out = []
    seq = [None] * n

    def walk(pos, depth):
        if pos == n:
            if depth == 1:
                out.append(tuple(seq))
            return
        left = n - pos - 1
        for lf in leaves:
            if depth + 1 - left <= 1:
                seq[pos] = ("L", lf)
                walk(pos + 1, depth + 1)
        if depth >= 1:
            for op in UN:
                if depth - left <= 1:
                    seq[pos] = ("U", op)
                    walk(pos + 1, depth)
        if depth >= 2:
            for op in BI:
                if depth - 1 - left <= 1:
                    seq[pos] = ("B", op)
                    walk(pos + 1, depth - 1)
        seq[pos] = None

    walk(0, 0)
    return out


def rpn_to_tree(seq):
    st = []
    for kind, name in seq:
        if kind == "L":
            st.append((name, None))
        elif kind == "U":
            st.append((name, (st.pop(),)))
        else:
            b = st.pop()
            a = st.pop()
            st.append((name, (a, b)))
    return st[0]


def expressions(budget, leaves):
    out = []
    for n in range(1, budget + 1):
        for seq in rpn_sequences(n, leaves):
            out.append(rpn_to_tree(seq))
    return out


def render_expr(t):
    tag, kids = t
    if kids is None:
        return tag
    if len(kids) == 1:
        return "%s(%s)" % (tag, render_expr(kids[0]))
    return "%s(%s,%s)" % (tag, render_expr(kids[0]), render_expr(kids[1]))


def mul_bank_head_read(flags, hsig, b2sig):
    ops = flags["ops"]
    if flags["L"] == 2:
        stage1 = bool(b2sig is not None and b2sig["dep_U"] and hsig["dep_S1"])
        stage2 = bool(hsig["dep_S1"])
        return ((ops[0] == "MUL" and stage1) or (ops[1] == "MUL" and stage2))
    reads = (hsig["dep_S1"], hsig["dep_S2"])
    for k in range(flags["r"]):
        if ops[k] == "MUL" and reads[k]:
            return True
    return False


def gh_class(flags, hsig, bsig, b2sig):
    """FREEZE_V1.md section 6.2, written from that text."""
    if flags["kind"] != "NONE" and hsig["dep_RESP"]:
        return "RESPONSE_SPACE_SEARCH"
    if mul_bank_head_read(flags, hsig, b2sig):
        return "MULTIPLICATIVE_ACCUMULATION"
    if flags["r"] == 2 and hsig["dep_S1"] and hsig["dep_S2"]:
        if (not hsig["aff_S1"]) or (not hsig["aff_S2"]):
            return "NORMALISED_RATIO"
        return "COUPLED_FOLDS"
    if flags["L"] == 2:
        if b2sig is not None and not b2sig["aff_U"]:
            return "LAYERED_NONLINEAR"
        return "LAYERED_AFFINE"
    if flags["p"] != NIDX:
        return "TIED_PARAMETER"
    if hsig["dep_STATE"]:
        return "PERSISTENT_STATE"
    if bsig is not None and not bsig["aff_ARG"]:
        return "LIFTED_BASIS"
    if not hsig["aff_S1"]:
        return "NONLINEAR_LINK"
    return "AFFINE_SCORE"


def head_sig(t):
    u = ["S1", "S2", "BIAS", "STATE", "RESP"]
    return {"dep_S1": varies_with(t, "S1", u), "dep_S2": varies_with(t, "S2", u),
            "dep_STATE": varies_with(t, "STATE", u),
            "dep_RESP": varies_with(t, "RESP", u),
            "aff_S1": straight_in(t, "S1", u), "aff_S2": straight_in(t, "S2", u)}


def body_sig(t):
    return {"aff_ARG": straight_in(t, "ARG", ["ARG", "PARAM"])}


def body2_sig(t):
    return {"aff_U": straight_in(t, "U", ["U", "PARAM2"]),
            "dep_U": varies_with(t, "U", ["U", "PARAM2"])}


def charged(flags, bodies, body2, head):
    total = sum(count_nodes(b) for b in bodies)
    if flags["L"] == 2:
        total += count_nodes(body2)
    total += count_nodes(head)
    total += 1 if flags["r"] == 2 else 0
    total += 1 if flags["L"] == 2 else 0
    total += 1 if flags["p"] != NIDX else 0
    total += 1 if flags["kind"] != "NONE" else 0
    return total


def render_program(flags, bodies, body2, head):
    return ";".join([
        "r=%d" % flags["r"], "L=%d" % flags["L"], "p=%d" % flags["p"],
        "kind=" + flags["kind"], "ops=" + "+".join(flags["ops"]),
        "bodies=" + "|".join(render_expr(b) for b in bodies),
        "body2=" + (render_expr(body2) if body2 is not None else "-"),
        "head=" + render_expr(head)])


# ---------------------------------------------- derivational ecologies ------

class Rng(object):
    def __init__(self, seed):
        self.s = seed

    def __call__(self):
        self.s = (1103515245 * self.s + 12345) % (2 ** 31)
        return self.s


def draw(g, scope):
    if scope == "SIGMA_E34":
        a = tuple(F(g() % 3 - 1) for _ in range(NIDX))
        p = tuple(F(g() % 3 - 1) for _ in range(NIDX))
    else:
        a = tuple(F(g() % 11) for _ in range(NIDX))
        raw = [g() % 21 - 10 for _ in range(NIDX)]
        p = tuple(F(x) if x != 0 else F(1) for x in raw)
    m = tuple(tuple(F(g() % 7 - 3) for _ in range(WST)) for _ in range(NIDX))
    q = tuple(F(g() % 7 - 3) for _ in range(WST))
    return {"A": a, "P": p, "M": m, "Q": q}


PIN_S = ((1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0), (1,) * 12)
PIN_H = ((1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), (-1, -1) + (1,) * 10)


def make_rows(scope, seed, count, pin=None):
    g = Rng(seed)
    rows = []
    rebuilds = 0
    for idx in range(count):
        r = draw(g, scope)
        if scope == "SIGMA_E17":
            while sum(r["A"]) == 0:
                rebuilds += 1
                r = draw(g, scope)
        if scope == "SIGMA_E34" and pin is not None and idx == 0:
            r = dict(r)
            r["A"] = tuple(F(x) for x in pin[0])
            r["P"] = tuple(F(x) for x in pin[1])
        rows.append(r)
    return rows, rebuilds


def quantise(score):
    pairs = sorted((abs(score + y), y) for y in YSET)
    best = pairs[0][0]
    return min(y for e, y in pairs if e == best)


def target(scope, row):
    """Closed form, accumulated in a different shape from route A."""
    A, P, M, Qc = row["A"], row["P"], row["M"], row["Q"]
    if scope == "SIGMA_E17":
        num = sum((A[i] * P[i] for i in range(NIDX)), F(0))
        den = sum(A, F(0))
        return num / den
    if scope == "SIGMA_E20":
        tot = F(0)
        for j in range(WST):
            u = sum((A[i] * M[i][j] for i in range(NIDX)), F(0))
            tot += (F(1) if u > 0 else F(0)) * Qc[j]
        return tot
    if scope == "SIGMA_E22":
        return sum((A[i] * P[i % 3] for i in range(NIDX)), F(0))
    if scope == "SIGMA_E32":
        prod = F(1)
        for v in P:
            prod *= v
        return prod * sum(A, F(0))
    if scope == "SIGMA_E34":
        return quantise(sum((A[i] * P[i] for i in range(NIDX)), F(0)))
    raise ValueError(scope)


def control(scope, row):
    A, P, M, Qc = row["A"], row["P"], row["M"], row["Q"]
    if scope == "SIGMA_E17":
        return sum((A[i] * P[i] for i in range(NIDX)), F(0))
    if scope == "SIGMA_E20":
        tot = F(0)
        for j in range(WST):
            u = sum((A[i] * M[i][j] for i in range(NIDX)), F(0))
            tot += u * Qc[j]
        return tot
    if scope == "SIGMA_E22":
        return sum((A[i] * P[i] for i in range(NIDX)), F(0))
    if scope == "SIGMA_E32":
        return sum(P, F(0)) * sum(A, F(0))
    if scope == "SIGMA_E34":
        return F(0) - sum((A[i] * P[i] for i in range(NIDX)), F(0))
    raise ValueError(scope)


def slices():
    search = tuple(i for i in range(48) if i % 4 in (0, 1))
    regen = tuple(i for i in range(48) if i % 4 == 3)
    return search, regen


# ------------------------------------------------------ derivational run ----

def fold1(body, op, p, row):
    acc = IDENT[op]
    A, P = row["A"], row["P"]
    for i in range(NIDX):
        v = evaluate(body, {"ARG": A[i], "PARAM": P[i % p]})
        acc = acc + v if op == "ADD" else acc * v
    return acc


def fold2(body1, op1, p, body2, op2, row):
    A, M, Qc = row["A"], row["M"], row["Q"]
    acc2 = IDENT[op2]
    for j in range(WST):
        acc = IDENT[op1]
        for i in range(NIDX):
            v = evaluate(body1, {"ARG": A[i], "PARAM": M[i % p][j]})
            acc = acc + v if op1 == "ADD" else acc * v
        u = evaluate(body2, {"U": acc, "PARAM2": Qc[j]})
        acc2 = acc2 + u if op2 == "ADD" else acc2 * u
    return acc2


def emit(head, s1, s2, bias, state, kind):
    if kind == "NONE":
        return evaluate(head, {"S1": s1, "S2": s2, "BIAS": bias,
                               "STATE": state, "RESP": F(0)})
    if kind == "RSUM":
        return sum((evaluate(head, {"S1": s1, "S2": s2, "BIAS": bias,
                                    "STATE": state, "RESP": y}) for y in YSET), F(0))
    best = None
    best_e = None
    for y in YSET:
        e = evaluate(head, {"S1": s1, "S2": s2, "BIAS": bias,
                            "STATE": state, "RESP": y})
        if best_e is None or e < best_e:
            best_e = e
            best = y
    return best


def output_of(prog, row, state):
    flags, bodies, body2, head = prog
    if flags["L"] == 2:
        s1 = fold2(bodies[0], flags["ops"][0], flags["p"], body2,
                   flags["ops"][1], row)
        s2 = F(0)
    else:
        s1 = fold1(bodies[0], flags["ops"][0], flags["p"], row)
        s2 = (fold1(bodies[1], flags["ops"][1], flags["p"], row)
              if flags["r"] == 2 else F(0))
    return emit(head, s1, s2, row["Q"][0], state, flags["kind"])


def matches(prog, rows, ys, idxs):
    state = F(0)
    for t in idxs:
        out = output_of(prog, rows[t], state)
        if out != ys[t]:
            return False
        state = out
    return True


def configs():
    out = []
    for L in (1, 2):
        for r in ((1, 2) if L == 1 else (1,)):
            nops = r if L == 1 else 2
            ops_list = ([("ADD",), ("MUL",)] if nops == 1
                        else [(a, b) for a in BI for b in BI])
            for ops in ops_list:
                for p in MODULI:
                    for kind in ("NONE", "ARGMIN", "RSUM"):
                        ch = ((1 if r == 2 else 0) + (1 if L == 2 else 0)
                              + (1 if p != NIDX else 0) + (1 if kind != "NONE" else 0))
                        out.append({"r": r, "L": L, "ops": ops, "p": p,
                                    "kind": kind, "charge": ch})
    return out


def canonical_ok(flags, bodies, body2, head, hsig, b2sig):
    if flags["r"] == 2 and not hsig["dep_S2"]:
        return False
    if flags["L"] == 2 and not hsig["dep_S1"]:
        return False
    if flags["p"] != NIDX:
        if not any("PARAM" in leaves_of(b) for b in bodies):
            return False
    if flags["kind"] != "NONE" and not hsig["dep_RESP"]:
        return False
    return True


def ascending_search(rows, ys, idxs, max_cost, gs_only=False, stop_at_first=True):
    """Route B's own ascending-cost search. Filters on the LAST search row."""
    bodies = expressions(3, BODY_L)
    bodies2 = expressions(4, BODY2_L)
    heads = expressions(4, HEAD_L if not gs_only else GSHEAD_L)
    hsigs = dict((render_expr(h), head_sig(h)) for h in heads)
    bsigs = dict((render_expr(b), body_sig(b)) for b in bodies)
    b2sigs = dict((render_expr(b), body2_sig(b)) for b in bodies2)
    cfgs = configs()
    if gs_only:
        cfgs = [c for c in cfgs if c["r"] == 1 and c["L"] == 1
                and c["p"] == NIDX and c["kind"] == "NONE" and c["ops"] == ("ADD",)]
    last = idxs[-1]
    found = []
    for cost in range(1, max_cost + 1):
        for cfg in cfgs:
            budget = cost - cfg["charge"]
            if budget < 2:
                continue
            flags = {"r": cfg["r"], "L": cfg["L"], "p": cfg["p"],
                     "kind": cfg["kind"], "ops": cfg["ops"]}
            for head in heads:
                nh = count_nodes(head)
                if nh > budget - 1:
                    continue
                hs = hsigs[render_expr(head)]
                rest = budget - nh
                if flags["L"] == 2:
                    for b1 in bodies:
                        n1 = count_nodes(b1)
                        for b2 in bodies2:
                            if n1 + count_nodes(b2) != rest:
                                continue
                            b2s = b2sigs[render_expr(b2)]
                            if not canonical_ok(flags, [b1], b2, head, hs, b2s):
                                continue
                            prog = (flags, [b1], b2, head)
                            if output_of(prog, rows[last], F(0)) != ys[last] and not hs["dep_STATE"]:
                                continue
                            if matches(prog, rows, ys, idxs):
                                found.append((prog, cost))
                elif flags["r"] == 1:
                    for b1 in bodies:
                        if count_nodes(b1) != rest:
                            continue
                        if not canonical_ok(flags, [b1], None, head, hs, None):
                            continue
                        prog = (flags, [b1], None, head)
                        if output_of(prog, rows[last], F(0)) != ys[last] and not hs["dep_STATE"]:
                            continue
                        if matches(prog, rows, ys, idxs):
                            found.append((prog, cost))
                else:
                    for b1 in bodies:
                        n1 = count_nodes(b1)
                        for b2 in bodies:
                            if n1 + count_nodes(b2) != rest:
                                continue
                            if not canonical_ok(flags, [b1, b2], None, head, hs, None):
                                continue
                            prog = (flags, [b1, b2], None, head)
                            if output_of(prog, rows[last], F(0)) != ys[last] and not hs["dep_STATE"]:
                                continue
                            if matches(prog, rows, ys, idxs):
                                found.append((prog, cost))
        if found and stop_at_first:
            break
    if not found:
        return None, None, []
    rendered = sorted((render_program(*p[0]), p[0], p[1]) for p in found)
    return rendered[0][1], rendered[0][2], rendered


def describe_prog(prog, cost):
    flags, bodies, body2, head = prog
    hs = head_sig(head)
    bs = body_sig(bodies[0])
    b2s = body2_sig(body2) if body2 is not None else None
    return {"render": render_program(flags, bodies, body2, head),
            "class": gh_class(flags, hs, bs, b2s), "cost": cost,
            "flags": {"r": flags["r"], "L": flags["L"], "p": flags["p"],
                      "kind": flags["kind"], "ops": list(flags["ops"])},
            "mul_bank_head_read": mul_bank_head_read(flags, hs, b2s)}


def parse_render(text):
    """Rebuild a program from its rendering (route A's committed pool)."""
    parts = dict()
    for chunk in text.split(";"):
        k, v = chunk.split("=", 1)
        parts[k] = v
    flags = {"r": int(parts["r"]), "L": int(parts["L"]), "p": int(parts["p"]),
             "kind": parts["kind"], "ops": tuple(parts["ops"].split("+"))}
    bodies = [parse(b) for b in parts["bodies"].split("|")]
    body2 = None if parts["body2"] == "-" else parse(parts["body2"])
    head = parse(parts["head"])
    return (flags, bodies, body2, head)


def construct_heldout(pool, cand_rows, target_n=12, forced_first=None):
    states = [F(0)] * len(pool)
    chosen = []
    n_dis = 0
    examined = 0
    for k, row in enumerate(cand_rows):
        if len(chosen) >= target_n:
            break
        examined += 1
        outs = [output_of(p, row, states[i]) for i, p in enumerate(pool)]
        distinct = len(set(outs)) > 1
        if distinct:
            n_dis += 1
        if distinct or (forced_first is not None and k == forced_first):
            chosen.append(k)
            states = outs
    return chosen, n_dis, examined


# ------------------------------------------------------------------ main ----

def main():
    out = {"schema": "GMI833HRevivalOracleV1", "route": "B",
           "imports_primary_executor": False}

    # ---- real-scale scopes
    real = {}
    for key in REAL_KEYS:
        rec = fetch(REAL, "scope_%s.json" % key)
        klass = gs_class(rec["chosen"]["body"], rec["chosen"]["head"])
        class_ok = (klass == rec["chosen"]["class"])
        entry = {"class_rederived": klass, "class_matches": bool(class_ok),
                 "sigma_matches": bool(rec["sigma"] == EXPECT_SIGMA[key]),
                 "real_scale_thresholds_met": bool(rec["n_fit"] >= 100000
                                                   and rec["n_held"] >= 20000)}
        if key == "V02":
            sse, errs = replay_squared(rec)
            entry["exact_replay_sse_matches"] = bool(sse == F(rec["replay"]["partial_sse"]))
            entry["exact_replay_decisions_match"] = bool(errs == rec["replay"]["partial_decision_errors"])
            entry["recomputed_partial_sse"] = str(sse)
            entry["recomputed_partial_decision_errors"] = errs
            replay_ok = entry["exact_replay_sse_matches"] and entry["exact_replay_decisions_match"]
        else:
            preds, ys = replay_real(rec)
            arms = rec["arms"]["replay"]
            mu_const = [F(arms["mu_intercept_only"])] * len(preds)
            mu_log = [F(v) for v in arms["mu_log"]]
            mu_id = [F(v) for v in arms["mu_identity"]]
            entry["mu_chosen_matches"] = bool([str(v) for v in preds] == rec["replay"]["mu_chosen"])
            entry["chosen_nonpositive"] = nonpositive(preds)
            entry["identity_nonpositive"] = nonpositive(mu_id)
            d1 = deviance_difference(ys, preds, mu_const)
            d2 = deviance_difference(ys, preds, mu_log)
            entry["chosen_minus_intercept_only"] = d1
            entry["chosen_minus_log_link"] = d2
            a1 = arms["partial_chosen_minus_intercept_only"]
            a2 = arms["partial_chosen_minus_log_link"]
            same1 = (d1["status"] == a1["status"] and d1.get("sign") == a1.get("sign"))
            same2 = (d2["status"] == a2["status"] and d2.get("sign") == a2.get("sign"))
            # the two independent bracketings must also intersect
            def intersects(x, y):
                if "lo" not in x or "lo" not in y:
                    return True
                return not (F(x["hi"]) < F(y["lo"]) or F(y["hi"]) < F(x["lo"]))
            entry["brackets_intersect"] = bool(intersects(d1, a1) and intersects(d2, a2))
            entry["certified_signs_agree"] = bool(same1 and same2)
            entry["nonpositive_counts_agree"] = bool(
                entry["chosen_nonpositive"] == arms["partial_chosen_nonpositive_means"]
                and entry["identity_nonpositive"] == arms["partial_identity_nonpositive_means"])
            replay_ok = (entry["mu_chosen_matches"] and entry["certified_signs_agree"]
                         and entry["brackets_intersect"] and entry["nonpositive_counts_agree"])
        table = rerank(rec)
        want = rec["search_sample"]["primary_ranking_on_this_block"]
        top_ok = bool(table and want and table[0][3] == want[0]["body"]
                      and table[0][4] == want[0]["head"])
        entry["independent_top1"] = list(table[0][3:]) if table else None
        entry["primary_top1_on_this_block"] = [want[0]["body"], want[0]["head"]] if want else None
        entry["independent_top1_matches"] = top_ok
        entry["survivors_reranked"] = len(table)
        entry["block_rows"] = rec["search_sample"]["rows"]
        m_star = rec["crossover"]["m_star"]
        cross_ok = True
        if m_star is not None:
            nb = count_nodes(parse(rec["chosen"]["body"]))
            nh = count_nodes(parse(rec["chosen"]["head"]))
            st = 1 if rec["chosen"]["attributes"]["reads_state"] else 0

            def prog_cost(m):
                return m * nb + m + nh + m + 1 + st
            cross_ok = (m_star + 2 ** m_star > prog_cost(m_star)
                        and (m_star == 1 or (m_star - 1) + 2 ** (m_star - 1) <= prog_cost(m_star - 1)))
        entry["crossover_arithmetic_ok"] = bool(cross_ok)
        entry["agrees"] = bool(class_ok and replay_ok and top_ok and cross_ok
                               and entry["sigma_matches"]
                               and entry["real_scale_thresholds_met"])
        real[key] = entry
        print("[%s] class=%s replay=%s top1=%s agrees=%s"
              % (key, klass, replay_ok, top_ok, entry["agrees"]), flush=True)
    out["real_scopes"] = real

    # ---- derivational scopes
    dev = fetch(DERIV, "derivational.json")
    search_idx, regen_idx = slices()
    deriv = {}
    for scope in DERIV_SCOPES:
        rec = dev["scopes"][scope]
        rows, rebuilds = make_rows(scope, CHANNEL_SEED, 48, pin=PIN_S)
        ys = tuple(target(scope, r) for r in rows)
        prog, cost, cheapest = ascending_search(rows, ys, search_idx, BMAX)
        d = describe_prog(prog, cost) if prog is not None else None
        gsprog, gscost, _ = ascending_search(rows, ys, search_idx, BMAX, gs_only=True)
        crows, _ = make_rows(scope, CANDIDATE_SEED, 480, pin=PIN_H)
        pool = [parse_render(m["render"]) for m in rec["pool"]["members"]]
        pool_matches = all(matches(p, rows, ys, search_idx) for p in pool)
        forced = 0 if scope == "SIGMA_E34" else None
        chosen, n_dis, examined = construct_heldout(pool, crows, 12, forced)
        ctl_rows = rows
        ctl_ys = tuple(control(scope, r) for r in ctl_rows)
        cprog, ccost, _ = ascending_search(ctl_rows, ctl_ys, search_idx, BMAX)
        cd = describe_prog(cprog, ccost) if cprog is not None else None
        rprog, rcost, _ = ascending_search(rows, ys, regen_idx, BMAX)
        rd = describe_prog(rprog, rcost) if rprog is not None else None
        ra = rec["recovered"]
        entry = {
            "recovered": d, "gs_match_found": gsprog is not None,
            "render_matches": bool(d is not None and d["render"] == ra["render"]),
            "cost_matches": bool(d is not None and d["cost"] == ra["cost"]),
            "class_matches": bool(d is not None and d["class"] == ra["class"]),
            "pool_size": len(pool),
            "every_pool_member_matches_the_search_slice": bool(pool_matches),
            "heldout_rows_rederived": [int(k) for k in chosen],
            "heldout_disagreement_rows": n_dis,
            "heldout_candidates_examined": examined,
            "heldout_matches_primary": bool(
                [int(k) for k in chosen] == list(rec["R08_heldout"]["constructed_rows"])
                and n_dis == rec["R08_heldout"]["disagreement_rows_found"]),
            "control": cd,
            "control_matches": bool(cd is not None and rec["R05_control"].get("recovered")
                                    and cd["render"] == rec["R05_control"]["recovered"]["render"]),
            "regeneration": rd,
            "regeneration_matches": bool(rd is not None and rec["R09_regeneration"].get("recovered")
                                         and rd["class"] == rec["R09_regeneration"]["recovered"]["class"]),
            "ecology_rebuilds": rebuilds,
        }
        entry["agrees"] = bool(entry["render_matches"] and entry["cost_matches"]
                               and entry["class_matches"] and not entry["gs_match_found"]
                               and entry["every_pool_member_matches_the_search_slice"]
                               and entry["heldout_matches_primary"]
                               and entry["control_matches"] and entry["regeneration_matches"])
        deriv[scope] = entry
        print("[%s] class=%s cost=%s pool=%d heldout=%s agrees=%s"
              % (scope, d and d["class"], cost, len(pool), chosen, entry["agrees"]), flush=True)
    out["deriv_scopes"] = deriv
    out["ln_bracket_method"] = ("2*atanh((x-1)/(x+1)) in exact rational interval "
                                "arithmetic with a geometric tail bound; no decimal "
                                "module and no float")
    bad = ([k for k in REAL_KEYS if not real[k]["agrees"]]
           + [s for s in DERIV_SCOPES if not deriv[s]["agrees"]])
    out["all_agree"] = not bad
    with open(os.path.join(WHERE, "ORACLE_RESULT_V1.json"), "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True, default=str)
        handle.write("\n")
    print("route B agreement: %s" % ("every scope" if not bad else "DISAGREES on " + ",".join(bad)))


if __name__ == "__main__":
    main()
