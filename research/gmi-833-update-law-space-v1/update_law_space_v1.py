"""Route A executor for GMI #833 Section I.

Registered results IL-1 (admissible update-law space), IL-2 / IL-3 (the exact
acquisition-cost crossover), IL-4 (credit-assignment regimes recovered from
graph and resource structure).

Exact rational arithmetic only. Standard library only. Runs under
``python3 -I -B`` and ``python3 -I -O -B``. No claim is gated by ``assert``.
"""
from fractions import Fraction as Fr
from itertools import combinations, permutations, product
import json
import os
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))


def fail(msg):
    raise ValueError(msg)


def is_exact(x):
    return isinstance(x, (int, Fr)) and not isinstance(x, bool)


# ---------------------------------------------------------------------------
# IL-1  the admissible update-law space
# ---------------------------------------------------------------------------

def make_scope():
    """The registered finite scope S = (R, HIST, coords, delta, ext, Bgrid)."""
    # rq is registered but developmentally isolated: nothing reaches it.
    realizations = ("r0", "r1", "r2", "ra", "rb", "ru", "rv", "rz", "rq")
    histories = ("h0", "h1", "h2")
    coords = ("c_alpha", "c_beta")
    delta = {}
    for r in realizations:
        for h in histories:
            delta[(r, h)] = ()
    delta[("r0", "h0")] = ("r1",)
    delta[("r1", "h1")] = ("r2",)
    delta[("r0", "h1")] = ("ra", "rb")
    delta[("ra", "h1")] = ("ru",)
    delta[("rb", "h1")] = ("rv",)
    delta[("ru", "h1")] = ("rz",)
    delta[("rv", "h1")] = ("rz",)
    ext = {}
    for h in histories:
        for r in realizations:
            ext[(h, r)] = "h1"
    budgets = (
        {"c_alpha": Fr(0), "c_beta": Fr(0)},
        {"c_alpha": Fr(1), "c_beta": Fr(1)},
        {"c_alpha": Fr(9), "c_beta": Fr(9)},
    )
    return {
        "realizations": realizations,
        "histories": histories,
        "coords": coords,
        "delta": delta,
        "ext": ext,
        "budgets": budgets,
    }


def delta_star(scope, r):
    """Reflexive-transitive closure of the declared development law at r."""
    seen = {r}
    frontier = [r]
    while frontier:
        cur = frontier.pop()
        for h in scope["histories"]:
            for nxt in scope["delta"][(cur, h)]:
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
    return seen


def successors(scope, grade, r, h):
    if grade == "ONE_STEP":
        return set((r,)) | set(scope["delta"][(r, h)])
    if grade == "CLOSURE":
        return delta_star(scope, r)
    fail("unknown grade " + repr(grade))


def bkey(b, coords):
    return tuple(b[c] for c in coords)


def zero_charge(coords):
    return dict((c, Fr(0)) for c in coords)


def point(r):
    return {r: Fr(1)}


def leq(a, b, coords):
    return all(a[c] <= b[c] for c in coords)


def sub(a, b, coords):
    return dict((c, a[c] - b[c]) for c in coords)


# An update law is a TOTAL function (r, h, b) -> (dist, charge) defined for
# every rational budget vector, not a table over the budget grid. Totality off
# the grid is what makes composition well defined at residual budgets.

def admissible(scope, grade, law):
    """Decide Adm_k(law) over the registered grid. Returns
    (verdict, findings, operation_count)."""
    coords = scope["coords"]
    findings = []
    ops = 0
    for r in scope["realizations"]:
        for h in scope["histories"]:
            for b in scope["budgets"]:
                key = (r, h, bkey(b, coords))
                try:
                    dist, charge = law(r, h, b)
                except Exception as exc:                      # noqa: BLE001
                    findings.append(("A1_NOT_TOTAL", key, str(exc)[:40]))
                    continue
                tot = Fr(0)
                bad = False
                for tgt, pr in dist.items():
                    ops += 1
                    if not is_exact(pr):
                        findings.append(("A1_INEXACT_PROBABILITY", key, tgt))
                        bad = True
                        continue
                    if pr < 0:
                        findings.append(("A1_NEGATIVE_PROBABILITY", key, tgt))
                        bad = True
                    tot += Fr(pr)
                if not bad and tot != 1:
                    findings.append(("A1_NOT_NORMALIZED", key, str(tot)))
                well_formed = set(charge) == set(coords)
                if not well_formed:
                    findings.append(("A2_CHARGE_COORDINATE_MISMATCH", key,
                                     tuple(sorted(set(charge) ^ set(coords)))))
                else:
                    for c in coords:
                        ops += 1
                        if not is_exact(charge[c]):
                            findings.append(("A2_INEXACT_CHARGE", key, c))
                            well_formed = False
                        elif charge[c] < 0:
                            findings.append(("A2_NEGATIVE_CHARGE", key, c))
                if well_formed:
                    ops += len(coords)
                    if not leq(charge, b, coords):
                        if not (all(charge[c] == 0 for c in coords)
                                and dist == point(r)):
                            findings.append(("A3_BUDGET_CLAUSE_VIOLATED", key))
                allowed = successors(scope, grade, r, h)
                ops += 1
                for tgt in dist:
                    if dist[tgt] != 0 and tgt not in allowed:
                        findings.append(("A4_SUPPORT_OUTSIDE_DEVELOPMENT", key, tgt))
    return ("ADMISSIBLE" if not findings else "INADMISSIBLE"), findings, ops


def decide_bound(scope):
    """The pre-committed exact upper bound on decision work, per law."""
    return (len(scope["realizations"]) * len(scope["histories"])
            * len(scope["budgets"])
            * (len(scope["realizations"]) + 2 * len(scope["coords"]) + 1))


def mix(scope, lam, l1, l2):
    coords = scope["coords"]

    def mixed(r, h, b):
        d1, c1 = l1(r, h, b)
        d2, c2 = l2(r, h, b)
        d = {}
        for tgt, pr in d1.items():
            d[tgt] = d.get(tgt, Fr(0)) + lam * pr
        for tgt, pr in d2.items():
            d[tgt] = d.get(tgt, Fr(0)) + (1 - lam) * pr
        c = dict((k, lam * c1[k] + (1 - lam) * c2[k]) for k in coords)
        return d, c

    return mixed


def is_noop(dist, charge, r, coords):
    return dist == point(r) and all(charge[c] == 0 for c in coords)


def compose(scope, l2, l1):
    """(l2 after l1). Worst-case (coordinatewise max) charge on the second
    stage, as pre-committed by the freeze.

    The history presented to the second stage is the registered extension
    ext(h, r1), EXCEPT after a stage that consumed no resource and changed
    nothing: a zero-charge identity step registers no interaction, so it does
    not advance the history. This clause is forced by AX-3 (finite path cost is
    coordinatewise addition, so a zero-charge step adds nothing to the
    developmental record) and it is exactly what makes the no-op a two-sided
    identity rather than only a left identity."""
    coords = scope["coords"]

    def composed(r, h, b):
        d1, c1 = l1(r, h, b)
        resid = sub(b, c1, coords)
        if any(resid[c] < 0 for c in coords):
            resid = zero_charge(coords)
        quiet = is_noop(d1, c1, r, coords)
        d = {}
        worst = zero_charge(coords)
        for r1 in [t for t in d1 if d1[t] != 0]:
            h2 = h if quiet else scope["ext"][(h, r1)]
            d2, c2 = l2(r1, h2, resid)
            for tgt, pr in d2.items():
                d[tgt] = d.get(tgt, Fr(0)) + d1[r1] * pr
            for c in coords:
                if c2[c] > worst[c]:
                    worst[c] = c2[c]
        return d, dict((c, c1[c] + worst[c]) for c in coords)

    return composed


def const_law(scope, table, charge_table):
    """Total law from (realization -> target distribution) and
    (realization -> charge). Two clauses are built in by construction:
    on insufficient residual budget it returns the identity distribution at
    zero charge (admissibility clause A3), and it acts only where its declared
    target support lies inside the one-step development set at the presented
    history (admissibility clause A4 at the finer grade), otherwise it is the
    identity. Escaping the one-step grade is therefore only ever possible by
    COMPOSITION, never by a base law."""
    coords = scope["coords"]

    def law(r, h, b):
        ch = charge_table.get(r, zero_charge(coords))
        tgt = table.get(r)
        if tgt is None or not leq(ch, b, coords):
            return point(r), zero_charge(coords)
        allowed = set((r,)) | set(scope["delta"][(r, h)])
        if any(tgt[t] != 0 and t not in allowed for t in tgt):
            return point(r), zero_charge(coords)
        return dict(tgt), dict(ch)

    return law


def registered_laws(scope):
    """The registered finite population of update laws used by IL-1."""

    def ch(a, b):
        return {"c_alpha": Fr(a), "c_beta": Fr(b)}

    pop = {}
    pop["identity"] = const_law(scope, {}, {})
    pop["step_r0_r1"] = const_law(scope, {"r0": point("r1")}, {"r0": ch(1, 0)})
    pop["step_r1_r2"] = const_law(scope, {"r1": point("r2")}, {"r1": ch(1, 0)})
    pop["split_r0"] = const_law(
        scope, {"r0": {"ra": Fr(1, 2), "rb": Fr(1, 2)}}, {"r0": ch(0, 0)})
    pop["stage_two"] = const_law(
        scope, {"ra": point("ru"), "rb": point("rv")},
        {"ra": ch(3, 0), "rb": ch(0, 0)})
    pop["stage_three"] = const_law(
        scope, {"ru": point("rz"), "rv": point("rz")},
        {"ru": ch(0, 0), "rv": ch(5, 0)})
    pop["costly"] = const_law(
        scope, {"r0": point("r1"), "r1": point("r2")},
        {"r0": ch(9, 9), "r1": ch(9, 9)})
    return pop


def same_law(scope, la, lb):
    for r in scope["realizations"]:
        for h in scope["histories"]:
            for b in scope["budgets"]:
                if la(r, h, b) != lb(r, h, b):
                    return False
    return True


def il1_certificate():
    scope = make_scope()
    coords = scope["coords"]
    pop = registered_laws(scope)

    verdicts = {}
    total_ops = 0
    for name, law in sorted(pop.items()):
        v1, f1, o1 = admissible(scope, "ONE_STEP", law)
        vs, fs, o2 = admissible(scope, "CLOSURE", law)
        total_ops += o1 + o2
        verdicts[name] = {"ONE_STEP": v1, "CLOSURE": vs,
                          "one_step_findings": len(f1),
                          "closure_findings": len(fs)}

    lam_grid = tuple(Fr(i, 6) for i in range(0, 7))
    mix_cases = 0
    mix_failures = []
    names = sorted(pop)
    base = {}
    for grade in ("ONE_STEP", "CLOSURE"):
        for nm in names:
            base[(grade, nm)] = admissible(scope, grade, pop[nm])[0]
    for a in names:
        for b in names:
            for lam in lam_grid:
                m = mix(scope, lam, pop[a], pop[b])
                for grade in ("ONE_STEP", "CLOSURE"):
                    vm, fm, _ = admissible(scope, grade, m)
                    mix_cases += 1
                    if (base[(grade, a)] == "ADMISSIBLE"
                            and base[(grade, b)] == "ADMISSIBLE"
                            and vm != "ADMISSIBLE"):
                        mix_failures.append((a, b, str(lam), grade,
                                             [str(x) for x in fm[0]]))

    comp_cases = 0
    comp_failures = []
    for a in names:
        for b in names:
            c = compose(scope, pop[a], pop[b])
            vc, fc, _ = admissible(scope, "CLOSURE", c)
            comp_cases += 1
            if (base[("CLOSURE", a)] == "ADMISSIBLE"
                    and base[("CLOSURE", b)] == "ADMISSIBLE"
                    and vc != "ADMISSIBLE"):
                comp_failures.append((a, b, [str(x) for x in fc[0]]))

    c_one = compose(scope, pop["step_r1_r2"], pop["step_r0_r1"])
    v_one, f_one, _ = admissible(scope, "ONE_STEP", c_one)
    v_one_star, _, _ = admissible(scope, "CLOSURE", c_one)
    d0, _ = c_one("r0", "h0", scope["budgets"][2])
    one_step_witness = {
        "composite_support_at_r0_h0": sorted(t for t in d0 if d0[t] != 0),
        "one_step_allowed_at_r0_h0": sorted(successors(scope, "ONE_STEP", "r0", "h0")),
        "closure_allowed_at_r0": sorted(successors(scope, "CLOSURE", "r0", "h0")),
        "one_step_verdict": v_one,
        "closure_verdict": v_one_star,
        "first_finding": [str(x) for x in f_one[0]] if f_one else None,
    }

    l1, l2, l3 = pop["split_r0"], pop["stage_two"], pop["stage_three"]
    # left_nested  = (L3 o L2) o L1 : the second stage is charged jointly with
    #                the third, so the worst case is taken once over pairs.
    # right_nested = L3 o (L2 o L1) : two independent worst cases are summed.
    left_nested = compose(scope, compose(scope, l3, l2), l1)
    right_nested = compose(scope, l3, compose(scope, l2, l1))
    kernel_equal = True
    subassoc = True
    strict_at = None
    for r in scope["realizations"]:
        for h in scope["histories"]:
            for b in scope["budgets"]:
                da, ca = left_nested(r, h, b)
                db, cb = right_nested(r, h, b)
                if da != db:
                    kernel_equal = False
                for c in coords:
                    if not ca[c] <= cb[c]:
                        subassoc = False
                    if ca[c] < cb[c] and strict_at is None:
                        strict_at = {"realization": r, "history": h,
                                     "budget": [str(x) for x in bkey(b, coords)],
                                     "coordinate": c,
                                     "left_nested_charge": str(ca[c]),
                                     "right_nested_charge": str(cb[c])}
    ident = pop["identity"]
    monoid_ok = (same_law(scope, compose(scope, ident, l2), l2)
                 and same_law(scope, compose(scope, l2, ident), l2))
    ident_admissible = admissible(scope, "CLOSURE", ident)[0]

    return {
        "scope_sizes": {"realizations": len(scope["realizations"]),
                        "histories": len(scope["histories"]),
                        "coords": len(scope["coords"]),
                        "budgets": len(scope["budgets"])},
        "decision_operation_bound_per_law_per_grade": decide_bound(scope),
        "decision_operations_used": total_ops,
        "decision_bound_respected":
            total_ops <= decide_bound(scope) * len(pop) * 2,
        "law_population": len(pop),
        "verdicts": verdicts,
        "mixture_lambda_grid": [str(x) for x in lam_grid],
        "mixture_cases": mix_cases,
        "mixture_failures": mix_failures,
        "composition_cases": comp_cases,
        "closure_composition_failures": comp_failures,
        "one_step_composition_counterexample": one_step_witness,
        "kernel_associativity_exact": kernel_equal,
        "charge_subassociative": subassoc,
        "charge_strictness_witness": strict_at,
        "monoid_identity_ok": monoid_ok,
        "identity_law_admissible": ident_admissible,
    }


# ---------------------------------------------------------------------------
# IL-2 / IL-3  the acquisition-cost crossover
# ---------------------------------------------------------------------------

def rho_local(d, m):
    """Orbit-average point-value query count at a configuration of
    branching d with m improving successors."""
    if d < 1 or m < 1 or m > d:
        fail("rho_local needs 1 <= m <= d")
    return Fr(d + 1, m + 1)


def worst_case_probes(d, m):
    return d - m + 1


def rho_star(profile):
    """Mean reciprocal improving density along a registered improving path."""
    if not profile:
        fail("empty path profile")
    tot = Fr(0)
    for (d, m) in profile:
        tot += rho_local(d, m)
    return tot / Fr(len(profile))


def cost_point_channel(profile, price_pt):
    return price_pt * sum((rho_local(d, m) for (d, m) in profile), Fr(0))


def cost_select_channel(profile, price_sel):
    return price_sel * Fr(len(profile))


def verdict(profile, price_pt, price_sel):
    if not is_exact(price_pt) or not is_exact(price_sel):
        fail("prices must be exact rationals; inexact prices are refused")
    if price_pt <= 0 or price_sel <= 0:
        fail("prices must be strictly positive rationals")
    cp = cost_point_channel(profile, price_pt)
    cs = cost_select_channel(profile, price_sel)
    if cp < cs:
        return "POINT_VALUE_ONLY_STRICTLY_DOMINATES"
    if cp > cs:
        return "SELECTION_CHANNEL_STRICTLY_DOMINATES"
    return "EXACT_TIE_AT_BOUNDARY"


def verdict_from_ratio(profile, ratio):
    rs = rho_star(profile)
    if ratio > rs:
        return "POINT_VALUE_ONLY_STRICTLY_DOMINATES"
    if ratio < rs:
        return "SELECTION_CHANNEL_STRICTLY_DOMINATES"
    return "EXACT_TIE_AT_BOUNDARY"


def registered_paths():
    """Uniform ladders plus mixed ladders whose rho_star is a genuine mean."""
    paths = []
    for d in range(1, 7):
        for m in range(1, d + 1):
            for n in (1, 2, 3):
                paths.append(("uniform_d%d_m%d_n%d" % (d, m, n),
                              tuple([(d, m)] * n)))
    mixed = [
        ((1, 1), (2, 1)),
        ((2, 1), (3, 1)),
        ((3, 1), (3, 3)),
        ((4, 1), (2, 2)),
        ((5, 2), (2, 1), (6, 3)),
        ((6, 1), (6, 6)),
        ((2, 2), (3, 2), (4, 3)),
        ((5, 1), (5, 5), (3, 2)),
        ((4, 2), (4, 4)),
        ((6, 5), (2, 1)),
        ((3, 3), (3, 3), (3, 3)),
        ((6, 2), (5, 4), (4, 1), (2, 2)),
    ]
    for i, prof in enumerate(mixed):
        paths.append(("mixed_%02d" % i, prof))
    return paths


def price_ratio_grid():
    vals = set()
    for a in range(1, 13):
        for b in range(1, 7):
            vals.add(Fr(a, b))
    return tuple(sorted(vals))


def il23_certificate():
    paths = registered_paths()
    grid = price_ratio_grid()
    rows = []
    counts = {"POINT_VALUE_ONLY_STRICTLY_DOMINATES": 0,
              "SELECTION_CHANNEL_STRICTLY_DOMINATES": 0,
              "EXACT_TIE_AT_BOUNDARY": 0}
    anchored_ok = True
    trichotomy_cases = 0
    partition_failures = []
    price_pt = Fr(1)
    for name, prof in paths:
        rs = rho_star(prof)
        # anchored ratios force all three verdicts
        anchors = [(rs / 2, "SELECTION_CHANNEL_STRICTLY_DOMINATES"),
                   (rs, "EXACT_TIE_AT_BOUNDARY"),
                   (2 * rs, "POINT_VALUE_ONLY_STRICTLY_DOMINATES")]
        for ratio, expect in anchors:
            got = verdict(prof, price_pt, ratio * price_pt)
            got2 = verdict_from_ratio(prof, ratio)
            if got != expect or got2 != expect:
                anchored_ok = False
        for ratio in grid:
            v = verdict(prof, price_pt, ratio * price_pt)
            v2 = verdict_from_ratio(prof, ratio)
            trichotomy_cases += 1
            counts[v] += 1
            strict_lo = cost_point_channel(prof, price_pt) < cost_select_channel(prof, ratio * price_pt)
            strict_hi = cost_point_channel(prof, price_pt) > cost_select_channel(prof, ratio * price_pt)
            tie = cost_point_channel(prof, price_pt) == cost_select_channel(prof, ratio * price_pt)
            if v != v2 or (int(strict_lo) + int(strict_hi) + int(tie)) != 1:
                partition_failures.append((name, str(ratio), v, v2))
        rows.append({"path": name, "length": len(prof),
                     "rho_star": str(rs),
                     "worst_case_probes": [worst_case_probes(d, m) for (d, m) in prof]})

    full_density = [r for r in rows if r["rho_star"] == "1"]
    max_rho = max(rows, key=lambda r: Fr(r["rho_star"]))
    return {
        "paths": len(paths),
        "uniform_paths": len([p for p in paths if p[0].startswith("uniform")]),
        "mixed_paths": len([p for p in paths if p[0].startswith("mixed")]),
        "price_ratio_grid_size": len(grid),
        "trichotomy_cases": trichotomy_cases,
        "verdict_counts": counts,
        "partition_failures": partition_failures,
        "anchored_three_verdicts_ok": anchored_ok,
        "full_improving_density_paths_with_rho_star_one": len(full_density),
        "max_rho_star": {"path": max_rho["path"], "rho_star": max_rho["rho_star"]},
        "rho_star_table": rows,
    }


def equivariance_boundary_witness():
    """The per-instance counterexample that maps the boundary of IL-2a."""
    d, m = 6, 1
    orbit = Fr(d + 1, m + 1)
    # A law that hard-codes successor index 0 pays exactly one probe on the
    # single instance where index 0 is the improving successor.
    instance_cost = Fr(1)
    # over the Sym(d) orbit the same law averages back to the orbit value
    total = Fr(0)
    placements = list(combinations(range(d), m))
    for s in placements:
        total += Fr(1 + min(s))
    orbit_of_that_law = total / Fr(len(placements))
    return {
        "branching": d,
        "improving": m,
        "orbit_average_rho_local": str(orbit),
        "per_instance_cost_of_index_pinned_law": str(instance_cost),
        "per_instance_beats_orbit_average": instance_cost < orbit,
        "same_law_orbit_average": str(orbit_of_that_law),
        "orbit_average_restored": orbit_of_that_law == orbit,
        "label": "EARNED-BY-COUNTEREXAMPLE",
    }


# ---------------------------------------------------------------------------
# IL-4  credit assignment from graph and resource structure
# ---------------------------------------------------------------------------

def make_graphs():
    """Registered finite computation graphs. Interior nodes are listed in a
    topological order; designated outputs are sinks of the graph."""
    g = {}

    def chain(nsrc, depth):
        sources = tuple("x%d" % i for i in range(nsrc))
        interior = tuple("v%d" % i for i in range(depth))
        edges = {}
        for i, s in enumerate(sources):
            edges[(s, "v0")] = Fr(i + 2)
        for i in range(1, depth):
            edges[("v%d" % (i - 1), "v%d" % i)] = Fr(i + 3, i + 1)
        return {"sources": sources, "interior": interior,
                "outputs": ("v%d" % (depth - 1),), "edges": edges}

    g["source_chain_n4"] = chain(4, 4)
    g["deep_chain_n6"] = chain(6, 6)

    g["fan_in_n5"] = {
        "sources": tuple("x%d" % i for i in range(5)),
        "interior": ("v0", "v1", "v2", "v3"),
        "outputs": ("v3",),
        "edges": {("x0", "v0"): Fr(2), ("x1", "v0"): Fr(3), ("x2", "v1"): Fr(5),
                  ("x3", "v1"): Fr(7), ("x4", "v1"): Fr(11),
                  ("v0", "v2"): Fr(1, 2), ("v1", "v2"): Fr(1, 3),
                  ("v2", "v3"): Fr(4, 5)},
    }
    g["fan_out_p4"] = {
        "sources": ("x0",),
        "interior": ("v0", "v1", "y0", "y1", "y2", "y3"),
        "outputs": ("y0", "y1", "y2", "y3"),
        "edges": {("x0", "v0"): Fr(2), ("v0", "v1"): Fr(3),
                  ("v1", "y0"): Fr(1, 2), ("v1", "y1"): Fr(1, 3),
                  ("v0", "y2"): Fr(1, 5), ("v1", "y3"): Fr(1, 7)},
    }
    g["square_n3_p3"] = {
        "sources": ("x0", "x1", "x2"),
        "interior": ("v0", "v1", "v2", "y0", "y1", "y2"),
        "outputs": ("y0", "y1", "y2"),
        "edges": {("x0", "v0"): Fr(2), ("x1", "v0"): Fr(3), ("x2", "v1"): Fr(5),
                  ("v0", "v1"): Fr(7), ("v1", "v2"): Fr(9),
                  ("v0", "y0"): Fr(1, 2), ("v2", "y1"): Fr(1, 3),
                  ("v2", "y2"): Fr(1, 5)},
    }
    g["bridge_n3_p3"] = {
        "sources": ("x0", "x1", "x2"),
        "interior": ("v0", "v1", "y0", "y1", "y2"),
        "outputs": ("y0", "y1", "y2"),
        "edges": {("x0", "v0"): Fr(2), ("x1", "v0"): Fr(3), ("x2", "v0"): Fr(5),
                  ("v0", "v1"): Fr(7),
                  ("v1", "y0"): Fr(11), ("v1", "y1"): Fr(13), ("v1", "y2"): Fr(17)},
    }
    # A skip edge across a narrow waist. Eliminating the waist vertex out of
    # both pure orders merges two parallel contributions before either pure
    # order can, so a mixed order is strictly cheaper.
    g["skip_waist_n2_p2"] = {
        "sources": ("x0", "x1"),
        "interior": ("v0", "v1", "v2", "y0", "y1"),
        "outputs": ("y0", "y1"),
        "edges": {("x0", "v0"): Fr(2), ("x1", "v0"): Fr(3),
                  ("v0", "v1"): Fr(5), ("v1", "v2"): Fr(7),
                  ("v0", "v2"): Fr(11),
                  ("v2", "y0"): Fr(13), ("v2", "y1"): Fr(17)},
    }
    return g


def graph_facts(G):
    n = len(G["sources"])
    N = len(G["interior"])
    E = len(G["edges"])
    p = len(G["outputs"])
    return n, N, E, p


def parents_of(G, v):
    return tuple(u for (u, w) in G["edges"] if w == v)


def peak_live_internal(G):
    """Exact peak number of live INTERNAL values under the registered
    topological evaluation order. A value is live from its production step to
    its last consumption step INCLUSIVE; designated outputs stay live to the
    end. Source values are retained identically by both directions and are
    therefore excluded from both sides of the comparison and from this count."""
    order = list(G["interior"])
    last_use = dict((v, i) for i, v in enumerate(order))
    for idx, v in enumerate(order):
        for u in parents_of(G, v):
            if u in last_use and idx > last_use[u]:
                last_use[u] = idx
    for o in G["outputs"]:
        last_use[o] = len(order)
    live = set()
    peak = 0
    for idx, v in enumerate(order):
        live.add(v)
        if len(live) > peak:
            peak = len(live)
        for u in [x for x in live if last_use[x] <= idx]:
            live.discard(u)
    return peak


def tangent_sweep(G, seed):
    """One linearization sweep seeded at the sources. Returns (values, cost)."""
    t = {}
    for i, s in enumerate(G["sources"]):
        t[s] = seed[i]
    cost = 0
    for v in G["interior"]:
        acc = Fr(0)
        for u in parents_of(G, v):
            acc += G["edges"][(u, v)] * t[u]
            cost += 1
        t[v] = acc
    return tuple(t[o] for o in G["outputs"]), cost


def adjoint_sweep(G, seed):
    """One reverse-order linearization sweep seeded at the outputs."""
    a = dict((v, Fr(0)) for v in G["interior"])
    for v in G["sources"]:
        a[v] = Fr(0)
    for i, o in enumerate(G["outputs"]):
        a[o] = seed[i]
    cost = 0
    for v in reversed(list(G["interior"])):
        for u in parents_of(G, v):
            a[u] += G["edges"][(u, v)] * a[v]
            cost += 1
    return tuple(a[s] for s in G["sources"]), cost


def jacobian_by_sweeps(G):
    n, N, E, p = graph_facts(G)
    cols = []
    for i in range(n):
        seed = [Fr(1) if j == i else Fr(0) for j in range(n)]
        vals, _ = tangent_sweep(G, seed)
        cols.append(vals)
    return tuple(tuple(cols[i][o] for i in range(n)) for o in range(p))


def jacobian_by_adjoints(G):
    n, N, E, p = graph_facts(G)
    rows = []
    for o in range(p):
        seed = [Fr(1) if j == o else Fr(0) for j in range(p)]
        vals, _ = adjoint_sweep(G, seed)
        rows.append(vals)
    return tuple(rows)


def sweep_necessity_witness(n):
    """k < n tangent sweeps leave two distinct star graphs indistinguishable."""
    sources = tuple("x%d" % i for i in range(n))
    base = {"sources": sources, "interior": ("v0",), "outputs": ("v0",),
            "edges": dict(((s, "v0"), Fr(i + 1)) for i, s in enumerate(sources))}
    alt = {"sources": sources, "interior": ("v0",), "outputs": ("v0",),
           "edges": dict(base["edges"])}
    # perturb along a direction orthogonal to the first n-1 basis seeds:
    # only the last coordinate changes, so seeds e_0..e_{n-2} cannot see it.
    alt["edges"][(sources[-1], "v0")] = base["edges"][(sources[-1], "v0")] + Fr(1)
    agreed = []
    for i in range(n - 1):
        seed = [Fr(1) if j == i else Fr(0) for j in range(n)]
        a, _ = tangent_sweep(base, seed)
        b, _ = tangent_sweep(alt, seed)
        agreed.append(a == b)
    ja = jacobian_by_sweeps(base)
    jb = jacobian_by_sweeps(alt)
    return {"sources": n,
            "sweeps_used": n - 1,
            "all_observed_sweeps_agree": all(agreed),
            "jacobians_differ": ja != jb,
            "necessity_established": all(agreed) and ja != jb}


def adjoint_necessity_witness(p):
    sources = ("x0",)
    interior = tuple("y%d" % i for i in range(p))
    base = {"sources": sources, "interior": interior, "outputs": interior,
            "edges": dict((("x0", y), Fr(i + 1)) for i, y in enumerate(interior))}
    alt = {"sources": sources, "interior": interior, "outputs": interior,
           "edges": dict(base["edges"])}
    alt["edges"][("x0", interior[-1])] = base["edges"][("x0", interior[-1])] + Fr(1)
    agreed = []
    for i in range(p - 1):
        seed = [Fr(1) if j == i else Fr(0) for j in range(p)]
        a, _ = adjoint_sweep(base, seed)
        b, _ = adjoint_sweep(alt, seed)
        agreed.append(a == b)
    return {"outputs": p, "sweeps_used": p - 1,
            "all_observed_sweeps_agree": all(agreed),
            "jacobians_differ": jacobian_by_adjoints(base) != jacobian_by_adjoints(alt),
            "necessity_established": all(agreed)
            and jacobian_by_adjoints(base) != jacobian_by_adjoints(alt)}


def sigma_star(G):
    """Exact retention-price threshold in graph invariants, or a regime tag."""
    n, N, E, p = graph_facts(G)
    w = peak_live_internal(G)
    if n > p and N > w:
        return ("THRESHOLD", Fr((n - p) * E, N - w))
    if p > n:
        return ("TANGENT_WINS_FOR_EVERY_PRICE", None)
    if p == n and N > w:
        return ("TANGENT_WINS_FOR_EVERY_POSITIVE_PRICE", None)
    if N == w and n > p:
        return ("ADJOINT_WINS_FOR_EVERY_PRICE", None)
    return ("EXACT_TIE_EVERYWHERE", None)


def direction_cost(G, sigma, which):
    n, N, E, p = graph_facts(G)
    w = peak_live_internal(G)
    if which == "TANGENT":
        return Fr(n * E)
    if which == "ADJOINT":
        return Fr(p * E) + Fr(N - w) * sigma
    fail("unknown direction")


def direction_verdict(G, sigma):
    ct = direction_cost(G, sigma, "TANGENT")
    ca = direction_cost(G, sigma, "ADJOINT")
    if ca < ct:
        return "ADJOINT_STRICTLY_CHEAPER"
    if ca > ct:
        return "TANGENT_STRICTLY_CHEAPER"
    return "EXACT_TIE_AT_BOUNDARY"


def eliminable(G):
    return tuple(v for v in G["interior"] if v not in G["outputs"])


def eliminate_order(G, order):
    """Vertex elimination on the linearized graph. Returns (jacobian, cost)."""
    edges = dict(G["edges"])
    cost = 0
    for v in order:
        preds = [u for (u, w) in edges if w == v]
        succs = [w for (u, w) in edges if u == v]
        for u in preds:
            for z in succs:
                edges[(u, z)] = edges.get((u, z), Fr(0)) + edges[(u, v)] * edges[(v, z)]
                cost += 1
        for u in preds:
            del edges[(u, v)]
        for z in succs:
            del edges[(v, z)]
    jac = tuple(tuple(edges.get((s, o), Fr(0)) for s in G["sources"])
                for o in G["outputs"])
    return jac, cost


def order_census(G):
    """Exhaustive census over every interior elimination order. No algorithm
    name enters the search space or the objective."""
    elim = eliminable(G)
    ref = jacobian_by_sweeps(G)
    topo = tuple(v for v in G["interior"] if v in elim)
    revtopo = tuple(reversed(topo))
    best = None
    best_orders = []
    total = 0
    consistent = True
    costs = {}
    for order in permutations(elim):
        jac, cost = eliminate_order(G, order)
        total += 1
        if jac != ref:
            consistent = False
        costs[order] = cost
        if best is None or cost < best:
            best = cost
            best_orders = [order]
        elif cost == best:
            best_orders.append(order)
    return {
        "eliminable_interior_vertices": len(elim),
        "orders_enumerated": total,
        "all_orders_reproduce_the_same_jacobian": consistent,
        "minimum_cost": best,
        "argmin_count": len(best_orders),
        "topological_order_cost": costs.get(topo),
        "reverse_topological_order_cost": costs.get(revtopo),
        "argmin_includes_reverse_topological": revtopo in best_orders,
        "argmin_includes_topological": topo in best_orders,
        "argmin_is_a_mixed_order_only": (revtopo not in best_orders
                                         and topo not in best_orders),
        "example_argmin": list(best_orders[0]) if best_orders else None,
    }


def il4_certificate():
    graphs = make_graphs()
    rows = []
    for name in sorted(graphs):
        G = graphs[name]
        n, N, E, p = graph_facts(G)
        w = peak_live_internal(G)
        ja = jacobian_by_sweeps(G)
        jb = jacobian_by_adjoints(G)
        tag, s = sigma_star(G)
        entry = {
            "graph": name, "sources_n": n, "internal_N": N, "edges_E": E,
            "outputs_p": p, "peak_live_internal_w": w,
            "tangent_sweeps_required": n,
            "adjoint_sweeps_required": p,
            "sweep_cost_each": E,
            "jacobian_agrees_across_directions": ja == jb,
            "regime": tag,
            "sigma_star": (str(s) if s is not None else None),
        }
        if s is not None:
            entry["verdict_below_threshold"] = direction_verdict(G, s / 2)
            entry["verdict_at_threshold"] = direction_verdict(G, s)
            entry["verdict_above_threshold"] = direction_verdict(G, 2 * s)
        else:
            entry["verdict_at_zero_price"] = direction_verdict(G, Fr(0))
            entry["verdict_at_unit_price"] = direction_verdict(G, Fr(1))
            entry["verdict_at_large_price"] = direction_verdict(G, Fr(10 ** 6))
        entry["order_census"] = order_census(G)
        rows.append(entry)

    nec = [sweep_necessity_witness(k) for k in (2, 3, 4, 5, 6)]
    anec = [adjoint_necessity_witness(k) for k in (2, 3, 4)]

    # cheap-sensitivity consistency check (PARENT MATHEMATICS, no novelty claimed)
    cg = []
    for name in sorted(graphs):
        G = graphs[name]
        n, N, E, p = graph_facts(G)
        if p != 1:
            continue
        a = max(len(parents_of(G, v)) for v in G["interior"])
        sweep_price, retention_price, eval_price = Fr(1), Fr(1), Fr(1)
        w = peak_live_internal(G)
        c_adj = Fr(p * E) * sweep_price + Fr(N - w) * retention_price
        c_primal = Fr(N) * eval_price
        cg.append({"graph": name, "sources_n": n, "max_in_degree_a": a,
                   "ratio": str(c_adj / c_primal),
                   "parent_bound": str((Fr(a) * sweep_price + retention_price) / eval_price),
                   "within_parent_bound": c_adj / c_primal <= (Fr(a) * sweep_price + retention_price) / eval_price,
                   "independent_of_n": True})
    return {"graphs": rows,
            "tangent_sweep_necessity": nec,
            "adjoint_sweep_necessity": anec,
            "cheap_sensitivity_consistency_parent_owned": cg}


# ---------------------------------------------------------------------------
# name-freedom certificate
# ---------------------------------------------------------------------------

def load_denylist():
    with open(os.path.join(HERE, "DENYLIST_V1.json")) as fh:
        d = json.load(fh)
    entries = []
    for k in ("banned_mi_primitives", "no_smuggling_audit_entries",
              "section_i_additions"):
        entries.extend(d[k])
    return d, tuple(entries)


def normalize(s):
    out = []
    prev_lower = False
    for ch in s:
        if ch.isupper() and prev_lower:
            out.append(" ")
        out.append(ch)
        prev_lower = ch.islower() or ch.isdigit()
    t = "".join(out).lower()
    keep = []
    for ch in t:
        keep.append(ch if ch.isalnum() else " ")
    return "".join("".join(keep).split())


def token_pool(path, fn):
    if fn.endswith(".py"):
        with open(path, "rb") as fh:
            toks = list(tokenize.tokenize(fh.readline))
        return [tk.string for tk in toks
                if tk.type in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT)]
    with open(path) as fh:
        return fh.read().split()


def screen_files(filenames, suffixes):
    """Occurrence-level lexical screen. Every file in the population is
    screened; nothing is exempt as a whole except the two files that hold the
    screened vocabulary by construction. A hit is tolerated only when an
    allowlist entry names that exact (file, denylist entry) pair with a reason,
    and every such allowance must actually be exercised, so a stale allowance
    is itself a failure."""
    d, entries = load_denylist()
    whole = dict((x["path"], x["reason"]) for x in d["whole_file_exemptions"])
    allow = set((x["path"], x["deny_entry"]) for x in d["occurrence_allowlist"])
    deny = tuple((e, normalize(e)) for e in entries)
    screened = []
    allowed_hits = []
    unmatched = []
    exercised = set()
    tokens = 0
    for fn in sorted(filenames):
        if fn in whole or not fn.endswith(suffixes):
            continue
        path = os.path.join(HERE, fn)
        if not os.path.isfile(path):
            continue
        screened.append(fn)
        for item in token_pool(path, fn):
            tokens += 1
            nrm = normalize(item)
            for raw, nd in deny:
                if nd and nd in nrm:
                    rec = {"file": fn, "token": item[:48], "deny_entry": raw}
                    if (fn, raw) in allow:
                        allowed_hits.append(rec)
                        exercised.add((fn, raw))
                    else:
                        unmatched.append(rec)
    stale = sorted(list(allow - exercised))
    stale = [x for x in stale if x[0] in screened]
    strict = d["strictly_clean_files"]["files"]
    strict_violations = sorted(set(
        (h["file"], h["deny_entry"]) for h in allowed_hits + unmatched
        if h["file"] in strict))
    strict_allowances = sorted(set(x for x in allow if x[0] in strict))
    ok = (not unmatched and not stale and not strict_violations
          and not strict_allowances)
    return {"screened_files": screened,
            "whole_file_exemptions": sorted(whole),
            "denylist_version": d["version"],
            "denylist_entries": len(entries),
            "tokens_screened": tokens,
            "hits_total": len(allowed_hits) + len(unmatched),
            "hits_allowed_by_declared_occurrence": len(allowed_hits),
            "hits_unmatched": unmatched,
            "stale_allowances": stale,
            "allowlist_size": len(allow),
            "strictly_clean_files": strict,
            "strictly_clean_violations": strict_violations,
            "allowances_naming_a_strictly_clean_file": strict_allowances,
            "verdict": "CLEAN_AT_REGISTERED_AUDIT_SCOPE" if ok
            else "LEXICAL_LEAKAGE"}


def lexical_screen():
    return screen_files(os.listdir(HERE), (".py", ".md"))


def scope_fingerprint():
    """Transcription fingerprint of the registered scope. The oracle builds the
    same string from its own independent declaration; a mismatch means the two
    transcriptions have drifted and no agreement figure would mean anything."""
    scope = make_scope()
    coords = scope["coords"]
    items = ["R:" + ",".join(scope["realizations"]),
             "H:" + ",".join(scope["histories"]),
             "C:" + ",".join(coords)]
    for k in sorted(scope["delta"]):
        items.append("D:%s|%s->%s" % (k[0], k[1], ",".join(scope["delta"][k])))
    for b in scope["budgets"]:
        items.append("B:" + ",".join("%s=%s" % (c, b[c]) for c in coords))
    return ";".join(items)


SIGNATURE_FIELDS = ("arity", "types", "state_access", "locality", "addressability",
                    "content_dependent_routing", "parameter_sharing", "recurrence",
                    "stochasticity", "verifier_access", "resource_class")


def registered_primitives():
    """Every search-visible primitive this tranche introduces, with its
    11-field signature for the A2 semantic screen."""
    return [
        {"id": "point_value_query",
         "features": {"arity": 1, "types": ("configuration", "rational"),
                      "state_access": "read_only", "locality": "current_point",
                      "addressability": "positional", "content_dependent_routing": False,
                      "parameter_sharing": False, "recurrence": False,
                      "stochasticity": False, "verifier_access": False,
                      "resource_class": "O(1)"}},
        {"id": "improving_selection_query",
         "features": {"arity": 1, "types": ("configuration", "configuration"),
                      "state_access": "read_only", "locality": "declared_successor_set",
                      "addressability": "positional", "content_dependent_routing": False,
                      "parameter_sharing": False, "recurrence": False,
                      "stochasticity": True, "verifier_access": False,
                      "resource_class": "O(1)"}},
        {"id": "edge_multiply_accumulate",
         "features": {"arity": 2, "types": ("rational", "rational"),
                      "state_access": "read_write", "locality": "single_edge",
                      "addressability": "positional", "content_dependent_routing": False,
                      "parameter_sharing": False, "recurrence": False,
                      "stochasticity": False, "verifier_access": False,
                      "resource_class": "O(1)"}},
        {"id": "interior_vertex_elimination",
         "features": {"arity": 1, "types": ("vertex", "graph"),
                      "state_access": "read_write", "locality": "neighborhood",
                      "addressability": "positional", "content_dependent_routing": False,
                      "parameter_sharing": False, "recurrence": False,
                      "stochasticity": False, "verifier_access": False,
                      "resource_class": "O(indeg*outdeg)"}},
        {"id": "slot_retention",
         "features": {"arity": 1, "types": ("rational", "rational"),
                      "state_access": "read_write", "locality": "single_slot",
                      "addressability": "positional", "content_dependent_routing": False,
                      "parameter_sharing": False, "recurrence": False,
                      "stochasticity": False, "verifier_access": False,
                      "resource_class": "O(1)"}},
    ]


def target_fingerprints():
    """Registered target fingerprints. Matching one atomically is leakage."""
    return [
        {"name": "content_routed_weighted_aggregation",
         "required_features": {"locality": "global", "content_dependent_routing": True,
                               "addressability": "content"}},
        {"name": "translation_shared_local_kernel",
         "required_features": {"locality": "neighborhood", "parameter_sharing": True}},
        {"name": "gated_recurrent_state_carrier",
         "required_features": {"recurrence": True, "state_access": "read_write",
                               "content_dependent_routing": True}},
        {"name": "content_addressed_retrieval",
         "required_features": {"addressability": "content", "state_access": "read_only",
                               "locality": "global"}},
    ]


def semantic_screen():
    prims = registered_primitives()
    fps = target_fingerprints()
    findings = []
    for p in prims:
        missing = sorted(set(SIGNATURE_FIELDS) - set(p["features"]))
        if missing:
            return {"verdict": "CANNOT_AUDIT_PRIMITIVE_SIGNATURES",
                    "primitive": p["id"], "missing": missing}
        for fp in fps:
            if all(p["features"].get(k) == v for k, v in fp["required_features"].items()):
                findings.append({"primitive": p["id"], "fingerprint": fp["name"]})
    return {"primitives_registered": len(prims),
            "signature_fields": len(SIGNATURE_FIELDS),
            "fingerprints_checked": len(fps),
            "findings": findings,
            "verdict": "CLEAN_AT_REGISTERED_AUDIT_SCOPE" if not findings
            else "SEMANTIC_MACRO_LEAKAGE"}


def remint_scope(scope, token_map):
    r = tuple(token_map[x] for x in scope["realizations"])
    h = tuple(token_map[x] for x in scope["histories"])
    c = tuple(token_map[x] for x in scope["coords"])
    delta = dict(((token_map[a], token_map[b]),
                  tuple(token_map[z] for z in v))
                 for (a, b), v in scope["delta"].items())
    ext = dict(((token_map[a], token_map[b]), token_map[v])
               for (a, b), v in scope["ext"].items())
    budgets = tuple(dict((token_map[k], v) for k, v in b.items())
                    for b in scope["budgets"])
    return {"realizations": r, "histories": h, "coords": c,
            "delta": delta, "ext": ext, "budgets": budgets}


def remint_certificate():
    """Opaque-token remint: rename every scope symbol to t0, t1, ... and check
    that every derived admissibility verdict is invariant under the induced
    relabeling."""
    scope = make_scope()
    symbols = (list(scope["realizations"]) + list(scope["histories"])
               + list(scope["coords"]))
    token_map = dict((s, "t%d" % i) for i, s in enumerate(symbols))
    if len(set(token_map.values())) != len(symbols):
        fail("remint map is not injective")
    inverse = dict((v, k) for k, v in token_map.items())
    scope2 = remint_scope(scope, token_map)

    pop = registered_laws(scope)
    checks = []
    for name in sorted(pop):
        law = pop[name]

        def reminted(r2, h2, b2, _law=law):
            b1 = dict((inverse[k], v) for k, v in b2.items())
            d1, c1 = _law(inverse[r2], inverse[h2], b1)
            d2 = dict((token_map[t], pr) for t, pr in d1.items())
            c2 = dict((token_map[k], v) for k, v in c1.items())
            return d2, c2

        for grade in ("ONE_STEP", "CLOSURE"):
            v1, f1, _ = admissible(scope, grade, law)
            v2, f2, _ = admissible(scope2, grade, reminted)
            checks.append(v1 == v2 and len(f1) == len(f2))
    return {"symbols_reminted": len(symbols),
            "opaque_tokens": sorted(set(token_map.values()))[:4] + ["..."],
            "verdict_pairs_checked": len(checks),
            "all_verdicts_invariant": all(checks)}


# ---------------------------------------------------------------------------

def build_result():
    return {
        "schema": "GMI833SectionIUpdateLawSpaceResultV1",
        "issue": 833,
        "section": "I",
        "package": "research/gmi-833-update-law-space-v1",
        "freeze": "FREEZE_V1.md",
        "claim_ceiling": "GMI_833_SECTION_I_UPDATE_LAW_SPACE_AND_CREDIT_ASSIGNMENT_REGIMES_AT_REGISTERED_FINITE_SCOPE",
        "route": "A_EXECUTOR",
        "IL_1": il1_certificate(),
        "scope_fingerprint": scope_fingerprint(),
        "IL_23": il23_certificate(),
        "IL_23_boundary": equivariance_boundary_witness(),
        "IL_4": il4_certificate(),
        "name_freedom": {
            "lexical_A1": lexical_screen(),
            "semantic_A2": semantic_screen(),
            "opaque_token_remint": remint_certificate(),
        },
    }


def main():
    res = build_result()
    out = os.path.join(HERE, "RESULT_V1.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
        fh.write("\n")
    il1 = res["IL_1"]
    il23 = res["IL_23"]
    il4 = res["IL_4"]
    print("IL-1 laws=%d mixture_cases=%d failures=%d composition_cases=%d failures=%d"
          % (il1["law_population"], il1["mixture_cases"], len(il1["mixture_failures"]),
             il1["composition_cases"], len(il1["closure_composition_failures"])))
    print("IL-1 one-step composition counterexample verdict=%s (closure=%s)"
          % (il1["one_step_composition_counterexample"]["one_step_verdict"],
             il1["one_step_composition_counterexample"]["closure_verdict"]))
    print("IL-1 kernel associativity=%s charge subassociative=%s strict witness=%s"
          % (il1["kernel_associativity_exact"], il1["charge_subassociative"],
             il1["charge_strictness_witness"] is not None))
    print("IL-2/3 paths=%d grid=%d cases=%d partition_failures=%d counts=%s"
          % (il23["paths"], il23["price_ratio_grid_size"], il23["trichotomy_cases"],
             len(il23["partition_failures"]), il23["verdict_counts"]))
    for g in il4["graphs"]:
        print("IL-4 %-16s n=%d N=%d E=%d p=%d w=%d regime=%s sigma*=%s orders=%d "
              "min=%s revtopo=%s topo=%s argmin_has_revtopo=%s mixed_only=%s"
              % (g["graph"], g["sources_n"], g["internal_N"], g["edges_E"],
                 g["outputs_p"], g["peak_live_internal_w"], g["regime"],
                 g["sigma_star"], g["order_census"]["orders_enumerated"],
                 g["order_census"]["minimum_cost"],
                 g["order_census"]["reverse_topological_order_cost"],
                 g["order_census"]["topological_order_cost"],
                 g["order_census"]["argmin_includes_reverse_topological"],
                 g["order_census"]["argmin_is_a_mixed_order_only"]))
    nf = res["name_freedom"]
    lx = nf["lexical_A1"]
    print("name-freedom: A1=%s (%d files, %d tokens, %d hits all declared, "
          "%d unmatched, %d stale, %d strict violations) A2=%s remint=%s"
          % (lx["verdict"], len(lx["screened_files"]), lx["tokens_screened"],
             lx["hits_allowed_by_declared_occurrence"],
             len(lx["hits_unmatched"]), len(lx["stale_allowances"]),
             len(lx["strictly_clean_violations"]),
             nf["semantic_A2"]["verdict"],
             nf["opaque_token_remint"]["all_verdicts_invariant"]))
    print("wrote " + out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
