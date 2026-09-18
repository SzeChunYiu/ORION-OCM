"""Route B independent oracle for GMI #833 Section I.

This file deliberately shares NO module with the Route A executor and imports
nothing from it. Rational helpers are duplicated inline. Every contested
quantity is recomputed by a materially different method:

* IL-1 admissibility and closure: literal tuple enumeration and explicit set
  operations instead of predicate composition.
* IL-2 / IL-3 expected probe counts: exhaustive enumeration over every
  placement of the improving set and every probe order, averaged with exact
  Fractions. The closed form (d+1)/(m+1) is never used to produce the number,
  only compared against afterwards.
* IL-4 Jacobians: explicit enumeration of every directed source-to-output path
  and summation of path products. Sweep and elimination costs by literal
  simulation.

The registered objects are re-declared here by independent transcription; a
cross-check refuses to proceed if the two declarations disagree.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations
import json
import os
import sys

WHERE = os.path.dirname(os.path.abspath(__file__))


def refuse(msg):
    raise ValueError(msg)


# --- IL-2 / IL-3 by exhaustive placement and order enumeration --------------

def probes_for_order(marked, order):
    """Literal simulation: walk the probe order, stop at the first marked."""
    step = 0
    for idx in order:
        step += 1
        if idx in marked:
            return step
    refuse("no marked successor reached; the improving set must be nonempty")


def expected_probes_by_enumeration(d, m):
    """Average over every C(d,m) placement and every one of the d! probe
    orders. No closed form is consulted."""
    if not (1 <= m <= d):
        refuse("need 1 <= m <= d")
    placements = list(combinations(range(d), m))
    orders = list(permutations(range(d)))
    total = Q(0)
    count = 0
    for marked in placements:
        mk = set(marked)
        for order in orders:
            total += Q(probes_for_order(mk, order))
            count += 1
    return total / Q(count)


def expected_probes_per_order(d, m):
    """Per-order averages over placements; every order must give the same
    value, which is the order-independence half of the lemma."""
    placements = list(combinations(range(d), m))
    vals = []
    for order in permutations(range(d)):
        total = Q(0)
        for marked in placements:
            total += Q(probes_for_order(set(marked), order))
        vals.append(total / Q(len(placements)))
    return vals


def worst_case_by_enumeration(d, m):
    placements = list(combinations(range(d), m))
    worst = 0
    for marked in placements:
        mk = set(marked)
        for order in permutations(range(d)):
            v = probes_for_order(mk, order)
            if v > worst:
                worst = v
    return worst


def repeat_waste_witness(d, m):
    """A probe sequence that repeats an index is strictly worse."""
    placements = list(combinations(range(d), m))
    clean = tuple(range(d))
    dirty = (0,) + tuple(range(d))
    a = Q(0)
    b = Q(0)
    for marked in placements:
        mk = set(marked)
        a += Q(probes_for_order(mk, clean))
        b += Q(probes_for_order(mk, dirty))
    a = a / Q(len(placements))
    b = b / Q(len(placements))
    return {"clean": str(a), "with_one_repeat": str(b), "repeat_is_worse": b > a}


def oracle_paths():
    """Independent transcription of the registered paths."""
    out = []
    for d in range(1, 7):
        for m in range(1, d + 1):
            for n in (1, 2, 3):
                out.append(("uniform_d%d_m%d_n%d" % (d, m, n), tuple([(d, m)] * n)))
    mixed = [
        ((1, 1), (2, 1)), ((2, 1), (3, 1)), ((3, 1), (3, 3)), ((4, 1), (2, 2)),
        ((5, 2), (2, 1), (6, 3)), ((6, 1), (6, 6)), ((2, 2), (3, 2), (4, 3)),
        ((5, 1), (5, 5), (3, 2)), ((4, 2), (4, 4)), ((6, 5), (2, 1)),
        ((3, 3), (3, 3), (3, 3)), ((6, 2), (5, 4), (4, 1), (2, 2)),
    ]
    for i, prof in enumerate(mixed):
        out.append(("mixed_%02d" % i, prof))
    return out


def oracle_ratio_grid():
    vals = set()
    for a in range(1, 13):
        for b in range(1, 7):
            vals.add(Q(a, b))
    return tuple(sorted(vals))


def oracle_il23():
    table = {}
    per_order_uniform = True
    for d in range(1, 7):
        for m in range(1, d + 1):
            table[(d, m)] = expected_probes_by_enumeration(d, m)
            vals = expected_probes_per_order(d, m)
            if len(set(vals)) != 1:
                per_order_uniform = False
    verdicts = {}
    for name, prof in oracle_paths():
        acc = Q(0)
        for (d, m) in prof:
            acc += table[(d, m)]
        mean = acc / Q(len(prof))
        row = {}
        for ratio in oracle_ratio_grid():
            # cost comparison done from the enumerated table, not a formula
            cost_point = acc
            cost_select = ratio * Q(len(prof))
            if cost_point < cost_select:
                row[str(ratio)] = "POINT_VALUE_ONLY_STRICTLY_DOMINATES"
            elif cost_point > cost_select:
                row[str(ratio)] = "SELECTION_CHANNEL_STRICTLY_DOMINATES"
            else:
                row[str(ratio)] = "EXACT_TIE_AT_BOUNDARY"
        verdicts[name] = {"rho_star": str(mean), "row": row}
    return {"local_table": dict(("%d,%d" % k, str(v)) for k, v in table.items()),
            "worst_case_table": dict(("%d,%d" % (d, m), worst_case_by_enumeration(d, m))
                                     for d in range(1, 7) for m in range(1, d + 1)),
            "per_order_averages_all_equal": per_order_uniform,
            "repeat_waste": dict(("%d,%d" % (d, m), repeat_waste_witness(d, m))
                                 for (d, m) in ((3, 1), (4, 2), (5, 1))),
            "verdicts": verdicts}


# --- IL-1 by literal enumeration -------------------------------------------

def oracle_scope():
    realizations = ("r0", "r1", "r2", "ra", "rb", "ru", "rv", "rz", "rq")
    histories = ("h0", "h1", "h2")
    coords = ("c_alpha", "c_beta")
    named = {("r0", "h0"): ("r1",), ("r1", "h1"): ("r2",),
             ("r0", "h1"): ("ra", "rb"), ("ra", "h1"): ("ru",),
             ("rb", "h1"): ("rv",), ("ru", "h1"): ("rz",), ("rv", "h1"): ("rz",)}
    delta = {}
    for r in realizations:
        for h in histories:
            delta[(r, h)] = named.get((r, h), ())
    budgets = ({"c_alpha": Q(0), "c_beta": Q(0)},
               {"c_alpha": Q(1), "c_beta": Q(1)},
               {"c_alpha": Q(9), "c_beta": Q(9)})
    return realizations, histories, coords, delta, budgets


def oracle_reach(delta, histories, realizations, r):
    """Transitive closure by repeated literal expansion to a fixed point."""
    cur = set([r])
    while True:
        nxt = set(cur)
        for x in cur:
            for h in histories:
                for y in delta[(x, h)]:
                    nxt.add(y)
        if nxt == cur:
            return cur
        cur = nxt


def oracle_law_table(realizations, histories, coords, delta, budgets,
                     targets, charges):
    """Build one law as an EXPLICIT TABLE over the registered grid. No closure,
    no predicate composition: every triple is written out."""
    tab = {}
    for r in realizations:
        for h in histories:
            for b in budgets:
                key = (r, h, tuple(b[c] for c in coords))
                ch = charges.get(r, dict((c, Q(0)) for c in coords))
                tgt = targets.get(r)
                over = False
                for c in coords:
                    if ch[c] > b[c]:
                        over = True
                allowed = [r] + list(delta[(r, h)])
                escapes = False
                if tgt is not None:
                    for t in tgt:
                        if tgt[t] != 0 and t not in allowed:
                            escapes = True
                if tgt is None or over or escapes:
                    tab[key] = ({r: Q(1)}, dict((c, Q(0)) for c in coords))
                else:
                    tab[key] = (dict(tgt), dict(ch))
    return tab


def oracle_laws():
    realizations, histories, coords, delta, budgets = oracle_scope()

    def c(a, b):
        return {"c_alpha": Q(a), "c_beta": Q(b)}

    spec = {
        "identity": ({}, {}),
        "step_r0_r1": ({"r0": {"r1": Q(1)}}, {"r0": c(1, 0)}),
        "step_r1_r2": ({"r1": {"r2": Q(1)}}, {"r1": c(1, 0)}),
        "split_r0": ({"r0": {"ra": Q(1, 2), "rb": Q(1, 2)}}, {"r0": c(0, 0)}),
        "stage_two": ({"ra": {"ru": Q(1)}, "rb": {"rv": Q(1)}},
                      {"ra": c(3, 0), "rb": c(0, 0)}),
        "stage_three": ({"ru": {"rz": Q(1)}, "rv": {"rz": Q(1)}},
                        {"ru": c(0, 0), "rv": c(5, 0)}),
        "costly": ({"r0": {"r1": Q(1)}, "r1": {"r2": Q(1)}},
                   {"r0": c(9, 9), "r1": c(9, 9)}),
    }
    return dict((k, oracle_law_table(realizations, histories, coords, delta,
                                     budgets, t, ch))
                for k, (t, ch) in spec.items())


def oracle_decide(tab, grade):
    """An independently written admissibility predicate. Walks the explicit
    table and returns the list of violated clause names."""
    realizations, histories, coords, delta, budgets = oracle_scope()
    bad = []
    for r in realizations:
        for h in histories:
            for b in budgets:
                key = (r, h, tuple(b[c] for c in coords))
                if key not in tab:
                    bad.append("A1")
                    continue
                dist, charge = tab[key]
                s = Q(0)
                for t in dist:
                    if not isinstance(dist[t], (int, Q)) or isinstance(dist[t], bool):
                        bad.append("A1")
                    elif dist[t] < 0:
                        bad.append("A1")
                    else:
                        s += dist[t]
                if s != 1:
                    bad.append("A1")
                if sorted(charge) != sorted(coords):
                    bad.append("A2")
                else:
                    for cc in coords:
                        if not isinstance(charge[cc], (int, Q)) or charge[cc] < 0:
                            bad.append("A2")
                    over = False
                    for cc in coords:
                        if charge[cc] > b[cc]:
                            over = True
                    if over:
                        zero = True
                        for cc in coords:
                            if charge[cc] != 0:
                                zero = False
                        if not (zero and dist == {r: Q(1)}):
                            bad.append("A3")
                if grade == "ONE_STEP":
                    allowed = [r] + list(delta[(r, h)])
                else:
                    allowed = sorted(oracle_reach(delta, histories,
                                                  realizations, r))
                for t in dist:
                    if dist[t] != 0 and t not in allowed:
                        bad.append("A4")
    return sorted(set(bad))


def oracle_mix_tables(t1, t2, lam, coords):
    out = {}
    for key in t1:
        d1, c1 = t1[key]
        d2, c2 = t2[key]
        d = {}
        for t in d1:
            d[t] = d.get(t, Q(0)) + lam * d1[t]
        for t in d2:
            d[t] = d.get(t, Q(0)) + (1 - lam) * d2[t]
        out[key] = (d, dict((c, lam * c1[c] + (1 - lam) * c2[c]) for c in coords))
    return out


def oracle_compose_tables(t2, t1):
    """Compose two explicit tables. The second stage is looked up at the
    residual budget, which may leave the registered grid, so the second law is
    re-tabulated on demand from its own spec by direct arithmetic."""
    realizations, histories, coords, delta, budgets = oracle_scope()
    ext = "h1"
    out = {}
    for r in realizations:
        for h in histories:
            for b in budgets:
                key = (r, h, tuple(b[c] for c in coords))
                d1, c1 = t1[key]
                resid = {}
                neg = False
                for c in coords:
                    resid[c] = b[c] - c1[c]
                    if resid[c] < 0:
                        neg = True
                if neg:
                    resid = dict((c, Q(0)) for c in coords)
                quiet = (d1 == {r: Q(1)}
                         and all(c1[c] == 0 for c in coords))
                d = {}
                worst = dict((c, Q(0)) for c in coords)
                for r1 in sorted(t for t in d1 if d1[t] != 0):
                    h2 = h if quiet else ext
                    k2 = (r1, h2, tuple(resid[c] for c in coords))
                    if k2 in t2:
                        d2, c2 = t2[k2]
                    else:
                        d2, c2 = oracle_stage_at(t2, r1, h2, resid)
                    for t in d2:
                        d[t] = d.get(t, Q(0)) + d1[r1] * d2[t]
                    for c in coords:
                        if c2[c] > worst[c]:
                            worst[c] = c2[c]
                out[key] = (d, dict((c, c1[c] + worst[c]) for c in coords))
    return out


def oracle_stage_at(tab, r, h, budget):
    """Evaluate a tabulated law at an off-grid budget: take the behaviour it
    shows at the largest registered budget it can afford, which for these laws
    is fully determined by whether the charge fits."""
    realizations, histories, coords, delta, budgets = oracle_scope()
    big = (r, h, tuple(budgets[-1][c] for c in coords))
    dist, charge = tab[big]
    fits = True
    for c in coords:
        if charge[c] > budget[c]:
            fits = False
    if fits:
        return dict(dist), dict(charge)
    return {r: Q(1)}, dict((c, Q(0)) for c in coords)


def oracle_closure_census():
    """The IL-1 closure census, recomputed entirely from explicit tables."""
    realizations, histories, coords, delta, budgets = oracle_scope()
    laws = oracle_laws()
    names = sorted(laws)
    base = {}
    for g in ("ONE_STEP", "CLOSURE"):
        for n in names:
            base[(g, n)] = oracle_decide(laws[n], g)
    lam_grid = [Q(i, 6) for i in range(7)]
    mix_cases = 0
    mix_fail = []
    for a in names:
        for b in names:
            for lam in lam_grid:
                m = oracle_mix_tables(laws[a], laws[b], lam, coords)
                for g in ("ONE_STEP", "CLOSURE"):
                    mix_cases += 1
                    bad = oracle_decide(m, g)
                    if not base[(g, a)] and not base[(g, b)] and bad:
                        mix_fail.append((a, b, str(lam), g, bad))
    comp_cases = 0
    comp_fail = []
    for a in names:
        for b in names:
            comp = oracle_compose_tables(laws[a], laws[b])
            comp_cases += 1
            bad = oracle_decide(comp, "CLOSURE")
            if not base[("CLOSURE", a)] and not base[("CLOSURE", b)] and bad:
                comp_fail.append((a, b, bad))
    one = oracle_compose_tables(laws["step_r1_r2"], laws["step_r0_r1"])
    ident = laws["identity"]
    left_id = oracle_compose_tables(laws["stage_two"], ident)
    right_id = oracle_compose_tables(ident, laws["stage_two"])
    two_sided = (left_id == laws["stage_two"] and right_id == laws["stage_two"])
    return {"law_population": len(names),
            "base_verdicts": dict(("%s|%s" % k, v) for k, v in base.items()),
            "mixture_cases": mix_cases, "mixture_failures": mix_fail,
            "composition_cases": comp_cases,
            "closure_composition_failures": comp_fail,
            "one_step_composite_clauses": oracle_decide(one, "ONE_STEP"),
            "closure_composite_clauses": oracle_decide(one, "CLOSURE"),
            "monoid_identity_two_sided": two_sided}


def oracle_scope_fingerprint():
    """A transcription fingerprint of the registered scope, so that Route A can
    refuse if the two declarations ever drift apart."""
    realizations, histories, coords, delta, budgets = oracle_scope()
    items = ["R:" + ",".join(realizations), "H:" + ",".join(histories),
             "C:" + ",".join(coords)]
    for k in sorted(delta):
        items.append("D:%s|%s->%s" % (k[0], k[1], ",".join(delta[k])))
    for b in budgets:
        items.append("B:" + ",".join("%s=%s" % (c, b[c]) for c in coords))
    return ";".join(items)


def oracle_one_step_counterexample():
    realizations, histories, coords, delta, budgets = oracle_scope()
    allowed = set(["r0"]) | set(delta[("r0", "h0")])
    reach = oracle_reach(delta, histories, realizations, "r0")
    composite_target = "r2"
    return {"one_step_allowed_at_r0_h0": sorted(allowed),
            "closure_reach_from_r0": sorted(reach),
            "composite_target": composite_target,
            "outside_one_step": composite_target not in allowed,
            "inside_closure": composite_target in reach}


def oracle_charge_subassociativity():
    """Recompute both bracketings of the worst-case charge by hand-rolled
    arithmetic on the registered three-stage witness."""
    d1 = {"ra": Q(1, 2), "rb": Q(1, 2)}          # stage one splits r0
    c1 = Q(0)
    c2 = {"ra": Q(3), "rb": Q(0)}                # stage two charges
    t2 = {"ra": "ru", "rb": "rv"}
    c3 = {"ru": Q(0), "rv": Q(5)}                # stage three charges
    left_nested = c1 + max(c2[r] + c3[t2[r]] for r in d1)
    right_nested = c1 + max(c2[r] for r in d1) + max(c3[t2[r]] for r in d1)
    return {"left_nested": str(left_nested), "right_nested": str(right_nested),
            "subassociative": left_nested <= right_nested,
            "strict": left_nested < right_nested}


# --- IL-4 by path enumeration ----------------------------------------------

def oracle_graphs():
    """Independent transcription of the registered computation graphs."""
    g = {}

    def chain(nsrc, depth):
        sources = tuple("x%d" % i for i in range(nsrc))
        interior = tuple("v%d" % i for i in range(depth))
        edges = {}
        for i, s in enumerate(sources):
            edges[(s, "v0")] = Q(i + 2)
        for i in range(1, depth):
            edges[("v%d" % (i - 1), "v%d" % i)] = Q(i + 3, i + 1)
        return {"sources": sources, "interior": interior,
                "outputs": ("v%d" % (depth - 1),), "edges": edges}

    g["source_chain_n4"] = chain(4, 4)
    g["deep_chain_n6"] = chain(6, 6)
    g["fan_in_n5"] = {
        "sources": tuple("x%d" % i for i in range(5)),
        "interior": ("v0", "v1", "v2", "v3"), "outputs": ("v3",),
        "edges": {("x0", "v0"): Q(2), ("x1", "v0"): Q(3), ("x2", "v1"): Q(5),
                  ("x3", "v1"): Q(7), ("x4", "v1"): Q(11),
                  ("v0", "v2"): Q(1, 2), ("v1", "v2"): Q(1, 3),
                  ("v2", "v3"): Q(4, 5)}}
    g["fan_out_p4"] = {
        "sources": ("x0",), "interior": ("v0", "v1", "y0", "y1", "y2", "y3"),
        "outputs": ("y0", "y1", "y2", "y3"),
        "edges": {("x0", "v0"): Q(2), ("v0", "v1"): Q(3),
                  ("v1", "y0"): Q(1, 2), ("v1", "y1"): Q(1, 3),
                  ("v0", "y2"): Q(1, 5), ("v1", "y3"): Q(1, 7)}}
    g["square_n3_p3"] = {
        "sources": ("x0", "x1", "x2"),
        "interior": ("v0", "v1", "v2", "y0", "y1", "y2"),
        "outputs": ("y0", "y1", "y2"),
        "edges": {("x0", "v0"): Q(2), ("x1", "v0"): Q(3), ("x2", "v1"): Q(5),
                  ("v0", "v1"): Q(7), ("v1", "v2"): Q(9),
                  ("v0", "y0"): Q(1, 2), ("v2", "y1"): Q(1, 3),
                  ("v2", "y2"): Q(1, 5)}}
    g["bridge_n3_p3"] = {
        "sources": ("x0", "x1", "x2"), "interior": ("v0", "v1", "y0", "y1", "y2"),
        "outputs": ("y0", "y1", "y2"),
        "edges": {("x0", "v0"): Q(2), ("x1", "v0"): Q(3), ("x2", "v0"): Q(5),
                  ("v0", "v1"): Q(7), ("v1", "y0"): Q(11), ("v1", "y1"): Q(13),
                  ("v1", "y2"): Q(17)}}
    g["skip_waist_n2_p2"] = {
        "sources": ("x0", "x1"), "interior": ("v0", "v1", "v2", "y0", "y1"),
        "outputs": ("y0", "y1"),
        "edges": {("x0", "v0"): Q(2), ("x1", "v0"): Q(3),
                  ("v0", "v1"): Q(5), ("v1", "v2"): Q(7), ("v0", "v2"): Q(11),
                  ("v2", "y0"): Q(13), ("v2", "y1"): Q(17)}}
    return g


def all_paths(G, src, dst):
    """Every directed path from src to dst, enumerated literally."""
    out = []
    stack = [(src, [src])]
    while stack:
        node, sofar = stack.pop()
        if node == dst and len(sofar) > 1:
            out.append(tuple(sofar))
            continue
        for (u, w) in G["edges"]:
            if u == node and w not in sofar:
                stack.append((w, sofar + [w]))
    return out


def jacobian_by_path_sum(G):
    rows = []
    for o in G["outputs"]:
        row = []
        for s in G["sources"]:
            acc = Q(0)
            for path in all_paths(G, s, o):
                prod = Q(1)
                for i in range(len(path) - 1):
                    prod *= G["edges"][(path[i], path[i + 1])]
                acc += prod
            row.append(acc)
        rows.append(tuple(row))
    return tuple(rows)


def oracle_peak_live(G):
    """Independent live-set computation. For every prefix of the evaluation
    order, count internal values already produced that are still live, where a
    value is live from production to its last consumption inclusive and an
    output stays live to the end."""
    order = list(G["interior"])
    consumers = {}
    for (u, w) in G["edges"]:
        if u in order:
            consumers.setdefault(u, []).append(order.index(w))
    peak = 0
    for k in range(len(order)):
        live = 0
        for j in range(k + 1):
            v = order[j]
            if v in G["outputs"] or j == k:
                live += 1
                continue
            cs = consumers.get(v, [])
            if any(c >= k for c in cs):
                live += 1
        if live > peak:
            peak = live
    return peak


def oracle_sweep_costs(G):
    """Literal simulation of one sweep in each direction, counting every
    multiply-accumulate individually."""
    fwd = 0
    for v in G["interior"]:
        for (u, w) in G["edges"]:
            if w == v:
                fwd += 1
    rev = 0
    for v in reversed(list(G["interior"])):
        for (u, w) in G["edges"]:
            if w == v:
                rev += 1
    return fwd, rev


def oracle_elimination(G, order):
    edges = dict(G["edges"])
    cost = 0
    for v in order:
        preds = sorted(set(u for (u, w) in edges if w == v))
        succs = sorted(set(w for (u, w) in edges if u == v))
        new = {}
        for u in preds:
            for z in succs:
                new[(u, z)] = new.get((u, z), Q(0)) + edges[(u, v)] * edges[(v, z)]
                cost += 1
        for u in preds:
            del edges[(u, v)]
        for z in succs:
            del edges[(v, z)]
        for k, val in new.items():
            edges[k] = edges.get(k, Q(0)) + val
    jac = tuple(tuple(edges.get((s, o), Q(0)) for s in G["sources"])
                for o in G["outputs"])
    return jac, cost


def oracle_order_census(G):
    elim = tuple(v for v in G["interior"] if v not in G["outputs"])
    ref = jacobian_by_path_sum(G)
    topo = elim
    revtopo = tuple(reversed(elim))
    best = None
    best_orders = []
    consistent = True
    costs = {}
    total = 0
    for order in permutations(elim):
        jac, cost = oracle_elimination(G, order)
        total += 1
        if jac != ref:
            consistent = False
        costs[order] = cost
        if best is None or cost < best:
            best, best_orders = cost, [order]
        elif cost == best:
            best_orders.append(order)
    return {"orders_enumerated": total,
            "all_orders_reproduce_the_same_jacobian": consistent,
            "minimum_cost": best,
            "topological_order_cost": costs.get(topo),
            "reverse_topological_order_cost": costs.get(revtopo),
            "argmin_includes_reverse_topological": revtopo in best_orders,
            "argmin_includes_topological": topo in best_orders,
            "argmin_is_a_mixed_order_only": (revtopo not in best_orders
                                             and topo not in best_orders),
            "argmin_count": len(best_orders)}


def oracle_sigma_star(G):
    n = len(G["sources"])
    N = len(G["interior"])
    E = len(G["edges"])
    p = len(G["outputs"])
    w = oracle_peak_live(G)
    if n > p and N > w:
        return "THRESHOLD", Q((n - p) * E, N - w)
    if p > n:
        return "TANGENT_WINS_FOR_EVERY_PRICE", None
    if p == n and N > w:
        return "TANGENT_WINS_FOR_EVERY_POSITIVE_PRICE", None
    if N == w and n > p:
        return "ADJOINT_WINS_FOR_EVERY_PRICE", None
    return "EXACT_TIE_EVERYWHERE", None


def oracle_il4():
    out = {}
    for name in sorted(oracle_graphs()):
        G = oracle_graphs()[name]
        fwd, rev = oracle_sweep_costs(G)
        tag, s = oracle_sigma_star(G)
        out[name] = {
            "sources_n": len(G["sources"]), "internal_N": len(G["interior"]),
            "edges_E": len(G["edges"]), "outputs_p": len(G["outputs"]),
            "peak_live_internal_w": oracle_peak_live(G),
            "sweep_cost_forward": fwd, "sweep_cost_reverse": rev,
            "jacobian": [[str(x) for x in row] for row in jacobian_by_path_sum(G)],
            "regime": tag, "sigma_star": (str(s) if s is not None else None),
            "order_census": oracle_order_census(G),
        }
    return out


def build():
    return {
        "schema": "GMI833SectionIUpdateLawSpaceOracleV1",
        "route": "B_INDEPENDENT_ORACLE",
        "method": {
            "IL_1": "literal tuple enumeration, fixed-point closure, hand-rolled charge arithmetic",
            "IL_23": "exhaustive enumeration over every improving-set placement and every probe order",
            "IL_4": "explicit directed-path enumeration (path sum), literal sweep and elimination simulation",
        },
        "IL_1": {"one_step_counterexample": oracle_one_step_counterexample(),
                 "charge_subassociativity": oracle_charge_subassociativity(),
                 "closure_census": oracle_closure_census(),
                 "scope_fingerprint": oracle_scope_fingerprint()},
        "IL_23": oracle_il23(),
        "IL_4": oracle_il4(),
    }


def main():
    res = build()
    path = os.path.join(WHERE, "ORACLE_RESULT_V1.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("oracle IL-2/3 local table entries=%d per-order-uniform=%s"
          % (len(res["IL_23"]["local_table"]),
             res["IL_23"]["per_order_averages_all_equal"]))
    cc = res["IL_1"]["closure_census"]
    print("oracle IL-1 closure census: mixtures=%d failures=%d compositions=%d "
          "failures=%d one_step_clauses=%s monoid=%s"
          % (cc["mixture_cases"], len(cc["mixture_failures"]),
             cc["composition_cases"], len(cc["closure_composition_failures"]),
             cc["one_step_composite_clauses"], cc["monoid_identity_two_sided"]))
    print("oracle IL-1 one-step outside=%s inside-closure=%s charge strict=%s"
          % (res["IL_1"]["one_step_counterexample"]["outside_one_step"],
             res["IL_1"]["one_step_counterexample"]["inside_closure"],
             res["IL_1"]["charge_subassociativity"]["strict"]))
    for k in sorted(res["IL_4"]):
        g = res["IL_4"][k]
        print("oracle IL-4 %-16s w=%d regime=%s sigma*=%s min=%s revtopo=%s mixed_only=%s"
              % (k, g["peak_live_internal_w"], g["regime"], g["sigma_star"],
                 g["order_census"]["minimum_cost"],
                 g["order_census"]["reverse_topological_order_cost"],
                 g["order_census"]["argmin_is_a_mixed_order_only"]))
    print("wrote " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
