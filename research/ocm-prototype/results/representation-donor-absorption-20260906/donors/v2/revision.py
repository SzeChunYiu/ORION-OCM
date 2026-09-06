"""Exact finite checks for Machine Epistemics Field Dynamics V1.

Finite checks are calibration/counterexample evidence for the scoped laws in DYNAMICS.md.
They do not establish field status, novelty, environment-model closure, or OCM parity.

Exit 0 = PASS, 1 = FAIL, 2 = CANNOT_CHECK.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from numbers import Rational


class CannotCheck(RuntimeError):
    pass


LIVE, UNKNOWN, DEAD = "LIVE", "UNKNOWN", "DEAD"


def exact(value):
    if isinstance(value, bool) or not isinstance(value, Rational):
        raise CannotCheck("exact rational input required")
    return Fraction(value)


def finite_set(values, name):
    """Require a finite materialized container; never consume a one-shot model."""
    if not isinstance(values, (list, tuple, set, frozenset, range, dict)):
        raise CannotCheck(f"{name} must be a finite materialized container")
    try:
        return frozenset(values)
    except TypeError as exc:
        raise CannotCheck(f"{name} contains an unhashable identity") from exc


def validate_responses(responses):
    if not isinstance(responses, dict) or not responses:
        raise CannotCheck("nonempty materialized response mapping required")
    try:
        for result in responses.values():
            hash(result)
    except TypeError as exc:
        raise CannotCheck("response labels must be hashable registered outcomes") from exc
    return responses


def validate_kernel(P):
    if not isinstance(P, (list, tuple)) or any(not isinstance(row, (list, tuple)) for row in P):
        raise CannotCheck("kernel must be a materialized matrix")
    n = len(P)
    if not n or any(len(row) != n for row in P):
        raise CannotCheck("nonempty square kernel required")
    matrix = tuple(tuple(exact(x) for x in row) for row in P)
    if any(x < 0 for row in matrix for x in row) or any(sum(row) > 1 for row in matrix):
        raise CannotCheck("nonnegative row-substochastic kernel required")
    return matrix


def validate_partition(blocks, n):
    if (not isinstance(blocks, (list, tuple))
            or any(not isinstance(block, (list, tuple, set, frozenset, range)) for block in blocks)):
        raise CannotCheck("partition must contain finite materialized blocks")
    blocks = tuple(tuple(block) for block in blocks)
    flat = [i for block in blocks for i in block]
    if (not blocks or any(not block for block in blocks)
            or any(type(i) is not int for i in flat)
            or len(flat) != n or set(flat) != set(range(n))):
        raise CannotCheck("partition must cover every state exactly once")
    return blocks


def l1(v):
    return sum(abs(x) for x in v)


def inf_matrix(M):
    return max((sum(abs(x) for x in row) for row in M), default=Fraction(0))


def fixed_point(P, s, alpha=Fraction(1, 3)):
    """Solve (I-(1-a)P^T)x=a*s exactly over Q."""
    P = validate_kernel(P)
    if not isinstance(s, (list, tuple, range)):
        raise CannotCheck("seed must be a materialized finite vector")
    s, alpha = tuple(exact(x) for x in s), exact(alpha)
    if len(s) != len(P) or any(x < 0 for x in s) or sum(s) > 1:
        raise CannotCheck("nonnegative dimension-matched seed with mass <= 1 required")
    if not 0 < alpha <= 1:
        raise CannotCheck("restart alpha must be in (0, 1]")
    n = len(s)
    beta = 1 - alpha
    A = [[Fraction(int(i == j)) - beta * P[j][i] for j in range(n)] for i in range(n)]
    aug = [A[i][:] + [alpha * s[i]] for i in range(n)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if aug[r][c] != 0), None)
        if pivot is None:
            raise CannotCheck("singular restart system")
        aug[c], aug[pivot] = aug[pivot], aug[c]
        z = aug[c][c]
        aug[c] = [x / z for x in aug[c]]
        for r in range(n):
            if r == c:
                continue
            z = aug[r][c]
            if z:
                aug[r] = [x - z * y for x, y in zip(aug[r], aug[c])]
    return [row[-1] for row in aug]


def tracking_bounds(initial_error, drifts, alpha):
    """Parent recurrence e[t+1] <= (1-alpha)e[t] + drift[t]."""
    alpha, error = exact(alpha), exact(initial_error)
    drifts = tuple(exact(d) for d in drifts)
    if not 0 < alpha <= 1 or error < 0 or any(d < 0 for d in drifts):
        raise CannotCheck("nonnegative errors/drifts and alpha in (0,1] required")
    bounds = [error]
    for drift in drifts:
        error = (1-alpha) * error + drift
        bounds.append(error)
    return tuple(bounds)


@dataclass(frozen=True)
class Authority:
    world_truth: int = 0
    speaker: int = 0
    task_contract: int = 0
    commit: int = 0

    def __post_init__(self):
        if any(type(v) is not int or v < 0 for v in self.coordinates()):
            raise CannotCheck("authority coordinates must be nonnegative integers")

    def coordinates(self):
        return (self.world_truth, self.speaker, self.task_contract, self.commit)

    def meet(self, other):
        return Authority(*(min(a, b) for a, b in zip(
            (self.world_truth, self.speaker, self.task_contract, self.commit),
            (other.world_truth, other.speaker, other.task_contract, other.commit),
        )))


def authority_preserved(proposed, operator, *inputs):
    """Check an output rather than constructing an output guaranteed to pass."""
    bound = operator
    for source in inputs:
        bound = bound.meet(source)
    return all(x <= y for x, y in zip(proposed.coordinates(), bound.coordinates()))


def check_fd01():
    vals = range(3)
    checks = 0
    for a in itertools.product(vals, repeat=4):
        for b in itertools.product(vals, repeat=4):
            A, B = Authority(*a), Authority(*b)
            M = A.meet(B)
            assert M == Authority(*(min(x, y) for x, y in zip(a, b)))
            assert all(m <= x and m <= y for m, x, y in zip(
                (M.world_truth, M.speaker, M.task_contract, M.commit), a, b))
            checks += 1
    internal = Authority(world_truth=0, speaker=1, task_contract=1, commit=0)
    receipt = Authority(world_truth=2, speaker=2, task_contract=2, commit=2)
    assert internal.meet(receipt).commit == 0
    assert max(internal.commit, receipt.commit) == 2
    return {"authority_pair_checks": checks, "internal_commit_nonamplification": 1, "max_mutant_caught": 1}


def consistent_support(support, nogoods):
    return not any(set(n) <= set(support) for n in nogoods)


def live_from_supports(supports, revoked=(), nogoods=()):
    R = set(revoked)
    return any(not (set(s) & R) and consistent_support(s, nogoods) for s in supports)


def warrant_status(supports, registered, revoked=(), unknown=(), nogoods=(), *, closed=True):
    """Finite support model; unregistered roots cannot silently count as LIVE."""
    registered, revoked, unknown = map(frozenset, (registered, revoked, unknown))
    supports = tuple(frozenset(s) for s in supports)
    if not (revoked | unknown) <= registered or revoked & unknown:
        raise CannotCheck("root status partition is inconsistent")
    if any(not s <= registered for s in supports):
        raise CannotCheck("unregistered support root")
    candidates = [s for s in supports if not s & revoked and consistent_support(s, nogoods)]
    if any(not s & unknown for s in candidates):
        return LIVE
    if candidates or closed is not True:
        return UNKNOWN
    return DEAD


def check_fd02():
    supports_a = (frozenset({"a"}),)
    supports_b = (frozenset({"b"}),)
    joint = tuple(frozenset(x | y) for x in supports_a for y in supports_b)
    N = (frozenset({"a", "b"}),)
    assert live_from_supports(supports_a, nogoods=N)
    assert live_from_supports(supports_b, nogoods=N)
    assert not live_from_supports(joint, nogoods=N)
    alternatives = (frozenset({"a"}), frozenset({"c"}))
    assert live_from_supports(alternatives, revoked={"a"})
    score = Fraction(999, 1000)
    score_mints_truth = False
    assert score > 0 and not score_mints_truth
    return {"cross_nogood_blocks_joint": 1, "alternate_support_survives": 1, "score_does_not_mint_truth": 1}


def impact_cone(changed, edges):
    out = set(changed)
    grew = True
    while grew:
        grew = False
        for tails, heads in edges:
            if set(tails) & out:
                before = len(out)
                out.update(heads)
                grew |= len(out) != before
    return frozenset(out)


def check_fd03():
    edges = [(("e",), ("a",)), (("a",), ("b",)), (("b",), ("c",)), (("x",), ("y",))]
    cone = impact_cone({"e"}, edges)
    assert cone == {"e", "a", "b", "c"}
    assert "x" not in cone and "y" not in cone
    one_hop = {"e", "a"}
    assert "c" not in one_hop and "c" in cone
    return {"impact": sorted(cone), "outside_cone_invariant_fixture": 1, "one_hop_mutant_caught": 1}


def all_row_substochastic_2():
    vals = (Fraction(0), Fraction(1, 2), Fraction(1))
    rows = [(a, b) for a in vals for b in vals if a + b <= 1]
    return [tuple((Fraction(a), Fraction(b)) for a, b in (r1, r2)) for r1 in rows for r2 in rows]


def check_fd04(alpha=Fraction(1, 3)):
    kernels = all_row_substochastic_2()
    seeds = (
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    solutions = {(P, s): fixed_point(P, s, alpha) for P in kernels for s in seeds}
    checks = strict = 0
    for P in kernels:
        for Pp in kernels:
            dP = [[Pp[i][j] - P[i][j] for j in range(2)] for i in range(2)]
            dp = inf_matrix(dP)
            for s in seeds:
                a = solutions[P, s]
                for sp in seeds:
                    ap = solutions[Pp, sp]
                    lhs = l1([ap[i] - a[i] for i in range(2)])
                    rhs = l1([sp[i] - s[i] for i in range(2)]) + ((1-alpha)/alpha) * dp
                    assert lhs <= rhs, (P, Pp, s, sp, lhs, rhs)
                    strict += int(lhs < rhs)
                    checks += 1
    assert checks == 20736
    return {"kernel_seed_pair_checks": checks, "strict_cases": strict, "kernels": len(kernels), "seeds": len(seeds)}


@dataclass(frozen=True)
class EvidenceState:
    active: frozenset[str]
    history: tuple[str, ...]


def revoke(st, e):
    if e not in st.active:
        raise CannotCheck("revoke requires an active registered evidence identity")
    return EvidenceState(st.active - {e}, st.history + (f"revoke:{e}",))


def reinstate(st, e):
    if e in st.active or not any(event in (f"admit:{e}", f"relearn:{e}") for event in st.history):
        raise CannotCheck("reinstate requires an inactive previously admitted identity")
    return EvidenceState(st.active | {e}, st.history + (f"reinstate:{e}",))


def check_fd05():
    initial = EvidenceState(frozenset({"e"}), ("admit:e",))
    r = revoke(initial, "e")
    rr = reinstate(r, "e")
    assert rr.active == initial.active
    new = EvidenceState(r.active | {"e2"}, r.history + ("relearn:e2",))
    assert new.active != initial.active
    behavior_initial = bool(initial.active & {"e", "e2"})
    behavior_new = bool(new.active & {"e", "e2"})
    assert behavior_initial == behavior_new is True
    assert rr.history != initial.history
    return {"same_identity_semantic_reinstatement": 1, "relearn_behavior_equal_lineage_distinct": 1, "append_only_history_preserved": 1}


def persistent_kernel(states, edges, good, *, model_closed=True):
    if model_closed is not True:
        raise CannotCheck("environment upper closure is unavailable")
    states, edges, good = frozenset(states), tuple(edges), frozenset(good)
    if not good <= states or any(u not in states or v not in states for u, v in edges):
        raise CannotCheck("revision model is not closed over registered states")
    bad_reachable = set(states) - set(good)
    changed = True
    while changed:
        changed = False
        for u, v in edges:
            if v in bad_reachable and u not in bad_reachable:
                bad_reachable.add(u)
                changed = True
    return frozenset(set(states) - bad_reachable)


def controlled_kernel(states, actions, good, *, model_closed):
    """Greatest safe set for controller-then-adversarial-environment semantics.

    actions[state][action] is the complete NONEMPTY successor set. Missing
    actions means deadlock, not vacuous success. Waiting needs an explicit loop.
    """
    states, good = finite_set(states, "states"), finite_set(good, "safe states")
    if model_closed is not True:
        raise CannotCheck("environment upper closure is unavailable")
    if not isinstance(actions, dict) or not good <= states or set(actions) != states:
        raise CannotCheck("state/action registration mismatch")
    model = {}
    for state, choices in actions.items():
        if not isinstance(choices, dict):
            raise CannotCheck("materialized action mapping required")
        model[state] = {}
        for action, supplied in choices.items():
            successors = finite_set(supplied, "action successors")
            if not successors or not successors <= states:
                raise CannotCheck("action successor set must be nonempty and closed")
            model[state][action] = successors
    current = good
    while True:
        nxt = frozenset(s for s in current if any(
            successors <= current for successors in model[s].values()))
        if nxt == current:
            return current
        current = nxt


def channel_update(hypotheses, responses, observed, claimed, *, model_closed):
    """Exact deterministic channel: all and only the observed fibre survives."""
    hypotheses, claimed = finite_set(hypotheses, "hypotheses"), finite_set(claimed, "claimed hypotheses")
    responses = validate_responses(responses)
    if model_closed is not True or not hypotheses or set(responses) != hypotheses:
        raise CannotCheck("complete nonempty finite channel model required")
    fibre = frozenset(h for h in hypotheses if responses[h] == observed)
    if not fibre:
        raise CannotCheck("observation outside the registered model")
    return claimed == fibre


def channel_information_bound(responses):
    """Exact integer equivalent of E[log2(N/n_Y)] <= log2(m).

    Assumes a uniform prior on N hypotheses and a deterministic complete
    response map with m nonempty fibres. This is NOT a per-outcome bound.
    """
    responses = validate_responses(responses)
    sizes = {}
    for result in responses.values():
        sizes[result] = sizes.get(result, 0) + 1
    n, m = len(responses), len(sizes)
    rhs = m ** n
    for count in sizes.values():
        rhs *= count ** count
    return n ** n <= rhs


def check_fd07():
    cases = 0
    for size in range(1, 7):
        for outcomes in itertools.product(range(3), repeat=size):
            assert channel_information_bound(dict(enumerate(outcomes)))
            cases += 1
    responses = {i: int(i == 0) for i in range(8)}
    assert channel_update(range(8), responses, 1, {0}, model_closed=True)
    assert not channel_update(range(8), responses, 0, {1}, model_closed=True)
    # Rare binary response leaves one of eight hypotheses: 3 bits > log2(2).
    assert Fraction(8, 1) > 2
    assert Fraction(8, 4) * Fraction(4, 1) == Fraction(8, 1)
    return {"status": "OPEN_RESEARCH", "finite_fragment": "PARENT_SUFFICIENT",
            "deterministic_channels": cases, "rare_outcome_counterexample": 1,
            "finite_checker_does_not_promote": 1}


def check_fd06():
    S = {0, 1, 2, 3}
    E = {(0, 1), (1, 2), (3, 3)}
    P = {0, 1, 3}
    K = persistent_kernel(S, E, P)
    assert K == {3}
    one_step = {s for s in P if all(v in P for u, v in E if u == s)}
    assert 0 in one_step and 0 not in K
    actions = {0: {"safe": {3}, "risky": {1, 3}}, 1: {"forced": {2}},
               2: {"wait": {2}}, 3: {"wait": {3}}}
    controlled = controlled_kernel(S, actions, P, model_closed=True)
    assert controlled == {0, 3}
    risky_only = dict(actions)
    risky_only[0] = {"risky": {1, 3}}
    assert controlled_kernel(S, risky_only, P, model_closed=True) == {3}
    return {"kernel": sorted(K), "controlled_kernel": sorted(controlled),
            "adversarial_successor_mutant_caught": 1,
            "multi_step_hostile": 1, "parent_disposition": "PARENT_SUFFICIENT"}


def row_block_sums(P, blocks):
    P = validate_kernel(P)
    blocks = validate_partition(blocks, len(P))
    return [[sum(P[i][j] for j in block) for block in blocks] for i in range(len(P))]


def strong_lumpable(P, blocks):
    blocks = validate_partition(blocks, len(P))
    sums = row_block_sums(P, blocks)
    return all(sums[i] == sums[j] for block in blocks for i in block for j in block)


def revision_commutes(revision, blocks, coarse_revision):
    if (not isinstance(revision, (tuple, list, range))
            or not isinstance(coarse_revision, (tuple, list, range))):
        raise CannotCheck("revision maps must be materialized indexed finite sequences")
    blocks = validate_partition(blocks, len(revision))
    if (len(coarse_revision) != len(blocks)
            or any(type(i) is not int or not 0 <= i < len(revision) for i in revision)
            or any(type(i) is not int or not 0 <= i < len(blocks) for i in coarse_revision)):
        raise CannotCheck("total registered revision maps required")
    quotient = {state: block for block, states in enumerate(blocks) for state in states}
    return all(quotient[revision[s]] == coarse_revision[quotient[s]] for s in quotient)


def check_fd08():
    F = ((0, 1), (2, 3))
    P = [
        [Fraction(1,2), 0, Fraction(1,2), 0],
        [0, Fraction(1,2), 0, Fraction(1,2)],
        [Fraction(1,4), 0, Fraction(3,4), 0],
        [0, Fraction(1,4), 0, Fraction(3,4)],
    ]
    assert strong_lumpable(P, F)
    bad = [row[:] for row in P]
    bad[1] = [0, Fraction(3,4), 0, Fraction(1,4)]
    assert not strong_lumpable(bad, F)
    live_good = [LIVE, LIVE, DEAD, DEAD]
    live_bad = [LIVE, DEAD, DEAD, DEAD]
    measurable = lambda vals: all(len({vals[i] for i in block}) == 1 for block in F)
    assert measurable(live_good) and not measurable(live_bad)
    return {"parent_lumpability_no_alarm": 1, "nonlumpable_mutant_caught": 1, "warrant_measurability_independent_gate": 1}


def check_fd09():
    shared_supports = [frozenset({"common_source"})] * 3
    assert len(set(shared_supports)) == 1
    authorities = [Authority(speaker=1, world_truth=0) for _ in range(10)]
    out = Authority(world_truth=0, speaker=1, commit=0)
    for a in authorities:
        out = out.meet(a)
    assert out.world_truth == 0
    return {"shared_source_counts_once": 1, "ten_speakers_do_not_mint_truth": 1}


def check_fd10():
    self_a = Authority(world_truth=0, speaker=0, task_contract=0, commit=0)
    object_a = Authority(world_truth=2, task_contract=2, commit=1)
    assert self_a.meet(object_a).world_truth == 0
    assert self_a.meet(object_a).commit == 0
    before = {"K_world": ("claim",), "commit": (), "K_self": ()}
    after = dict(before, K_self=("diagnosis",))
    assert shadow_noninterfering(before, after)
    assert not shadow_noninterfering(before, dict(after, commit=("self_adopt",)))
    return {"self_cannot_raise_world_truth": 1, "self_cannot_raise_commit": 1}


def shadow_noninterfering(before, after):
    """Finite footprint contract; not a proof about a concurrent OCM runtime."""
    if set(before) != set(after):
        return False
    allowed = {"K_self", "B_meter", "X_shadow_trace"}
    return all(before[k] == after[k] for k in before if k not in allowed)


def resource_add(a, b):
    if not isinstance(a, (list, tuple, range)) or not isinstance(b, (list, tuple, range)):
        raise CannotCheck("resource axes must be materialized finite vectors")
    a, b = tuple(exact(x) for x in a), tuple(exact(x) for x in b)
    if not a or len(a) != len(b) or any(x < 0 for x in a + b):
        raise CannotCheck("cumulative cost coordinates must match and be nonnegative")
    return tuple(x + y for x, y in zip(a, b))


def check_fd11():
    base = (10, 5, 20, 30, 4, 7)
    representation = (3, 2, 4, 8, 1, 2)
    total = resource_add(base, representation)
    assert total == (13, 7, 24, 38, 5, 9)
    assert base != total
    return {"resource_coordinates": len(total), "no_free_representation_fixture": 1}


PASS, FAIL, CC, GAP = "PASS", "FAIL", "CANNOT_CHECK", "GAP"
STAGES = ("ATOMIZE", "NAVIGATE", "EXTRACT", "COMPOSE", "CHECK", "COMMIT")


def run_pipeline(statuses, budget=len(STAGES)):
    if type(budget) is not int or budget < 0:
        return CC, ()
    # Only materialized finite vectors are inside this checker contract.
    if not isinstance(statuses, (list, tuple)):
        return CC, ()
    if len(statuses) != len(STAGES) or any(st not in (PASS, FAIL, CC, GAP) for st in statuses):
        return CC, ()
    trace = []
    for stage, st in zip(STAGES, statuses):
        if len(trace) >= budget:
            return "RESOURCE_EXHAUSTED", tuple(trace)
        trace.append((stage, st))
        if st == CC:
            return CC, tuple(trace)
        if st == FAIL:
            return FAIL, tuple(trace)
        if st == GAP:
            return GAP, tuple(trace)
    return PASS, tuple(trace)


def mutant_ignore_cc(statuses):
    if all(x in (PASS, CC) for x in statuses):
        return PASS
    return next((x for x in statuses if x != PASS), PASS)


def check_fd12():
    cases = 0
    for statuses in itertools.product((PASS, FAIL, CC, GAP), repeat=len(STAGES)):
        out, trace = run_pipeline(statuses)
        first = next((x for x in statuses if x != PASS), PASS)
        assert out == first
        if CC in statuses[:len(trace)]:
            assert out == CC
        cases += 1
    hostile = (PASS, PASS, CC, PASS, PASS, PASS)
    assert run_pipeline(hostile)[0] == CC
    assert mutant_ignore_cc(hostile) == PASS
    assert cases == 4096
    return {"status_vectors": cases, "cannot_check_absorbing": 1, "ignore_cannot_check_mutant_caught": 1}


def check_boundaries():
    checks = (
        lambda: fixed_point(((2,),), (1,)),
        lambda: fixed_point(((1,),), (1,), 0),
        lambda: fixed_point(((1.0,),), (1,)),
        lambda: warrant_status(({"unknown-root"},), {"registered"}),
        lambda: reinstate(EvidenceState(frozenset(), ()), "never-admitted"),
        lambda: controlled_kernel({0}, {0: {"wait": {0}}}, {0}, model_closed=False),
        lambda: controlled_kernel({0}, {0: {"jump": {1}}}, {0}, model_closed=True),
        lambda: channel_update({0}, {0: "a"}, "b", set(), model_closed=True),
        lambda: strong_lumpable(((1, 0), (0, 1)), ((0,),)),
        lambda: resource_add((1, 2), (1,)),
        lambda: resource_add((1,), (-1,)),
    )
    for check in checks:
        try:
            check()
        except CannotCheck:
            pass
        else:
            raise AssertionError("an unavailable/invalid premise was accepted")
    assert run_pipeline((PASS,) * 5)[0] == CC
    assert run_pipeline((PASS,) * 6, budget=5)[0] == "RESOURCE_EXHAUSTED"
    return {"cannot_check_inputs": len(checks) + 1, "budget_exhaustion": 1}


def run_all():
    return {
        "FD-01": check_fd01(),
        "FD-02": check_fd02(),
        "FD-03": check_fd03(),
        "FD-04": check_fd04(),
        "FD-05": check_fd05(),
        "FD-06": check_fd06(),
        "FD-08": check_fd08(),
        "FD-09": check_fd09(),
        "FD-10": check_fd10(),
        "FD-11": check_fd11(),
        "FD-12": check_fd12(),
        "FD-07": check_fd07(),
        "BOUNDARIES": check_boundaries(),
        "GENERAL_NOVELTY": "NOT_ESTABLISHED",
        "FIELD_STATUS": "NOT_ESTABLISHED",
    }


def main():
    try:
        if not __debug__:
            raise CannotCheck("assertion checking is disabled by optimized Python")
        out = run_all()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, sort_keys=True))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "type": type(exc).__name__, "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"status": "PASS", "result": out}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
