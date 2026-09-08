"""Exact finite cost-refinement checks and anytime lifetime benefit evidence.

These helpers verify mathematical inputs, not their correspondence to OCM code,
measurement completeness, sampling independence, or universal runtime safety.
Standard-library only. No ML, network, subprocesses, or production admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from collections import deque
from typing import Mapping


def rational(value: int | F) -> F:
    if type(value) not in (int, F):
        raise ValueError('exact built-in int or Fraction required; no floats/bools')
    return F(value)


def vector(values, *, nonnegative: bool = True) -> tuple[F, ...]:
    out = tuple(rational(x) for x in values)
    if not out or (nonnegative and any(x < 0 for x in out)):
        raise ValueError('nonempty nonnegative resource vector required')
    return out


@dataclass(frozen=True)
class Step:
    successor: str
    observation: tuple[str, ...]
    cost: tuple[F, ...]


@dataclass(frozen=True)
class Machine:
    states: tuple[str, ...]
    initial: str
    initial_cost: tuple[F, ...]
    events: tuple[str, ...]
    steps: Mapping[tuple[str, str], Step]
    # Every workload may end at any state. Teardown, flushing and final replay
    # required by the registered contract must be included here.
    close_costs: Mapping[str, tuple[F, ...]]
    close_observations: Mapping[str, tuple[str, ...]]


def _strings(values) -> tuple[str, ...]:
    out = tuple(values)
    if not out or any(type(s) is not str or not s for s in out) or len(set(out)) != len(out):
        raise ValueError('distinct nonempty string identifiers required')
    return out


def _observation(value):
    if type(value) is not tuple or any(type(x) is not str for x in value):
        raise ValueError('observations must be tuples of literal strings')
    return value


def validate_machine(machine: Machine) -> int:
    states, events = _strings(machine.states), _strings(machine.events)
    if machine.initial not in states:
        raise ValueError('unknown initial state')
    if set(machine.steps) != {(s, e) for s in states for e in events}:
        raise ValueError('transition relation must cover every state/event exactly')
    if set(machine.close_costs) != set(states) or set(machine.close_observations) != set(states):
        raise ValueError('complete stopping/cleanup contract required')
    widths = {len(vector(machine.initial_cost))}
    for step in machine.steps.values():
        if step.successor not in states:
            raise ValueError('unknown successor')
        _observation(step.observation)
        widths.add(len(vector(step.cost)))
    for s in states:
        widths.add(len(vector(machine.close_costs[s])))
        _observation(machine.close_observations[s])
    if len(widths) != 1:
        raise ValueError('inconsistent resource dimensions')
    return next(iter(widths))


def dot(price, cost) -> F:
    p, c = vector(price), vector(cost)
    if len(p) != len(c) or not any(p):
        raise ValueError('matching dimensions and nonzero price required')
    return sum((a * b for a, b in zip(p, c)), F(0))


def product_pairs(candidate: Machine, parent: Machine):
    if validate_machine(candidate) != validate_machine(parent):
        raise ValueError('different resource dimensions')
    if set(candidate.events) != set(parent.events):
        raise ValueError('different legal event alphabets')
    initial = (candidate.initial, parent.initial)
    seen, queue = {initial}, deque([initial])
    while queue:
        c, p = queue.popleft()
        for event in candidate.events:
            pair = (candidate.steps[c, event].successor, parent.steps[p, event].successor)
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    return seen


def refinement_certificate(candidate: Machine, parent: Machine, price,
                           ratio: int | F, potential: Mapping[tuple[str, str], int | F]):
    """Check C_candidate <= ratio*C_parent + additive for ALL finite event words.

    Each system evolves its OWN state. The potential is supplied on the reachable
    product, never on an assumed common cache. Source-level refinement is separate.
    """
    rho = rational(ratio)
    if rho < 0:
        raise ValueError('negative comparison ratio')
    pairs = product_pairs(candidate, parent)
    if set(potential) != pairs:
        raise ValueError('potential must cover exactly the reachable product')
    phi = {pair: rational(value) for pair, value in potential.items()}
    failures = []
    for c, p in sorted(pairs):
        for event in candidate.events:
            cs, ps = candidate.steps[c, event], parent.steps[p, event]
            if cs.observation != ps.observation:
                failures.append((c, p, event, 'PROTECTED_OBSERVATION_MISMATCH'))
            slack = dot(price, cs.cost) - rho * dot(price, ps.cost)
            slack += phi[cs.successor, ps.successor] - phi[c, p]
            if slack > 0:
                failures.append((c, p, event, 'POSITIVE_AMORTIZED_SLACK', slack))
        if candidate.close_observations[c] != parent.close_observations[p]:
            failures.append((c, p, 'CLOSE', 'PROTECTED_OBSERVATION_MISMATCH'))
    initial = (candidate.initial, parent.initial)
    setup = dot(price, candidate.initial_cost) - rho * dot(price, parent.initial_cost)
    additive = setup + max(phi[initial] - phi[c, p]
                   + dot(price, candidate.close_costs[c])
                   - rho * dot(price, parent.close_costs[p]) for c, p in pairs)
    return {'verified': not failures, 'ratio': rho, 'additive': additive,
            'product_states': len(pairs), 'failures': failures,
            'scope': 'Supplied finite machines only; source refinement not certified'}


def synthesize_refinement(candidate: Machine, parent: Machine, price, ratio: int | F):
    """Find an exact potential, or reject a reachable positive-cost cycle.

    Finite graph difference constraints suffice: repeated relaxation computes
    longest simple-path distances from a zero-cost super-source. An improvement
    on round |Z| certifies a positive cycle, so no finite additive bound exists
    at this ratio for arbitrary event words. Observation matching is checked
    separately by refinement_certificate, including CLOSE.
    """
    rho = rational(ratio)
    if rho < 0:
        raise ValueError('negative comparison ratio')
    pairs = sorted(product_pairs(candidate, parent))
    edges = []
    for c, p in pairs:
        for event in candidate.events:
            cs, ps = candidate.steps[c, event], parent.steps[p, event]
            edges.append(((c, p), (cs.successor, ps.successor),
                          dot(price, cs.cost) - rho * dot(price, ps.cost)))
    distance = {pair: F(0) for pair in pairs}
    for _ in range(len(pairs)):
        updated = dict(distance)
        for start, end, weight in edges:
            updated[end] = max(updated[end], distance[start] + weight)
        if updated == distance:
            potential = {pair: -value for pair, value in distance.items()}
            result = refinement_certificate(candidate, parent, price, rho, potential)
            result['potential'] = potential
            return result
        distance = updated
    return {'verified': False, 'ratio': rho, 'potential': None,
            'reason': 'REACHABLE_POSITIVE_CYCLE',
            'scope': 'No finite additive cost bound at this ratio on supplied finite machines'}


def rollout(machine: Machine, events, price):
    validate_machine(machine)
    state, total, observations = machine.initial, dot(price, machine.initial_cost), []
    for event in events:
        if event not in machine.events:
            raise ValueError('illegal event')
        step = machine.steps[state, event]
        total += dot(price, step.cost)
        observations.append(step.observation)
        state = step.successor
    total += dot(price, machine.close_costs[state])
    observations.append(machine.close_observations[state])
    return total, tuple(observations), state


def live_use_value(joint_live_and_use_probabilities, saving_per_use, fixed_cost):
    """Expected benefit of one fixed investment from JOINT valid-use probabilities.

    No independence of reuse and revocation is silently assumed. Miss overhead,
    maintenance and close costs must be included in fixed_cost or the savings.
    """
    probabilities = tuple(rational(x) for x in joint_live_and_use_probabilities)
    saving, fixed = rational(saving_per_use), rational(fixed_cost)
    if any(not 0 <= p <= 1 for p in probabilities) or saving < 0 or fixed < 0:
        raise ValueError('invalid probability/cost')
    return saving * sum(probabilities, F(0)) - fixed


PHASES = ('setup', 'discovery', 'validation', 'solve', 'maintenance', 'checkpoint', 'close')


def complete_total(charges: Mapping[str, tuple[F, ...]]) -> tuple[F, ...]:
    """Require explicit entries, including zeros; this cannot detect hidden work."""
    if set(charges) != set(PHASES):
        raise ValueError('incomplete or unknown cost phase')
    rows = [vector(charges[p]) for p in PHASES]
    if len({len(row) for row in rows}) != 1:
        raise ValueError('resource dimensions differ by phase')
    return tuple(sum(column, F(0)) for column in zip(*rows))


class LifetimeEvidence:
    """Exact mixture e-processes for frozen IID paired LIFETIME trials.

    A trial is a whole independently initialized lifetime, not a query from a
    persistent run. Costs use each parent's own execution. All models, prices,
    caps and practical margins must be frozen before fresh evaluation begins.
    Rejection is statistical evidence conditional on these assumptions, not
    a certificate of protected correctness, deployment or architecture necessity.
    """
    def __init__(self, parents, prices, caps, *, alpha=F(1, 20), improvement=F(1, 20)):
        self.parents = _strings(parents)
        self.prices = tuple(vector(w) for w in prices)
        self.caps = vector(caps)
        self.alpha, self.improvement = rational(alpha), rational(improvement)
        if not self.prices or any(x <= 0 for x in self.caps):
            raise ValueError('positive caps and at least one price required')
        if not 0 < self.alpha < 1 or not 0 <= self.improvement < 1:
            raise ValueError('invalid alpha or improvement')
        self.budgets = tuple(dot(w, self.caps) for w in self.prices)
        self.lambdas = (F(1, 8), F(1, 4), F(1, 2))
        self.wealth = {(p, k): [F(1)] * len(self.lambdas)
                       for p in self.parents for k in range(len(self.prices))}
        self.seen = set()
        self.failed_contract = False
        self.invalid_record_seen = False

    def add(self, trial_id: str, candidate_charges, parent_charges,
            candidate_observations: tuple[str, ...], parent_observations):
        try:
            return self._add(trial_id, candidate_charges, parent_charges,
                             candidate_observations, parent_observations)
        except (ValueError, TypeError, KeyError):
            # Invalid/capped/partial measurements cannot be silently discarded
            # followed by a later positive claim from the same gate.
            self.invalid_record_seen = True
            raise

    def _add(self, trial_id, candidate_charges, parent_charges,
             candidate_observations, parent_observations):
        if type(trial_id) is not str or not trial_id or trial_id in self.seen:
            raise ValueError('new nonempty lifetime identity required')
        if set(parent_charges) != set(self.parents) or set(parent_observations) != set(self.parents):
            raise ValueError('every registered parent must be observed')
        candidate = complete_total(candidate_charges)
        parents = {p: complete_total(parent_charges[p]) for p in self.parents}
        for row in (candidate, *parents.values()):
            if len(row) != len(self.caps) or any(x > b for x, b in zip(row, self.caps)):
                raise ValueError('cost cap violated; no retrospective clipping')
        _observation(candidate_observations)
        for observation in parent_observations.values():
            _observation(observation)
        # Validate completely before changing state. A contract mismatch is
        # permanently retained and cannot be dropped as a cheap failed trial.
        mismatch = any(parent_observations[p] != candidate_observations for p in self.parents)
        self.seen.add(trial_id)
        self.failed_contract |= mismatch
        for p in self.parents:
            for k, price in enumerate(self.prices):
                gain = ((1 - self.improvement) * dot(price, parents[p])
                        - dot(price, candidate)) / self.budgets[k]
                if not -1 <= gain <= 1:
                    raise AssertionError('normalization invariant violated')
                self.wealth[p, k] = [v * (1 + lam * gain)
                                    for v, lam in zip(self.wealth[p, k], self.lambdas)]

    def report(self):
        count = len(self.wealth)
        threshold = F(count) / self.alpha
        evidence = {key: sum(values, F(0)) / len(values) for key, values in self.wealth.items()}
        crossed = all(value >= threshold for value in evidence.values())
        status = ('INVALID_EVALUATION_RECORD' if self.invalid_record_seen else
                  'CONTRACT_MISMATCH' if self.failed_contract else
                  'CONDITIONAL_IID_NET_BENEFIT_EVIDENCE' if self.seen and crossed else
                  'INSUFFICIENT_NET_BENEFIT_EVIDENCE')
        return {'terminal': status, 'lifetimes': len(self.seen), 'threshold': threshold,
                'e_values': evidence, 'production_authorized': False,
                'architecture_necessity_established': False,
                'sampling_independence_verified': False,
                'hidden_work_exclusion_verified': False}
