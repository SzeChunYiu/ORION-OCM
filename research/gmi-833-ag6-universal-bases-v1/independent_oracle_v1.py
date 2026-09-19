"""AG6 route B - materially independent oracle.

Imports NOTHING from ag6_universal_bases_v1.py and nothing from any parent
package.  It rebuilds MEALY_2x2 and the word set from their definitions and
recomputes every quantity in the two-route agreement set by a different
mechanism:

  * the combinatory basis is checked by evaluating the SOURCE LAMBDA TERM
    directly under normal order with capture-avoiding substitution, comparing
    de Bruijn normal forms - bracket abstraction and the S/K machine are both
    bypassed, so the compiler and the reduction engine are independently checked;
  * the cellular basis is run as an explicit rule TABLE applied as a block map
    over shifted sequences (Curtis-Hedlund-Lyndon form), not as an index loop
    over a closure, with the alphabet closed by a worklist rather than by
    repeated full scans;
  * the register basis is re-derived from the declared compiler specification
    with a different code shape and an integer-coded dispatch interpreter;
  * Kendall's five counts come from a Fenwick tree sweep plus value-multiplicity
    arithmetic instead of the O(n^2) pair loop;
  * the Pareto frontier comes from a sort-and-sweep instead of the O(n^2)
    domination loop.

NOT in the agreement set, and declared as such: the combinatory STEP counts.
A contraction count is a property of a reduction strategy and representation;
route B counts beta-steps on lambda terms, which is a different quantity.  This
mirrors AJ5/AG5, where charged instruction counts are excluded from transfer.

    python3 -I -B research/gmi-833-ag6-universal-bases-v1/independent_oracle_v1.py
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.setrecursionlimit(200000)

# --------------------------------------------------------------------------
# scope, rebuilt from the definition
# --------------------------------------------------------------------------

def bits4():
    return [(a, b, c, d) for a in (0, 1) for b in (0, 1)
            for c in (0, 1) for d in (0, 1)]


KEYS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def words_upto(n):
    acc = [()]
    out = [()]
    for _ in range(n):
        acc = [w + (b,) for w in acc for b in (0, 1)]
        out.extend(acc)
    return out


WORDS = words_upto(3)
MACHINES = []
for db in bits4():
    for ob in bits4():
        MACHINES.append((dict(zip(KEYS, db)), dict(zip(KEYS, ob))))


def transduce(delta, out, w):
    q = 0
    acc = []
    for a in w:
        acc.append(out[(q, a)])
        q = delta[(q, a)]
    return tuple(acc)


def behaviour(delta, out):
    return tuple(transduce(delta, out, w) for w in WORDS)


def capability(delta, out):
    total = 0
    for w in WORDS:
        g = transduce(delta, out, w)
        total += (1 if g == tuple(w) else 0)
        total += (1 if g == tuple(1 - a for a in w) else 0)
        total += (1 if g == tuple([0] * len(w)) else 0)
    return total


# --------------------------------------------------------------------------
# CMB via a direct lambda evaluator
# --------------------------------------------------------------------------

def lam(v, b):
    return ("L", v, b)


def ap(*xs):
    t = xs[0]
    for y in xs[1:]:
        t = ("A", t, y)
    return t


def vr(n):
    return ("V", n)


TRUE = lam("p", lam("q", vr("p")))
FALSE = lam("p", lam("q", vr("q")))


def cb(b):
    return TRUE if b == 1 else FALSE


NIL = lam("c", lam("n", vr("n")))
CONS = lam("h", lam("t", lam("c", lam("n",
       ap(vr("c"), vr("h"), ap(vr("t"), vr("c"), vr("n")))))))


def machine_term(delta, out):
    O = lam("s", lam("a", ap(vr("s"),
        ap(vr("a"), cb(out[(0, 1)]), cb(out[(0, 0)])),
        ap(vr("a"), cb(out[(1, 1)]), cb(out[(1, 0)])))))
    N = lam("s", lam("a", ap(vr("s"),
        ap(vr("a"), cb(1 - delta[(0, 1)]), cb(1 - delta[(0, 0)])),
        ap(vr("a"), cb(1 - delta[(1, 1)]), cb(1 - delta[(1, 0)])))))
    STEP = lam("a", lam("k", lam("s",
        ap(CONS, ap(O, vr("s"), vr("a")), ap(vr("k"), ap(N, vr("s"), vr("a")))))))
    return lam("w", ap(vr("w"), STEP, lam("s", NIL), cb(1)))


def word_term(w):
    body = vr("n")
    for a in reversed(w):
        body = ap(vr("c"), cb(a), body)
    return lam("c", lam("n", body))


_FRESH = [0]


def freevars(t):
    k = t[0]
    if k == "V":
        return set([t[1]])
    if k == "A":
        return freevars(t[1]) | freevars(t[2])
    s = freevars(t[2])
    s.discard(t[1])
    return s


def subst(t, x, s):
    k = t[0]
    if k == "V":
        return s if t[1] == x else t
    if k == "A":
        return ("A", subst(t[1], x, s), subst(t[2], x, s))
    if t[1] == x:
        return t
    if t[1] in freevars(s):
        _FRESH[0] += 1
        fresh = "#%d" % _FRESH[0]
        body = subst(t[2], t[1], vr(fresh))
        return ("L", fresh, subst(body, x, s))
    return ("L", t[1], subst(t[2], x, s))


def beta_nf(t, budget):
    steps = 0
    while True:
        t2, did, s = _one(t, budget - steps)
        steps += s
        if not did:
            return t, steps
        t = t2
        if steps > budget:
            raise RuntimeError("budget")


def _one(t, budget):
    k = t[0]
    if k == "V":
        return t, False, 0
    if k == "L":
        b, did, s = _one(t[2], budget)
        return (("L", t[1], b), did, s) if did else (t, False, 0)
    f, x = t[1], t[2]
    if f[0] == "L":
        return subst(f[2], f[1], x), True, 1
    f2, did, s = _one(f, budget)
    if did:
        return ("A", f2, x), True, s
    x2, did, s = _one(x, budget)
    if did:
        return ("A", f, x2), True, s
    return t, False, 0


def debruijn(t, env=None):
    env = env or []
    k = t[0]
    if k == "V":
        for i, n in enumerate(env):
            if n == t[1]:
                return ("b", i)
        return ("f", t[1])
    if k == "A":
        return ("a", debruijn(t[1], env), debruijn(t[2], env))
    return ("l", debruijn(t[2], [t[1]] + env))


# --------------------------------------------------------------------------
# CMB size: the declared optimized bracket abstraction, written as a worklist
# --------------------------------------------------------------------------

def to_cl(t):
    """lambda -> pure S,K, with the declared Curry-optimized abstraction."""
    k = t[0]
    if k == "V":
        return ("v", t[1])
    if k == "A":
        return ("@", to_cl(t[1]), to_cl(t[2]))
    return bracket(t[1], to_cl(t[2]))


I_CL = ("@", ("@", "S", "K"), "K")


def cl_free(u, seen=None):
    out = set()
    stack = [u]
    while stack:
        z = stack.pop()
        if isinstance(z, str):
            continue
        if z[0] == "v":
            out.add(z[1])
        else:
            stack.append(z[1])
            stack.append(z[2])
    return out


def bracket(x, u):
    if u == ("v", x):
        return I_CL
    free = cl_free(u)
    if x not in free:
        return ("@", "K", u)
    if u[2] == ("v", x) and x not in cl_free(u[1]):
        return u[1]
    return ("@", ("@", "S", bracket(x, u[1])), bracket(x, u[2]))


def cl_serialize(u):
    """Canonical bracketed string; size is recovered by token counting."""
    if isinstance(u, str):
        return u
    return "(" + cl_serialize(u[1]) + " " + cl_serialize(u[2]) + ")"


def cl_size_by_tokens(u):
    s = cl_serialize(u)
    leaves = s.count("S") + s.count("K")
    apps = s.count("(")
    return leaves + apps


# --------------------------------------------------------------------------
# REG, re-derived from the declared specification, integer-coded interpreter
# --------------------------------------------------------------------------

REGS = ["x", "s", "z0", "z1"]
OPUNITS = {"READ": 3, "INC": 3, "EMIT": 3, "DECJZ": 4, "HALT": 1}


def reg_program(delta, out):
    rows = [
        ("P", "INC", "z1", "L0", None),
        ("L0", "READ", "x", "L1", None),
        ("L1", "DECJZ", "x", "L2", "A0"),
        ("L2", "DECJZ", "x", "L3", "A1"),
        ("L3", "HALT", None, None, None),
        ("A0", "DECJZ", "s", "C10", "C00"),
        ("A1", "DECJZ", "s", "C11", "C01"),
    ]
    for q in (0, 1):
        for a in (0, 1):
            lab = "C%d%d" % (q, a)
            tgt = ("D%d%d" % (q, a)) if delta[(q, a)] else "L0"
            rows.append((lab, "EMIT", "z%d" % out[(q, a)], tgt, None))
            if delta[(q, a)]:
                rows.append(("D%d%d" % (q, a), "INC", "s", "L0", None))
    return rows


def reg_size_rows(rows):
    return len(REGS) + 1 + sum(OPUNITS[r[1]] for r in rows)


def reg_execute(rows, w):
    index = dict((r[0], i) for i, r in enumerate(rows))
    ridx = dict((r, i) for i, r in enumerate(REGS))
    code = []
    for r in rows:
        code.append((r[1],
                     ridx.get(r[2], -1),
                     index.get(r[3], -1),
                     index.get(r[4], -1)))
    vals = [0] * len(REGS)
    stream = list(w) + [2]
    pc = index["P"]
    pos = 0
    emitted = []
    steps = 0
    while steps <= 6 * len(w) + 10:
        op, r, n1, n2 = code[pc]
        if op == "HALT":
            return tuple(emitted), steps
        steps += 1
        if op == "READ":
            if pos >= len(stream):
                return None, steps
            vals[r] = stream[pos]
            pos += 1
            pc = n1
        elif op == "INC":
            vals[r] += 1
            pc = n1
        elif op == "EMIT":
            if vals[r] not in (0, 1):
                return None, steps
            emitted.append(vals[r])
            pc = n1
        else:
            if vals[r] == 0:
                pc = n2
            else:
                vals[r] -= 1
                pc = n1
    return None, steps


# --------------------------------------------------------------------------
# CEL as an explicit table applied as a block map over shifted sequences
# --------------------------------------------------------------------------

QUI = ("-", "-", "-")


def cel_local(delta, out):
    def d(l, c, r):
        ci, co, ch = c
        if ch == "A" or ch == "B":
            if ci == "0" or ci == "1":
                return ("-", str(out[(0 if ch == "A" else 1, int(ci))]), "-")
            return (ci, co, "H")
        if ch == "H":
            return c
        li = l[0]
        lh = l[2]
        if (lh == "A" or lh == "B") and (li == "0" or li == "1"):
            return (ci, co, "A" if delta[(0 if lh == "A" else 1, int(li))] == 0 else "B")
        return c
    return d


def cel_start(w):
    cells = [(str(b), "-", "-") for b in w]
    if cells:
        cells[0] = (cells[0][0], "-", "A")
        cells.append(QUI)
    else:
        cells = [("-", "-", "A")]
    return tuple(cells)


def cel_alphabet_worklist(d, delta, out):
    sigma = set([QUI])
    for w in WORDS:
        sigma.update(cel_start(w))
    work = list(sigma)
    while work:
        cur = sorted(sigma)
        added = []
        for l in cur:
            for c in cur:
                for r in cur:
                    v = d(l, c, r)
                    if v not in sigma:
                        sigma.add(v)
                        added.append(v)
        work = added
    return tuple(sorted(sigma))


def cel_table(d, sigma):
    tbl = {}
    for l in sigma:
        for c in sigma:
            for r in sigma:
                tbl[(l, c, r)] = d(l, c, r)
    return tbl


def cel_block_map(conf, tbl, d):
    left = (QUI,) + conf[:-1]
    right = conf[1:] + (QUI,)
    return tuple(tbl.get(k, d(*k)) for k in zip(left, conf, right))


def cel_execute(tbl, d, w):
    conf = cel_start(w)
    steps = 0
    while steps <= len(w) + 4:
        if not any(cell[2] in ("A", "B") for cell in conf):
            break
        conf = cel_block_map(conf, tbl, d)
        steps += 1
    if any(cell[2] in ("A", "B") for cell in conf):
        return None, steps
    acc = []
    for i in range(len(w)):
        if conf[i][1] == "-":
            return None, steps
        acc.append(int(conf[i][1]))
    return tuple(acc), steps


# --------------------------------------------------------------------------
# Kendall by Fenwick sweep; Pareto by sort-and-sweep
# --------------------------------------------------------------------------

class Fenwick(object):
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i):
        i += 1
        while i <= self.n:
            self.t[i] += 1
            i += i & (-i)

    def pref(self, i):
        i += 1
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & (-i)
        return s


def kendall_fenwick(xs, ys):
    n = len(xs)
    total = n * (n - 1) // 2
    ycodes = sorted(set(ys))
    ymap = dict((v, i) for i, v in enumerate(ycodes))
    order = sorted(range(n), key=lambda i: (xs[i], ys[i]))
    bit = Fenwick(len(ycodes))
    conc = disc = 0
    placed = 0
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and xs[order[j]] == xs[order[i]]:
            j += 1
        for k in range(i, j):
            yc = ymap[ys[order[k]]]
            less = bit.pref(yc - 1) if yc > 0 else 0
            lesseq = bit.pref(yc)
            conc += less
            disc += placed - lesseq
        for k in range(i, j):
            bit.add(ymap[ys[order[k]]])
            placed += 1
        i = j
    cx = {}
    cy = {}
    cxy = {}
    for a, b in zip(xs, ys):
        cx[a] = cx.get(a, 0) + 1
        cy[b] = cy.get(b, 0) + 1
        cxy[(a, b)] = cxy.get((a, b), 0) + 1
    tx = sum(v * (v - 1) // 2 for v in cx.values())
    ty = sum(v * (v - 1) // 2 for v in cy.values())
    tb = sum(v * (v - 1) // 2 for v in cxy.values())
    return {"pairs": total, "concordant": conc, "discordant": disc,
            "tied_first_only": tx - tb, "tied_second_only": ty - tb,
            "tied_both": tb,
            "tau_a": Fraction(conc - disc, total),
            "tau_restricted": (Fraction(conc - disc, conc + disc)
                               if conc + disc else None)}


def pareto_sweep(qs, cs):
    """Sort-and-sweep.  i is dominated iff some point with strictly smaller cost
    has capability >= Q_i, or some point with equal cost has capability > Q_i."""
    n = len(qs)
    order = sorted(range(n), key=lambda i: (cs[i], -qs[i]))
    front = []
    best_before = None
    i = 0
    while i < n:
        j = i
        while j < n and cs[order[j]] == cs[order[i]]:
            j += 1
        group = order[i:j]
        gmax = max(qs[k] for k in group)
        for k in group:
            if qs[k] == gmax and (best_before is None or qs[k] > best_before):
                front.append(k)
        if best_before is None or gmax > best_before:
            best_before = gmax
        i = j
    return tuple(sorted(front))


# --- independent SK machinery, used only for the geometry agreement ----------

def sk_redex_paths(t, path=()):
    """Recursive generator; a different traversal from route A's explicit stack."""
    out = []
    if isinstance(t, tuple):
        head = t
        k = 0
        while isinstance(head, tuple):
            head = head[0]
            k += 1
        if (head == "K" and k >= 2) or (head == "S" and k >= 3):
            out.append(path)
        out.extend(sk_redex_paths(t[0], path + (0,)))
        out.extend(sk_redex_paths(t[1], path + (1,)))
    return out


def sk_spine(t):
    args = []
    head = t
    while isinstance(head, tuple):
        args.append(head[1])
        head = head[0]
    args.reverse()
    return head, args


def sk_contract_root(t):
    head, args = sk_spine(t)
    if head == "K":
        new, rest = args[0], args[2:]
    else:
        new = ((args[0], args[2]), (args[1], args[2]))
        rest = args[3:]
    for a in rest:
        new = (new, a)
    return new


def sk_contract(t, path):
    if not path:
        return sk_contract_root(t)
    if path[0] == 0:
        return (sk_contract(t[0], path[1:]), t[1])
    return (t[0], sk_contract(t[1], path[1:]))


def sk_nf(t, budget):
    """Naive normal-order normaliser: repeat the leftmost-outermost step."""
    steps = 0
    while True:
        t2, ok = sk_lo_step(t)
        if not ok:
            return t, steps
        t = t2
        steps += 1
        if steps > budget:
            raise RuntimeError("sk budget")


def sk_lo_step(t):
    head, args = sk_spine(t)
    if (head == "K" and len(args) >= 2) or (head == "S" and len(args) >= 3):
        return sk_contract_root(t), True
    for i, a in enumerate(args):
        a2, ok = sk_lo_step(a)
        if ok:
            new = head
            for j, b in enumerate(args):
                new = (new, a2 if j == i else b)
            return new, True
    return t, False


def sk_from_cl(u):
    if isinstance(u, str):
        return u
    return (sk_from_cl(u[1]), sk_from_cl(u[2]))


def cmb_geometry_oracle(delta, out, w, confluence=False):
    term = sk_from_cl(to_cl(machine_term(delta, out)))
    wt = sk_from_cl(to_cl(word_term(w)))
    pairify = sk_from_cl(to_cl(lam("h", lam("r", lam("k",
                 ap(vr("k"), vr("h"), vr("r")))))))
    t0 = (((term, wt), pairify), ("K", "S"))
    corridor = [t0]
    t = t0
    while True:
        t2, ok = sk_lo_step(t)
        if not ok:
            break
        t = t2
        corridor.append(t)
        if len(corridor) > 4000:
            break
    degs = [len(sk_redex_paths(c)) for c in corridor]
    branch = sum(1 for d in degs if d >= 2)
    same = 0
    if confluence:
        for c in corridor:
            ps = sk_redex_paths(c)
            if len(ps) < 2:
                continue
            nfs = set()
            for p in ps:
                nfs.add(sk_nf(sk_contract(c, p), 200000)[0])
            if len(nfs) == 1:
                same += 1
    return {"corridor_length": len(corridor), "max_out_degree": max(degs),
            "branching_configurations": branch,
            "branching_all_successors_share_normal_form": same}


def reg_corridor(rows, w):
    index = dict((r[0], i) for i, r in enumerate(rows))
    ridx = dict((r, i) for i, r in enumerate(REGS))
    vals = [0] * len(REGS)
    stream = list(w) + [2]
    pc = index["P"]
    pos = 0
    emitted = []
    trace = [(pc, tuple(vals), pos, tuple(emitted))]
    while len(trace) <= 6 * len(w) + 12:
        r = rows[pc]
        op = r[1]
        if op == "HALT":
            break
        if op == "READ":
            vals[ridx[r[2]]] = stream[pos]
            pos += 1
            pc = index[r[3]]
        elif op == "INC":
            vals[ridx[r[2]]] += 1
            pc = index[r[3]]
        elif op == "EMIT":
            emitted.append(vals[ridx[r[2]]])
            pc = index[r[3]]
        else:
            if vals[ridx[r[2]]] == 0:
                pc = index[r[4]]
            else:
                vals[ridx[r[2]]] -= 1
                pc = index[r[3]]
        trace.append((pc, tuple(vals), pos, tuple(emitted)))
    return trace


def cel_corridor_len(machine, w):
    delta, out = machine
    d = cel_local(delta, out)
    sigma = cel_alphabet_worklist(d, delta, out)
    tbl = cel_table(d, sigma)
    conf = cel_start(w)
    n = 1
    while any(cell[2] in ("A", "B") for cell in conf) and n <= len(w) + 5:
        conf = cel_block_map(conf, tbl, d)
        n += 1
    return n


def frac(x):
    return "%d/%d" % (x.numerator, x.denominator) if x is not None else None


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main():
    res = {"schema": "GMI833AG6UniversalBasesOracleV1", "route": "B",
           "independent_of": "ag6_universal_bases_v1.py"}
    res["machines"] = len(MACHINES)
    res["words"] = len(WORDS)
    res["distinct_behaviours_on_W"] = len(set(behaviour(d, o) for d, o in MACHINES))

    reg_ok = cmb_ok = cel_ok = 0
    reg_steps = []
    cel_steps = []
    reg_sizes = []
    cmb_sizes = []
    cel_sizes = []
    qs = []
    tasks = 0
    for delta, out in MACHINES:
        qs.append(capability(delta, out))
        rows = reg_program(delta, out)
        reg_sizes.append(reg_size_rows(rows))
        cl = to_cl(machine_term(delta, out))
        cmb_sizes.append(cl_size_by_tokens(cl))
        d = cel_local(delta, out)
        sigma = cel_alphabet_worklist(d, delta, out)
        tbl = cel_table(d, sigma)
        support = sum(1 for k, v in tbl.items() if v != k[1])
        cel_sizes.append(len(sigma) + 4 * support)
        mt = machine_term(delta, out)
        rtot = ctot = 0
        good_r = good_c = good_e = True
        for w in WORDS:
            tasks += 1
            want = transduce(delta, out, w)
            got, st = reg_execute(rows, w)
            rtot += st
            if got != want:
                good_r = False
            got, st = cel_execute(tbl, d, w)
            ctot += st
            if got != want:
                good_e = False
            lamres, _s = beta_nf(("A", mt, word_term(w)), 200000)
            if debruijn(lamres) != debruijn(beta_nf(word_term(want), 200000)[0]):
                good_c = False
        reg_steps.append(rtot)
        cel_steps.append(ctot)
        reg_ok += 1 if good_r else 0
        cmb_ok += 1 if good_c else 0
        cel_ok += 1 if good_e else 0

    res["tasks"] = tasks
    res["machines_realized"] = {"REG": reg_ok, "CMB": cmb_ok, "CEL": cel_ok}
    res["size_range"] = {"REG": [min(reg_sizes), max(reg_sizes)],
                         "CMB": [min(cmb_sizes), max(cmb_sizes)],
                         "CEL": [min(cel_sizes), max(cel_sizes)]}
    res["steps_range"] = {"REG": [min(reg_steps), max(reg_steps)],
                          "CEL": [min(cel_steps), max(cel_steps)]}
    res["capability"] = {"min": min(qs), "max": max(qs),
                         "distinct": len(set(qs))}
    sizes = {"REG": reg_sizes, "CMB": cmb_sizes, "CEL": cel_sizes}
    kk = {}
    for a, b in (("REG", "CMB"), ("REG", "CEL"), ("CMB", "CEL")):
        k = kendall_fenwick(sizes[a], sizes[b])
        k["tau_a"] = frac(k["tau_a"])
        k["tau_restricted"] = frac(k["tau_restricted"])
        kk["size__%s_vs_%s" % (a, b)] = k
    res["kendall"] = kk
    fr = {}
    for name in ("REG", "CMB", "CEL"):
        f = pareto_sweep(qs, sizes[name])
        fr[name] = {"frontier_size": len(f), "frontier": list(f)}
    fr["all_three_equal"] = (set(fr["REG"]["frontier"]) ==
                             set(fr["CMB"]["frontier"]) ==
                             set(fr["CEL"]["frontier"]))
    fr["REG_vs_CMB_equal"] = set(fr["REG"]["frontier"]) == set(fr["CMB"]["frontier"])
    fr["REG_vs_CEL_symmetric_difference"] = len(
        set(fr["REG"]["frontier"]) ^ set(fr["CEL"]["frontier"]))
    fr["CMB_vs_CEL_symmetric_difference"] = len(
        set(fr["CMB"]["frontier"]) ^ set(fr["CEL"]["frontier"]))
    res["pareto_size_coordinate"] = fr
    geo = {}
    for idx in (0, 85, 170, 255):
        dl, ou = MACHINES[idx]
        geo[str(idx)] = cmb_geometry_oracle(dl, ou, (0, 1, 0),
                                            confluence=(idx == 0))
    res["cmb_geometry"] = geo
    res["reg_corridor_length"] = len(reg_corridor(reg_program(*MACHINES[0]), (0, 1, 0)))
    res["cel_corridor_length"] = cel_corridor_len(MACHINES[0], (0, 1, 0))
    res["excluded_from_agreement_set"] = [
        "CMB_step_counts__contraction_counts_are_strategy_and_representation_relative"
    ]
    return res


if __name__ == "__main__":
    r = main()
    here = os.path.dirname(os.path.abspath(__file__))
    blob = json.dumps(r, indent=1, sort_keys=True)
    with open(os.path.join(here, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(blob + "\n")
    print(blob)
