#!/usr/bin/env python3
"""Lane #200 revival — the rectangularity criterion, decomposability, and the
version-space warrant class (natural non-rectangular lifecycle classes).

Obstruction under revival (``theory/OCM_LANE_200_TERMINAL_V1.md`` §8): every
registered lifecycle class is *rectangular* — ``Im(B, Z) = Im(B) x Im(Z)`` — and
blindness is exactly rectangularity (Theorem D).  This module:

A.  states the coordinate criterion (R0) and re-verifies the first pass's claim
    on the committed modules — 3 registered classes / 2,048 worlds rectangular,
    3 planted coupled classes / 648 worlds not — with the planted classes as the
    control that fires;

B.  states the *learning-theoretic* criterion the obstruction actually needs,
    **decomposability**: with a behaviour oracle (membership queries) and a
    warrant oracle (liveness / coordinate queries), the deterministic exact
    query complexity ``D(Omega)`` equals the best *sequential product* strategy
    (learn one factor completely, then the other inside its fibre).  The
    interaction term ``I = min(B_first, Z_first) - D(Omega) >= 0`` is computed
    by two independently written exact solvers that must agree, with every
    optimal strategy re-established by simulation on every world.  Finding: the
    three planted non-rectangular classes of the first pass all have ``I = 0``
    — coordinate non-rectangularity does not by itself produce anything a
    product of two parent learners does not already attain.  A planted
    pointer-chasing class with ``I = 1`` is the control the procedure must fire on;

C.  registers the **version-space warrant class** ``VSW(X, C)``: worlds are
    ``(c, S)`` with ``c`` a concept of a class ``C`` over a finite domain ``X``
    and ``S`` the set of certified examples (evidence atoms); the record for a
    query point ``x`` is live after revoking ``R`` iff every concept consistent
    with the surviving evidence ``c|_(S \\ R)`` agrees at ``x`` — i.e. the
    warrant profile of ``x`` is the ATMS label induced by the hypothesis class,
    computed as an antichain of minimal specifying sets and evaluated through the
    committed ``rcl_model.live``; an independently written direct evaluator must
    agree on every cell.  Theorem R (affinity): ``VSW(X, C)`` is rectangular iff
    the agreement map is label-independent iff ``C`` is an affine subspace of
    ``F_2^X`` — the ``<=`` direction is a hand proof, the equivalence is verified
    exhaustively over every nonempty class on 2, 3 and 4 points (15 + 255 +
    65,535 classes).  The registered parity classes are rectangular *because*
    parity is affine.  Every non-affine concept class is a natural
    non-rectangular class;

D.  computes the interaction term on named families: monotone conjunctions,
    threshold functions and singletons on 4 points are decomposable; the
    **singletons class on 5 points** (Angluin 1988's membership-query
    lower-bound class) has ``I = 1``: liveness queries act as subset queries
    (``live(x, R)`` with ``x`` outside the surviving evidence ``J`` answers
    ``[c in {e_a : a in J}]``, or is unconditionally live in the elimination
    case ``X \\ J = {x}`` — verified on every cell), which membership queries
    cannot emulate.  This is the registered natural non-rectangular,
    non-decomposable instance.  Its strongest parents are named in the theory
    record; nothing here is a novelty claim.

Mutation controls (asserted applied on a witness before the check runs):

* ``M1`` sequential cost taken as ``D_first + max fibre cost`` instead of the
  exact weighted quotient tree (a defect actually made while writing this
  module: it overstated ``Z_first`` on LTF_2 by one; an earlier draft also
  pruned on the world count and reported a spurious ``I = 1`` on MONO_CONJ_2);
* ``M2`` affinity test that checks closure under pairwise XOR (a subspace
  test) — misclassifies a non-zero coset;
* ``M3`` label-independence test over ``S = {}`` only — vacuous, passes every class;
* ``M4`` joint solver without warrant queries — the pointer control cannot fire.

Exit codes: ``0`` pass, ``1`` a check failed for its registered reason, ``2``
could not check (a committed module failed to import; never a pass).

Authority: finite enumeration only.  Establishes no novelty, priority,
architecture or separation claim; all-size statements are hand proofs or
parents named in ``theory/OCM_NONRECTANGULAR_CLASS_V1.md``.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from collections.abc import Hashable, Sequence
from functools import cache
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
RCL_MODEL = HERE.parent / "revocation_complete_learning" / "rcl_model.py"


class CannotCheck(RuntimeError):
    """A check could not be run.  Never reported as a pass."""


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CannotCheck(f"cannot load committed module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - the CANNOT_CHECK route
        raise CannotCheck(f"committed module {name} failed to import: {exc}") from exc
    return module


# ----------------------------------------------------------------------------
# B. Decomposability: a query class and two independent exact solvers
# ----------------------------------------------------------------------------

Query = tuple[str, tuple[int, ...]]  # (name, answer per world), answers in {0,1}


class QueryClass:
    """Finite worlds with a behaviour value ``B`` per world, behaviour queries
    (functions of ``B``) and warrant queries (functions of the warrant object)."""

    def __init__(self, name: str, worlds: Sequence[Hashable], B: Sequence[Hashable], b_queries: Sequence[Query], z_queries: Sequence[Query]) -> None:
        self.name = name
        self.worlds = tuple(worlds)
        self.B = tuple(B)
        self.b_queries = tuple(b_queries)
        self.z_queries = tuple(z_queries)
        n = len(self.worlds)
        if n == 0:
            raise CannotCheck(f"{name}: empty class")
        for q in self.b_queries + self.z_queries:
            if len(q[1]) != n or any(v not in (0, 1) for v in q[1]):
                raise CannotCheck(f"{name}: malformed query {q[0]}")
        self.Z = tuple(tuple(q[1][i] for q in self.z_queries) for i in range(n))

    @property
    def n(self) -> int:
        return len(self.worlds)


def _distinct_on(mask: int, target: Sequence[Hashable]) -> int:
    vals = set()
    m = mask
    while m:
        i = (m & -m).bit_length() - 1
        vals.add(target[i])
        m &= m - 1
    return len(vals)


Tree = dict[str, object]  # {"q": index, "0": Tree, "1": Tree} or {"leaf": target value}


def _ones(queries: Sequence[Query]) -> list[int]:
    out = []
    for _, a in queries:
        m = 0
        for i, v in enumerate(a):
            if v:
                m |= 1 << i
        out.append(m)
    return out


def _restrict(queries: Sequence[Query], idx: Sequence[int]) -> list[Query]:
    return [(name, tuple(a[i] for i in idx)) for name, a in queries]


def _popcount(mask: int) -> int:
    return mask.bit_count()


def _kraft_lower_bound(costs: Sequence[int]) -> int:
    """A decision tree whose leaf ``v`` sits at depth ``d_v`` and then pays ``c_v``
    has total cost ``T >= d_v + c_v`` for every leaf; Kraft gives
    ``sum 2^{-d_v} <= 1``, hence ``T >= log2 sum_v 2^{c_v}``."""
    if len(costs) <= 1:
        return costs[0] if costs else 0
    return math.ceil(math.log2(sum(1 << c for c in costs)))


def solve_weighted(n: int, queries: Sequence[Query], target: Sequence[Hashable], leaf_cost: dict[Hashable, int] | None = None) -> tuple[int | None, Tree | None]:
    """Solver A.  Exact minimum over decision trees of ``max_leaf (depth + leaf_cost)``
    where the tree must make ``target`` constant at every leaf.  ``leaf_cost``
    defaults to 0 (plain exact identification).  Bitmask recursion, memo, and a
    Kraft prune; returns the cost and an explicit optimal tree."""
    ones = _ones(queries)
    lc = leaf_cost or {}

    def leaf_costs(mask: int) -> list[int]:
        seen: dict[Hashable, int] = {}
        m = mask
        while m:
            i = (m & -m).bit_length() - 1
            seen.setdefault(target[i], lc.get(target[i], 0))
            m &= m - 1
        return list(seen.values())

    @cache
    def D(mask: int) -> tuple[int | None, int]:
        costs = leaf_costs(mask)
        if len(costs) <= 1:
            return costs[0], -1
        lb = _kraft_lower_bound(costs)
        best: int | None = None
        best_q = -1
        # scan the most balanced splits first (a search-order heuristic; exactness is unaffected)
        order = sorted(range(len(ones)), key=lambda qi: abs(2 * _popcount(mask & ones[qi]) - _popcount(mask)))
        for qi in order:
            qm = ones[qi]
            m1 = mask & qm
            m0 = mask & ~qm
            if not m1 or not m0:
                continue
            d0, _ = D(m0)
            if d0 is None:
                continue
            d1, _ = D(m1)
            if d1 is None:
                continue
            c = 1 + max(d0, d1)
            if best is None or c < best:
                best, best_q = c, qi
                if best <= lb:
                    break
        return best, best_q

    def build(mask: int) -> Tree | None:
        d, q = D(mask)
        if d is None:
            return None
        if q < 0:
            i = (mask & -mask).bit_length() - 1
            return {"leaf": target[i]}
        qm = ones[q]
        return {"q": q, "0": build(mask & ~qm), "1": build(mask & qm)}

    full = (1 << n) - 1
    cost, _ = D(full)
    return cost, (build(full) if cost is not None else None)


def solve_weighted_b(n: int, queries: Sequence[Query], target: Sequence[Hashable], leaf_cost: dict[Hashable, int] | None = None) -> int | None:
    """Solver B, independently written: frozenset recursion, queries scanned in
    reverse, the Kraft bound recomputed from a Counter-style dict, no tree.  Must
    agree with solver A wherever both are run."""
    lc = leaf_cost or {}
    qs = [(name, a) for name, a in reversed(list(queries))]

    @cache
    def D(ws: frozenset[int]) -> int | None:
        by_value: dict[Hashable, int] = {}
        for i in ws:
            by_value[target[i]] = lc.get(target[i], 0)
        if len(by_value) == 1:
            return next(iter(by_value.values()))
        total = 0
        for c in by_value.values():
            total += 2 ** c
        bound = math.ceil(math.log2(total))
        best: int | None = None
        for _, a in qs:
            w1 = frozenset(i for i in ws if a[i])
            w0 = ws - w1
            if not w1 or not w0:
                continue
            d0 = D(w0)
            d1 = D(w1) if d0 is not None else None
            if d0 is None or d1 is None:
                continue
            c = 1 + max(d0, d1)
            if best is None or c < best:
                best = c
                if best <= bound:
                    break
        return best

    return D(frozenset(range(n)))


def solve_minimax(n: int, queries: Sequence[Query], target: Sequence[Hashable]) -> int | None:
    return solve_weighted(n, queries, target)[0]


def simulate_tree(tree: Tree, queries: Sequence[Query], target: Sequence[Hashable], idx: Sequence[int], leaf_cost: dict[Hashable, int] | None = None) -> int:
    """Run the tree on every world in ``idx``; every leaf must name the world's
    target; returns the worst ``depth + leaf_cost`` actually incurred."""
    lc = leaf_cost or {}
    worst = 0
    for i in idx:
        node = tree
        depth = 0
        while "leaf" not in node:
            depth += 1
            node = node[str(queries[node["q"]][1][i])]  # type: ignore[index]
        if node["leaf"] != target[i]:
            raise AssertionError("simulated tree misidentifies a world")
        worst = max(worst, depth + lc.get(node["leaf"], 0))
    return worst


def exists_tree(mask: int, depth: int, ones: Sequence[int], target: Sequence[Hashable]) -> bool:
    """Third formulation: does a tree of depth <= ``depth`` exist?  Existence
    search rather than minimisation; used as a witness on small instances."""
    if _distinct_on(mask, target) <= 1:
        return True
    if depth == 0:
        return False
    for qm in ones:
        m1 = mask & qm
        m0 = mask & ~qm
        if m0 and m1 and exists_tree(m0, depth - 1, ones, target) and exists_tree(m1, depth - 1, ones, target):
            return True
    return False


CROSS_CHECK_MAX_WORLDS = 64


def _quotient(values: Sequence[Hashable], queries: Sequence[Query]) -> tuple[list[Hashable], list[Query], dict[Hashable, list[int]]]:
    """Distinct factor values with their query answers (queries must be functions
    of the value) and the fibre of world indices over each value."""
    fibres: dict[Hashable, list[int]] = {}
    for i, v in enumerate(values):
        fibres.setdefault(v, []).append(i)
    rep = {v: idx[0] for v, idx in fibres.items()}
    for name, a in queries:
        for i, v in enumerate(values):
            if a[i] != a[rep[v]]:
                raise CannotCheck(f"query {name} is not a function of the factor value")
    idx = list(rep.values())
    return [values[i] for i in idx], _restrict(queries, idx), fibres


def _sequential(qc: QueryClass, first: str, *, formula: bool = False) -> dict[str, object]:
    """Exact cost of the strategy that determines factor ``first`` (``'B'`` or
    ``'Z'``) completely before querying the other factor inside its fibre:
    a weighted tree on the factor quotient whose leaf cost is the exact cost of
    the fibre.  ``formula=True`` is mutation M1: the first-draft estimate
    ``D_first + max fibre cost``, which is not attained by any strategy of this
    shape whenever the deepest leaf and the costliest fibre differ."""
    if first == "B":
        values, fq, oq = qc.B, qc.b_queries, qc.z_queries
    else:
        values, fq, oq = qc.Z, qc.z_queries, qc.b_queries
    qvals, qq, fibres = _quotient(values, fq)
    fibre_cost: dict[Hashable, int] = {}
    fibre_cost_b: dict[Hashable, int] = {}
    fibre_trees: dict[Hashable, tuple[Tree, list[Query], list[int]]] = {}
    for v, idx in fibres.items():
        sub = _restrict(oq, idx)
        ident = tuple(range(len(idx)))
        c, t = solve_weighted(len(idx), sub, ident)
        cb = solve_weighted_b(len(idx), sub, ident)
        if c is None or cb is None:
            raise CannotCheck(f"{qc.name}: a fibre of {first} is not identifiable from the other factor's queries")
        if c != cb:
            raise AssertionError(f"{qc.name}: solvers disagree on a {first}-fibre ({c} vs {cb})")
        fibre_cost[v] = c
        fibre_cost_b[v] = cb
        fibre_trees[v] = (t, sub, idx)  # type: ignore[arg-type]
    m = len(qvals)
    d_first, _ = solve_weighted(m, qq, qvals)
    if formula:
        return {"first": first, "D_first": d_first, "worst_fibre": max(fibre_cost.values()), "cost": (d_first or 0) + max(fibre_cost.values())}
    cost, tree = solve_weighted(m, qq, qvals, fibre_cost)
    cost_b = solve_weighted_b(m, qq, qvals, fibre_cost_b)
    if cost is None or cost_b is None:
        raise CannotCheck(f"{qc.name}: factor {first} is not identifiable from its own queries")
    if cost != cost_b:
        raise AssertionError(f"{qc.name}: solvers disagree on the {first}-first cost ({cost} vs {cost_b})")
    # simulate the composite strategy on every world: factor tree on the quotient, then the fibre tree
    worst = 0
    for i in range(qc.n):
        v = values[i]
        node = tree
        depth = 0
        while "leaf" not in node:  # type: ignore[operator]
            depth += 1
            node = node[str(fq[node["q"]][1][i])]  # type: ignore[index]
        if node["leaf"] != v:  # type: ignore[index]
            raise AssertionError(f"{qc.name}: {first}-tree misidentifies a factor value")
        t, sub, idx = fibre_trees[v]
        worst = max(worst, depth + simulate_tree(t, sub, tuple(range(len(idx))), [idx.index(i)]))
    if worst != cost:
        raise AssertionError(f"{qc.name}: simulated {first}-first strategy costs {worst}, solver says {cost}")
    return {"first": first, "D_first": d_first, "worst_fibre": max(fibre_cost.values()), "fibres": m, "cost": cost, "cost_solver_b": cost_b, "cost_simulated": worst}


def decomposition(qc: QueryClass, *, cross_check: bool | None = None, witness: bool = False) -> dict[str, object]:
    """``D_joint`` = exact cost with all queries (solver A, explicit tree
    simulated on every world; solver B on the joint problem when
    ``n <= CROSS_CHECK_MAX_WORLDS``).  ``B_first`` / ``Z_first`` = exact cost of
    the two sequential-product strategies (weighted quotient trees; solvers A and
    B agree; composite strategy simulated).  ``I = min(B_first, Z_first) - D_joint``.
    The joint lower bound is counting (``ceil log2 n``); when ``D_joint`` meets it
    the value is certified without any solver."""
    n = qc.n
    ident = tuple(range(n))
    allq = list(qc.b_queries) + list(qc.z_queries)
    if cross_check is None:
        cross_check = n <= CROSS_CHECK_MAX_WORLDS
    d_joint, joint_tree = solve_weighted(n, allq, ident)
    if d_joint is None or joint_tree is None:
        raise CannotCheck(f"{qc.name}: worlds not identifiable from the registered queries")
    ub_joint = simulate_tree(joint_tree, allq, ident, range(n))
    if ub_joint != d_joint:
        raise AssertionError(f"{qc.name}: simulated joint tree depth {ub_joint} != D_joint {d_joint}")
    lb_joint = math.ceil(math.log2(n))
    solvers_agree: bool | None = None
    if cross_check:
        d_joint_b = solve_weighted_b(n, allq, ident)
        if d_joint_b != d_joint:
            raise AssertionError(f"{qc.name}: the two exact solvers disagree on D_joint ({d_joint} vs {d_joint_b})")
        solvers_agree = True
    b_first = _sequential(qc, "B")
    z_first = _sequential(qc, "Z")
    seq = min(b_first["cost"], z_first["cost"])  # type: ignore[type-var]
    out: dict[str, object] = {
        "name": qc.name,
        "worlds": n,
        "log2_worlds": math.log2(n),
        "joint_lower_bound_counting": lb_joint,
        "behaviour_values": b_first["fibres"],
        "warrant_values": z_first["fibres"],
        "b_queries": len(qc.b_queries),
        "z_queries": len(qc.z_queries),
        "D_joint": d_joint,
        "D_joint_simulated": ub_joint,
        "D_joint_meets_counting_bound": d_joint == lb_joint,
        "solvers_agree_on_D_joint": solvers_agree,
        "B_first": b_first,
        "Z_first": z_first,
        "interaction_term": seq - d_joint,
        "decomposable": seq == d_joint,
        "certified": {
            "how": "sequential costs: solvers A and B agree and the composite strategy is simulated; joint: explicit tree simulated (upper bound) and counting (lower bound)",
            "interaction_lower_bound": seq - ub_joint,
            "interaction_upper_bound": seq - lb_joint,
            "decomposability_certified": (seq == d_joint) and (d_joint == lb_joint or solvers_agree is True),
            "nondecomposability_certified": seq - ub_joint >= 1,
        },
    }
    if witness:
        ones = _ones(allq)
        full = (1 << n) - 1
        out["witness"] = {
            "tree_of_depth_D_joint_exists": exists_tree(full, d_joint, ones, ident),
            "tree_of_depth_D_joint_minus_1_exists": exists_tree(full, d_joint - 1, ones, ident),
        }
        if not out["witness"]["tree_of_depth_D_joint_exists"] or out["witness"]["tree_of_depth_D_joint_minus_1_exists"]:
            raise AssertionError(f"{qc.name}: existence witness contradicts D_joint")
    return out


# ----------------------------------------------------------------------------
# A. Coordinate rectangularity (R0) on the committed lane-200 classes
# ----------------------------------------------------------------------------

def lane200_module() -> ModuleType:
    return _load("ocm_lane200_decomposition_exact", HERE / "ocm_lane200_decomposition_exact.py")


def lane200_query_class(cls: object) -> QueryClass:
    worlds = cls.worlds  # type: ignore[attr-defined]
    B = [cls.behaviour(w) for w in worlds]  # type: ignore[attr-defined]
    bq = [(f"mem{x}", tuple(cls.transcript(w, (x,))[0] for w in worlds)) for x in cls.all_queries]  # type: ignore[attr-defined]
    width = len(cls.warrant(worlds[0]))  # type: ignore[attr-defined]
    zq = [(f"z{k}", tuple(cls.warrant(w)[k] for w in worlds)) for k in range(width)]  # type: ignore[attr-defined]
    return QueryClass(cls.name, worlds, B, bq, zq)  # type: ignore[attr-defined]


def check_R0_on_committed(l200: ModuleType) -> dict[str, object]:
    reg = l200.registered_classes()
    planted = l200.planted_classes()
    reg_rows = []
    for c in reg:
        r = l200.rectangularity(c)
        if not r["rectangular"]:
            raise AssertionError(f"{c.name}: registered class not rectangular")
        reg_rows.append({"name": c.name, "worlds": len(c.worlds), **r})
    pl_rows = []
    for c in planted:
        r = l200.rectangularity(c)
        if r["rectangular"]:
            raise AssertionError(f"{c.name}: planted coupled class passed R0")
        pl_rows.append({"name": c.name, "worlds": len(c.worlds), **r})
    return {
        "criterion": "R0: |Im(B,Z)| == |Im B| * |Im Z| (equivalently every behaviour fibre carries every warrant value; equivalently H0(B,Z) = H0(B) + H0(Z))",
        "registered": reg_rows,
        "registered_worlds": sum(r["worlds"] for r in reg_rows),
        "planted_non_rectangular": pl_rows,
        "planted_worlds": sum(r["worlds"] for r in pl_rows),
        "control_fired": all(not r["rectangular"] for r in pl_rows),
    }


# ----------------------------------------------------------------------------
# B'. Planted decomposability controls
# ----------------------------------------------------------------------------

def pointer_chasing_class() -> QueryClass:
    """z0 selects which behaviour bit is live; that bit selects which of four
    warrant bits is live.  8 worlds; the joint tree has depth 3; both sequential
    products need 4.  Planted: must fire (I > 0)."""
    worlds = []
    for z0 in (0, 1):
        for bv in (0, 1):
            for zv in (0, 1):
                b = [0, 0]
                b[z0] = bv
                z = [0, 0, 0, 0]
                z[2 * z0 + bv] = zv
                worlds.append((z0, tuple(b), tuple(z)))
    B = [w[1] for w in worlds]
    bq = [(f"b{k}", tuple(w[1][k] for w in worlds)) for k in range(2)]
    zq = [("z0", tuple(w[0] for w in worlds))] + [(f"z{k + 1}", tuple(w[2][k] for w in worlds)) for k in range(4)]
    return QueryClass("POINTER_3", worlds, B, bq, zq)


def rectangular_control_class(p: int = 2, N: int = 2) -> QueryClass:
    """Parity x free bits: rectangular, additive, I = 0 (no-alarm)."""
    allx = list(itertools.product((0, 1), repeat=p))

    def dot(a: Sequence[int], b: Sequence[int]) -> int:
        return sum(x * y for x, y in zip(a, b, strict=True)) % 2

    worlds = [(t, z) for t in itertools.product((0, 1), repeat=p) for z in itertools.product((0, 1), repeat=N)]
    B = [w[0] for w in worlds]
    bq = [(f"mem{x}", tuple(dot(x, w[0]) for w in worlds)) for x in allx]
    zq = [(f"z{k}", tuple(w[1][k] for w in worlds)) for k in range(N)]
    return QueryClass(f"RECT_p{p}_N{N}", worlds, B, bq, zq)


# ----------------------------------------------------------------------------
# C. The version-space warrant class VSW(X, C)
# ----------------------------------------------------------------------------

Concept = tuple[int, ...]


def subsets_of(n: int) -> list[frozenset[int]]:
    return [frozenset(s) for r in range(n + 1) for s in itertools.combinations(range(n), r)]


def agreement(C: Sequence[Concept], c: Concept, J: frozenset[int], n: int) -> tuple[bool, ...]:
    """Direct evaluator: the version space of ``c|_J`` within ``C`` agrees at ``x``."""
    cons = [d for d in C if all(d[j] == c[j] for j in J)]
    return tuple(all(d[x] == cons[0][x] for d in cons) for x in range(n))


def is_affine(C: Sequence[Concept]) -> bool:
    """Nonempty ``C`` is a coset of a subspace of F_2^X iff closed under a+b+c."""
    Cs = set(C)
    return all(tuple(a ^ b ^ c for a, b, c in zip(x, y, z, strict=True)) in Cs for x in C for y in C for z in C)


def is_subspace_closed(C: Sequence[Concept]) -> bool:
    """M2: closure under pairwise XOR — a subspace test, wrong on non-zero cosets."""
    Cs = set(C)
    return all(tuple(a ^ b for a, b in zip(x, y, strict=True)) in Cs for x in C for y in C)


def label_independent(C: Sequence[Concept], n: int, *, samples: Sequence[frozenset[int]] | None = None) -> bool:
    """For every sample ``S`` (or the given ones), every consistent labelling of
    ``S`` yields the same agreement region."""
    for S in subsets_of(n) if samples is None else samples:
        Sl = sorted(S)
        regions = set()
        for lab in itertools.product((0, 1), repeat=len(Sl)):
            cons = [d for d in C if all(d[j] == v for j, v in zip(Sl, lab, strict=True))]
            if not cons:
                continue
            regions.add(tuple(all(d[x] == cons[0][x] for d in cons) for x in range(n)))
        if len(regions) > 1:
            return False
    return True


def affinity_census(n: int) -> dict[str, int]:
    funcs = list(itertools.product((0, 1), repeat=n))
    cnt = {"affine_label_independent": 0, "affine_label_dependent": 0, "nonaffine_label_independent": 0, "nonaffine_label_dependent": 0}
    for mask in range(1, 1 << len(funcs)):
        C = [funcs[i] for i in range(len(funcs)) if mask >> i & 1]
        a, li = is_affine(C), label_independent(C, n)
        cnt[("affine" if a else "nonaffine") + ("_label_independent" if li else "_label_dependent")] += 1
    cnt["classes"] = (1 << len(funcs)) - 1
    return cnt


def vsw_class(name: str, C: Sequence[Concept], rcl: ModuleType) -> tuple[QueryClass, dict[str, object]]:
    """Build VSW(X, C) with X = range(n): worlds (c, S) quotiented by their
    lifecycle target (B = c, Z = liveness signature over all (x, R)); the profile
    of each record x is the antichain of minimal specifying sets inside S (an ATMS
    label), and ``rcl_model.live(profile, R)`` must agree with the direct
    evaluator on every (world, x, R) cell."""
    n = len(C[0])
    subs = subsets_of(n)
    seen: set[tuple[Concept, tuple[tuple[bool, ...], ...]]] = set()
    worlds: list[tuple[Concept, frozenset[int], tuple[tuple[bool, ...], ...]]] = []
    for c in C:
        for S in subs:
            sig = tuple(agreement(C, c, S - R, n) for R in subs)
            key = (c, sig)
            if key in seen:
                continue
            seen.add(key)
            worlds.append((c, S, sig))
    # profile = ATMS label; compare rcl.live with the direct evaluator on every cell
    cells = 0
    mismatches = 0
    for c, S, sig in worlds:
        for x in range(n):
            minimal = [J for J in subs if J <= S and agreement(C, c, J, n)[x]]
            profile = rcl.canonical_profile(minimal)
            for ri, R in enumerate(subs):
                cells += 1
                via_profile = bool(profile) and rcl.live(profile, R)
                if via_profile != sig[ri][x]:
                    mismatches += 1
    if mismatches:
        raise AssertionError(f"{name}: ATMS-label liveness disagrees with the direct evaluator on {mismatches}/{cells} cells")
    B = [w[0] for w in worlds]
    bq = [(f"mem{x}", tuple(w[0][x] for w in worlds)) for x in range(n)]
    zq: list[Query] = []
    for ri, R in enumerate(subs):
        for x in range(n):
            a = tuple(int(w[2][ri][x]) for w in worlds)
            if len(set(a)) > 1:
                zq.append((f"live(x{x},R={sorted(R)})", a))
    qc = QueryClass(name, worlds, B, bq, zq)
    pairs = {(b, z) for b, z in zip(qc.B, qc.Z, strict=True)}
    nb, nz = len(set(qc.B)), len(set(qc.Z))
    meta = {
        "name": name,
        "domain_points": n,
        "concepts": len(C),
        "affine": is_affine(C),
        "label_independent": label_independent(C, n),
        "worlds_quotient": qc.n,
        "behaviour_values": nb,
        "warrant_values": nz,
        "pairs": len(pairs),
        "rectangular": len(pairs) == nb * nz,
        "atms_label_cells_checked": cells,
        "atms_label_mismatches": mismatches,
    }
    return qc, meta


def singletons(m: int, *, with_empty: bool = False) -> list[Concept]:
    C = [tuple(int(i == j) for j in range(m)) for i in range(m)]
    if with_empty:
        C.append(tuple([0] * m))
    return C


def named_families_on_4_points() -> dict[str, list[Concept]]:
    X2 = list(itertools.product((0, 1), repeat=2))

    def dedup(cs: Sequence[Concept]) -> list[Concept]:
        out: list[Concept] = []
        for c in cs:
            if c not in out:
                out.append(c)
        return out

    linear = [tuple(sum(a * b for a, b in zip(x, th, strict=True)) % 2 for x in X2) for th in itertools.product((0, 1), repeat=2)]
    mono = [tuple(int(all(x[i] for i in T)) for x in X2) for T in [(), (0,), (1,), (0, 1)]]
    ltf = dedup([tuple(int(w0 * x[0] + w1 * x[1] + b > 0) for x in X2) for w0 in range(-2, 3) for w1 in range(-2, 3) for b in range(-2, 3)])
    return {"LINEAR_F2^2": linear, "MONO_CONJ_2": mono, "LTF_2": ltf, "SINGLETONS_4": singletons(4)}


def subset_query_identity(m: int) -> dict[str, int]:
    """For singletons: live(x, R) with x outside the surviving evidence J = S\\R
    equals [c in {e_a : a in J}] — a subset query in Angluin's sense — except
    in the elimination case X \\ J = {x}, where the version space collapses to
    {e_x} and the record is live for every c.  Both clauses are checked on every
    cell; the elimination cells are counted separately."""
    C = singletons(m)
    subs = subsets_of(m)
    ok = tot = elim = 0
    for c in C:
        ci = c.index(1)
        for J in subs:
            reg = agreement(C, c, J, m)
            for x in range(m):
                if x in J:
                    continue
                tot += 1
                elimination = len(J) == m - 1
                elim += int(elimination)
                ok += int(reg[x] == ((ci in J) or elimination))
    if ok != tot:
        raise AssertionError(f"subset-query identity fails on {tot - ok}/{tot} cells")
    return {"cells": tot, "identity_holds_on": ok, "elimination_cells": elim}


# ----------------------------------------------------------------------------
# E. Mutation controls
# ----------------------------------------------------------------------------

def mutation_controls(rcl: ModuleType) -> dict[str, object]:
    out: dict[str, object] = {}
    # M1: first-draft sequential formula D_first + max fibre cost — applied iff it differs from the
    # exact weighted cost on LTF_2 (deepest leaf and costliest cofibre differ there).
    qc, _ = vsw_class("LTF_2", named_families_on_4_points()["LTF_2"], rcl)
    exact = _sequential(qc, "Z")
    formula = _sequential(qc, "Z", formula=True)
    if formula["cost"] == exact["cost"]:
        raise AssertionError("M1 not applied")
    out["M1_sequential_cost_by_formula"] = {
        "applied": True,
        "Z_first_exact": exact["cost"],
        "Z_first_formula": formula["cost"],
        "detected": formula["cost"] > exact["cost_simulated"],
        "caught_by": "LTF_2: the simulated Z-first strategy is cheaper than the formula claims, so the formula is not the cost of any strategy of that shape",
    }
    # M2: subspace test on a non-zero coset.
    coset = [(0, 0, 1, 1), (1, 1, 1, 1)]  # coset of span{(1,1,0,0)}
    if is_subspace_closed(coset) == is_affine(coset):
        raise AssertionError("M2 not applied")
    out["M2_subspace_test"] = {"applied": True, "affine": is_affine(coset), "subspace_test": is_subspace_closed(coset), "detected": is_affine(coset) and not is_subspace_closed(coset)}
    # M3: label-independence over the empty sample only — vacuous.
    mono = named_families_on_4_points()["MONO_CONJ_2"]
    vac = label_independent(mono, 4, samples=[frozenset()])
    full = label_independent(mono, 4)
    if vac == full:
        raise AssertionError("M3 not applied")
    out["M3_empty_sample_label_independence"] = {"applied": True, "vacuous_verdict": vac, "full_verdict": full, "detected": vac and not full}
    # M4: joint solver without warrant queries — the pointer control cannot fire.
    pc = pointer_chasing_class()
    stripped = QueryClass("POINTER_3_no_Z", pc.worlds, pc.B, pc.b_queries, ())
    fired_clean = decomposition(pc)["certified"]["nondecomposability_certified"]
    try:
        decomposition(stripped)
        fired_mutated = True
    except CannotCheck:
        fired_mutated = False  # worlds unidentifiable without Z: the check cannot fire
    if fired_mutated == fired_clean:
        raise AssertionError("M4 not applied")
    out["M4_joint_solver_without_warrant_queries"] = {"applied": True, "control_fires_clean": fired_clean, "control_fires_mutated": fired_mutated, "detected": fired_clean and not fired_mutated}
    for k, row in out.items():
        if not row["detected"]:
            raise AssertionError(f"{k} not detected")
    return out


# ----------------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------------

def run_exact_calibration(*, census_max_points: int = 4) -> dict[str, object]:
    l200 = lane200_module()
    rcl = _load("rcl_model", RCL_MODEL)

    # A. coordinate criterion on the committed classes
    r0 = check_R0_on_committed(l200)

    # B. decomposability of the first pass's planted non-rectangular classes: must all be I = 0
    planted_rows = []
    for c in l200.planted_classes():
        row = decomposition(lane200_query_class(c))
        row["R0_rectangular"] = l200.rectangularity(c)["rectangular"]
        if row["R0_rectangular"] or not row["certified"]["decomposability_certified"]:
            raise AssertionError(f"{c.name}: expected non-rectangular and certified decomposable")
        planted_rows.append(row)
    rect_row = decomposition(rectangular_control_class(), witness=True)
    if not rect_row["certified"]["decomposability_certified"]:
        raise AssertionError("rectangular control is not decomposable")
    pointer_row = decomposition(pointer_chasing_class(), witness=True)
    if not pointer_row["certified"]["nondecomposability_certified"]:
        raise AssertionError("planted pointer-chasing control did not fire")

    # C. affinity census and named families
    census = {f"points_{n}": affinity_census(n) for n in range(2, census_max_points + 1)}
    for n, cnt in census.items():
        if cnt["affine_label_dependent"] or cnt["nonaffine_label_independent"]:
            raise AssertionError(f"affinity <=> label-independence fails at {n}")
    families: list[dict[str, object]] = []
    for name, C in named_families_on_4_points().items():
        qc, meta = vsw_class(name, C, rcl)
        if meta["rectangular"] != meta["affine"] or meta["label_independent"] != meta["affine"]:
            raise AssertionError(f"{name}: rectangular/label-independent/affine disagree")
        row = decomposition(qc, witness=(qc.n <= 16))
        families.append({**meta, **row})
    affine_names = [f["name"] for f in families if f["affine"]]
    nonaffine_names = [f["name"] for f in families if not f["affine"]]
    if not affine_names or not nonaffine_names:
        raise AssertionError("named families must include an affine (no-alarm) and a non-affine (firing) class")

    # D. the registered natural non-decomposable instance: singletons on 5 points
    s5_qc, s5_meta = vsw_class("SINGLETONS_5", singletons(5), rcl)
    s5 = {**s5_meta, **decomposition(s5_qc)}
    if s5["rectangular"] or not s5["certified"]["nondecomposability_certified"]:
        raise AssertionError("SINGLETONS_5 expected non-rectangular with certified interaction term >= 1")
    s5e_qc, s5e_meta = vsw_class("SINGLETONS_EMPTY_5", singletons(5, with_empty=True), rcl)
    s5e = {**s5e_meta, **decomposition(s5e_qc)}
    identity = {f"points_{m}": subset_query_identity(m) for m in (4, 5)}

    mutations = mutation_controls(rcl)

    return {
        "schema": "orion.ocm.nonrectangular-class.exact-results.v1",
        "terminal": "NATURAL_NONRECTANGULAR_CLASSES_EXIST__ONE_NATURAL_NONDECOMPOSABLE_INSTANCE_REGISTERED__PARENT_OWNED",
        "A_coordinate_rectangularity": r0,
        "B_decomposability": {
            "definition": "D_joint = exact query complexity with behaviour and warrant queries; B_first = D_B + max_b D(fibre_b); Z_first = D_Z + max_z D(cofibre_z); I = min(B_first, Z_first) - D_joint",
            "first_pass_planted_classes": planted_rows,
            "rectangular_control": rect_row,
            "pointer_chasing_control": pointer_row,
            "finding": "all three planted non-rectangular classes are decomposable (I = 0); coordinate non-rectangularity is not the obstruction's content",
        },
        "C_version_space_warrant_class": {
            "affinity_census": census,
            "named_families_4_points": families,
            "theorem_R": "VSW(X, C) rectangular <=> agreement label-independent <=> C affine; exhaustive on every nonempty class on 2, 3, 4 points",
        },
        "D_registered_natural_nondecomposable_instance": {
            "SINGLETONS_5": s5,
            "SINGLETONS_EMPTY_5": s5e,
            "subset_query_identity": identity,
            "mechanism": "liveness queries on singletons are Angluin subset queries; membership queries split 1 : m-1",
        },
        "mutation_controls": mutations,
        "denominators": {
            "registered_worlds_R0": r0["registered_worlds"],
            "planted_worlds_non_R0": r0["planted_worlds"],
            "affinity_classes_enumerated": sum(c["classes"] for c in census.values()),
            "named_families": len(families),
            "atms_label_cells_checked": sum(f["atms_label_cells_checked"] for f in families) + s5["atms_label_cells_checked"] + s5e["atms_label_cells_checked"],
            "mutations_planted": len(mutations),
        },
        "authority": {
            "finite_enumeration_only": True,
            "all_size_authority": "hand proofs and parents in theory/OCM_NONRECTANGULAR_CLASS_V1.md",
            "novelty_established": False,
            "separation_established": False,
            "architecture_separation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except CannotCheck as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except AssertionError as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        d = result["denominators"]
        s5 = result["D_registered_natural_nondecomposable_instance"]["SINGLETONS_5"]
        print(
            f"PASS non-rectangular class: R0 holds on {d['registered_worlds_R0']} registered worlds, fails on "
            f"{d['planted_worlds_non_R0']} planted; affinity census over {d['affinity_classes_enumerated']} classes; "
            f"SINGLETONS_5 non-rectangular with I={s5['interaction_term']} (D_joint={s5['D_joint']}, B_first={s5['B_first']}, "
            f"Z_first={s5['Z_first']}); {d['mutations_planted']} mutations detected"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
