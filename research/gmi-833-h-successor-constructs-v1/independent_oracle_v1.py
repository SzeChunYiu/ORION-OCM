"""Route B: source-separated oracle for gmi-833-h-successor-constructs-v1.

Written from FREEZE_V1.md and FREEZE_V1_ADDENDUM.md only. It imports nothing
from route A. Every part is built by a materially different scheme:

  * expressions are enumerated as reverse-polish token sequences with arity
    bookkeeping, then parsed, rather than assembled by recursive node tiers;
  * expressions are evaluated by a recursive interpreter over a dictionary
    environment, rather than by compiled positional closures;
  * every ecology response is recomputed in closed form with a different
    accumulation shape;
  * programs are materialised as a sorted (cost, rendering) list, rather than
    visited in a stratified ascending-cost loop.

Run:  python3 -I -B independent_oracle_v1.py
"""
from fractions import Fraction as F
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

UN = ("NEG", "ABS", "STEP", "RECIP")
BI = ("ADD", "MUL")
BODY_L = ("ARG", "PARAM", "C0", "C1")
BODY2_L = ("U", "PARAM2", "C0", "C1")
HEAD_L = ("S1", "S2", "BIAS", "STATE", "RESP", "C0", "C1")
GSHEAD_L = ("S1", "BIAS", "STATE", "C0", "C1")
CONST = {"C0": F(0), "C1": F(1)}
NIDX = 12
WST = 4
MODULI = (1, 2, 3, 4, 6, 12)
YSET = (F(-6), F(-4), F(0), F(4), F(6))
IDENT = {"ADD": F(0), "MUL": F(1)}
BMAX = 10
SCOPES = ("SIGMA_D17", "SIGMA_D20", "SIGMA_D22", "SIGMA_D32", "SIGMA_D34")


# ------------------------------------------------- reverse-polish enumeration

def rpn_sequences(n, leaves):
    """All valid reverse-polish token sequences of exactly n tokens."""
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
            st.append(("LEAF", name))
        elif kind == "U":
            st.append((name, st.pop()))
        else:
            b = st.pop()
            a = st.pop()
            st.append((name, a, b))
    return st[0]


def expressions(budget, leaves):
    out = []
    for n in range(1, budget + 1):
        for seq in rpn_sequences(n, leaves):
            out.append(rpn_to_tree(seq))
    return out


def render_expr(t):
    if t[0] == "LEAF":
        return t[1]
    if len(t) == 2:
        return "%s(%s)" % (t[0], render_expr(t[1]))
    return "%s(%s,%s)" % (t[0], render_expr(t[1]), render_expr(t[2]))


def size(t):
    if t[0] == "LEAF":
        return 1
    return 1 + sum(size(k) for k in t[1:])


_LV = {}


def leaves_of(t):
    hit = _LV.get(t)
    if hit is not None:
        return hit
    if t[0] == "LEAF":
        hit = set([t[1]])
    else:
        hit = set()
        for k in t[1:]:
            hit = hit | leaves_of(k)
    _LV[t] = hit
    return hit


def ev(t, env):
    tag = t[0]
    if tag == "LEAF":
        nm = t[1]
        return CONST[nm] if nm in CONST else env[nm]
    if tag == "NEG":
        return -ev(t[1], env)
    if tag == "ABS":
        x = ev(t[1], env)
        return -x if x < 0 else x
    if tag == "STEP":
        return F(1) if ev(t[1], env) > 0 else F(0)
    if tag == "RECIP":
        x = ev(t[1], env)
        return F(0) if x == 0 else F(1) / x
    if tag == "ADD":
        return ev(t[1], env) + ev(t[2], env)
    if tag == "MUL":
        return ev(t[1], env) * ev(t[2], env)
    raise ValueError(tag)


PROBE = (F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(2))
AGRID = (F(-2), F(-1), F(0), F(1), F(2))


def _assignments(names):
    if not names:
        yield {}
        return
    head = names[0]
    for rest in _assignments(names[1:]):
        for v in PROBE:
            d = dict(rest)
            d[head] = v
            yield d


def moves_with(t, leaf):
    if leaf not in leaves_of(t):
        return False
    others = sorted(leaves_of(t) - set([leaf]) - set(CONST))
    for base in _assignments(others):
        vals = set()
        for v in PROBE:
            e = dict(base)
            e[leaf] = v
            vals.add(ev(t, e))
        if len(vals) > 1:
            return True
    return False


def affine_wrt(t, leaf):
    if leaf not in leaves_of(t):
        return True
    others = sorted(leaves_of(t) - set([leaf]) - set(CONST))
    for base in _assignments(others):
        ys = []
        for v in AGRID:
            e = dict(base)
            e[leaf] = v
            ys.append(ev(t, e))
        for i in range(len(ys) - 2):
            if ys[i] - 2 * ys[i + 1] + ys[i + 2] != 0:
                return False
    return True


# ------------------------------------------------------------ ecology (own)

class Rng(object):
    def __init__(self):
        self.s = 20260918

    def __call__(self):
        self.s = (1103515245 * self.s + 12345) % (2 ** 31)
        return self.s


def make_rows(scope):
    g = Rng()
    rows = []
    rebuilds = 0

    def one():
        if scope == "SIGMA_D34":
            a = tuple(F(g() % 3 - 1) for _ in range(NIDX))
            p = tuple(F(g() % 3 - 1) for _ in range(NIDX))
        else:
            a = tuple(F(g() % 11) for _ in range(NIDX))
            raw = [g() % 21 - 10 for _ in range(NIDX)]
            p = tuple(F(x) if x != 0 else F(1) for x in raw)
        m = tuple(tuple(F(g() % 7 - 3) for _ in range(WST))
                  for _ in range(NIDX))
        q = tuple(F(g() % 7 - 3) for _ in range(WST))
        return {"A": a, "P": p, "M": m, "Q": q}

    for idx in range(48):
        r = one()
        if scope == "SIGMA_D17":
            while sum(r["A"]) == 0:
                rebuilds += 1
                r = one()
        if scope == "SIGMA_D34" and idx == 0:
            r = dict(r)
            r["A"] = tuple(F(x) for x in (1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0))
            r["P"] = tuple(F(1) for _ in range(NIDX))
        if scope == "SIGMA_D34" and idx == 2:
            r = dict(r)
            r["A"] = tuple(F(x) for x in (1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            r["P"] = tuple(F(x) for x in
                           (-1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))
        rows.append(r)
    return rows, rebuilds


def quantise(score):
    pairs = sorted((abs(score + y), y) for y in YSET)
    best = pairs[0][0]
    return min(y for e, y in pairs if e == best)


def target(scope, r):
    a, p, m, q = r["A"], r["P"], r["M"], r["Q"]
    if scope == "SIGMA_D17":
        return sum(x * y for x, y in zip(a, p)) / sum(a)
    if scope == "SIGMA_D20":
        us = [sum(a[i] * m[i][j] for i in range(NIDX)) for j in range(WST)]
        return sum((F(1) if u > 0 else F(0)) * q[j]
                   for j, u in enumerate(us))
    if scope == "SIGMA_D22":
        return sum(a[i] * p[i % 3] for i in range(NIDX))
    if scope == "SIGMA_D32":
        pr = F(1)
        for v in p:
            pr = pr * v
        return pr * sum(a)
    if scope == "SIGMA_D34":
        return quantise(sum(x * y for x, y in zip(a, p)))
    raise ValueError(scope)


def twin(scope, r):
    a, p, m, q = r["A"], r["P"], r["M"], r["Q"]
    if scope == "SIGMA_D17":
        return sum(x * y for x, y in zip(a, p))
    if scope == "SIGMA_D20":
        us = [sum(a[i] * m[i][j] for i in range(NIDX)) for j in range(WST)]
        return sum(u * q[j] for j, u in enumerate(us))
    if scope == "SIGMA_D22":
        return sum(x * y for x, y in zip(a, p))
    if scope == "SIGMA_D32":
        return sum(p) * sum(a)
    if scope == "SIGMA_D34":
        return -sum(x * y for x, y in zip(a, p))
    raise ValueError(scope)


def eco(scope, is_twin=False):
    rows, rb = make_rows(scope)
    fn = twin if is_twin else target
    ys = tuple(fn(scope, r) for r in rows)
    idx = list(range(48))
    return {"scope": scope, "rows": rows, "y": ys, "rebuilds": rb,
            "search": tuple(i for i in idx if i % 4 < 2),
            "held": tuple(i for i in idx if i % 4 == 2),
            "regen": tuple(i for i in idx if i % 4 == 3),
            "twin": is_twin}


def eco_digest(e):
    h = hashlib.sha256()
    h.update(e["scope"].encode())
    h.update(b"twin" if e["twin"] else b"target")
    for i, r in enumerate(e["rows"]):
        h.update(("#%d" % i).encode())
        for k in ("A", "P", "Q"):
            h.update((",".join(str(v) for v in r[k])).encode())
        for line in r["M"]:
            h.update((",".join(str(v) for v in line)).encode())
        h.update(str(e["y"][i]).encode())
    return h.hexdigest()


# --------------------------------------------------------------- programs

def program_cost(spec):
    c = sum(size(b) for b in spec["bodies"]) + size(spec["head"])
    if spec["L"] == 2:
        c += size(spec["body2"])
        c += 1
    if spec["r"] == 2:
        c += 1
    if spec["p"] != NIDX:
        c += 1
    if spec["kind"] != "NONE":
        c += 1
    return c


def program_render(spec):
    return ";".join([
        "r=%d" % spec["r"], "L=%d" % spec["L"], "p=%d" % spec["p"],
        "kind=" + spec["kind"], "ops=" + "+".join(spec["ops"]),
        "bodies=" + "|".join(render_expr(b) for b in spec["bodies"]),
        "body2=" + (render_expr(spec["body2"]) if spec["L"] == 2 else "-"),
        "head=" + render_expr(spec["head"])])


def fold1(body, op, p, row):
    acc = IDENT[op]
    for i in range(NIDX):
        v = ev(body, {"ARG": row["A"][i], "PARAM": row["P"][i % p]})
        acc = acc + v if op == "ADD" else acc * v
    return acc


def fold2(body1, op1, p, body2, op2, row):
    acc2 = IDENT[op2]
    for j in range(WST):
        acc = IDENT[op1]
        for i in range(NIDX):
            v = ev(body1, {"ARG": row["A"][i], "PARAM": row["M"][i % p][j]})
            acc = acc + v if op1 == "ADD" else acc * v
        u = ev(body2, {"U": acc, "PARAM2": row["Q"][j]})
        acc2 = acc2 + u if op2 == "ADD" else acc2 * u
    return acc2


def output(spec, row, state):
    if spec["L"] == 2:
        s1 = fold2(spec["bodies"][0], spec["ops"][0], spec["p"],
                   spec["body2"], spec["ops"][1], row)
        s2 = F(0)
    else:
        s1 = fold1(spec["bodies"][0], spec["ops"][0], spec["p"], row)
        s2 = (fold1(spec["bodies"][1], spec["ops"][1], spec["p"], row)
              if spec["r"] == 2 else F(0))
    env = {"S1": s1, "S2": s2, "BIAS": row["Q"][0], "STATE": state,
           "RESP": F(0)}
    if spec["kind"] == "NONE":
        return ev(spec["head"], env)
    if spec["kind"] == "RSUM":
        tot = F(0)
        for y in YSET:
            env["RESP"] = y
            tot = tot + ev(spec["head"], env)
        return tot
    best = None
    beste = None
    for y in YSET:
        env["RESP"] = y
        e = ev(spec["head"], env)
        if beste is None or e < beste:
            beste = e
            best = y
    return best


def matches(spec, e, idxs, order=None):
    """Exact agreement on every row. `order` may permute the rows only for a
    memoryless head, whose verdict cannot depend on the order."""
    if order is not None:
        idxs = order
    state = F(0)
    for t in idxs:
        o = output(spec, e["rows"][t], state)
        if o != e["y"][t]:
            return False
        state = o
    return True


def build_specs(cost, gs_only=False):
    """Every well-formed program of exactly this charged cost, materialised as
    a flat sequence in construction order."""
    bodies = BODY_CACHE
    bodies2 = BODY2_CACHE
    heads = GSHEAD_CACHE if gs_only else HEAD_CACHE
    if gs_only:
        combos = [(1, 1, ("ADD",), NIDX, "NONE")]
    else:
        combos = []
        for L in (1, 2):
            rs = (1, 2) if L == 1 else (1,)
            for r in rs:
                k = r if L == 1 else 2
                oplists = ([("ADD",), ("MUL",)] if k == 1 else
                           [(a, b) for a in ("ADD", "MUL")
                            for b in ("ADD", "MUL")])
                for ops in oplists:
                    for p in MODULI:
                        for kind in ("NONE", "ARGMIN", "RSUM"):
                            combos.append((L, r, ops, p, kind))
    for L, r, ops, p, kind in combos:
        charge = (1 if r == 2 else 0) + (1 if L == 2 else 0) \
            + (1 if p != NIDX else 0) + (1 if kind != "NONE" else 0)
        budget = cost - charge
        if budget < 2:
            continue
        for hd in heads:
            hl = hd["lv"]
            if ("S2" in hl) != (r == 2):
                continue
            if ("RESP" in hl) != (kind != "NONE"):
                continue
            if L == 2 and "S1" not in hl:
                continue
            rest = budget - hd["n"]
            if rest < 1:
                continue
            head = hd["t"]
            if L == 2:
                for b1 in bodies:
                    if p != NIDX and "PARAM" not in b1["lv"]:
                        continue
                    n2 = rest - b1["n"]
                    if n2 < 1:
                        continue
                    for b2 in bodies2:
                        if b2["n"] != n2:
                            continue
                        yield {"r": r, "L": L, "ops": ops, "p": p,
                               "kind": kind, "bodies": [b1["t"]],
                               "body2": b2["t"], "head": head,
                               "bk": [b1["key"]], "b2k": b2["key"],
                               "hk": hd["key"]}
            elif r == 1:
                for b1 in bodies:
                    if b1["n"] != rest:
                        continue
                    if p != NIDX and "PARAM" not in b1["lv"]:
                        continue
                    yield {"r": r, "L": L, "ops": ops, "p": p,
                           "kind": kind, "bodies": [b1["t"]],
                           "body2": None, "head": head,
                           "bk": [b1["key"]], "b2k": None, "hk": hd["key"]}
            else:
                for b1 in bodies:
                    n2 = rest - b1["n"]
                    if n2 < 1:
                        continue
                    for b2 in bodies:
                        if b2["n"] != n2:
                            continue
                        if p != NIDX and not ("PARAM" in b1["lv"]
                                              or "PARAM" in b2["lv"]):
                            continue
                        yield {"r": r, "L": L, "ops": ops, "p": p,
                               "kind": kind, "bodies": [b1["t"], b2["t"]],
                               "body2": None, "head": head,
                               "bk": [b1["key"], b2["key"]], "b2k": None,
                               "hk": hd["key"]}


def find(e, idxs, gs_only=False, bmax=BMAX):
    """Cheapest exact-agreement programs, by ascending charged cost.

    The first row examined is chosen by a rule of this route's own: the slice
    row of largest absolute response, for a memoryless head, and otherwise the
    first slice row, where the delay cell is still zero. Both are exact
    necessary conditions, so the verdict is unaffected.
    """
    ranked = sorted(idxs, key=lambda t: (-abs(e["y"][t]), t))
    probe_row = ranked[0]
    first_row = idxs[0]
    memo1 = {}
    memo2 = {}

    def g1(spec, which, t):
        k = (spec["bk"][which], spec["ops"][which], spec["p"], t)
        v = memo1.get(k)
        if v is None:
            v = fold1(spec["bodies"][which], spec["ops"][which], spec["p"],
                      e["rows"][t])
            memo1[k] = v
        return v

    def g2(spec, t):
        k = (spec["bk"][0], spec["ops"][0], spec["p"], spec["b2k"],
             spec["ops"][1], t)
        v = memo2.get(k)
        if v is None:
            v = fold2(spec["bodies"][0], spec["ops"][0], spec["p"],
                      spec["body2"], spec["ops"][1], e["rows"][t])
            memo2[k] = v
        return v

    for cost in range(2, bmax + 1):
        hit = []
        for sp in build_specs(cost, gs_only):
            stateful = "STATE" in leaves_of(sp["head"])
            t = first_row if stateful else probe_row
            order = None if stateful else ranked
            if sp["L"] == 2:
                s1 = g2(sp, t)
                s2 = F(0)
            else:
                s1 = g1(sp, 0, t)
                s2 = g1(sp, 1, t) if sp["r"] == 2 else F(0)
            env = {"S1": s1, "S2": s2, "BIAS": e["rows"][t]["Q"][0],
                   "STATE": F(0), "RESP": F(0)}
            if sp["kind"] == "NONE":
                o = ev(sp["head"], env)
            elif sp["kind"] == "RSUM":
                o = F(0)
                for y in YSET:
                    env["RESP"] = y
                    o = o + ev(sp["head"], env)
            else:
                o = None
                be = None
                for y in YSET:
                    env["RESP"] = y
                    val = ev(sp["head"], env)
                    if be is None or val < be:
                        be = val
                        o = y
            if o != e["y"][t]:
                continue
            if matches(sp, e, idxs, order):
                hit.append(sp)
        if hit:
            hit.sort(key=program_render)
            return {"cost": cost, "specs": hit, "n": len(hit)}
    return {"cost": None, "specs": [], "n": 0}


def classify(spec):
    hl = leaves_of(spec["head"])
    if spec["kind"] != "NONE" and moves_with(spec["head"], "RESP"):
        return "RESPONSE_SPACE_SEARCH"
    if "MUL" in spec["ops"]:
        return "MULTIPLICATIVE_ACCUMULATION"
    if spec["r"] == 2 and moves_with(spec["head"], "S1") \
            and moves_with(spec["head"], "S2"):
        if not affine_wrt(spec["head"], "S1") \
                or not affine_wrt(spec["head"], "S2"):
            return "NORMALISED_RATIO"
        return "COUPLED_FOLDS"
    if spec["L"] == 2:
        if not affine_wrt(spec["body2"], "U"):
            return "LAYERED_NONLINEAR"
        return "LAYERED_AFFINE"
    if spec["p"] != NIDX:
        return "TIED_PARAMETER"
    if moves_with(spec["head"], "STATE"):
        return "PERSISTENT_STATE"
    if not affine_wrt(spec["bodies"][0], "ARG"):
        return "LIFTED_BASIS"
    if not affine_wrt(spec["head"], "S1"):
        return "NONLINEAR_LINK"
    return "AFFINE_SCORE"


def serve(spec, m, y_size):
    ops = 0
    store = 0
    if spec["L"] == 2:
        ops += m * WST * size(spec["bodies"][0]) + m * WST
        ops += WST * size(spec["body2"]) + WST
        store += (m if spec["p"] == NIDX else spec["p"]) * WST + WST + 1
    else:
        for b in spec["bodies"]:
            ops += m * size(b) + m
        store += (m if spec["p"] == NIDX else spec["p"]) + spec["r"]
    ops += (y_size if spec["kind"] != "NONE" else 1) * size(spec["head"])
    store += 1
    return ops + store


def crossover(spec, y_size, mmax=64):
    for m in range(1, mmax + 1):
        if m + 2 ** m > serve(spec, m, y_size):
            return m
    return None


def _tab(budget, leaves):
    out = []
    for t in expressions(budget, leaves):
        out.append({"t": t, "n": size(t), "lv": leaves_of(t),
                    "key": render_expr(t)})
    return out


BODY_CACHE = _tab(3, BODY_L)
BODY2_CACHE = _tab(4, BODY2_L)
HEAD_CACHE = _tab(4, HEAD_L)
GSHEAD_CACHE = _tab(4, GSHEAD_L)


def main():
    t0 = time.time()
    out = {"schema": "GMI833HSuccessorConstructsOracleV1", "route": "B",
           "package": "gmi-833-h-successor-constructs-v1",
           "enumeration": {"body": len(BODY_CACHE),
                           "body2": len(BODY2_CACHE),
                           "head": len(HEAD_CACHE),
                           "gs_head": len(GSHEAD_CACHE)},
           "scopes": {}}
    for scope in SCOPES:
        e = eco(scope)
        rec = {"ecology_digest": eco_digest(e), "rebuilds": e["rebuilds"]}
        gs = find(e, e["search"], gs_only=True)
        rec["gs_match_found"] = gs["cost"] is not None
        r = find(e, e["search"])
        if r["cost"] is None:
            rec["recovered"] = None
        else:
            sp = r["specs"][0]
            rec["recovered"] = {"render": program_render(sp),
                                "cost": program_cost(sp),
                                "class": classify(sp),
                                "n_matches": r["n"]}
            rec["heldout_pass"] = matches(sp, e, e["held"])
            rec["heldout_search_only"] = sum(
                0 if matches(sp2, e, e["held"]) else 1 for sp2 in r["specs"])
            rec["crossover_m"] = crossover(sp, len(YSET))
            rg = find(e, e["regen"])
            rec["remint"] = (None if rg["cost"] is None else
                             {"render": program_render(rg["specs"][0]),
                              "cost": program_cost(rg["specs"][0]),
                              "class": classify(rg["specs"][0])})
        tw = eco(scope, True)
        tr = find(tw, tw["search"])
        rec["twin"] = (None if tr["cost"] is None else
                       {"render": program_render(tr["specs"][0]),
                        "cost": program_cost(tr["specs"][0]),
                        "class": classify(tr["specs"][0]),
                        "digest": eco_digest(tw)})
        out["scopes"][scope] = rec
        sys.stderr.write("oracle %s done %.1fs\n" % (scope, time.time() - t0))
        sys.stderr.flush()
    out["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
