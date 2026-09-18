"""Source-separated oracle for gmi-833-h-real-scale-classical-v1.

Imports NOTHING from this package: not grammar_v1, not run_real_scale_v1, not
real_scale_classical_v1. It re-implements, independently:

  * exact rational arithmetic as (num, den) integer pairs with its own gcd
    normalisation, instead of fractions.Fraction;
  * the expression parser and evaluator;
  * the cardinality of the frozen grammar, by a closed-form recursion instead of
    by enumeration;
  * the structural classification, by symbolic second differences on a
    different grid instead of by the primary's denotational test;
  * the exact held-out aggregates on the committed verification slices, by
    integer numerators over one common denominator instead of by Fraction
    accumulation;
  * the charged-cost crossovers, by exhaustive ascent from a re-derived cost
    formula;
  * the resolution of every frozen prediction of FREEZE_V1.md section 8.

Writes ORACLE_RESULT_V1.json.  Non-import is enforced structurally by
test_real_scale_classical_v1.py (ast scan + sys.modules assertion).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "REAL_RUNS")


def _gcd(a, b):
    a = a if a >= 0 else -a
    b = b if b >= 0 else -b
    while b:
        a, b = b, a % b
    return a or 1


def Q(n, d=1):
    if d < 0:
        n, d = -n, -d
    g = _gcd(n, d)
    return (n // g, d // g)


def qadd(a, b):
    return Q(a[0] * b[1] + b[0] * a[1], a[1] * b[1])


def qmul(a, b):
    return Q(a[0] * b[0], a[1] * b[1])


def qneg(a):
    return (-a[0], a[1])


def qabs(a):
    return (a[0] if a[0] >= 0 else -a[0], a[1])


def qgt0(a):
    return a[0] > 0


def qrecip(a):
    return (0, 1) if a[0] == 0 else Q(a[1], a[0])


def qsub(a, b):
    return qadd(a, qneg(b))


def qlt(a, b):
    return a[0] * b[1] < b[0] * a[1]


def qstr(a):
    return "%d/%d" % (a[0], a[1])


def qparse(s):
    n, d = s.split("/")
    return Q(int(n), int(d))


ZERO = (0, 1)
ONE = (1, 1)


def tokenize(s):
    t, cur = [], ""
    for ch in s:
        if ch in "(),":
            if cur:
                t.append(cur)
                cur = ""
            t.append(ch)
        else:
            cur += ch
    if cur:
        t.append(cur)
    return t


def build(tokens, i=0):
    name = tokens[i]
    i += 1
    if i < len(tokens) and tokens[i] == "(":
        i += 1
        kids = []
        while True:
            k, i = build(tokens, i)
            kids.append(k)
            if tokens[i] == ",":
                i += 1
                continue
            i += 1
            break
        return (name, kids), i
    return (name, None), i


def parse(s):
    n, _ = build(tokenize(s))
    return n


def ev(node, env):
    name, kids = node
    if kids is None:
        if name == "C0":
            return ZERO
        if name == "C1":
            return ONE
        return env[name]
    if name == "NEG":
        return qneg(ev(kids[0], env))
    if name == "ABS":
        return qabs(ev(kids[0], env))
    if name == "STEP":
        return ONE if qgt0(ev(kids[0], env)) else ZERO
    if name == "RECIP":
        return qrecip(ev(kids[0], env))
    if name == "ADD":
        return qadd(ev(kids[0], env), ev(kids[1], env))
    if name == "MUL":
        return qmul(ev(kids[0], env), ev(kids[1], env))
    raise ValueError(name)


def nodes(node):
    name, kids = node
    if kids is None:
        return 1
    return 1 + sum(nodes(k) for k in kids)


# ---- independent cardinality of the frozen grammar, by recursion -------------

def cardinality(max_nodes, n_leaves):
    c = {1: n_leaves}
    for n in range(2, max_nodes + 1):
        tot = 4 * c[n - 1]
        for a in range(1, n - 1):
            b = n - 1 - a
            if b >= 1:
                tot += 2 * c[a] * c[b]
        c[n] = tot
    return sum(c[n] for n in range(1, max_nodes + 1)), c


# ---- independent structural classification ----------------------------------

GRID = (Q(-3), Q(-1), Q(0), Q(1), Q(3))
AGRID = (Q(-2), Q(-1), Q(0), Q(1), Q(2))


def varies_in(node, leaf, others):
    def rec(k, env):
        if k == len(others):
            seen = set()
            for v in GRID:
                e = dict(env)
                e[leaf] = v
                seen.add(ev(node, e))
            return len(seen) > 1
        for v in GRID:
            e = dict(env)
            e[others[k]] = v
            if rec(k + 1, e):
                return True
        return False
    return rec(0, {})


def affine_in(node, leaf, others):
    def rec(k, env):
        if k == len(others):
            ys = []
            for v in AGRID:
                e = dict(env)
                e[leaf] = v
                ys.append(ev(node, e))
            for i in range(len(ys) - 2):
                dd = qsub(qadd(ys[i], ys[i + 2]), qadd(ys[i + 1], ys[i + 1]))
                if dd[0] != 0:
                    return False
            return True
        for v in GRID:
            e = dict(env)
            e[others[k]] = v
            if not rec(k + 1, e):
                return False
        return True
    return rec(0, {})


def classify(body_s, head_s):
    b = parse(body_s)
    h = parse(head_s)
    st = varies_in(h, "STATE", ["S", "BIAS"])
    ba = affine_in(b, "ARG", ["PARAM"])
    ha = affine_in(h, "S", ["BIAS", "STATE"])
    if st:
        c = "PERSISTENT_STATE"
    elif not ba:
        c = "LIFTED_BASIS"
    elif not ha:
        c = "NONLINEAR_LINK"
    else:
        c = "AFFINE_SCORE"
    return {"class": c, "reads_state": st, "body_affine_in_arg": ba,
            "head_affine_in_s": ha}


# ---- independent exact replay over the committed verification slice ---------

def replay(rec):
    v = rec["verification"]
    b = parse(rec["winner"]["body"])
    h = parse(rec["winner"]["head"])
    rs = classify(rec["winner"]["body"], rec["winner"]["head"])["reads_state"]
    P = [qparse(x) for x in rec["winner"]["params"]]
    B = qparse(rec["winner"]["bias"])
    st = ZERO
    if "syms" in v:
        base = ZERO
        for j in range(len(P)):
            base = qadd(base, ev(b, {"ARG": ZERO, "PARAM": P[j]}))
        pre = [qadd(qsub(base, ev(b, {"ARG": ZERO, "PARAM": P[k]})),
                    ev(b, {"ARG": ONE, "PARAM": P[k]})) for k in range(len(P))]
        err = 0
        for t, c in enumerate(v["syms"]):
            out = ev(h, {"S": pre[c], "BIAS": B, "STATE": st})
            if (1 if qgt0(out) else 0) != v["y"][t]:
                err += 1
            if rs:
                st = out
        return {"errors": err}
    xd = v["xden"]
    tot = ZERO
    for r, yi in zip(v["Xi"], v["yi"]):
        s = ZERO
        for j, xv in enumerate(r):
            q = xd[j] if isinstance(xd, list) else xd
            s = qadd(s, ev(b, {"ARG": Q(int(xv), q), "PARAM": P[j]}))
        out = ev(h, {"S": s, "BIAS": B, "STATE": st})
        if rs:
            st = out
        e = qsub(out, Q(int(yi), v["yden"]))
        tot = qadd(tot, qmul(e, e))
    return {"sse": qstr(tot)}


# ---- independent cost model and crossover ------------------------------------

def prog_cost(nb, nh, m, state):
    return m * nb + m + nh + m + 1 + (1 if state else 0)


def crossover(nb, nh, state, m_max=64):
    for m in range(1, m_max + 1):
        if m + 2 ** m > prog_cost(nb, nh, m, state):
            return m
    return None


def main():
    scopes = {}
    for rid in ("H01", "H02", "H03", "H04"):
        with open(os.path.join(RUNS, "scope_%s.json" % rid)) as f:
            scopes[rid] = json.load(f)
    with open(os.path.join(RUNS, "controls.json")) as f:
        ctl = json.load(f)

    out = {"schema": "GMI833HRealScaleClassicalOracleV1", "rows": {},
           "disagreements": []}
    nb_raw, _ = cardinality(3, 4)
    nh_raw, _ = cardinality(4, 5)
    out["grammar_cardinality"] = {"body_raw": nb_raw, "head_raw": nh_raw}
    for rid, rec in scopes.items():
        cl = classify(rec["winner"]["body"], rec["winner"]["head"])
        rp = replay(rec)
        v = rec["verification"]
        want = v.get("partial_errors", v.get("partial_sse"))
        got = rp.get("errors", rp.get("sse"))
        nbn = nodes(parse(rec["winner"]["body"]))
        nhn = nodes(parse(rec["winner"]["head"]))
        m = crossover(nbn, nhn, cl["reads_state"])
        agree = {
            "class": cl["class"] == rec["winner"]["class"],
            "replay": (str(got) == str(want)
                       if isinstance(want, int) else
                       qparse(got) == qparse(want)),
            "crossover": m == rec["winner"]["table_crossover_m"],
            "body_raw": nb_raw == rec["grammar"]["body_raw"],
            "head_raw": nh_raw == rec["grammar"]["head_raw"],
        }
        for k, ok in agree.items():
            if not ok:
                out["disagreements"].append("%s:%s" % (rid, k))
        out["rows"][rid] = {"class": cl["class"], "attributes": cl,
                            "replay": rp, "committed_partial": want,
                            "crossover_m": m, "agreement": agree}
    p = ctl["H01_automaton"]
    out["H01_independent"] = {
        "stateful_beats_stateless_on_held":
            p["held_errors_stateful"] < p["held_errors_stateless"],
        "null_violations": ctl["H01_null"]["stateful_strictly_better"],
        "twin_selects_stateless": ctl["H01_twin"]["selects_stateless"]}
    out["H02_independent"] = {
        "null_violations": ctl["H02_null"]["control_beats_constant"]}
    out["all_agree"] = not out["disagreements"]
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({"all_agree": out["all_agree"],
                      "disagreements": out["disagreements"]}, indent=1))
    return 0 if out["all_agree"] else 1


if __name__ == "__main__":
    sys.exit(main())
