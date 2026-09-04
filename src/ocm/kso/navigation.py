"""Query-conditioned typed navigation — the replaceable reference mechanic (contract §5–§6, §29).

* structural denominators are computed **before** warrant gating and never renormalised after a
  revocation (KS-T04: dead mass dissipates into restart mass; the renormalising parent is the
  planted control);
* restart dynamics ``a ← α s + (1-α) Pᵀ a`` is an ℓ1 contraction (KS-T05) with an exact rational
  fixed point and an iterative/float solver for scale;
* reaction surprise ranks atoms by query-specific reaction relative to a background fixed point
  (KS-T06/T06b) so generic hubs do not dominate;
* ``navigate`` returns the four-valued outcome FOUND / GAP_NOT_FOUND / OBSTRUCTION_WITNESSED /
  CANNOT_CHECK; an obstruction is witnessed only when the ungated ceiling walker also fails
  (KS-T19; H-EXT-1R escalation rule).

Query-conditioned relevance β_r(Q) is a real parameter here (the inherited checker fixed it at 1).
Parents: personalised PageRank / local graph partitioning (Andersen, Chung & Lang 2006), random walks
on hypergraphs (Chitra & Raphael 2019), spreading activation; the frozen-denominator gate is the
JTMS/ATMS ∘ spreading-activation product (`KSO_PARENT_SUBTRACTION_V1.md`), a design choice.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Callable, Hashable, Iterable, Mapping, Sequence

from .resources import ResourceVector
from .space import Hyperedge, KnowledgeSpace, TypedRejection
from .warrant import CannotCheck, Liveness

Relevance = Mapping[str, Fraction] | Callable[[str], Fraction] | None


def _beta(relevance: Relevance, relation_type: str) -> Fraction:
    if relevance is None:
        return Fraction(1, 1)
    if callable(relevance):
        return Fraction(relevance(relation_type))
    return Fraction(relevance.get(relation_type, Fraction(1, 1)))


class NavigationMode(str, Enum):
    WARRANTED = "WARRANTED"      # gate on LIVE only (UNKNOWN is gated out)
    EXPLORATORY = "EXPLORATORY"  # ungated: the ceiling walker's structure


def _gate(liveness: Liveness, mode: NavigationMode) -> Fraction:
    if mode is NavigationMode.EXPLORATORY:
        return Fraction(1, 1)
    return Fraction(1, 1) if liveness is Liveness.LIVE else Fraction(0, 1)


def structural_denominators(ks: KnowledgeSpace, relevance: Relevance = None) -> dict[str, Fraction]:
    """D_Q(v) = Σ_{h: v ∈ T_h} w_h β_{r_h}(Q) — pre-revocation, a property of the registered structure."""
    denom = {x: Fraction(0, 1) for x in ks.ids}
    for e in ks.hyperedges:
        mass = e.weight * _beta(relevance, e.relation_type)
        for t in e.tails:
            denom[t] += mass
    return denom


@dataclass(frozen=True)
class NavigationMatrix:
    ids: tuple[str, ...]
    rows: tuple[tuple[Fraction, ...], ...]   # rows[i][j] = P(v_i → v_j)
    denominators: tuple[Fraction, ...]
    mode: NavigationMode
    revoked: frozenset

    def index(self, atom_id: str) -> int:
        return self.ids.index(atom_id)

    def row_mass(self, atom_id: str) -> Fraction:
        return sum(self.rows[self.index(atom_id)], Fraction(0, 1))

    def is_substochastic(self) -> bool:
        return all(all(x >= 0 for x in r) and sum(r, Fraction(0, 1)) <= 1 for r in self.rows)

    def as_lists(self) -> list[list[Fraction]]:
        return [list(r) for r in self.rows]


def navigation_matrix(
    ks: KnowledgeSpace,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
) -> NavigationMatrix:
    """P_{Q,R}(v,u) = Σ_h (w_h β_r / D_Q(v)) γ_h(u) g(v) g(h) g(u) Π_{z∈T_h} g(z), frozen D_Q."""
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    n = len(ids)
    out = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    denom = structural_denominators(ks, relevance)
    for e in ks.hyperedges:
        structural_mass = e.weight * _beta(relevance, e.relation_type)
        if structural_mass == 0:
            continue
        edge_gate = _gate(e.liveness(rv), mode)
        tails_gate = min((_gate(amap[t].liveness(rv), mode) for t in e.tails), default=Fraction(0, 1))
        if edge_gate == 0 or tails_gate == 0:
            continue
        hweights = e.normalized_head_weights()
        for tail in e.tails:
            if denom[tail] == 0:
                continue
            edge_prob = structural_mass / denom[tail]
            for head, hw in zip(e.heads, hweights, strict=True):
                dst_gate = _gate(amap[head].liveness(rv), mode)
                out[idx[tail]][idx[head]] += edge_gate * tails_gate * dst_gate * edge_prob * hw
    return NavigationMatrix(ids, tuple(tuple(r) for r in out), tuple(denom[x] for x in ids), mode, rv)


def navigation_matrix_by_pruning(
    ks: KnowledgeSpace,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
) -> NavigationMatrix:
    """Independent implementation of KS-T04: prune every non-live atom/edge, keep the original
    denominators.  Must agree entry-wise with ``navigation_matrix`` (WARRANTED mode)."""
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    n = len(ids)
    out = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    denom = structural_denominators(ks, relevance)
    live_atom = {x: amap[x].is_live(rv) for x in ids}
    live_edge = {e.edge_id: e.warrant.is_live(rv) and all(live_atom[t] for t in e.tails) for e in ks.hyperedges}
    for e in ks.hyperedges:
        if not live_edge[e.edge_id]:
            continue
        m = e.weight * _beta(relevance, e.relation_type)
        for tail in e.tails:
            if not live_atom[tail] or denom[tail] == 0:
                continue
            for head, hw in zip(e.heads, e.normalized_head_weights(), strict=True):
                if live_atom[head]:
                    out[idx[tail]][idx[head]] += (m / denom[tail]) * hw
    return NavigationMatrix(ids, tuple(tuple(r) for r in out), tuple(denom[x] for x in ids), NavigationMode.WARRANTED, rv)


def mutant_navigation_matrix_renormalize(ks: KnowledgeSpace, *, revoked: Iterable[Hashable] = ()) -> NavigationMatrix:
    """Planted defect (the RWR/CBR parents' retraction): redistribute dead mass onto survivors."""
    rv = frozenset(revoked)
    ids = ks.ids
    idx = {x: i for i, x in enumerate(ids)}
    amap = ks.atom_map()
    out = [[Fraction(0, 1) for _ in ids] for _ in ids]
    denom = [Fraction(0, 1) for _ in ids]
    for tail in ids:
        if not amap[tail].is_live(rv):
            continue
        live_rows = [
            e
            for e in ks.hyperedges
            if tail in e.tails
            and e.warrant.is_live(rv)
            and all(amap[t].is_live(rv) for t in e.tails)
            and all(amap[h].is_live(rv) for h in e.heads)
        ]
        total = sum((e.weight for e in live_rows), Fraction(0, 1))
        denom[idx[tail]] = total
        for e in live_rows:
            if total == 0:
                continue
            for head, hw in zip(e.heads, e.normalized_head_weights(), strict=True):
                out[idx[tail]][idx[head]] += (e.weight / total) * hw
    return NavigationMatrix(ids, tuple(tuple(r) for r in out), tuple(denom), NavigationMode.WARRANTED, rv)


# --------------------------------------------------------------------------------------------
# seeds and restart dynamics
# --------------------------------------------------------------------------------------------


def seed_vector(ks: KnowledgeSpace, seeds: Mapping[str, Fraction]) -> list[Fraction]:
    ids = ks.ids
    total = sum(seeds.values(), Fraction(0, 1))
    if total <= 0 or any(v < 0 for v in seeds.values()) or any(s not in ids for s in seeds):
        raise TypedRejection("UNBOUND_SEED", "seeds must be a non-negative distribution over atoms")
    return [Fraction(seeds.get(x, Fraction(0, 1))) / total for x in ids]


def uniform_seed(ks: KnowledgeSpace) -> list[Fraction]:
    n = len(ks.ids)
    return [Fraction(1, n) for _ in range(n)]


def gated_seed(ks: KnowledgeSpace, seed: Sequence[Fraction], revoked: Iterable[Hashable], mode: NavigationMode = NavigationMode.WARRANTED) -> list[Fraction]:
    """s_{Q,R} = g_R ⊙ s_Q — entry-wise, NOT renormalised (contract §25)."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    return [Fraction(s) * _gate(amap[x].liveness(rv), mode) for x, s in zip(ks.ids, seed, strict=True)]


def _transpose(m: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [list(col) for col in zip(*m, strict=True)]


def _solve_exact(a: list[list[Fraction]], b: list[Fraction]) -> list[Fraction]:
    n = len(a)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b, strict=True)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            raise CannotCheck("singular exact system")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [x / p for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col]:
                f = aug[r][col]
                aug[r] = [x - f * y for x, y in zip(aug[r], aug[col], strict=True)]
    return [row[-1] for row in aug]


def restart_step(p: Sequence[Sequence[Fraction]], seed: Sequence[Fraction], x: Sequence[Fraction], alpha: Fraction) -> list[Fraction]:
    pt = _transpose(p)
    return [alpha * seed[i] + (1 - alpha) * sum((pt[i][j] * x[j] for j in range(len(x))), Fraction(0, 1)) for i in range(len(x))]


def restart_fixed_point_exact(p: Sequence[Sequence[Fraction]], seed: Sequence[Fraction], alpha: Fraction) -> list[Fraction]:
    """Solve (I − (1−α)Pᵀ) a = α s exactly over ℚ (KS-T05 fixed point)."""
    if not (Fraction(0, 1) < alpha <= Fraction(1, 1)):
        raise ValueError("alpha must be in (0,1]")
    n = len(p)
    if len(seed) != n or any(x < 0 for x in seed) or sum(seed, Fraction(0, 1)) > 1:
        raise ValueError("seed must be a non-negative sub-probability vector")
    pt = _transpose(p)
    a = [[Fraction(int(i == j), 1) - (1 - alpha) * pt[i][j] for j in range(n)] for i in range(n)]
    return _solve_exact(a, [alpha * x for x in seed])


def restart_iterate(
    p: Sequence[Sequence[Fraction]], seed: Sequence[Fraction], alpha: Fraction, steps: int
) -> tuple[list[Fraction], int]:
    """Iterate the contraction ``steps`` times from the seed; returns (vector, steps_used)."""
    a = list(seed)
    for k in range(steps):
        a = restart_step(p, seed, a, alpha)
    return a, steps


def restart_fixed_point_float(
    p: Sequence[Sequence[Fraction]], seed: Sequence[Fraction], alpha: float, *, tol: float = 1e-12, max_iter: int = 10_000
) -> tuple[list[float], int]:
    """Float power iteration for scale; geometric convergence at rate (1−α) (KS-T05)."""
    n = len(p)
    pt = [[float(p[j][i]) for j in range(n)] for i in range(n)]
    s = [float(x) for x in seed]
    a = s[:]
    for k in range(1, max_iter + 1):
        nxt = [alpha * s[i] + (1 - alpha) * sum(pt[i][j] * a[j] for j in range(n)) for i in range(n)]
        delta = sum(abs(u - v) for u, v in zip(nxt, a, strict=True))
        a = nxt
        if delta <= tol:
            return a, k
    raise CannotCheck(f"float restart iteration did not converge within {max_iter} steps")


def l1(x: Sequence[Fraction]) -> Fraction:
    return sum((abs(v) for v in x), Fraction(0, 1))


def fixed_point(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    alpha: Fraction,
    *,
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
    mode: NavigationMode = NavigationMode.WARRANTED,
    matrix: NavigationMatrix | None = None,
) -> dict[str, Fraction]:
    """a*_{Q,R} with the gated, un-renormalised seed (KS-T04b)."""
    m = matrix or navigation_matrix(ks, revoked=revoked, relevance=relevance, mode=mode)
    s = gated_seed(ks, seed, revoked, mode)
    return dict(zip(ks.ids, restart_fixed_point_exact(m.as_lists(), s, alpha), strict=True))


# --------------------------------------------------------------------------------------------
# reaction surprise (KS-T06 / T06b) — a registered design choice, replaceable
# --------------------------------------------------------------------------------------------


def reaction_surprise(query: Fraction | float, background: Fraction | float, eps: float = 1e-12) -> float:
    q, b = float(query), float(background)
    if q <= 0:
        return 0.0
    return max(0.0, q * math.log((q + eps) / (b + eps)))


def surprise_vector(query: Mapping[str, Fraction], background: Mapping[str, Fraction]) -> dict[str, float]:
    return {x: reaction_surprise(query[x], background[x]) for x in query}


def rank_by(values: Mapping[str, float | Fraction], exclude: Iterable[str] = ()) -> tuple[str, ...]:
    ex = set(exclude)
    return tuple(sorted((x for x in values if x not in ex), key=lambda x: (-float(values[x]), x)))


def mutant_popularity_rank(activation: Mapping[str, Fraction], exclude: Iterable[str] = ()) -> tuple[str, ...]:
    """Planted control: rank by raw activation (hub popularity) instead of reaction surprise."""
    return rank_by(activation, exclude)


# --------------------------------------------------------------------------------------------
# closures and the four-valued outcome (KS-T19)
# --------------------------------------------------------------------------------------------


def ungated_closure(ks: KnowledgeSpace, start: Iterable[str]) -> frozenset[str]:
    """The ceiling walker C°: unbounded, ungated forward reachability (any tail reached).
    Worklist over a tail-indexed adjacency: O(|incidences|)."""
    by_tail: dict[str, list[Hyperedge]] = {}
    for e in ks.hyperedges:
        for t in e.tails:
            by_tail.setdefault(t, []).append(e)
    reached = set(start)
    work = list(reached)
    while work:
        v = work.pop()
        for e in by_tail.get(v, ()):
            for h in e.heads:
                if h not in reached:
                    reached.add(h)
                    work.append(h)
    return frozenset(reached)


def gated_closure(ks: KnowledgeSpace, start: Iterable[str], revoked: Iterable[Hashable] = ()) -> frozenset[str]:
    """C^R: reachability over LIVE atoms and LIVE edges with all tails reached (conjunctive).
    Worklist with per-edge pending-tail counters: O(|incidences|)."""
    rv = frozenset(revoked)
    amap = ks.atom_map()
    live = {x: amap[x].is_live(rv) for x in ks.ids}
    by_tail: dict[str, list[int]] = {}
    pending: list[int] = []
    for i, e in enumerate(ks.hyperedges):
        pending.append(len(e.tails))
        for t in e.tails:
            by_tail.setdefault(t, []).append(i)
    reached = {x for x in start if live[x]}
    work = list(reached)
    while work:
        v = work.pop()
        for i in by_tail.get(v, ()):
            pending[i] -= 1
            e = ks.hyperedges[i]
            if pending[i] == 0 and e.warrant.is_live(rv):
                for h in e.heads:
                    if h not in reached and live[h]:
                        reached.add(h)
                        work.append(h)
    return frozenset(reached)


class NavigationOutcome(str, Enum):
    FOUND = "FOUND"
    GAP_NOT_FOUND = "GAP_NOT_FOUND"
    OBSTRUCTION_WITNESSED = "OBSTRUCTION_WITNESSED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True, slots=True)
class NavigationBudget:
    steps: int
    restarts: int
    depth: int

    def validate(self) -> None:
        if min(self.steps, self.restarts, self.depth) <= 0:
            raise CannotCheck(f"navigation budget must be positive: {self}")

    def as_tuple(self) -> tuple[int, int, int]:
        return (self.steps, self.restarts, self.depth)


def assert_matched_budgets(arms: Mapping[str, NavigationBudget]) -> None:
    """Budget clause: arms with different budgets cannot be compared (``CANNOT_CHECK``)."""
    if not arms:
        raise CannotCheck("no arms")
    for b in arms.values():
        b.validate()
    distinct = {b.as_tuple() for b in arms.values()}
    if len(distinct) != 1:
        raise CannotCheck(f"UNMATCHED_NAVIGATION_BUDGET: {sorted(arms)} -> {sorted(distinct)}")


@dataclass(frozen=True, slots=True)
class ObstructionWitness:
    incumbent_mechanism: str
    failed_obligation: str
    witness_atoms: tuple[str, ...]
    lower_level_dispositions: tuple[str, ...]
    resource_bound: str
    kind: str = "GLOBAL_OBSTRUCTION"

    def jump_trigger_fields(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "incumbent_level": 1,  # J1 local repair / composition is the incumbent navigation level
            "witness_ids": self.witness_atoms,
            "lower_level_dispositions": self.lower_level_dispositions,
        }

    def to_jump_trigger(self, trigger_id: str = "kso-obstruction"):
        from .jump import JumpLevel, JumpTrigger, TriggerKind

        f = self.jump_trigger_fields()
        return JumpTrigger(
            trigger_id=trigger_id,
            kind=TriggerKind(f["kind"]),
            incumbent_level=JumpLevel(f["incumbent_level"]),
            witness_ids=tuple(f["witness_ids"]),
            lower_level_dispositions=tuple(f["lower_level_dispositions"]),
        )


@dataclass(frozen=True, slots=True)
class NavigationResult:
    outcome: NavigationOutcome
    target: str
    reason: str
    steps_used: int
    activation: Fraction | None = None
    witness: ObstructionWitness | None = None
    gap_channel_hook: str = ""
    resources: ResourceVector = field(default_factory=ResourceVector)


def navigate(
    ks: KnowledgeSpace,
    seed: Sequence[Fraction],
    target: str,
    budget: NavigationBudget,
    *,
    alpha: Fraction = Fraction(1, 3),
    threshold: Fraction = Fraction(1, 1000),
    revoked: Iterable[Hashable] = (),
    relevance: Relevance = None,
) -> NavigationResult:
    """Four-valued navigation under a budget (KS-T19).

    FOUND iff the gated walk activates the target above ``threshold`` within ``budget.steps``;
    GAP_NOT_FOUND with reason TARGET_ABSENT / WARRANT_GATED / BUDGET_EXHAUSTED otherwise, unless the
    target lies outside the ungated ceiling closure, which is OBSTRUCTION_WITNESSED.  A zero budget
    is CANNOT_CHECK.  Timeout alone is never an obstruction.
    """
    budget.validate()
    ids = ks.ids
    rv = frozenset(revoked)
    if target not in ids:
        return NavigationResult(NavigationOutcome.GAP_NOT_FOUND, target, "TARGET_ABSENT", 0, gap_channel_hook="ACQUISITION_CHANNELS")
    m = navigation_matrix(ks, revoked=rv, relevance=relevance)
    p = m.as_lists()
    s = gated_seed(ks, seed, rv)
    # a_0 = α·s: the iterates are the partial Neumann sums, monotone from below and ≤ a*, so a
    # FOUND at any budget is sound for the fixed point (MEG-06 / T2).  The frozen reference started
    # at s, whose iterates overshoot a* — a documented tightening (steps_used may differ).
    a = [alpha * x for x in s]
    ti = ids.index(target)
    work = 0
    for k in range(1, budget.steps + 1):
        a = restart_step(p, s, a, alpha)
        work += len(ids) * len(ids)
        if a[ti] >= threshold:
            return NavigationResult(
                NavigationOutcome.FOUND, target, "ACTIVATION_ABOVE_THRESHOLD", k, activation=a[ti],
                resources=ResourceVector(navigation_steps=k, navigation_work=work),
            )
    support = [x for x, v in zip(ids, seed, strict=True) if v > 0]
    ceiling = ungated_closure(ks, support)
    bracket = (1 - alpha) ** (budget.steps + 1) * sum(s, Fraction(0, 1))  # a*(t) ∈ [a_k(t), a_k(t) + bracket]
    res = ResourceVector(navigation_steps=budget.steps, navigation_work=work)
    if target not in ceiling:
        witness = ObstructionWitness(
            incumbent_mechanism="restart_navigation_over_registered_relations",
            failed_obligation=f"reach {target} from seed support {tuple(support)}",
            witness_atoms=tuple(sorted(ceiling)),
            lower_level_dispositions=(
                "BUDGET: irrelevant, closure is exact and budget-independent",
                "WARRANT: irrelevant, closure is ungated",
                "RESTART: irrelevant, every seed-support atom is in the closure",
            ),
            resource_bound=f"steps={budget.steps},restarts={budget.restarts},depth={budget.depth}",
        )
        return NavigationResult(NavigationOutcome.OBSTRUCTION_WITNESSED, target, "TARGET_OUTSIDE_UNGATED_CLOSURE", budget.steps, activation=a[ti], witness=witness, resources=res)
    if target not in gated_closure(ks, support, rv):
        amap = ks.atom_map()
        why = "WARRANT_GATED_TARGET_CLOSURE_REACHABLE"
        if amap[target].liveness(rv) is Liveness.UNKNOWN:
            why = "WARRANT_UNKNOWN_TARGET_CLOSURE_REACHABLE"
        return NavigationResult(NavigationOutcome.GAP_NOT_FOUND, target, why, budget.steps, activation=a[ti], gap_channel_hook="ACQUIRE_WARRANT", resources=res)
    decided_negative = a[ti] + bracket < threshold  # the bracket excludes θ: more budget cannot help
    return NavigationResult(NavigationOutcome.GAP_NOT_FOUND, target, "BUDGET_EXHAUSTED_TARGET_CLOSURE_REACHABLE" if not decided_negative else "BUDGET_BRACKET_EXCLUDES_THRESHOLD", budget.steps, activation=a[ti], gap_channel_hook="MORE_BUDGET" if not decided_negative else "ACQUIRE_WARRANT_OR_STRUCTURE", resources=res)


def identification_witness(ks: KnowledgeSpace, activation: Mapping[str, Fraction], target: str) -> ObstructionWitness | None:
    """STRUCTURAL_NONIDENTIFIABILITY: another atom of the same type carries exactly the same
    activation under the committed seed (ME-X2 ``CANNOT_IDENTIFY``)."""
    amap = ks.atom_map()
    t = amap[target]
    twins = tuple(sorted(x for x, a in amap.items() if x != target and a.atom_type == t.atom_type and activation[x] == activation[target]))
    if not twins:
        return None
    return ObstructionWitness(
        incumbent_mechanism="restart_navigation_over_registered_relations",
        failed_obligation=f"identify {target} among same-type atoms",
        witness_atoms=(target, *twins),
        lower_level_dispositions=("BUDGET: irrelevant, activations are exact fixed points", "WARRANT: irrelevant, all twins live", "RESTART: irrelevant, same committed seed"),
        resource_bound="exact",
        kind="STRUCTURAL_NONIDENTIFIABILITY",
    )
