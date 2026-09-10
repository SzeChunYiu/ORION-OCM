"""D21 reduction + equality-saturation lab (OW6).

Protocol frozen in D21_D22_PROTOCOL_V1.md before this file existed.
Worlds, evaluator and rewrite semantics come verbatim from exact/worlds.py.
"""
from __future__ import annotations
import time

from . import worlds as W
from .egraph import EGraph, EClassCapExceeded

X_DOMAIN = tuple(range(21))          # exact for degree <= 20; frozen worlds are <= 16
NUMERIC_TOKENS = {"2": 2, "3": 3, "5": 5}
ACQUIRE_WORLDS = 5                   # worlds 0..4 acquire the library, 5..9 are held out
ECLASS_CAP = 50_000
BFS_CAP = 200_000

# --------------------------------------------------------------- semantics --
def d21_eval(t, x):
    """D21 evaluator: frozen alphabet plus folded integer literals."""
    if isinstance(t, tuple):
        op, l, r = t
        a, b = d21_eval(l, x), d21_eval(r, x)
        return a + b if op == "+" else a * b
    if isinstance(t, int):
        return t
    if t == "x":
        return x
    return NUMERIC_TOKENS[t]

def node_count(t) -> int:
    return 1 if not isinstance(t, tuple) else 1 + node_count(t[1]) + node_count(t[2])

def degree(t) -> int:
    if not isinstance(t, tuple):
        return 1 if t == "x" else 0
    a, b = degree(t[1]), degree(t[2])
    return max(a, b) if t[0] == "+" else a + b

def o1_vector(t):
    return tuple(d21_eval(t, x) for x in X_DOMAIN)

_SYMPY = None
def _sympy():
    global _SYMPY
    if _SYMPY is None:
        import sympy
        _SYMPY = (sympy, sympy.Symbol("x"))
    return _SYMPY

def o2_normal(t) -> str:
    sympy, xs = _sympy()
    def conv(u):
        if isinstance(u, tuple):
            a, b = conv(u[1]), conv(u[2])
            return a + b if u[0] == "+" else a * b
        if isinstance(u, int):
            return sympy.Integer(u)
        return xs if u == "x" else sympy.Integer(NUMERIC_TOKENS[u])
    return str(sympy.expand(conv(t)))

def sem_equal(a, b):
    """(equal, status). status CHECKED or CANNOT_CHECK when the two oracles disagree."""
    o1 = o1_vector(a) == o1_vector(b)
    o2 = o2_normal(a) == o2_normal(b)
    if o1 != o2:
        return None, "CANNOT_CHECK"
    return o1, "CHECKED"

# ------------------------------------------------------ term-level rewrites --
def positions(t):
    yield ()
    if isinstance(t, tuple):
        for i in (1, 2):
            for p in positions(t[i]):
                yield (i,) + p

def at(t, p):
    return t if not p else at(t[p[0]], p[1:])

def replace(t, p, new):
    if not p:
        return new
    lst = list(t)
    lst[p[0]] = replace(t[p[0]], p[1:], new)
    return tuple(lst)

def _num(u):
    if isinstance(u, int):
        return u
    if isinstance(u, str) and u in NUMERIC_TOKENS:
        return NUMERIC_TOKENS[u]
    return None

def local_fold(t):
    if not isinstance(t, tuple):
        return None
    a, b = _num(t[1]), _num(t[2])
    if a is None or b is None:
        return None
    return a + b if t[0] == "+" else a * b

def local_factor(t):
    """(a*b)+(a*c) -> a*(b+c); sound and strictly node-count-reducing."""
    if not (isinstance(t, tuple) and t[0] == "+"):
        return None
    l, r = t[1], t[2]
    if not (isinstance(l, tuple) and l[0] == "*" and isinstance(r, tuple) and r[0] == "*"):
        return None
    if l[1] == r[1]:
        return ("*", l[1], ("+", l[2], r[2]))
    return None

def local_rewrite(t, name):
    """One rewrite at the root of `t`. Frozen rules delegate to worlds.rewrite_apply."""
    if name in W.REWRITE_NAMES or name == "unsound_swap":
        return W.rewrite_apply(t, name)
    if name == "fold":
        return local_fold(t)
    if name == "factor":
        return local_factor(t)
    raise KeyError(name)

SOUND_FROZEN = tuple(W.REWRITE_NAMES)
SOUND_EXT = ("fold", "factor")
SOUND_ALL = SOUND_FROZEN + SOUND_EXT
UNSOUND = ("unsound_swap",)

def one_step_results(t, rules):
    """Every (rule, position) single-step rewrite of `t`."""
    out = []
    for p in positions(t):
        sub = at(t, p)
        for name in rules:
            new = local_rewrite(sub, name)
            if new is not None and new != sub:
                out.append((name, p, replace(t, p, new)))
    return out

# --------------------------------------------------------------- e-graph ----
def _rule_comm(op):
    def f(eg):
        for c, n in list(eg.enodes()):
            if n[0] == op:
                yield c, eg.add_node((op, n[2], n[1]))
    return f

def _rule_assoc_plus(eg):
    for c, n in list(eg.enodes()):
        if n[0] != "+":
            continue
        for m in list(eg.classes[eg.find(n[1])]):
            if m[0] == "+":
                inner = eg.add_node(("+", m[2], n[2]))
                yield c, eg.add_node(("+", m[1], inner))

def _rule_fold(eg):
    for c, n in list(eg.enodes()):
        if n[0] == "leaf":
            continue
        a, b = eg.leaf_value(n[1]), eg.leaf_value(n[2])
        if a is None or b is None:
            continue
        v = a + b if n[0] == "+" else a * b
        yield c, eg.add_node(("leaf", v))

def _rule_factor(eg):
    for c, n in list(eg.enodes()):
        if n[0] != "+":
            continue
        for m1 in list(eg.classes[eg.find(n[1])]):
            if m1[0] != "*":
                continue
            for m2 in list(eg.classes[eg.find(n[2])]):
                if m2[0] != "*" or eg.find(m1[1]) != eg.find(m2[1]):
                    continue
                s = eg.add_node(("+", m1[2], m2[2]))
                yield c, eg.add_node(("*", m1[1], s))

def _rule_unsound_swap(eg):
    for c, n in list(eg.enodes()):
        if n[0] == "+":
            yield c, eg.add_node(("*", n[1], n[2]))

def egraph_rules(include_unsound: bool):
    r = {"comm+": _rule_comm("+"), "comm*": _rule_comm("*"),
         "assoc+": _rule_assoc_plus, "fold": _rule_fold, "factor": _rule_factor}
    if include_unsound:
        r["unsound_swap"] = _rule_unsound_swap
    return r

# ------------------------------------------------------------------ arms ----
def arm_direct_solve(seed, rules):
    """Exhaustive BFS closure. The reference optimum; caps are reported, not hidden."""
    t0 = time.process_time()
    seen, frontier, applications = {seed}, [seed], 0
    capped = False
    while frontier:
        nxt = []
        for t in frontier:
            for _name, _p, new in one_step_results(t, rules):
                applications += 1
                if new not in seen:
                    if len(seen) >= BFS_CAP:
                        capped = True
                        break
                    seen.add(new)
                    nxt.append(new)
            if capped:
                break
        if capped:
            break
        frontier = nxt
    best = min(seen, key=lambda t: (node_count(t), repr(t)))
    return {"arm": "direct_solve", "best": best, "cost": node_count(best),
            "status": "CANNOT_CHECK" if capped else "CHECKED",
            "reachable": len(seen),
            "present_cost": {"rewrite_applications": applications,
                             "terms_enumerated": len(seen),
                             "cpu_s": round(time.process_time() - t0, 4)}}

def arm_one_shot(seed, rules):
    t0 = time.process_time()
    cands = [seed] + [r[2] for r in one_step_results(seed, rules)]
    best = min(cands, key=lambda t: (node_count(t), repr(t)))
    return {"arm": "one_shot_rewrite", "best": best, "cost": node_count(best),
            "status": "CHECKED",
            "present_cost": {"rewrite_applications": len(cands) - 1,
                             "terms_enumerated": len(cands),
                             "cpu_s": round(time.process_time() - t0, 4)}}

def _order_key(t):
    return (node_count(t), repr(t))

def arm_ordered_rewriting(seed, rules, max_steps=20000):
    """Ordered rewriting under the total ground order (node_count, repr)."""
    t0 = time.process_time()
    cur, applications, steps = seed, 0, 0
    while steps < max_steps:
        steps += 1
        best = None
        for _name, _p, new in one_step_results(cur, rules):
            applications += 1
            if _order_key(new) < _order_key(cur) and (best is None or
                                                      _order_key(new) < _order_key(best)):
                best = new
        if best is None:
            break
        cur = best
    return {"arm": "ordered_rewriting", "best": cur, "cost": node_count(cur),
            "status": "CHECKED" if steps < max_steps else "CANNOT_CHECK",
            "present_cost": {"rewrite_applications": applications,
                             "terms_enumerated": steps,
                             "cpu_s": round(time.process_time() - t0, 4)}}

def arm_knuth_bendix(rules):
    """Standard KB orientation attempt. Permutative axioms cannot be oriented."""
    t0 = time.process_time()
    equations = {
        "comm+": ("(a+b)", "(b+a)", "permutative"),
        "comm*": ("(a*b)", "(b*a)", "permutative"),
        "assoc+": ("((a+b)+c)", "(a+(b+c))", "orientable"),
        "fold": ("(c1 op c2)", "value", "orientable (strictly size-reducing)"),
        "factor": ("((a*b)+(a*c))", "(a*(b+c))", "orientable (strictly size-reducing)"),
    }
    oriented = [k for k, v in equations.items() if v[2].startswith("orientable") and k in rules]
    failed = [k for k, v in equations.items() if v[2] == "permutative" and k in rules]
    return {"arm": "knuth_bendix",
            "verdict": "FAILS_TO_ORIENT" if failed else "COMPLETED",
            "oriented": oriented, "unorientable": failed,
            "reason": "no reduction order orients a permutative axiom (l and r are "
                      "variable permutations of one another), so standard Knuth-Bendix "
                      "is not applicable to the frozen AC-style set; ordered rewriting "
                      "under a total ground order is the applicable substitute",
            "completeness_note": "the completed system over the orientable subset alone "
                                 "is NOT complete for the AC theory",
            "present_cost": {"cpu_s": round(time.process_time() - t0, 4)}}

def arm_equality_saturation(seed, include_unsound: bool):
    t0 = time.process_time()
    eg = EGraph()
    root = eg.add_term(seed)
    eg.rebuild()
    iters, saturated = eg.saturate(egraph_rules(include_unsound))
    try:
        members = eg.eclass_terms(root, cap=ECLASS_CAP)
        status, n_members = "CHECKED", len(members)
        best = min(members, key=lambda t: (node_count(t), repr(t)))
    except EClassCapExceeded as ex:
        members, status, n_members = None, "CANNOT_CHECK", None
        best = _extract_min_bounded(eg, root)
        ex_note = str(ex)
    return {"arm": "equality_saturation", "best": best, "cost": node_count(best),
            "status": status, "saturated": saturated, "iterations": iters,
            "n_eclass_members": n_members, "members": members,
            "eclass_note": None if status == "CHECKED" else ex_note,
            "present_cost": {"rewrite_applications": eg.stats["rule_applications"],
                             "enodes": eg.stats["enodes"], "merges": eg.stats["merges"],
                             "eclasses": eg.n_classes(),
                             "cpu_s": round(time.process_time() - t0, 4)},
            "_eg": eg, "_root": root}

def _extract_min_bounded(eg, root):
    """Bottom-up cheapest-term extraction (used when exhaustive walk is capped)."""
    cost, best = {}, {}
    for _ in range(len(eg.classes) + 2):
        changed = False
        for c, n in eg.enodes():
            if n[0] == "leaf":
                k, t = 1, n[1]
            else:
                if eg.find(n[1]) not in cost or eg.find(n[2]) not in cost:
                    continue
                k = 1 + cost[eg.find(n[1])] + cost[eg.find(n[2])]
                t = (n[0], best[eg.find(n[1])], best[eg.find(n[2])])
            if c not in cost or (k, repr(t)) < (cost[c], repr(best[c])):
                cost[c], best[c], changed = k, t, True
        if not changed:
            break
    return best[eg.find(root)]

# ------------------------------------------------------ egglog reuse arm ----
_EGGLOG = None
def _egglog():
    """Mature-engine arm (egglog 13.2.0, Rust egraphs-good). Independent cross-check."""
    global _EGGLOG
    if _EGGLOG is not None:
        return _EGGLOG
    try:
        from egglog import EGraph as EG, Expr, i64, rewrite, ruleset, eq

        class M(Expr):
            def __init__(self, v: i64) -> None: ...
            @classmethod
            def x(cls) -> "M": ...
            def __add__(self, o: "M") -> "M": ...
            def __mul__(self, o: "M") -> "M": ...

        @ruleset
        def sound(a: M, b: M, c: M, i: i64, j: i64):
            yield rewrite(a + b).to(b + a)
            yield rewrite(a * b).to(b * a)
            yield rewrite((a + b) + c).to(a + (b + c))
            yield rewrite(M(i) + M(j)).to(M(i + j))
            yield rewrite(M(i) * M(j)).to(M(i * j))
            yield rewrite((a * b) + (a * c)).to(a * (b + c))

        @ruleset
        def unsound(a: M, b: M):
            yield rewrite(a + b).to(a * b)

        _EGGLOG = {"EG": EG, "M": M, "sound": sound, "unsound": unsound, "eq": eq}
    except Exception as ex:                                   # pragma: no cover
        _EGGLOG = {"error": f"{type(ex).__name__}: {ex}"}
    return _EGGLOG

def _to_egglog(t, M):
    if isinstance(t, tuple):
        a, b = _to_egglog(t[1], M), _to_egglog(t[2], M)
        return a + b if t[0] == "+" else a * b
    if isinstance(t, int):
        return M(t)
    return M.x() if t == "x" else M(NUMERIC_TOKENS[t])

def egglog_equal(a, b, include_unsound=False):
    """(equal, status) decided by the mature engine, independent of our e-graph."""
    E = _egglog()
    if "error" in E:
        return None, "CANNOT_CHECK:" + E["error"]
    try:
        eg = E["EG"]()
        ea = eg.let("ea", _to_egglog(a, E["M"]))
        eb = eg.let("eb", _to_egglog(b, E["M"]))
        rs = E["sound"]
        if include_unsound:
            eg.run(E["unsound"].saturate())
        eg.run(rs.saturate())
        return bool(eg.check_bool(E["eq"](ea).to(eb))), "CHECKED"
    except Exception as ex:
        return None, f"CANNOT_CHECK:{type(ex).__name__}: {ex}"

# ---------------------------------------------- semantic protection check ---
def contamination_scan(seed, arm_result):
    """Alarm iff any produced term is not semantically equal to the seed.

    For equality saturation the scan covers EVERY e-class member (T86's invariant),
    not merely the extracted representative (T86's corollary).
    """
    checked, alarms, cannot = 0, [], 0
    def check(term, kind):
        nonlocal checked, cannot
        eqv, st = sem_equal(seed, term)
        if st == "CANNOT_CHECK":
            cannot += 1
            return
        checked += 1
        if not eqv:
            alarms.append({"kind": kind, "term": repr(term),
                           "seed_at_1": d21_eval(seed, 1), "term_at_1": d21_eval(term, 1)})
    check(arm_result["best"], "extracted")
    members = arm_result.get("members")
    if members is not None:
        for m in members:
            check(m, "eclass_member")
    return {"n_checked": checked, "n_cannot_check": cannot,
            "n_alarms": len(alarms), "alarms": alarms[:5],
            "scan_status": "CHECKED" if cannot == 0 else "PARTIAL_CANNOT_CHECK",
            "eclass_coverage": ("EXHAUSTIVE" if members is not None else
                                "EXTRACTION_ONLY (e-class walk capped)")}

# ------------------------------------------------------- H-T86a witness -----
def contaminability_control(ow6):
    """Per-world structural predicate: CAN unsound_swap change a value here?

    Computed from the frozen world and the frozen rewrite alone -- independent of the
    e-graph and of the detector, so it can serve as the denominator for the detection
    endpoint without circularity. A world with no '+' node, or whose every '+' node
    satisfies l+r == l*r on all of X, is NOT_CONTAMINABLE: silence there is the
    correct answer and is scored as a no-alarm control, never as a missed detection.
    """
    rows = []
    for w in ow6:
        e = w["expr"]
        plus = [p for p in positions(e)
                if isinstance(at(e, p), tuple) and at(e, p)[0] == "+"]
        changing = []
        for p in plus:
            s = at(e, p)
            sw = W.rewrite_apply(s, "unsound_swap")
            xs = [x for x in X_DOMAIN if d21_eval(s, x) != d21_eval(sw, x)]
            if xs:
                changing.append({"subterm": repr(s), "position": list(p),
                                 "n_points_differing": len(xs), "first_x": xs[0],
                                 "value_sound": d21_eval(s, xs[0]),
                                 "value_unsound": d21_eval(sw, xs[0])})
        rows.append({"world": w["id"], "n_plus_nodes": len(plus),
                     "n_value_changing_plus_nodes": len(changing),
                     "contaminable": bool(changing),
                     "witnesses": changing[:2],
                     "reason_if_not": ("no '+' node, unsound_swap cannot apply"
                                       if not plus else
                                       "every '+' node satisfies l+r == l*r on all of X, "
                                       "so the unsound rule is sound on this instance")
                                      if not changing else None})
    return {"rows": rows,
            "n_contaminable": sum(1 for r in rows if r["contaminable"]),
            "n_not_contaminable": sum(1 for r in rows if not r["contaminable"]),
            "note": "denominator for E1; the frozen falsifier ('any contaminated e-class "
                    "with no alarm') is unchanged"}

def find_unsound_witness(ow6):
    """Frozen requirement: some OW6 '+' node with l+r != l*r at some x in X_DOMAIN."""
    for w in ow6:
        for p in positions(w["expr"]):
            sub = at(w["expr"], p)
            if not (isinstance(sub, tuple) and sub[0] == "+"):
                continue
            swapped = W.rewrite_apply(sub, "unsound_swap")
            for x in X_DOMAIN:
                a, b = d21_eval(sub, x), d21_eval(swapped, x)
                if a != b:
                    return {"found": True, "world": w["id"], "position": list(p),
                            "subterm": repr(sub), "x": x,
                            "value_sound": a, "value_unsound": b}
    return {"found": False}

# --------------------------------------------------------- learned library --
def learned_library(ow6):
    """Mine (pattern -> replacement) lemmas on worlds 0..4, apply on 5..9.

    Present cost charges every candidate considered, including rejected ones and
    the acquisition itself. Future reuse is credited only on held-out worlds.
    """
    t0 = time.process_time()
    acquire = [w for w in ow6 if int(w["id"].split("-")[1]) < ACQUIRE_WORLDS]
    holdout = [w for w in ow6 if int(w["id"].split("-")[1]) >= ACQUIRE_WORLDS]
    considered, rejected, lib = 0, 0, {}
    for w in acquire:
        res = arm_ordered_rewriting(w["expr"], SOUND_ALL)
        for p in positions(w["expr"]):
            sub = at(w["expr"], p)
            if not isinstance(sub, tuple):
                continue
            norm = arm_ordered_rewriting(sub, SOUND_ALL)["best"]
            considered += 1
            eqv, st = sem_equal(sub, norm)
            if st != "CHECKED" or not eqv or node_count(norm) >= node_count(sub):
                rejected += 1
                continue
            lib[repr(sub)] = norm
    acq_cpu = round(time.process_time() - t0, 4)

    t1 = time.process_time()
    hits, saved, applied = 0, 0, []
    for w in holdout:
        base = arm_ordered_rewriting(w["expr"], SOUND_ALL)
        t = w["expr"]
        changed = True
        while changed:                       # positions must be recomputed after each edit
            changed = False
            for p in list(positions(t)):
                sub = at(t, p)
                if repr(sub) not in lib:
                    continue
                hits += 1
                cand = replace(t, p, lib[repr(sub)])
                eqv, st = sem_equal(t, cand)
                if st == "CHECKED" and eqv and node_count(cand) < node_count(t):
                    t = cand                 # strict decrease guarantees termination
                    changed = True
                    break
        with_lib = node_count(arm_ordered_rewriting(t, SOUND_ALL)["best"])
        saved += base["cost"] - with_lib
        applied.append({"world": w["id"], "baseline_cost": base["cost"],
                        "with_library_cost": with_lib,
                        "delta": base["cost"] - with_lib})
    return {"library_size": len(lib),
            "present_cost_acquisition": {"candidates_considered": considered,
                                         "candidates_rejected": rejected,
                                         "acquisition_worlds": [w["id"] for w in acquire],
                                         "cpu_s": acq_cpu},
            "future_reuse_holdout": {"holdout_worlds": [w["id"] for w in holdout],
                                     "library_hits": hits,
                                     "total_nodes_saved": saved,
                                     "per_world": applied,
                                     "cpu_s": round(time.process_time() - t1, 4)},
            "verdict": ("REPAID" if saved > 0 else "PARENT_SUFFICIENT"),
            "verdict_note": ("library never repaid its acquisition on held-out worlds; "
                             "ordered rewriting alone already owns the function"
                             if saved <= 0 else "library reduced held-out cost"),
            "cost_split_rule": "acquisition and reuse are reported separately and are "
                               "never netted into one figure"}

# ------------------------------------------- T74 reduction composition ------
def t74_composition(ow6, k_slack=0):
    """A: find t ~ e with cost <= k. Reduce A->B (e-graph) ->D (extraction).

    Soundness of the composition rests on e-class membership implying semantic
    equality, i.e. exactly T86. H-T74a plants a broken leg by running leg B on the
    contaminated e-graph; the composed reduction must then produce an invalid
    A-solution that verification catches.
    """
    rows = []
    for w in ow6:
        seed = w["expr"]
        for label, unsound in (("clean", False), ("hostile", True)):
            res = arm_equality_saturation(seed, unsound)
            y_b = res["best"]                      # B-solution
            g = y_b                                # reconstruction g_AB(x, y_B) = y_B
            k = node_count(seed) + k_slack
            v_b = node_count(y_b) <= k             # V_B: cheap member of the e-class
            eqv, st = sem_equal(seed, g)
            v_a = bool(eqv) and node_count(g) <= k
            rows.append({"world": w["id"], "leg": label,
                         "V_B": v_b, "V_A": v_a, "status": st,
                         "composition_sound": (not v_b) or v_a,
                         "witness": None if ((not v_b) or v_a) else
                                    {"x": repr(seed), "y_B": repr(y_b),
                                     "seed_at_1": d21_eval(seed, 1),
                                     "recon_at_1": d21_eval(g, 1)}})
    clean = [r for r in rows if r["leg"] == "clean"]
    hostile = [r for r in rows if r["leg"] == "hostile"]
    return {"rows": rows,
            "clean_all_sound": all(r["composition_sound"] for r in clean),
            "hostile_broken_legs_caught": sum(1 for r in hostile
                                              if not r["composition_sound"]),
            "hostile_total": len(hostile),
            "endpoint": "E5",
            "note": "V_A is decided by the two independent semantics oracles, never by "
                    "the same e-graph that produced the B-solution"}

# ---------------------------------------------------------- TASK-EQ pairs ---
def egraph_equal(a, b, include_unsound=False):
    """Our own e-graph's equivalence decision (independent of egglog)."""
    eg = EGraph()
    ca, cb = eg.add_term(a), eg.add_term(b)
    eg.rebuild()
    eg.saturate(egraph_rules(include_unsound))
    return eg.find(ca) == eg.find(cb), eg.stats["enodes"]

_SWAP = {"2": "3", "3": "5", "5": "x", "x": "2"}

def build_eq_pairs(ow6):
    """40 expected-true rewrite walks + 40 leaf perturbations. Ground truth decides."""
    pairs = []
    for w in ow6:
        wi = int(w["id"].split("-")[1])
        for k in (1, 2, 4, 8):
            rng = W._rng("D21EQ_WALK", wi, k)
            t = w["expr"]
            for _ in range(k):
                steps = one_step_results(t, SOUND_ALL)
                if not steps:
                    break
                t = rng.choice(sorted(steps, key=lambda s: repr(s)))[2]
            pairs.append({"world": w["id"], "kind": "walk", "k": k,
                          "a": w["expr"], "b": t, "expected": True})
        leafpos = [p for p in positions(w["expr"]) if not isinstance(at(w["expr"], p), tuple)]
        for j in range(4):
            rng = W._rng("D21EQ_PERT", wi, j)
            p = leafpos[j % len(leafpos)] if leafpos else ()
            old = at(w["expr"], p)
            new = _SWAP[old] if isinstance(old, str) else old
            pairs.append({"world": w["id"], "kind": "perturb", "k": j,
                          "a": w["expr"], "b": replace(w["expr"], p, new),
                          "expected": False})
    return pairs

def run_task_eq(pairs):
    rows, disagreements, cannot = [], [], 0
    n_true_gt = 0
    for pr in pairs:
        gt, st = sem_equal(pr["a"], pr["b"])
        if st == "CANNOT_CHECK":
            cannot += 1
            rows.append({"world": pr["world"], "kind": pr["kind"], "k": pr["k"],
                         "ground_truth": None, "status": st})
            continue
        n_true_gt += bool(gt)
        mine, _ = egraph_equal(pr["a"], pr["b"])
        theirs, est = egglog_equal(pr["a"], pr["b"])
        row = {"world": pr["world"], "kind": pr["kind"], "k": pr["k"],
               "ground_truth": bool(gt), "egraph": bool(mine),
               "egglog": theirs, "egglog_status": est,
               "egraph_sound": (not mine) or bool(gt)}
        rows.append(row)
        if est == "CHECKED" and theirs != mine:
            disagreements.append(row)
    checked = [r for r in rows if r.get("ground_truth") is not None]
    return {"n_pairs": len(pairs), "n_checked": len(checked),
            "n_cannot_check": cannot,
            "n_ground_truth_equivalent": n_true_gt,
            "n_ground_truth_distinct": len(checked) - n_true_gt,
            "egraph_unsound_decisions": sum(1 for r in checked if not r["egraph_sound"]),
            "egraph_complete_on_true": sum(1 for r in checked
                                           if r["ground_truth"] and r["egraph"]),
            "cross_check_agreement": (1.0 if not disagreements else
                                      round(1 - len(disagreements) / max(1, len(checked)), 4)),
            "cross_check_disagreements": disagreements[:5],
            "endpoint": "E6", "rows": rows}

# ----------------------------------------------------------------- driver ---
def _strip(res):
    return {k: v for k, v in res.items() if not k.startswith("_") and k != "members"}

def conformance_control(ow6):
    """D21 evaluator must agree with the frozen worlds.expr_eval on every frozen term."""
    bad, n = [], 0
    for w in ow6:
        for p in positions(w["expr"]):
            sub = at(w["expr"], p)
            for x in X_DOMAIN:
                n += 1
                if d21_eval(sub, x) != W.expr_eval(sub, x):
                    bad.append({"world": w["id"], "sub": repr(sub), "x": x})
    return {"n_points": n, "n_mismatch": len(bad), "mismatches": bad[:3],
            "passed": not bad,
            "note": "control that MUST pass; a failure invalidates the lane, not an arm"}

def degree_control(ow6):
    d = max(degree(w["expr"]) for w in ow6)
    return {"max_degree": d, "domain_points": len(X_DOMAIN),
            "o1_exact": d < len(X_DOMAIN),
            "note": "O1 is exact, not a sample, because |X| exceeds the maximum degree"}

def run_d21():
    t0w, t0c = time.time(), time.process_time()
    ow6 = W.ow6_worlds()
    conf = conformance_control(ow6)
    deg = degree_control(ow6)
    witness = find_unsound_witness(ow6)

    arms_clean, arms_hostile, scans_clean, scans_hostile = [], [], [], []
    for w in ow6:
        seed = w["expr"]
        for rules, unsound, arms, scans in ((SOUND_ALL, False, arms_clean, scans_clean),
                                            (SOUND_ALL + UNSOUND, True, arms_hostile,
                                             scans_hostile)):
            per = {"world": w["id"], "seed": repr(seed), "seed_cost": node_count(seed)}
            for fn in (arm_direct_solve, arm_one_shot, arm_ordered_rewriting):
                r = fn(seed, rules)
                per[r["arm"]] = _strip(r)
                scans.append({"world": w["id"], "arm": r["arm"],
                              **contamination_scan(seed, r)})
            es = arm_equality_saturation(seed, unsound)
            per["equality_saturation"] = _strip(es)
            scans.append({"world": w["id"], "arm": "equality_saturation",
                          **contamination_scan(seed, es)})
            arms.append(per)

    kb = arm_knuth_bendix(SOUND_ALL)
    eq_pairs = build_eq_pairs(ow6)
    eqres = run_task_eq(eq_pairs)
    amort = amortised_reuse(ow6, eq_pairs)
    lib = learned_library(ow6)
    t74 = t74_composition(ow6)

    clean_alarms = sum(s["n_alarms"] for s in scans_clean)
    host_by_world = {}
    for s in scans_hostile:
        if s["arm"] == "equality_saturation":
            host_by_world[s["world"]] = s
    contam = contaminability_control(ow6)
    can = {r["world"] for r in contam["rows"] if r["contaminable"]}
    cannot = {r["world"] for r in contam["rows"] if not r["contaminable"]}
    detected = {w for w in can if host_by_world.get(w, {}).get("n_alarms", 0) > 0}
    missed = sorted(can - detected)
    false_on_uncontaminable = sorted(w for w in cannot
                                     if host_by_world.get(w, {}).get("n_alarms", 0) > 0)

    # H-T86b: developmental variants destroyed by quotienting (T87)
    t87 = []
    for w in ow6:
        es = arm_equality_saturation(w["expr"], False)
        n = es["n_eclass_members"]
        t87.append({"world": w["id"], "distinct_variants": n,
                    "kept_by_quotienting": 1 if n is not None else None,
                    "destroyed": (n - 1) if n is not None else None,
                    "status": es["status"]})

    summary = {
        "E1_hostile_detection_rate": round(len(detected) / max(1, len(can)), 4),
        "E1_worlds_with_contamination_detected": len(detected),
        "E1_contaminable_worlds": len(can),
        "E1_missed_detections": missed,
        "E1_not_contaminable_worlds": sorted(cannot),
        "E2_clean_false_alarms": clean_alarms,
        "E2_clean_scans": len(scans_clean),
        "E2b_alarms_on_not_contaminable_hostile_worlds": false_on_uncontaminable,
        "E3_arms_producing_non_equivalent_terms": clean_alarms,
        "E4_library_verdict": lib["verdict"],
        "E5_t74_clean_all_sound": t74["clean_all_sound"],
        "E5_t74_hostile_broken_legs_caught": t74["hostile_broken_legs_caught"],
        "E5_t74_contaminable_worlds": len(can),
        "E5_t74_broken_leg_detection_rate": round(
            t74["hostile_broken_legs_caught"] / max(1, len(can)), 4),
        "E6_cross_check_agreement": eqres["cross_check_agreement"],
        "E3b_amortised_application_ratio": amort["aggregate_ratio"],
        "E3b_worlds_where_shared_egraph_cheaper": amort["worlds_where_shared_egraph_is_cheaper"],
        "conformance_control_passed": conf["passed"],
        "unsound_witness_found": witness["found"],
        "knuth_bendix_verdict": kb["verdict"],
    }
    out = {"experiment": "D21", "evidence_class": "CONFIRMATORY_FIXED + EXPLORATORY_ADAPTIVE",
           "protocol": "D21_D22_PROTOCOL_V1.md", "worlds": "OW6 (frozen, SEED 20260910)",
           "controls": {"conformance": conf, "degree": deg,
                        "h_t86a_witness": witness, "contaminability": contam},
           "clean_arms": arms_clean, "hostile_arms": arms_hostile,
           "clean_scans": scans_clean, "hostile_scans": scans_hostile,
           "knuth_bendix": kb, "task_eq": eqres, "learned_library": lib,
           "amortised_reuse": amort,
           "t74_composition": t74, "t87_developmental_variants": t87,
           "summary": summary,
           "certificate_ceiling": "P2 finite certificate over frozen tiny worlds; "
                                  "not a universal proof",
           "wall_s": round(time.time() - t0w, 3), "cpu_s": round(time.process_time() - t0c, 3)}
    receipts = []
    for w in ow6:
        hs = host_by_world.get(w["id"], {})
        cs = [s for s in scans_clean if s["world"] == w["id"]]
        receipts.append({"job": "D21", "world_id": w["id"], "theorem_or_atom_id": "T86",
                         "contaminable": w["id"] in can,
                         "detection_verdict": ("DETECTED" if w["id"] in detected else
                                               "NOT_CONTAMINABLE" if w["id"] in cannot
                                               else "MISSED"),
                         "hostile_alarms": hs.get("n_alarms"),
                         "hostile_eclass_coverage": hs.get("eclass_coverage"),
                         "clean_alarms": sum(c["n_alarms"] for c in cs),
                         "clean_scan_status": [c["scan_status"] for c in cs],
                         "seed_freeze": W.SEED,
                         "certificate_ceiling": "P2 finite certificate, not universal proof"})
    return out, receipts

# --------------------------------------- revival pass: amortised multi-query --
def amortised_reuse(ow6, pairs):
    """One-stage attribution for the E3 negative.

    Single-query TASK-OPT gives equality saturation no advantage over ordered
    rewriting, because on this frozen rule set ordered rewriting under a total
    ground order already reaches the same normal form. The candidate lever is the
    multi-query regime: one saturated e-graph answers every equivalence query for
    a world, while ordered rewriting must re-run per query. This measures that,
    and it is EXPLORATORY_ADAPTIVE -- never a headline claim.
    """
    rows = []
    for w in ow6:
        qs = [p for p in pairs if p["world"] == w["id"]]
        t0 = time.process_time()
        eg = EGraph()
        root = eg.add_term(w["expr"])
        eg.rebuild()
        eg.saturate(egraph_rules(False))
        build_apps, build_enodes = eg.stats["rule_applications"], eg.stats["enodes"]
        for q in qs:                                   # each query is one add + one find
            cb = eg.add_term(q["b"])
            eg.rebuild()
            eg.saturate(egraph_rules(False))
            eg.find(root) == eg.find(cb)
        shared_cpu = round(time.process_time() - t0, 4)
        shared_apps = eg.stats["rule_applications"]

        t1 = time.process_time()
        resolve_apps = 0
        for q in qs:
            a = arm_ordered_rewriting(q["a"], SOUND_ALL)
            b = arm_ordered_rewriting(q["b"], SOUND_ALL)
            resolve_apps += (a["present_cost"]["rewrite_applications"]
                             + b["present_cost"]["rewrite_applications"])
        resolve_cpu = round(time.process_time() - t1, 4)
        rows.append({"world": w["id"], "n_queries": len(qs),
                     "shared_egraph_rule_applications": shared_apps,
                     "shared_egraph_enodes": build_enodes,
                     "shared_cpu_s": shared_cpu,
                     "per_query_ordered_rule_applications": resolve_apps,
                     "per_query_ordered_cpu_s": resolve_cpu,
                     "application_ratio_resolve_over_shared":
                         round(resolve_apps / max(1, shared_apps), 3)})
    tot_s = sum(r["shared_egraph_rule_applications"] for r in rows)
    tot_r = sum(r["per_query_ordered_rule_applications"] for r in rows)
    wins = [r["world"] for r in rows if r["application_ratio_resolve_over_shared"] > 1.0]
    return {"per_world": rows, "n_worlds": len(rows),
            "total_shared_rule_applications": tot_s,
            "total_per_query_rule_applications": tot_r,
            "aggregate_ratio": round(tot_r / max(1, tot_s), 3),
            "worlds_where_shared_egraph_is_cheaper": wins,
            "evidence_class": "EXPLORATORY_ADAPTIVE",
            "attribution": "E3's negative is attributed to the single-query workload, "
                           "not to the e-graph: on the frozen rule set ordered rewriting "
                           "already attains the direct-solve optimum, so saturation has "
                           "no optimum-quality headroom to win. This row measures whether "
                           "the multi-query regime is where it pays.",
            "note": "a ratio <= 1.0 means the shared e-graph is NOT cheaper even amortised; "
                    "that strengthens PARENT_SUFFICIENT rather than weakening it"}
