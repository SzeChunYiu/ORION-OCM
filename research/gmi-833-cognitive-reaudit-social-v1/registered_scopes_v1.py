#!/usr/bin/env python3
"""Registered finite scopes for the #833 Section-M social/metacognitive re-audit.

This module contains **data construction only**. It holds no decision rule, no
threshold, no optimality computation and no verdict. Both the analytic route
(`cognitive_reaudit_social_v1.py`) and the independent brute-force oracle
(`route_b_oracle_v1.py`) consume these registered objects; neither route's
decision logic lives here, so importing this module from both does not make the
two routes dependent.

All numeric values are exact: `int` or `fractions.Fraction`. No float is
constructed anywhere in this file.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product
from typing import Dict, Iterator, List, Sequence, Tuple


# --------------------------------------------------------------------------
# exact-value guard
# --------------------------------------------------------------------------

def exact(value) -> F:
    """Return `value` as an exact Fraction, refusing floats and booleans."""
    if isinstance(value, bool):
        raise ValueError("booleans are not registered exact values")
    if isinstance(value, float):
        raise ValueError("floating point is forbidden in every registered value")
    if not isinstance(value, (int, F)):
        raise ValueError("registered values must be int or Fraction")
    return F(value)


def exact_vector(values: Sequence) -> Tuple[F, ...]:
    return tuple(exact(v) for v in values)


def is_probability_vector(values: Sequence[F]) -> bool:
    """Exact simplex membership: nonnegative and summing to exactly 1."""
    total = F(0)
    for v in values:
        if not isinstance(v, F):
            return False
        if v < 0:
            return False
        total += v
    return total == F(1)


# --------------------------------------------------------------------------
# deterministic integer PRNG for the registered nulls (no float, no `random`)
# --------------------------------------------------------------------------

class Lcg:
    """Registered 64-bit linear congruential generator over integers."""

    MOD = 2 ** 64
    MUL = 6364136223846793005
    INC = 1442695040888963407

    def __init__(self, seed: int) -> None:
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed must be an int")
        self.state = seed % self.MOD

    def next_int(self, bound: int) -> int:
        """Uniform-ish integer in [0, bound); deterministic and reproducible."""
        if bound <= 0:
            raise ValueError("bound must be positive")
        self.state = (self.MUL * self.state + self.INC) % self.MOD
        return (self.state >> 17) % bound

    def choice(self, items: Sequence):
        return items[self.next_int(len(items))]


# --------------------------------------------------------------------------
# MC-1: registered deliberation scopes
# --------------------------------------------------------------------------
#
# A deliberation scope is a finite rooted tree of depth `DELIB_DEPTH` with
# branching `DELIB_BRANCH`. A node is addressed by the tuple of outcome indices
# on the path from the root. `node_value[path]` is the exact value of the action
# the system would finally choose if it stopped at that node. `price[path]` is
# the exact charge of taking one further deliberation step from that node.
# `prob[path]` is the exact outcome distribution of that step.

DELIB_DEPTH = 2
DELIB_BRANCH = 2

DELIB_VALUES = (F(0), F(1), F(2))
DELIB_PRICES = (F(1), F(2))
DELIB_PROBS = (
    (F(1, 2), F(1, 2)),
    (F(1, 3), F(2, 3)),
    (F(2, 3), F(1, 3)),
)


def delib_paths(depth: int = DELIB_DEPTH, branch: int = DELIB_BRANCH) -> List[Tuple[int, ...]]:
    """All node paths, root first, in a fixed deterministic order."""
    out = []  # type: List[Tuple[int, ...]]
    for level in range(depth + 1):
        for combo in product(range(branch), repeat=level):
            out.append(tuple(combo))
    return out


def delib_decision_paths(depth: int = DELIB_DEPTH, branch: int = DELIB_BRANCH) -> List[Tuple[int, ...]]:
    return [p for p in delib_paths(depth, branch) if len(p) < depth]


def iter_deliberation_scopes() -> Iterator[Dict[str, object]]:
    """Exhaustive registered deliberation-scope census.

    The root value is normalized to 0: registered values are the *improvement*
    of the finally chosen action relative to the system's current best action,
    so the normalization is a definition, not a restriction.
    """
    paths = delib_paths()
    non_root = [p for p in paths if p]
    decisions = delib_decision_paths()
    for values in product(DELIB_VALUES, repeat=len(non_root)):
        node_value = {(): F(0)}  # type: Dict[Tuple[int, ...], F]
        for path, val in zip(non_root, values):
            node_value[path] = val
        for root_price in DELIB_PRICES:
            for deep_price in DELIB_PRICES:
                price = {}  # type: Dict[Tuple[int, ...], F]
                for path in decisions:
                    price[path] = root_price if not path else deep_price
                for probs in DELIB_PROBS:
                    yield {
                        "node_value": node_value,
                        "price": price,
                        "prob": probs,
                        "depth": DELIB_DEPTH,
                        "branch": DELIB_BRANCH,
                    }


def random_deliberation_scope(rng: Lcg) -> Dict[str, object]:
    paths = delib_paths()
    decisions = delib_decision_paths()
    node_value = {(): F(0)}  # type: Dict[Tuple[int, ...], F]
    for path in paths:
        if path:
            node_value[path] = rng.choice(DELIB_VALUES)
    price = {}  # type: Dict[Tuple[int, ...], F]
    for path in decisions:
        price[path] = rng.choice(DELIB_PRICES)
    return {
        "node_value": node_value,
        "price": price,
        "prob": rng.choice(DELIB_PROBS),
        "depth": DELIB_DEPTH,
        "branch": DELIB_BRANCH,
    }


# The small registered instance set used for the exhaustive fixed-schedule
# aliasing census. Keeping it small is what makes brute-force enumeration over
# *all* fixed schedules (|traces| ** |instances|) exhaustive rather than sampled.

ALIASING_INSTANCE_LABELS = ("i0", "i1", "i2")


def aliasing_instance_scopes() -> Dict[str, Dict[str, object]]:
    """Three registered deliberation scopes, one per aliasing instance label."""
    census = iter_deliberation_scopes()
    picked = {}  # type: Dict[str, Dict[str, object]]
    wanted = {0: "i0", 2917: "i1", 6001: "i2"}
    for index, scope in enumerate(census):
        if index in wanted:
            picked[wanted[index]] = scope
        if len(picked) == len(wanted):
            break
    if len(picked) != len(ALIASING_INSTANCE_LABELS):
        raise RuntimeError("registered aliasing instance set is incomplete")
    return picked


# --------------------------------------------------------------------------
# MC-2: registered social-cognition ecologies
# --------------------------------------------------------------------------
#
# `prior[h]` is the exact probability of the other agent's hidden state `h`.
# `channel[h]` is the block id of the other agent's *observed action history*:
# two hidden states sharing a block are indistinguishable to a behaviour-reader.
# `score[h][u]` is the focal system's exact payoff.

SOCIAL_PRIORS_2 = (
    (F(1, 2), F(1, 2)),
    (F(1, 3), F(2, 3)),
    (F(3, 4), F(1, 4)),
    (F(1, 5), F(4, 5)),
)
SOCIAL_PRIORS_3 = (
    (F(1, 3), F(1, 3), F(1, 3)),
    (F(1, 2), F(1, 4), F(1, 4)),
    (F(1, 6), F(1, 3), F(1, 2)),
)


def set_partitions(n: int) -> List[Tuple[int, ...]]:
    """All set partitions of {0..n-1} in restricted-growth-string form."""
    if n <= 0:
        return [()]
    out = []  # type: List[Tuple[int, ...]]

    def grow(prefix: Tuple[int, ...], used: int) -> None:
        if len(prefix) == n:
            out.append(prefix)
            return
        for block in range(used + 1):
            grow(prefix + (block,), max(used, block + 1))

    grow((0,), 1)
    return out


def _score_tables(n_states: int, n_actions: int, levels: Tuple[F, ...]) -> Iterator[Tuple[Tuple[F, ...], ...]]:
    flat_len = n_states * n_actions
    for flat in product(levels, repeat=flat_len):
        yield tuple(
            tuple(flat[h * n_actions + u] for u in range(n_actions))
            for h in range(n_states)
        )


SOCIAL_FAMILIES = (
    ("A", 2, 2, (F(0), F(1), F(2)), SOCIAL_PRIORS_2),
    ("B", 3, 2, (F(0), F(1), F(2)), SOCIAL_PRIORS_3),
    ("C", 3, 3, (F(0), F(1)), SOCIAL_PRIORS_3),
)


def iter_social_ecologies() -> Iterator[Dict[str, object]]:
    for family, n_states, n_actions, levels, priors in SOCIAL_FAMILIES:
        channels = set_partitions(n_states)
        for score in _score_tables(n_states, n_actions, levels):
            for channel in channels:
                for prior in priors:
                    yield {
                        "family": family,
                        "n_states": n_states,
                        "n_actions": n_actions,
                        "prior": prior,
                        "channel": channel,
                        "score": score,
                    }


def random_social_ecology(rng: Lcg) -> Dict[str, object]:
    family, n_states, n_actions, levels, priors = rng.choice(SOCIAL_FAMILIES)
    channels = set_partitions(n_states)
    score = tuple(
        tuple(rng.choice(levels) for _ in range(n_actions))
        for _ in range(n_states)
    )
    return {
        "family": family,
        "n_states": n_states,
        "n_actions": n_actions,
        "prior": rng.choice(priors),
        "channel": rng.choice(channels),
        "score": score,
    }


# --------------------------------------------------------------------------
# MC-3: registered communication ecologies
# --------------------------------------------------------------------------

CHANNEL_PRICES = (F(0), F(1, 4), F(1, 2), F(1), F(2))

COMM_FAMILIES = (
    ("A", 3, 2, (F(0), F(1), F(2)), SOCIAL_PRIORS_3),
    ("B", 4, 2, (F(0), F(1)), (
        (F(1, 4), F(1, 4), F(1, 4), F(1, 4)),
        (F(1, 2), F(1, 6), F(1, 6), F(1, 6)),
    )),
)


def iter_communication_ecologies() -> Iterator[Dict[str, object]]:
    for family, n_states, n_actions, levels, priors in COMM_FAMILIES:
        partitions = set_partitions(n_states)
        for score in _score_tables(n_states, n_actions, levels):
            for partition in partitions:
                for prior in priors:
                    for price in CHANNEL_PRICES:
                        yield {
                            "family": family,
                            "n_states": n_states,
                            "n_actions": n_actions,
                            "prior": prior,
                            "partition": partition,
                            "score": score,
                            "price": price,
                        }


def random_communication_ecology(rng: Lcg) -> Dict[str, object]:
    family, n_states, n_actions, levels, priors = rng.choice(COMM_FAMILIES)
    partitions = set_partitions(n_states)
    score = tuple(
        tuple(rng.choice(levels) for _ in range(n_actions))
        for _ in range(n_states)
    )
    return {
        "family": family,
        "n_states": n_states,
        "n_actions": n_actions,
        "prior": rng.choice(priors),
        "partition": rng.choice(partitions),
        "score": score,
        "price": rng.choice(CHANNEL_PRICES),
    }


# --------------------------------------------------------------------------
# MC-4: registered imitation/teaching instances
# --------------------------------------------------------------------------
#
# `learner_control`  : learner acquisition charge with NO demonstration, same condition.
# `learner_demo`     : learner acquisition charge WITH the demonstration, same condition.
# `demonstrator`     : the demonstrator's own charge for producing the demonstration.
# `learners`         : how many learners the demonstration serves.
# `naive_pre`        : the learner charge observed in an EARLIER, different condition;
#                      a pre/post observer compares this against `learner_demo`.

TEACH_COSTS = (F(0), F(1, 2), F(1), F(3, 2), F(2), F(3))
TEACH_DEMONSTRATOR = (F(0), F(1, 2), F(1), F(3, 2), F(2), F(3))
TEACH_LEARNERS = (1, 2, 3, 5, 8)


def iter_teaching_instances() -> Iterator[Dict[str, object]]:
    for control in TEACH_COSTS:
        for demo in TEACH_COSTS:
            for demonstrator in TEACH_DEMONSTRATOR:
                for learners in TEACH_LEARNERS:
                    yield {
                        "learner_control": control,
                        "learner_demo": demo,
                        "demonstrator": demonstrator,
                        "learners": learners,
                    }


def random_concurrent_cause_instance(rng: Lcg) -> Dict[str, object]:
    """A registered hostile instance: the learner charge falls relative to an
    earlier condition because of a registered unrelated concurrent cause, while
    the demonstration itself is causally inert (control == demo at the same
    condition)."""
    demo = rng.choice((F(0), F(1, 2), F(1), F(3, 2)))
    drop = rng.choice((F(1, 2), F(1), F(3, 2), F(2)))
    demonstrator = rng.choice(TEACH_DEMONSTRATOR)
    return {
        "learner_control": demo,          # the cause lowers the control arm identically
        "learner_demo": demo,             # demonstration adds nothing
        "demonstrator": demonstrator,
        "learners": rng.choice(TEACH_LEARNERS),
        "naive_pre": demo + drop,         # the earlier, different condition
    }


# --------------------------------------------------------------------------
# MC-5: registered cultural-transmission trajectories
# --------------------------------------------------------------------------

CULTURE_FIDELITY = (
    F(0), F(1, 8), F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(7, 8), F(1),
)
CULTURE_INNOVATION = (F(0), F(1, 4), F(1, 2), F(1), F(2))
CULTURE_START = (F(0), F(1, 4), F(1, 2), F(1), F(2), F(4))
CULTURE_GENERATIONS = 8

CULTURE_UNIT_COSTS = (F(1, 2), F(1), F(2))


def iter_culture_triples() -> Iterator[Tuple[F, F, F]]:
    for phi in CULTURE_FIDELITY:
        for g in CULTURE_INNOVATION:
            for a0 in CULTURE_START:
                yield (phi, g, a0)


def iter_culture_cost_vectors() -> Iterator[Tuple[F, F, F]]:
    """(transmit_unit_cost t, rederive_unit_cost r, innovate_unit_cost k)."""
    for t in CULTURE_UNIT_COSTS:
        for r in CULTURE_UNIT_COSTS:
            for k in CULTURE_UNIT_COSTS:
                yield (t, r, k)


def random_culture_triple(rng: Lcg) -> Tuple[F, F, F]:
    return (
        rng.choice(CULTURE_FIDELITY),
        rng.choice(CULTURE_INNOVATION),
        rng.choice(CULTURE_START),
    )
