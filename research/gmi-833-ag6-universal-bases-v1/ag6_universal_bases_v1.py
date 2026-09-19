"""AG6 - three radically different universal low-level bases at one charged frame.

Route A (package executor).  Frozen by FREEZE_V1.md, commit 243ec345, BEFORE this
file existed.  Stdlib only.  Exact integer / Fraction arithmetic throughout; no
float enters any published quantity.

    python3 -I -B research/gmi-833-ag6-universal-bases-v1/ag6_universal_bases_v1.py
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from fractions import Fraction
from itertools import product

sys.setrecursionlimit(200000)
if hasattr(sys, "set_int_max_str_digits"):
    # Python 3.11+ caps int->str conversion; AG6B-6 publishes an exact 7322-digit
    # integer, so the cap is raised rather than the integer being truncated.
    sys.set_int_max_str_digits(20000)

SOURCE_MAIN = "50f833cc4bc3cadcefd44eca14fa58f73f815587"
FREEZE_COMMIT = "243ec345"
CLAIM_CEILING = (
    "GMI_AG6_THREE_UNIVERSAL_BASES_AT_REGISTERED_FINITE_SCOPE_WITH_BASIS_RELATIVE_COST"
)
FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_SIMPLICITER",
    "TURING_UNIVERSALITY_PROVED_HERE",
    "COMBINATORY_BASIS_TURING_UNIVERSAL_PROVED_HERE",
    "CELLULAR_BASIS_TURING_UNIVERSAL_PROVED_HERE",
    "REGISTER_BASIS_TURING_UNIVERSAL_PROVED_HERE",
    "BASIS_INDEPENDENT_DESCRIPTION_SIZE",
    "CROSS_BASIS_COST_UNIT_COMMENSURABLE",
    "PARETO_FRONTIER_INVARIANT_UNDER_ARBITRARY_RESOURCE_NORMALIZATION",
    "SEARCH_BURDEN_BASIS_INDEPENDENT",
    "UNIFORM_ENUMERATION_SEARCH_BURDEN_MEASURED",
    "INTELLIGENCE_FROM_UNIVERSALITY",
    "ALL_COMPUTATIONAL_MODELS_EMBEDDED",
    "MI_LAW_PROVED_BASIS_INVARIANT",
    "UNIQUE_MINIMAL_UNIVERSAL_GRAMMAR",
    "COMPLETE_GMI",
)

# Pinned from the merged parent gmi-833-g0-register-core-v1/RESULT_V1.json.
PARENT_REGISTER_CENSUS = {
    "machines": 256,
    "words_per_machine": 15,
    "comparisons": 3840,
    "behavior_mismatches": 0,
}

# ---------------------------------------------------------------------------
# 1. Registered scope (FREEZE 2.1 - 2.3, 2.8)
# ---------------------------------------------------------------------------

KEYS = ((0, 0), (0, 1), (1, 0), (1, 1))


def all_binary_words(max_len):
    out = []
    for n in range(max_len + 1):
        out.extend(product((0, 1), repeat=n))
    return tuple(out)


WORDS = all_binary_words(3)


def enumerate_machines():
    """MEALY_2x2 in the frozen order: delta table outer, out table inner."""
    machines = []
    for db in product((0, 1), repeat=4):
        for ob in product((0, 1), repeat=4):
            machines.append((dict(zip(KEYS, db)), dict(zip(KEYS, ob))))
    return tuple(machines)


MACHINES = enumerate_machines()


def direct_mealy(delta, out, w):
    q = 0
    res = []
    for a in w:
        res.append(out[(q, a)])
        q = delta[(q, a)]
    return tuple(res)


def behaviour(delta, out):
    return tuple(direct_mealy(delta, out, w) for w in WORDS)


BEHAVIOUR_INDEX = {}
for _i, (_d, _o) in enumerate(MACHINES):
    BEHAVIOUR_INDEX[behaviour(_d, _o)] = _i


def capability(delta, out):
    """Q(m): frozen three-task battery on W, integer in [0, 45]."""
    score = 0
    for w in WORDS:
        got = direct_mealy(delta, out, w)
        if got == tuple(w):
            score += 1
        if got == tuple(1 - a for a in w):
            score += 1
        if got == tuple(0 for _ in w):
            score += 1
    return score


# ---------------------------------------------------------------------------
# 2. Basis REG - register / counter (Minsky 1967; parent g0-register-core-v1)
# ---------------------------------------------------------------------------

REG_OPCODES = ("READ", "INC", "DECJZ", "EMIT", "HALT")
REG_REGISTERS = ("x", "s", "z0", "z1")
REG_START = "P"


def reg_compile(delta, out):
    """(registers, start_label, {label: instruction}) realizing the Mealy machine."""
    prog = {
        "P": ("INC", "z1", "L0"),
        "L0": ("READ", "x", "L1"),
        "L1": ("DECJZ", "x", "L2", "A0"),
        "L2": ("DECJZ", "x", "L3", "A1"),
        "L3": ("HALT",),
        "A0": ("DECJZ", "s", "C10", "C00"),
        "A1": ("DECJZ", "s", "C11", "C01"),
    }
    for q in (0, 1):
        for a in (0, 1):
            c = "C%d%d" % (q, a)
            emit_reg = "z1" if out[(q, a)] == 1 else "z0"
            if delta[(q, a)] == 1:
                d = "D%d%d" % (q, a)
                prog[c] = ("EMIT", emit_reg, d)
                prog[d] = ("INC", "s", "L0")
            else:
                prog[c] = ("EMIT", emit_reg, "L0")
    return (REG_REGISTERS, REG_START, prog)


REG_UNITS = {"READ": 3, "INC": 3, "EMIT": 3, "DECJZ": 4, "HALT": 1}


def reg_size(artifact):
    registers, start, prog = artifact
    n = len(registers) + 1
    for lab in sorted(prog):
        n += REG_UNITS[prog[lab][0]]
    return n


def reg_run(artifact, word, cap):
    registers, start, prog = artifact
    rv = dict((r, 0) for r in registers)
    stream = tuple(word) + (2,)
    pos = 0
    out = []
    label = start
    steps = 0
    while True:
        if label not in prog:
            return None, steps, "BAD_LABEL"
        ins = prog[label]
        op = ins[0]
        if op == "HALT":
            return tuple(out), steps, "HALTED"
        if steps >= cap:
            return None, steps, "CAP"
        steps += 1
        if op == "READ":
            r, nxt = ins[1], ins[2]
            if r not in rv:
                return None, steps, "BAD_REG"
            if pos >= len(stream):
                return None, steps, "INPUT_UNDERFLOW"
            rv[r] = stream[pos]
            pos += 1
            label = nxt
        elif op == "INC":
            r, nxt = ins[1], ins[2]
            if r not in rv:
                return None, steps, "BAD_REG"
            rv[r] += 1
            label = nxt
        elif op == "EMIT":
            r, nxt = ins[1], ins[2]
            if r not in rv:
                return None, steps, "BAD_REG"
            v = rv[r]
            if v not in (0, 1):
                return None, steps, "BAD_EMIT"
            out.append(v)
            label = nxt
        elif op == "DECJZ":
            r, nz, z = ins[1], ins[2], ins[3]
            if r not in rv:
                return None, steps, "BAD_REG"
            if rv[r] == 0:
                label = z
            else:
                rv[r] -= 1
                label = nz
        else:
            return None, steps, "BAD_OP"


def reg_cap(word):
    return 6 * len(word) + 10


def reg_config_trace(artifact, word, cap):
    """Full configuration corridor for the geometry probe."""
    registers, start, prog = artifact
    rv = dict((r, 0) for r in registers)
    stream = tuple(word) + (2,)
    pos = 0
    out = []
    label = start
    trace = [(label, tuple(sorted(rv.items())), pos, tuple(out))]
    steps = 0
    while steps < cap:
        ins = prog.get(label)
        if ins is None or ins[0] == "HALT":
            break
        op = ins[0]
        if op == "READ":
            rv[ins[1]] = stream[pos]
            pos += 1
            label = ins[2]
        elif op == "INC":
            rv[ins[1]] += 1
            label = ins[2]
        elif op == "EMIT":
            out.append(rv[ins[1]])
            label = ins[2]
        elif op == "DECJZ":
            if rv[ins[1]] == 0:
                label = ins[3]
            else:
                rv[ins[1]] -= 1
                label = ins[2]
        steps += 1
        trace.append((label, tuple(sorted(rv.items())), pos, tuple(out)))
    return trace


# ---------------------------------------------------------------------------
# 3. Basis CMB - combinatory / rewrite (Schoenfinkel 1924, Curry 1930)
# ---------------------------------------------------------------------------

def V(n):
    return ("var", n)


def LAM(n, b):
    return ("lam", n, b)


def AP(*ts):
    t = ts[0]
    for u in ts[1:]:
        t = ("app", t, u)
    return t


LT = LAM("x", LAM("y", V("x")))
LF = LAM("x", LAM("y", V("y")))


def lbit(b):
    return LT if b == 1 else LF


def lstate(q):
    return LT if q == 0 else LF


LNIL = LAM("c", LAM("n", V("n")))
LCONS = LAM("h", LAM("t", LAM("c", LAM("n",
          AP(V("c"), V("h"), AP(V("t"), V("c"), V("n")))))))


def machine_lambda(delta, out):
    OUT = LAM("s", LAM("a", AP(V("s"),
              AP(V("a"), lbit(out[(0, 1)]), lbit(out[(0, 0)])),
              AP(V("a"), lbit(out[(1, 1)]), lbit(out[(1, 0)])))))
    NXT = LAM("s", LAM("a", AP(V("s"),
              AP(V("a"), lstate(delta[(0, 1)]), lstate(delta[(0, 0)])),
              AP(V("a"), lstate(delta[(1, 1)]), lstate(delta[(1, 0)])))))
    STEP = LAM("a", LAM("k", LAM("s",
              AP(LCONS, AP(OUT, V("s"), V("a")),
                        AP(V("k"), AP(NXT, V("s"), V("a")))))))
    NILF = LAM("s", LNIL)
    return LAM("w", AP(V("w"), STEP, NILF, lstate(0)))


def word_lambda(w):
    body = V("n")
    for a in reversed(w):
        body = AP(V("c"), lbit(a), body)
    return LAM("c", LAM("n", body))


I_CL = ("@", ("@", "S", "K"), "K")
_FV = {}


def fv(t):
    if isinstance(t, str):
        return frozenset()
    r = _FV.get(t)
    if r is not None:
        return r
    if t[0] == "v":
        r = frozenset((t[1],))
    else:
        r = fv(t[1]) | fv(t[2])
    _FV[t] = r
    return r


def absvar(x, u, optimized):
    """Bracket abstraction into PURE S,K.  optimized=True adds the K-on-applications
    and eta rules (Curry-optimized); optimized=False is the naive translation."""
    if u == ("v", x):
        return I_CL
    if isinstance(u, str) or u[0] == "v":
        return ("@", "K", u)
    if optimized:
        if x not in fv(u):
            return ("@", "K", u)
        if u[2] == ("v", x) and x not in fv(u[1]):
            return u[1]
    return ("@", ("@", "S", absvar(x, u[1], optimized)), absvar(x, u[2], optimized))


def compile_lam(t, optimized):
    k = t[0]
    if k == "var":
        return ("v", t[1])
    if k == "app":
        return ("@", compile_lam(t[1], optimized), compile_lam(t[2], optimized))
    return absvar(t[1], compile_lam(t[2], optimized), optimized)


def to_runtime(t):
    if isinstance(t, str):
        return t
    if t[0] == "v":
        raise ValueError("free variable in closed term")
    return (to_runtime(t[1]), to_runtime(t[2]))


def cmb_size(t):
    if type(t) is not tuple:
        return 1
    stack = [t]
    n = 0
    while stack:
        u = stack.pop()
        n += 1
        if type(u) is tuple:
            stack.append(u[0])
            stack.append(u[1])
    return n


class Cap(Exception):
    pass


def whnf(t, budget):
    steps = 0
    stack = []
    while True:
        while type(t) is tuple:
            stack.append(t[1])
            t = t[0]
        if t == "K" and len(stack) >= 2:
            x = stack.pop()
            stack.pop()
            t = x
            steps += 1
        elif t == "S" and len(stack) >= 3:
            x = stack.pop()
            y = stack.pop()
            z = stack.pop()
            t = ((x, z), (y, z))
            steps += 1
        else:
            break
        if steps > budget:
            raise Cap()
    for a in reversed(stack):
        t = (t, a)
    return t, steps


def nf(t, budget):
    total = 0
    t, s = whnf(t, budget)
    total += s
    if type(t) is tuple:
        f, s1 = nf(t[0], budget - total)
        total += s1
        x, s2 = nf(t[1], budget - total)
        total += s2
        t = (f, x)
    return t, total


SK_T = "K"
SK_F = ("K", (("S", "K"), "K"))
SK_KI = ("K", (("S", "K"), "K"))
PAIRIFY = to_runtime(compile_lam(
    LAM("h", LAM("r", LAM("k", AP(V("k"), V("h"), V("r"))))), True))
NILP = ("K", "S")
CMB_BUDGET = 200000
WORD_CL = dict((w, to_runtime(compile_lam(word_lambda(w), True))) for w in WORDS)


def cmb_run(term, w, budget=CMB_BUDGET):
    """Decoded output bits and total contractions, per the frozen decode procedure."""
    steps = 0
    try:
        p = ((term, WORD_CL[w]), PAIRIFY)
        p = (p, NILP)
        p, s = whnf(p, budget)
        steps += s
        bits = []
        for _ in range(len(w)):
            b, s = nf((p, "K"), budget)
            steps += s
            if b == SK_T:
                bits.append(1)
            elif b == SK_F:
                bits.append(0)
            else:
                return None, steps, "BAD_BIT"
            p, s = whnf((p, SK_KI), budget)
            steps += s
        e, s = nf((p, "K"), budget)
        steps += s
        if e != "S":
            return None, steps, "BAD_END"
        return tuple(bits), steps, "OK"
    except Cap:
        return None, budget, "CAP"
    except RecursionError:
        return None, budget, "DEPTH"


def cmb_compile(delta, out, optimized=True):
    return to_runtime(compile_lam(machine_lambda(delta, out), optimized))


def cmb_redex_positions(t):
    """All redex positions (paths) in t, for the FULL one-step relation."""
    res = []
    stack = [(t, ())]
    while stack:
        u, path = stack.pop()
        if type(u) is tuple:
            spine = []
            head = u
            while type(head) is tuple:
                spine.append(head[1])
                head = head[0]
            nargs = len(spine)
            if (head == "K" and nargs >= 2) or (head == "S" and nargs >= 3):
                res.append(path)
            stack.append((u[0], path + (0,)))
            stack.append((u[1], path + (1,)))
    return res


def cmb_contract_at(t, path):
    if not path:
        spine = []
        head = t
        while type(head) is tuple:
            spine.append(head[1])
            head = head[0]
        spine.reverse()  # application order
        if head == "K":
            new = spine[0]
            rest = spine[2:]
        else:
            x, y, z = spine[0], spine[1], spine[2]
            new = ((x, z), (y, z))
            rest = spine[3:]
        for a in rest:
            new = (new, a)
        return new
    i = path[0]
    if i == 0:
        return (cmb_contract_at(t[0], path[1:]), t[1])
    return (t[0], cmb_contract_at(t[1], path[1:]))


# ---------------------------------------------------------------------------
# 4. Basis CEL - cellular / local (von Neumann 1966, Codd 1968, Smith 1971,
#    Margolus 1984, Cook 2004; Hedlund 1969 for the locality characterization)
# ---------------------------------------------------------------------------

QUIESCENT = ("-", "-", "-")


def cel_rule(delta, out):
    def d(l, c, r):
        ci, co, ch = c
        if ch in ("A", "B"):
            if ci in ("0", "1"):
                q = 0 if ch == "A" else 1
                a = int(ci)
                return ("-", str(out[(q, a)]), "-")
            return (ci, co, "H")
        if ch == "H":
            return c
        li, lo, lh = l
        if lh in ("A", "B") and li in ("0", "1"):
            q = 0 if lh == "A" else 1
            a = int(li)
            return (ci, co, "A" if delta[(q, a)] == 0 else "B")
        return c
    return d


def cel_initial(w):
    n = len(w)
    cells = []
    for i in range(n):
        cells.append((str(w[i]), "-", "A" if i == 0 else "-"))
    cells.append(("-", "-", "A" if n == 0 else "-"))
    return tuple(cells)


def cel_sweep(d, conf):
    n = len(conf)
    new = []
    for i in range(n):
        l = conf[i - 1] if i > 0 else QUIESCENT
        c = conf[i]
        r = conf[i + 1] if i + 1 < n else QUIESCENT
        new.append(d(l, c, r))
    return tuple(new)


def cel_run(d, w, cap=None):
    if cap is None:
        cap = len(w) + 4
    conf = cel_initial(w)
    steps = 0
    while steps < cap:
        if all(cell[2] not in ("A", "B") for cell in conf):
            break
        conf = cel_sweep(d, conf)
        steps += 1
    if any(cell[2] in ("A", "B") for cell in conf):
        return None, steps, "CAP"
    bits = []
    for i in range(len(w)):
        v = conf[i][1]
        if v == "-":
            return None, steps, "MISSING_OUTPUT"
        bits.append(int(v))
    return tuple(bits), steps, "HALTED"


def cel_trace(d, w, cap=None):
    if cap is None:
        cap = len(w) + 4
    conf = cel_initial(w)
    trace = [conf]
    steps = 0
    while steps < cap and any(cell[2] in ("A", "B") for cell in conf):
        conf = cel_sweep(d, conf)
        trace.append(conf)
        steps += 1
    return trace


def cel_alphabet(d):
    """Least alphabet containing every initial cell over W and closed under d."""
    sigma = set([QUIESCENT])
    for w in WORDS:
        sigma.update(cel_initial(w))
    changed = True
    while changed:
        changed = False
        cur = sorted(sigma)
        for l in cur:
            for c in cur:
                for r in cur:
                    v = d(l, c, r)
                    if v not in sigma:
                        sigma.add(v)
                        changed = True
    return tuple(sorted(sigma))


def cel_support(d, sigma):
    sup = []
    for l in sigma:
        for c in sigma:
            for r in sigma:
                v = d(l, c, r)
                if v != c:
                    sup.append(((l, c, r), v))
    return tuple(sup)


def cel_artifact(delta, out):
    d = cel_rule(delta, out)
    sigma = cel_alphabet(d)
    sup = cel_support(d, sigma)
    return {"rule": d, "sigma": sigma, "support": sup,
            "size": len(sigma) + 4 * len(sup)}


def cel_table_rule(table):
    """Rule presented as an explicit exception table over the quiescent default."""

    def d(l, c, r):
        v = table.get((l, c, r))
        if v is not None:
            return v
        return c
    return d


def cel_used_windows(d, w):
    used = set()
    for conf in cel_trace(d, w)[:-1]:
        n = len(conf)
        for i in range(n):
            l = conf[i - 1] if i > 0 else QUIESCENT
            c = conf[i]
            r = conf[i + 1] if i + 1 < n else QUIESCENT
            used.add((l, c, r))
    return used


# ---------------------------------------------------------------------------
# 5. Exact comparison machinery
# ---------------------------------------------------------------------------

def kendall_counts(xs, ys):
    """Exact 5-way breakdown over all unordered pairs."""
    n = len(xs)
    conc = disc = tie_x = tie_y = tie_both = 0
    for i in range(n):
        xi, yi = xs[i], ys[i]
        for j in range(i + 1, n):
            dx = xs[j] - xi
            dy = ys[j] - yi
            if dx == 0 and dy == 0:
                tie_both += 1
            elif dx == 0:
                tie_x += 1
            elif dy == 0:
                tie_y += 1
            elif (dx > 0) == (dy > 0):
                conc += 1
            else:
                disc += 1
    total = n * (n - 1) // 2
    tau_a = Fraction(conc - disc, total)
    untied = conc + disc
    tau_r = Fraction(conc - disc, untied) if untied else None
    return {"pairs": total, "concordant": conc, "discordant": disc,
            "tied_first_only": tie_x, "tied_second_only": tie_y,
            "tied_both": tie_both, "tau_a": tau_a, "tau_restricted": tau_r}


def pareto_frontier(qs, cs):
    """Undominated indices: m' dominates m iff Q'>=Q and C'<=C with one strict."""
    n = len(qs)
    front = []
    for i in range(n):
        dominated = False
        for j in range(n):
            if j == i:
                continue
            if qs[j] >= qs[i] and cs[j] <= cs[i] and (qs[j] > qs[i] or cs[j] < cs[i]):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return tuple(front)


def classify_bound(bound, observed_max, declared_max):
    """FREEZE 6: vacuity is tested against the declared range, not by attainment."""
    if bound >= declared_max:
        return "VACUOUS"
    if bound == observed_max:
        return "ATTAINED"
    if bound > observed_max:
        return "STRICT_UNATTAINED"
    return "VIOLATED"


def frac(x):
    return "%d/%d" % (x.numerator, x.denominator) if x is not None else None


# ---------------------------------------------------------------------------
# 6. The census
# ---------------------------------------------------------------------------

def build_all():
    reg, cmb, cel = [], [], []
    for delta, out in MACHINES:
        reg.append(reg_compile(delta, out))
        cmb.append(cmb_compile(delta, out, True))
        cel.append(cel_artifact(delta, out))
    return reg, cmb, cel


def realization_census(reg_art, cmb_art, cel_art):
    res = {}
    for name in ("REG", "CMB", "CEL"):
        res[name] = {"tasks": 0, "matches": 0, "mismatches": 0, "cap_hits": 0,
                     "steps_total": 0, "steps_max": 0, "machines_realized": 0}
    steps = {"REG": [], "CMB": [], "CEL": []}
    for i, (delta, out) in enumerate(MACHINES):
        ok = {"REG": True, "CMB": True, "CEL": True}
        tot = {"REG": 0, "CMB": 0, "CEL": 0}
        for w in WORDS:
            want = direct_mealy(delta, out, w)
            got, s, term = reg_run(reg_art[i], w, reg_cap(w))
            _acc(res["REG"], got, want, s, term, ok, tot, "REG")
            got, s, term = cmb_run(cmb_art[i], w)
            _acc(res["CMB"], got, want, s, term, ok, tot, "CMB")
            got, s, term = cel_run(cel_art[i]["rule"], w)
            _acc(res["CEL"], got, want, s, term, ok, tot, "CEL")
        for name in ("REG", "CMB", "CEL"):
            steps[name].append(tot[name])
            if ok[name]:
                res[name]["machines_realized"] += 1
    return res, steps


def _acc(bucket, got, want, s, term, ok, tot, name):
    bucket["tasks"] += 1
    bucket["steps_total"] += s
    if s > bucket["steps_max"]:
        bucket["steps_max"] = s
    tot[name] += s
    if term == "CAP":
        bucket["cap_hits"] += 1
    if got == want:
        bucket["matches"] += 1
    else:
        bucket["mismatches"] += 1
        ok[name] = False


# ---------------------------------------------------------------------------
# 7. Costs on the one charged frame (FREEZE 2.6, 2.9)
# ---------------------------------------------------------------------------

def cost_tables(reg_art, cmb_art, cel_art, cmb_naive):
    sizes = {"REG": [], "CMB": [], "CEL": [], "CMB_NAIVE": []}
    steps = {"REG": [], "CMB": [], "CEL": []}
    per_task = {"REG": [], "CMB": [], "CEL": []}
    for i, (delta, out) in enumerate(MACHINES):
        sizes["REG"].append(reg_size(reg_art[i]))
        sizes["CMB"].append(cmb_size(cmb_art[i]))
        sizes["CMB_NAIVE"].append(cmb_size(cmb_naive[i]))
        sizes["CEL"].append(cel_art[i]["size"])
        tot = {"REG": 0, "CMB": 0, "CEL": 0}
        for w in WORDS:
            _g, s, _t = reg_run(reg_art[i], w, reg_cap(w))
            tot["REG"] += s
            per_task["REG"].append((i, w, s))
            _g, s, _t = cmb_run(cmb_art[i], w)
            tot["CMB"] += s
            per_task["CMB"].append((i, w, s))
            _g, s, _t = cel_run(cel_art[i]["rule"], w)
            tot["CEL"] += s
            per_task["CEL"].append((i, w, s))
        for k in steps:
            steps[k].append(tot[k])
    return sizes, steps, per_task


def overhead_report(per_task):
    rep = {}
    declared = {
        "REG": max(Fraction(reg_cap(w), len(w) + 1) for w in WORDS),
        "CMB": Fraction(CMB_BUDGET, 1),
        "CEL": max(Fraction(len(w) + 4, len(w) + 1) for w in WORDS),
    }
    for name, rows in per_task.items():
        best = Fraction(0)
        arg = None
        for (i, w, s) in rows:
            r = Fraction(s, len(w) + 1)
            if r > best:
                best = r
                arg = (i, "".join(str(a) for a in w), s)
        rep[name] = {
            "max_steps_per_semantic_unit": frac(best),
            "argmax": {"machine": arg[0], "word": arg[1], "steps": arg[2]},
            "attained_bound": frac(best),
            "attained_bound_class": classify_bound(best, best, declared[name]),
            "declared_range_max": frac(declared[name]),
            "declared_range_bound_class": classify_bound(
                declared[name], best, declared[name]),
        }
    pairs = {}
    idx = dict((n, dict(((i, w), s) for (i, w, s) in rows))
               for n, rows in per_task.items())
    for a in ("CMB", "CEL"):
        for b in ("REG",):
            worst = Fraction(0)
            arg = None
            for key in idx[a]:
                sb = idx[b][key]
                if sb == 0:
                    continue
                r = Fraction(idx[a][key], sb)
                if r > worst:
                    worst = r
                    arg = (key[0], "".join(str(x) for x in key[1]))
            pairs["%s_over_%s_max" % (a, b)] = frac(worst)
            pairs["%s_over_%s_argmax" % (a, b)] = {"machine": arg[0], "word": arg[1]}
    for a, b in (("CMB", "REG"), ("CMB", "CEL"), ("REG", "CEL")):
        ta = sum(s for (_i, _w, s) in per_task[a])
        tb = sum(s for (_i, _w, s) in per_task[b])
        pairs["%s_over_%s_total" % (a, b)] = frac(Fraction(ta, tb))
    rep["cross_basis"] = pairs
    return rep


def description_bias(sizes, steps):
    rep = {}
    for label, tbl in (("size", sizes), ("steps", steps)):
        for a, b in (("REG", "CMB"), ("REG", "CEL"), ("CMB", "CEL")):
            k = kendall_counts(tbl[a], tbl[b])
            rep["%s__%s_vs_%s" % (label, a, b)] = _kfmt(k)
    k = kendall_counts(sizes["CMB"], sizes["CMB_NAIVE"])
    rep["size__CMB_optimized_vs_CMB_naive"] = _kfmt(k)
    rep["distinct_size_values"] = dict((n, len(set(v))) for n, v in sizes.items())
    rep["distinct_step_values"] = dict((n, len(set(v))) for n, v in steps.items())
    rep["size_range"] = dict((n, [min(v), max(v)]) for n, v in sizes.items())
    rep["steps_range"] = dict((n, [min(v), max(v)]) for n, v in steps.items())
    return rep


def _kfmt(k):
    d = dict(k)
    d["tau_a"] = frac(k["tau_a"])
    d["tau_restricted"] = frac(k["tau_restricted"])
    return d


# ---------------------------------------------------------------------------
# 8. Reachability geometry (FREEZE 2.11)
# ---------------------------------------------------------------------------

GEOM_PROBE_MACHINES = (0, 85, 170, 255)
GEOM_PROBE_WORD = (0, 1, 0)
GEOM_CORRIDOR_CAP = 4000
GEOM_NODE_CAP = 50000


def lo_step(t):
    spine = []
    head = t
    while type(head) is tuple:
        spine.append(head[1])
        head = head[0]
    n = len(spine)
    if (head == "K" and n >= 2) or (head == "S" and n >= 3):
        return cmb_contract_at(t, ()), True
    args = list(reversed(spine))
    for i, a in enumerate(args):
        a2, ok = lo_step(a)
        if ok:
            new = head
            for j, b in enumerate(args):
                new = (new, a2 if j == i else b)
            return new, True
    return t, False


def cmb_geometry(term, w):
    t0 = (((term, WORD_CL[w]), PAIRIFY), NILP)
    corridor = [t0]
    t = t0
    for _ in range(GEOM_CORRIDOR_CAP):
        t2, ok = lo_step(t)
        if not ok:
            break
        t = t2
        corridor.append(t)
    outdeg = []
    same_nf = 0
    diff_nf = 0
    branch_nodes = 0
    for c in corridor:
        pos = cmb_redex_positions(c)
        outdeg.append(len(pos))
        if len(pos) >= 2:
            branch_nodes += 1
            nfs = set()
            for p in pos:
                succ = cmb_contract_at(c, p)
                v, _s = nf(succ, CMB_BUDGET)
                nfs.add(v)
            if len(nfs) == 1:
                same_nf += 1
            else:
                diff_nf += 1
    fringe = set()
    for c in corridor:
        for p in cmb_redex_positions(c):
            fringe.add(cmb_contract_at(c, p))
    return {
        "corridor_length": len(corridor),
        "corridor_cap_reached": len(corridor) >= GEOM_CORRIDOR_CAP,
        "fringe_size": len(fringe),
        "max_out_degree": max(outdeg),
        "min_out_degree": min(outdeg),
        "terminal_configurations": sum(1 for d in outdeg if d == 0),
        "branching_configurations": branch_nodes,
        "branching_configurations_all_successors_share_normal_form": same_nf,
        "branching_configurations_with_divergent_normal_forms": diff_nf,
    }


def cmb_reachable_bounded(term, w):
    t0 = (((term, WORD_CL[w]), PAIRIFY), NILP)
    seen = set([t0])
    frontier = [t0]
    cap_hit = False
    while frontier:
        t = frontier.pop()
        for p in cmb_redex_positions(t):
            u = cmb_contract_at(t, p)
            if u not in seen:
                if len(seen) >= GEOM_NODE_CAP:
                    cap_hit = True
                    frontier = []
                    break
                seen.add(u)
                frontier.append(u)
    return len(seen), cap_hit


def deterministic_geometry(trace):
    outdeg = [1] * (len(trace) - 1) + [0]
    indeg = {}
    for c in trace[1:]:
        indeg[c] = indeg.get(c, 0) + 1
    return {
        "corridor_length": len(trace),
        "corridor_cap_reached": False,
        "fringe_size": len(set(trace[1:])),
        "max_out_degree": max(outdeg),
        "min_out_degree": min(outdeg),
        "terminal_configurations": 1,
        "branching_configurations": 0,
        "branching_configurations_all_successors_share_normal_form": 0,
        "branching_configurations_with_divergent_normal_forms": 0,
        "max_in_degree": max(indeg.values()) if indeg else 0,
    }


def geometry_report(reg_art, cmb_art, cel_art):
    rep = {"probe_machines": list(GEOM_PROBE_MACHINES),
           "probe_word": "".join(str(a) for a in GEOM_PROBE_WORD),
           "corridor_cap": GEOM_CORRIDOR_CAP, "node_cap": GEOM_NODE_CAP,
           "REG": {}, "CMB": {}, "CEL": {}}
    for i in GEOM_PROBE_MACHINES:
        rep["REG"][str(i)] = deterministic_geometry(
            reg_config_trace(reg_art[i], GEOM_PROBE_WORD, reg_cap(GEOM_PROBE_WORD)))
        rep["CEL"][str(i)] = deterministic_geometry(
            cel_trace(cel_art[i]["rule"], GEOM_PROBE_WORD))
        g = cmb_geometry(cmb_art[i], GEOM_PROBE_WORD)
        n, cap_hit = cmb_reachable_bounded(cmb_art[i], GEOM_PROBE_WORD)
        g["bounded_reachable_set"] = n
        g["bounded_reachable_set_class"] = (
            "LOWER_BOUND_ONLY" if cap_hit else "EXACT")
        rep["CMB"][str(i)] = g
    return rep


# ---------------------------------------------------------------------------
# 9. Developmental search burden: the one-edit landscape (FREEZE 2.10)
# ---------------------------------------------------------------------------

S16 = tuple(range(0, 256, 16))


def reg_slots(artifact):
    registers, start, prog = artifact
    slots = []
    for lab in sorted(prog):
        ins = prog[lab]
        slots.append(("op", lab, REG_OPCODES))
        if ins[0] != "HALT":
            slots.append(("reg", lab, registers))
            slots.append(("lab0", lab, tuple(sorted(prog))))
            if ins[0] == "DECJZ":
                slots.append(("lab1", lab, tuple(sorted(prog))))
    return slots


def reg_apply_edit(artifact, slot, value):
    registers, start, prog = artifact
    kind, lab, _dom = slot
    p = dict(prog)
    ins = p[lab]
    if kind == "op":
        reg = ins[1] if ins[0] != "HALT" else registers[0]
        nxt = ins[2] if ins[0] != "HALT" else start
        if value in ("READ", "INC", "EMIT"):
            p[lab] = (value, reg, nxt)
        elif value == "DECJZ":
            p[lab] = (value, reg, nxt, nxt)
        else:
            p[lab] = ("HALT",)
    elif kind == "reg":
        if len(ins) < 2:
            return artifact
        p[lab] = (ins[0], value) + tuple(ins[2:])
    elif kind == "lab0":
        if len(ins) < 3:
            return artifact
        p[lab] = (ins[0], ins[1], value) + tuple(ins[3:])
    else:
        if len(ins) < 4:
            return artifact
        p[lab] = (ins[0], ins[1], ins[2], value)
    return (registers, start, p)


def reg_behaviour(artifact):
    res = []
    for w in WORDS:
        got, _s, _t = reg_run(artifact, w, reg_cap(w))
        if got is None:
            return None
        res.append(got)
    return tuple(res)


def cmb_leaf_paths(t):
    paths = []
    stack = [(t, ())]
    while stack:
        u, p = stack.pop()
        if type(u) is tuple:
            stack.append((u[0], p + (0,)))
            stack.append((u[1], p + (1,)))
        else:
            paths.append(p)
    return paths


def cmb_replace_at(t, path, leaf):
    if not path:
        return leaf
    if path[0] == 0:
        return (cmb_replace_at(t[0], path[1:], leaf), t[1])
    return (t[0], cmb_replace_at(t[1], path[1:], leaf))


def cmb_leaf_at(t, path):
    for i in path:
        t = t[i]
    return t


def cmb_behaviour(term):
    res = []
    for w in WORDS:
        got, _s, _t = cmb_run(term, w)
        if got is None:
            return None
        res.append(got)
    return tuple(res)


def cel_behaviour(d):
    res = []
    for w in WORDS:
        got, _s, _t = cel_run(d, w)
        if got is None:
            return None
        res.append(got)
    return tuple(res)


def one_edit_report(reg_art, cmb_art, cel_art, rng):
    rep = {"subsample": list(S16), "subsample_size": len(S16),
           "REG": {}, "CMB": {}, "CEL": {}}
    for name in ("REG", "CMB", "CEL"):
        rep[name] = {"neighbourhood_total": 0, "preserving": 0, "viable": 0,
                     "per_machine": []}
    for i in S16:
        target = behaviour(*MACHINES[i])
        # REG -------------------------------------------------------------
        slots = reg_slots(reg_art[i])
        n_tot = pres = via = 0
        for slot in slots:
            cur = _reg_slot_value(reg_art[i], slot)
            for v in slot[2]:
                if v == cur:
                    continue
                n_tot += 1
                b = reg_behaviour(reg_apply_edit(reg_art[i], slot, v))
                if b is None:
                    continue
                if b == target:
                    pres += 1
                if b in BEHAVIOUR_INDEX:
                    via += 1
        _bump(rep["REG"], i, n_tot, pres, via)
        # CMB -------------------------------------------------------------
        paths = cmb_leaf_paths(cmb_art[i])
        n_tot = pres = via = 0
        for p in paths:
            cur = cmb_leaf_at(cmb_art[i], p)
            other = "S" if cur == "K" else "K"
            n_tot += 1
            b = cmb_behaviour(cmb_replace_at(cmb_art[i], p, other))
            if b is None:
                continue
            if b == target:
                pres += 1
            if b in BEHAVIOUR_INDEX:
                via += 1
        _bump(rep["CMB"], i, n_tot, pres, via)
        # CEL -------------------------------------------------------------
        art = cel_art[i]
        sigma = art["sigma"]
        table = dict(art["support"])
        used = set()
        for w in WORDS:
            used |= cel_used_windows(art["rule"], w)
        used_sup = [k for k in table if k in used]
        unused_sup = [k for k in table if k not in used]
        n_tot = len(table) * (len(sigma) - 1)
        pres = len(unused_sup) * (len(sigma) - 1)
        via = pres
        for k in used_sup:
            cur = table[k]
            for v in sigma:
                if v == cur:
                    continue
                t2 = dict(table)
                t2[k] = v
                b = cel_behaviour(cel_table_rule(t2))
                if b is None:
                    continue
                if b == target:
                    pres += 1
                if b in BEHAVIOUR_INDEX:
                    via += 1
        _bump(rep["CEL"], i, n_tot, pres, via)
        rep["CEL"]["per_machine"][-1]["used_support_entries"] = len(used_sup)
        rep["CEL"]["per_machine"][-1]["unused_support_entries"] = len(unused_sup)
    # analytic shortcut validated by brute force on a sample of unused entries
    checked = 0
    failures = 0
    for i in S16[:4]:
        art = cel_art[i]
        sigma = art["sigma"]
        table = dict(art["support"])
        used = set()
        for w in WORDS:
            used |= cel_used_windows(art["rule"], w)
        unused = [k for k in table if k not in used]
        target = behaviour(*MACHINES[i])
        rng.shuffle(unused)
        for k in unused[:50]:
            cur = table[k]
            for v in sigma:
                if v == cur:
                    continue
                t2 = dict(table)
                t2[k] = v
                checked += 1
                if cel_behaviour(cel_table_rule(t2)) != target:
                    failures += 1
                break
    rep["CEL"]["unused_entry_shortcut_validation"] = {
        "brute_force_checks": checked, "failures": failures}
    for name in ("REG", "CMB", "CEL"):
        t = rep[name]["neighbourhood_total"]
        rep[name]["preserving_fraction"] = frac(Fraction(rep[name]["preserving"], t))
        rep[name]["viable_fraction"] = frac(Fraction(rep[name]["viable"], t))
    return rep


def _reg_slot_value(artifact, slot):
    kind, lab, _dom = slot
    ins = artifact[2][lab]
    if kind == "op":
        return ins[0]
    if kind == "reg":
        return ins[1]
    if kind == "lab0":
        return ins[2]
    return ins[3]


def _bump(bucket, i, n_tot, pres, via):
    bucket["neighbourhood_total"] += n_tot
    bucket["preserving"] += pres
    bucket["viable"] += via
    bucket["per_machine"].append(
        {"machine": i, "neighbourhood": n_tot, "preserving": pres, "viable": via})


def enumeration_obstruction(cel_art):
    """Exact cardinalities showing why the uniform-enumeration reading of
    'search burden' is not executable across all three bases."""
    sizes = [len(a["sigma"]) for a in cel_art]
    s = max(sizes)
    return {
        "cellular_alphabet_max": s,
        "cellular_unrestricted_rule_space": str(s ** (s ** 3)),
        "cellular_unrestricted_rule_space_decimal_digits":
            len(str(s ** (s ** 3))),
        "verdict": "UNIFORM_ENUMERATION_NOT_EXECUTABLE_AT_ANY_BOUNDED_SCOPE",
    }


# ---------------------------------------------------------------------------
# 10. The MI-recovery test (FREEZE 2.9, r36)
# ---------------------------------------------------------------------------

NORMALIZATIONS = (
    ("times_7", lambda x: 7 * x),
    ("plus_1000", lambda x: x + 1000),
    ("square", lambda x: x * x),
)


def mi_recovery(sizes, steps, qs):
    rep = {}
    for label, tbl in (("size", sizes), ("steps", steps)):
        fronts = {}
        for name in ("REG", "CMB", "CEL"):
            f = pareto_frontier(qs, tbl[name])
            fronts[name] = f
        block = {}
        for name, f in fronts.items():
            block[name] = {"frontier_size": len(f), "frontier": list(f)}
            block[name]["vacuous"] = (len(f) <= 1 or len(f) >= len(MACHINES))
            block[name]["distinct_cost_values"] = len(set(tbl[name]))
            block[name]["cost_coordinate_constant"] = len(set(tbl[name])) == 1
            block[name]["degeneracy"] = (
                "DEGENERATE_CONSTANT_COST__FRONTIER_IS_ARGMAX_CAPABILITY"
                if len(set(tbl[name])) == 1 else "NON_DEGENERATE")
        for a, b in (("REG", "CMB"), ("REG", "CEL"), ("CMB", "CEL")):
            sa, sb = set(fronts[a]), set(fronts[b])
            block["%s_vs_%s" % (a, b)] = {
                "intersection": len(sa & sb),
                "symmetric_difference": len(sa ^ sb),
                "equal": sa == sb,
            }
        block["all_three_equal"] = (set(fronts["REG"]) == set(fronts["CMB"])
                                    == set(fronts["CEL"]))
        block["any_vacuous"] = any(block[n]["vacuous"] for n in
                                   ("REG", "CMB", "CEL"))
        block["any_degenerate"] = any(block[n]["cost_coordinate_constant"]
                                      for n in ("REG", "CMB", "CEL"))
        block["decisive"] = not (block["any_vacuous"] or block["any_degenerate"])
        block["verdict"] = ("VACUOUS" if block["any_vacuous"] else
                            ("LAW_SURVIVES" if block["all_three_equal"]
                             else "LAW_DOES_NOT_SURVIVE"))
        # invariance under uniform strictly increasing normalizations
        inv = {}
        for nm, f in NORMALIZATIONS:
            ok = True
            for name in ("REG", "CMB", "CEL"):
                if pareto_frontier(qs, [f(x) for x in tbl[name]]) != fronts[name]:
                    ok = False
            inv[nm] = ok
        block["frontier_unchanged_under_uniform_monotone_normalization"] = inv
        rep[label] = block
    return rep


# ---------------------------------------------------------------------------
# 11. Locality and closure checkers, validated on planted positives
# ---------------------------------------------------------------------------

def window_configs(cel_art, rng, n_random=500, width=5):
    confs = []
    for i in (0, 85, 170, 255):
        for w in WORDS:
            confs.extend(cel_trace(cel_art[i]["rule"], w))
    sigma = cel_art[0]["sigma"]
    for _ in range(n_random):
        confs.append(tuple(rng.choice(sigma) for _ in range(width)))
    return confs


def locality_violations(update_fn, confs):
    seen = {}
    viol = 0
    for conf in confs:
        n = len(conf)
        for i in range(n):
            l = conf[i - 1] if i > 0 else QUIESCENT
            c = conf[i]
            r = conf[i + 1] if i + 1 < n else QUIESCENT
            v = update_fn(conf, i)
            key = (l, c, r)
            if key in seen:
                if seen[key] != v:
                    viol += 1
            else:
                seen[key] = v
    return viol


def local_update(d):
    def f(conf, i):
        n = len(conf)
        l = conf[i - 1] if i > 0 else QUIESCENT
        c = conf[i]
        r = conf[i + 1] if i + 1 < n else QUIESCENT
        return d(l, c, r)
    return f


def radius2_update(d):
    """HOSTILE: the update peeks two cells to the left."""
    def f(conf, i):
        n = len(conf)
        l = conf[i - 1] if i > 0 else QUIESCENT
        c = conf[i]
        r = conf[i + 1] if i + 1 < n else QUIESCENT
        if i >= 2 and conf[i - 2][2] == "A":
            return QUIESCENT
        return d(l, c, r)
    return f


def closure_violations(d, sigma):
    sset = set(sigma)
    v = 0
    for l in sigma:
        for c in sigma:
            for r in sigma:
                if d(l, c, r) not in sset:
                    v += 1
    return v


def coordinate_dependence(d, sigma):
    """AG5's structure-dependence measurement, re-run for this local rule."""
    left = right = 0
    total = 0
    for c in sigma:
        for r in sigma:
            for a in range(len(sigma)):
                for b in range(a + 1, len(sigma)):
                    total += 1
                    if d(sigma[a], c, r) != d(sigma[b], c, r):
                        left += 1
    total_r = 0
    for l in sigma:
        for c in sigma:
            for a in range(len(sigma)):
                for b in range(a + 1, len(sigma)):
                    total_r += 1
                    if d(l, c, sigma[a]) != d(l, c, sigma[b]):
                        right += 1
    return {"left_differing_pairs": left, "left_pairs": total,
            "right_differing_pairs": right, "right_pairs": total_r}


def pointwise_rule(delta, out):
    """Control: a rule that ignores both neighbours."""
    def d(l, c, r):
        ci, co, ch = c
        if ch in ("A", "B"):
            if ci in ("0", "1"):
                q = 0 if ch == "A" else 1
                return ("-", str(out[(q, int(ci))]), "-")
            return (ci, co, "H")
        return c
    return d


# ---------------------------------------------------------------------------
# 12. Hostiles (each must be DETECTED, each paired with a clean control)
# ---------------------------------------------------------------------------

def whnf_transposed(t, budget):
    """HOSTILE: S x y z -> x y z' transposed contraction."""
    steps = 0
    stack = []
    while True:
        while type(t) is tuple:
            stack.append(t[1])
            t = t[0]
        if t == "K" and len(stack) >= 2:
            x = stack.pop()
            stack.pop()
            t = x
            steps += 1
        elif t == "S" and len(stack) >= 3:
            x = stack.pop()
            y = stack.pop()
            z = stack.pop()
            t = ((x, y), (z, z))
            steps += 1
        else:
            break
        if steps > budget:
            raise Cap()
    for a in reversed(stack):
        t = (t, a)
    return t, steps


def absvar_bad_eta(x, u, _opt=True):
    """HOSTILE: eta applied even when x occurs free in the operator."""
    if u == ("v", x):
        return I_CL
    if isinstance(u, str) or u[0] == "v":
        return ("@", "K", u)
    if x not in fv(u):
        return ("@", "K", u)
    if u[2] == ("v", x):
        return u[1]
    return ("@", ("@", "S", absvar_bad_eta(x, u[1])), absvar_bad_eta(x, u[2]))


def absvar_swapped(x, u):
    """HOSTILE: bracket abstraction emits S with its two arguments exchanged."""
    if u == ("v", x):
        return I_CL
    if isinstance(u, str) or u[0] == "v":
        return ("@", "K", u)
    if x not in fv(u):
        return ("@", "K", u)
    return ("@", ("@", "S", absvar_swapped(x, u[2])), absvar_swapped(x, u[1]))


def compile_lam_swapped(t):
    k = t[0]
    if k == "var":
        return ("v", t[1])
    if k == "app":
        return ("@", compile_lam_swapped(t[1]), compile_lam_swapped(t[2]))
    return absvar_swapped(t[1], compile_lam_swapped(t[2]))


def compile_lam_bad_eta(t):
    k = t[0]
    if k == "var":
        return ("v", t[1])
    if k == "app":
        return ("@", compile_lam_bad_eta(t[1]), compile_lam_bad_eta(t[2]))
    return absvar_bad_eta(t[1], compile_lam_bad_eta(t[2]))


def cmb_run_bad_decoder(term, w, budget=CMB_BUDGET):
    """HOSTILE: the tail probe uses K instead of KI."""
    steps = 0
    try:
        p = (((term, WORD_CL[w]), PAIRIFY), NILP)
        p, s = whnf(p, budget)
        steps += s
        bits = []
        for _ in range(len(w)):
            b, s = nf((p, "K"), budget)
            steps += s
            if b == SK_T:
                bits.append(1)
            elif b == SK_F:
                bits.append(0)
            else:
                return None
            p, s = whnf((p, "K"), budget)
            steps += s
        return tuple(bits)
    except (Cap, RecursionError):
        return None


def reg_run_no_decrement(artifact, word, cap):
    """HOSTILE: DECJZ branches but never decrements."""
    registers, start, prog = artifact
    rv = dict((r, 0) for r in registers)
    stream = tuple(word) + (2,)
    pos = 0
    out = []
    label = start
    steps = 0
    while steps < cap:
        ins = prog.get(label)
        if ins is None:
            return None
        if ins[0] == "HALT":
            return tuple(out)
        steps += 1
        op = ins[0]
        if op == "READ":
            if pos >= len(stream):
                return None
            rv[ins[1]] = stream[pos]
            pos += 1
            label = ins[2]
        elif op == "INC":
            rv[ins[1]] += 1
            label = ins[2]
        elif op == "EMIT":
            if rv[ins[1]] not in (0, 1):
                return None
            out.append(rv[ins[1]])
            label = ins[2]
        else:
            label = ins[3] if rv[ins[1]] == 0 else ins[2]
    return None


def reg_swap_emit(artifact):
    """HOSTILE: EMIT operands z0/z1 swapped."""
    registers, start, prog = artifact
    p = {}
    for lab, ins in prog.items():
        if ins[0] == "EMIT":
            p[lab] = ("EMIT", "z1" if ins[1] == "z0" else "z0", ins[2])
        else:
            p[lab] = ins
    return (registers, start, p)


def kendall_sign_swapped(xs, ys):
    """HOSTILE: concordant and discordant exchanged."""
    k = kendall_counts(xs, ys)
    return Fraction(k["discordant"] - k["concordant"], k["pairs"])


def pareto_frontier_reflexive(qs, cs):
    """HOSTILE: a point dominates itself, so nothing survives."""
    n = len(qs)
    front = []
    for i in range(n):
        dominated = False
        for j in range(n):
            if qs[j] >= qs[i] and cs[j] <= cs[i]:
                dominated = True
                break
        if not dominated:
            front.append(i)
    return tuple(front)


def hostile_report(reg_art, cmb_art, cel_art, sizes, steps, qs, rng):
    rep = {}
    probe = (0, 85, 170, 255, 37, 200)

    # H1 transposed S rule
    bad = 0
    for i in probe:
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            got = _cmb_run_with(whnf_transposed, cmb_art[i], w)
            if got != want:
                bad += 1
    clean = 0
    for i in probe:
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            got, _s, _t = cmb_run(cmb_art[i], w)
            if got != want:
                clean += 1
    rep["H1_cmb_transposed_S_rule"] = {
        "hostile_mismatches": bad, "control_mismatches": clean,
        "detected": bad > 0 and clean == 0}

    # H2 bracket abstraction emits S with exchanged arguments
    bad = 0
    for i in probe:
        term = to_runtime(compile_lam_swapped(machine_lambda(*MACHINES[i])))
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            got, _s, _t = cmb_run(term, w)
            if got != want:
                bad += 1
    rep["H2_cmb_swapped_S_abstraction"] = {
        "hostile_mismatches": bad, "control_mismatches": clean,
        "detected": bad > 0 and clean == 0}

    # Capability audit: a perturbation that provably cannot move the quantity is
    # EXCLUDED from the hostile count rather than being recorded as "detected".
    identical = 0
    for i in range(len(MACHINES)):
        lam = machine_lambda(*MACHINES[i])
        if to_runtime(compile_lam_bad_eta(lam)) == cmb_art[i]:
            identical += 1
    rep["excluded_inert_perturbation__unsound_eta"] = {
        "machines_checked": len(MACHINES),
        "compiled_terms_identical_to_the_sound_compiler": identical,
        "moves_the_quantity_it_perturbs": identical < len(MACHINES),
        "excluded_from_hostile_count": True,
        "note": ("the unsound eta rule abs(x, M x) = M fires only when x occurs "
                 "free in M, which never happens in this term family, so the "
                 "perturbation is inert here and is not counted as a hostile"),
    }

    # H3 broken decoder
    bad = 0
    for i in probe:
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            if cmb_run_bad_decoder(cmb_art[i], w) != want:
                bad += 1
    rep["H3_cmb_broken_decoder"] = {
        "hostile_mismatches": bad, "control_mismatches": clean,
        "detected": bad > 0 and clean == 0}

    # H4 planted radius-2 dependence
    confs = window_configs(cel_art, rng)
    v_true = locality_violations(local_update(cel_art[0]["rule"]), confs)
    v_bad = locality_violations(radius2_update(cel_art[0]["rule"]), confs)
    rep["H4_cel_radius2_dependence"] = {
        "hostile_locality_violations": v_bad,
        "control_locality_violations": v_true,
        "configurations_checked": len(confs),
        "detected": v_bad > 0 and v_true == 0}

    # H5 pointwise rule
    pw = pointwise_rule(*MACHINES[0])
    pw_mismatch = 0
    for w in WORDS:
        got, _s, _t = cel_run(pw, w)
        if got != direct_mealy(MACHINES[0][0], MACHINES[0][1], w):
            pw_mismatch += 1
    dep_true = coordinate_dependence(cel_art[0]["rule"], cel_art[0]["sigma"])
    dep_pw = coordinate_dependence(pw, cel_art[0]["sigma"])
    rep["H5_cel_pointwise_control"] = {
        "hostile_mismatches": pw_mismatch,
        "hostile_left_differing_pairs": dep_pw["left_differing_pairs"],
        "control_left_differing_pairs": dep_true["left_differing_pairs"],
        "detected": pw_mismatch > 0 and dep_pw["left_differing_pairs"] == 0
                    and dep_true["left_differing_pairs"] > 0}
    rep["cel_coordinate_dependence"] = dep_true

    # H6 alphabet not closed
    sigma = cel_art[0]["sigma"]
    trimmed = tuple(x for x in sigma if x != sigma[-1])
    rep["H6_cel_alphabet_not_closed"] = {
        "hostile_closure_violations":
            closure_violations(cel_art[0]["rule"], trimmed),
        "control_closure_violations":
            closure_violations(cel_art[0]["rule"], sigma),
        "detected": closure_violations(cel_art[0]["rule"], trimmed) > 0
                    and closure_violations(cel_art[0]["rule"], sigma) == 0}

    # H7 DECJZ without decrement
    bad = 0
    for i in probe:
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            if reg_run_no_decrement(reg_art[i], w, reg_cap(w)) != want:
                bad += 1
    reg_clean = 0
    for i in probe:
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            got, _s, _t = reg_run(reg_art[i], w, reg_cap(w))
            if got != want:
                reg_clean += 1
    rep["H7_reg_decjz_no_decrement"] = {
        "hostile_mismatches": bad, "control_mismatches": reg_clean,
        "detected": bad > 0 and reg_clean == 0}

    # H8 EMIT operands swapped
    bad = 0
    for i in probe:
        a = reg_swap_emit(reg_art[i])
        for w in WORDS:
            want = direct_mealy(MACHINES[i][0], MACHINES[i][1], w)
            got, _s, _t = reg_run(a, w, reg_cap(w))
            if got != want:
                bad += 1
    rep["H8_reg_emit_swapped"] = {
        "hostile_mismatches": bad, "control_mismatches": reg_clean,
        "detected": bad > 0 and reg_clean == 0}

    # H9 Kendall sign swap
    true_tau = kendall_counts(sizes["REG"], sizes["CMB"])["tau_a"]
    bad_tau = kendall_sign_swapped(sizes["REG"], sizes["CMB"])
    rep["H9_kendall_sign_swap"] = {
        "control_tau_a": frac(true_tau), "hostile_tau_a": frac(bad_tau),
        "detected": bad_tau == -true_tau and true_tau != 0}

    # H10 reflexive domination
    f_true = pareto_frontier(qs, sizes["REG"])
    f_bad = pareto_frontier_reflexive(qs, sizes["REG"])
    rep["H10_pareto_reflexive_domination"] = {
        "control_frontier_size": len(f_true),
        "hostile_frontier_size": len(f_bad),
        "detected": len(f_bad) == 0 and len(f_true) > 0}

    # H11 vacuity classifier
    rep["H11_vacuity_classifier"] = {
        "vacuous_bound_class": classify_bound(Fraction(16), Fraction(8), Fraction(16)),
        "attained_bound_class": classify_bound(Fraction(8), Fraction(8), Fraction(16)),
        "detected": classify_bound(Fraction(16), Fraction(8), Fraction(16)) == "VACUOUS"
                    and classify_bound(Fraction(8), Fraction(8), Fraction(16)) == "ATTAINED"}

    # H12 identity edit counted as an edit
    slots = reg_slots(reg_art[0])
    honest = sum(len(s[2]) - 1 for s in slots)
    inflated = sum(len(s[2]) for s in slots)
    rep["H12_identity_edit_counted"] = {
        "control_neighbourhood": honest, "hostile_neighbourhood": inflated,
        "detected": inflated - honest == len(slots) and len(slots) > 0}

    # H13 machine-dependent reweighting moves the frontier
    base = sizes["REG"]
    rew = [base[i] * (1 + (i % 7)) for i in range(len(base))]
    rep["H13_machine_dependent_reweighting"] = {
        "control_frontier_size": len(f_true),
        "reweighted_frontier_size": len(pareto_frontier(qs, rew)),
        "frontier_moved": pareto_frontier(qs, rew) != f_true,
        "detected": pareto_frontier(qs, rew) != f_true}
    rep["hostiles_total"] = 13
    rep["hostiles_detected"] = sum(
        1 for k, v in rep.items() if isinstance(v, dict) and v.get("detected"))
    return rep


def _cmb_run_with(whnf_impl, term, w, budget=CMB_BUDGET):
    def nf_local(t, b):
        total = 0
        t, s = whnf_impl(t, b)
        total += s
        if type(t) is tuple:
            f, s1 = nf_local(t[0], b - total)
            total += s1
            x, s2 = nf_local(t[1], b - total)
            total += s2
            t = (f, x)
        return t, total
    try:
        p = (((term, WORD_CL[w]), PAIRIFY), NILP)
        p, _s = whnf_impl(p, budget)
        bits = []
        for _ in range(len(w)):
            b, _s = nf_local((p, "K"), budget)
            if b == SK_T:
                bits.append(1)
            elif b == SK_F:
                bits.append(0)
            else:
                return None
            p, _s = whnf_impl((p, SK_KI), budget)
        e, _s = nf_local((p, "K"), budget)
        if e != "S":
            return None
        return tuple(bits)
    except (Cap, RecursionError):
        return None


# ---------------------------------------------------------------------------
# 13. Nulls
# ---------------------------------------------------------------------------

NULL_DRAWS = 200


def reg_run_roles(artifact, word, cap, rolemap):
    """REG interpreter whose opcode->role assignment is a parameter (null route)."""
    registers, start, prog = artifact
    rv = dict((r, 0) for r in registers)
    stream = tuple(word) + (2,)
    pos = 0
    out = []
    label = start
    steps = 0
    while steps < cap:
        ins = prog.get(label)
        if ins is None:
            return None
        role = rolemap[ins[0]]
        if role == "HALT":
            return tuple(out)
        steps += 1
        if ins[0] == "HALT":
            return None
        if role == "READ":
            if pos >= len(stream):
                return None
            rv[ins[1]] = stream[pos]
            pos += 1
            label = ins[2]
        elif role == "INC":
            rv[ins[1]] += 1
            label = ins[2]
        elif role == "EMIT":
            if rv[ins[1]] not in (0, 1):
                return None
            out.append(rv[ins[1]])
            label = ins[2]
        elif role == "DECJZ":
            if rv[ins[1]] == 0:
                label = ins[3] if len(ins) > 3 else ins[2]
            else:
                rv[ins[1]] -= 1
                label = ins[2]
    return None


def make_whnf(s_perm, k_index):
    """Reduction relation with S's recombination permuted and K's projection chosen."""
    def impl(t, budget):
        steps = 0
        stack = []
        while True:
            while type(t) is tuple:
                stack.append(t[1])
                t = t[0]
            if t == "K" and len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                t = a if k_index == 0 else b
                steps += 1
            elif t == "S" and len(stack) >= 3:
                args = (stack.pop(), stack.pop(), stack.pop())
                x, y, z = args[s_perm[0]], args[s_perm[1]], args[s_perm[2]]
                t = ((x, z), (y, z))
                steps += 1
            else:
                break
            if steps > budget:
                raise Cap()
        for a in reversed(stack):
            t = (t, a)
        return t, steps
    return impl


def _census_survives(runner):
    """Does this perturbed semantics reproduce the FULL 3840-task census?"""
    for i, (delta, out) in enumerate(MACHINES):
        for w in WORDS:
            if runner(i, w) != direct_mealy(delta, out, w):
                return False
    return True


def null_report(reg_art, cmb_art, cel_art, rng):
    """Randomized-semantics nulls in AG2's style: perturb the basis's own
    interpretation, then ask whether the full 3840-task census survives."""
    rep = {"design": "RANDOMIZED_SEMANTICS_MUST_NOT_REPRODUCE_THE_FULL_CENSUS"}

    perms = [p for p in _perms(REG_OPCODES) if p != REG_OPCODES]
    survived = 0
    for p in perms:
        rolemap = dict(zip(REG_OPCODES, p))
        if _census_survives(lambda i, w: reg_run_roles(
                reg_art[i], w, reg_cap(w), rolemap)):
            survived += 1
    rep["REG_opcode_role_permutations"] = {
        "draws": len(perms), "exhaustive": True,
        "identity_excluded": 1, "reproduced_full_census": survived}

    variants = []
    for sp in _perms((0, 1, 2)):
        for ki in (0, 1):
            if sp == (0, 1, 2) and ki == 0:
                continue
            variants.append((sp, ki))
    survived = 0
    for sp, ki in variants:
        impl = make_whnf(sp, ki)
        if _census_survives(lambda i, w: _cmb_run_with(impl, cmb_art[i], w)):
            survived += 1
    rep["CMB_reduction_rule_variants"] = {
        "draws": len(variants), "exhaustive": True,
        "identity_excluded": 1, "reproduced_full_census": survived}

    sigma = cel_art[0]["sigma"]
    survived = 0
    draws = 0
    for _ in range(NULL_DRAWS):
        idx = list(range(len(sigma)))
        rng.shuffle(idx)
        if idx == list(range(len(sigma))):
            continue
        draws += 1
        pi = dict(zip(sigma, [sigma[j] for j in idx]))

        def runner(i, w, pi=pi):
            d = cel_art[i]["rule"]
            got, _s, _t = cel_run(lambda l, c, r: pi.get(d(l, c, r), d(l, c, r)), w)
            return got
        if _census_survives(runner):
            survived += 1
    rep["CEL_alphabet_relabelings"] = {
        "draws": draws, "exhaustive": False,
        "identity_excluded": NULL_DRAWS - draws,
        "reproduced_full_census": survived}

    rep["total_reproduced"] = (
        rep["REG_opcode_role_permutations"]["reproduced_full_census"]
        + rep["CMB_reduction_rule_variants"]["reproduced_full_census"]
        + rep["CEL_alphabet_relabelings"]["reproduced_full_census"])
    return rep


def _perms(seq):
    seq = tuple(seq)
    if len(seq) <= 1:
        return [seq]
    out = []
    for i in range(len(seq)):
        for rest in _perms(seq[:i] + seq[i + 1:]):
            out.append((seq[i],) + rest)
    return out


def neutral_mutation_census(reg_art, cmb_art, cel_art, rng):
    """Reported, not gated: how often a random three-slot perturbation of the
    artifact for machine 0 still realizes machine 0, and how often it realizes
    some member of MEALY_2x2."""
    target = behaviour(*MACHINES[0])
    rep = {"draws": NULL_DRAWS, "slots_perturbed": 3}
    paths = cmb_leaf_paths(cmb_art[0])
    hits = viable = 0
    for _ in range(NULL_DRAWS):
        t = cmb_art[0]
        for p in rng.sample(paths, 3):
            cur = cmb_leaf_at(t, p)
            t = cmb_replace_at(t, p, "S" if cur == "K" else "K")
        b = cmb_behaviour(t)
        if b == target:
            hits += 1
        if b is not None and b in BEHAVIOUR_INDEX:
            viable += 1
    rep["CMB"] = {"still_realizes_machine_0": hits, "realizes_some_machine": viable}
    art = cel_art[0]
    sigma = art["sigma"]
    table = dict(art["support"])
    keys = list(table)
    hits = viable = 0
    for _ in range(NULL_DRAWS):
        t2 = dict(table)
        for k in rng.sample(keys, 3):
            t2[k] = rng.choice(sigma)
        b = cel_behaviour(cel_table_rule(t2))
        if b == target:
            hits += 1
        if b is not None and b in BEHAVIOUR_INDEX:
            viable += 1
    rep["CEL"] = {"still_realizes_machine_0": hits, "realizes_some_machine": viable}
    hits = viable = 0
    for _ in range(NULL_DRAWS):
        a = reg_art[0]
        for _ in range(3):
            sl = rng.choice(reg_slots(a))
            a = reg_apply_edit(a, sl, rng.choice(sl[2]))
        b = reg_behaviour(a)
        if b == target:
            hits += 1
        if b is not None and b in BEHAVIOUR_INDEX:
            viable += 1
    rep["REG"] = {"still_realizes_machine_0": hits, "realizes_some_machine": viable}
    return rep


# ---------------------------------------------------------------------------
# 14. main
# ---------------------------------------------------------------------------

def main():
    rng = random.Random(8331977)
    out = {
        "schema": "GMI833AG6UniversalBasesReceiptV1",
        "issue": 833,
        "comment_id": 5693520829,
        "section": "AG6",
        "rows": ["r34", "r35", "r36"],
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "scope": {
            "semantic_class": "MEALY_2x2",
            "machines": len(MACHINES),
            "words": len(WORDS),
            "tasks": len(MACHINES) * len(WORDS),
            "max_word_length": 3,
            "universality_sense": "REGISTERED_FINITE_SCOPE_ONLY",
            "distinct_behaviours_on_W": len(BEHAVIOUR_INDEX),
            "distinct_behaviours_note": (
                "machines whose second state is unreachable agree on W, so the "
                "256 machines induce fewer than 256 behaviours; realization is "
                "still per-machine and all 256 are realized"),
        },
    }
    reg_art = [reg_compile(d, o) for (d, o) in MACHINES]
    cmb_art = [cmb_compile(d, o, True) for (d, o) in MACHINES]
    cmb_naive = [cmb_compile(d, o, False) for (d, o) in MACHINES]
    cel_art = [cel_artifact(d, o) for (d, o) in MACHINES]

    census, _ = realization_census(reg_art, cmb_art, cel_art)
    out["realization"] = census
    out["registered_universal"] = dict(
        (k, census[k]["machines_realized"] == len(MACHINES)
            and census[k]["mismatches"] == 0 and census[k]["cap_hits"] == 0)
        for k in census)
    out["parent_register_census_pinned"] = PARENT_REGISTER_CENSUS
    out["parent_register_census_reproduced"] = {
        "comparisons": census["REG"]["tasks"],
        "behavior_mismatches": census["REG"]["mismatches"],
        "agrees": (census["REG"]["tasks"] == PARENT_REGISTER_CENSUS["comparisons"]
                   and census["REG"]["mismatches"] == 0),
    }

    sizes, steps, per_task = cost_tables(reg_art, cmb_art, cel_art, cmb_naive)
    qs = [capability(d, o) for (d, o) in MACHINES]
    out["capability_battery"] = {
        "tasks": ["IDENTITY", "COMPLEMENT", "CONST0"],
        "max_score": 3 * len(WORDS),
        "distinct_values": len(set(qs)),
        "min": min(qs), "max": max(qs),
    }
    out["overhead"] = overhead_report(per_task)
    out["description_bias"] = description_bias(sizes, steps)
    out["reachability_geometry"] = geometry_report(reg_art, cmb_art, cel_art)
    out["developmental_search_burden"] = one_edit_report(
        reg_art, cmb_art, cel_art, rng)
    out["developmental_search_burden"]["uniform_enumeration_obstruction"] = \
        enumeration_obstruction(cel_art)
    out["mi_recovery"] = mi_recovery(sizes, steps, qs)
    out["mi_recovery"]["decisive_coordinate"] = "size"
    out["mi_recovery"]["decisive_coordinate_reason"] = (
        "on the steps coordinate the cellular cost is constant across all 256 "
        "machines, so its frontier degenerates to argmax capability; the size "
        "coordinate is non-degenerate in all three bases and carries the verdict")
    out["hostiles"] = hostile_report(reg_art, cmb_art, cel_art, sizes, steps, qs, rng)
    out["nulls"] = null_report(reg_art, cmb_art, cel_art, rng)
    out["developmental_search_burden"]["neutral_mutation_census"] = \
        neutral_mutation_census(reg_art, cmb_art, cel_art, rng)

    # no-alarm case on the true configuration
    sigma0 = cel_art[0]["sigma"]
    out["no_alarm"] = {
        "realization_mismatches": sum(census[k]["mismatches"] for k in census),
        "cap_hits": sum(census[k]["cap_hits"] for k in census),
        "cel_closure_violations": sum(
            closure_violations(cel_art[i]["rule"], cel_art[i]["sigma"])
            for i in (0, 85, 170, 255)),
        "cel_locality_violations": locality_violations(
            local_update(cel_art[0]["rule"]), window_configs(cel_art, rng)),
        "cel_alphabet_size_range": [min(len(a["sigma"]) for a in cel_art),
                                    max(len(a["sigma"]) for a in cel_art)],
        "hostiles_undetected": 13 - out["hostiles"]["hostiles_detected"],
        "nulls_reproducing_target": out["nulls"]["total_reproduced"],
    }
    gates = [
        all(out["registered_universal"].values()),
        out["parent_register_census_reproduced"]["agrees"],
        out["hostiles"]["hostiles_detected"] == 13,
        out["no_alarm"]["realization_mismatches"] == 0,
        out["no_alarm"]["cap_hits"] == 0,
        out["no_alarm"]["cel_closure_violations"] == 0,
        out["no_alarm"]["cel_locality_violations"] == 0,
        out["no_alarm"]["nulls_reproducing_target"] == 0,
        out["developmental_search_burden"]["CEL"][
            "unused_entry_shortcut_validation"]["failures"] == 0,
    ]
    out["gates_passed"] = sum(1 for g in gates if g)
    out["gates_total"] = len(gates)
    out["terminal"] = ("GMI_833_AG6_UNIVERSAL_BASES_V1_ALL_GREEN"
                       if all(gates) else "GMI_833_AG6_UNIVERSAL_BASES_V1_RED")
    return out


if __name__ == "__main__":
    receipt = main()
    here = os.path.dirname(os.path.abspath(__file__))
    blob = json.dumps(receipt, indent=1, sort_keys=True)
    with open(os.path.join(here, "RESULT_V1.json"), "w") as fh:
        fh.write(blob + "\n")
    print(blob)
    print("sha256", hashlib.sha256((blob + "\n").encode("utf-8")).hexdigest())
