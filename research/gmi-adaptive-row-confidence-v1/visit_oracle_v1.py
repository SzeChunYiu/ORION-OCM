"""Exact finite Bernoulli path oracles, separate from concentration arithmetic."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product


def prefix_failure(p, horizon, epsilons):
    survivors, failed = {0: F(1)}, F(0)
    for n in range(1, horizon+1):
        nxt = defaultdict(F)
        for ones, mass in survivors.items():
            for bit, chance in ((0, 1-p), (1, p)):
                count, weight = ones+bit, mass*chance
                if abs(F(count, n)-p) > epsilons[n]:
                    failed += weight
                else:
                    nxt[count] += weight
        survivors = nxt
    if failed+sum(survivors.values()) != 1:
        raise ValueError("prefix law lost probability mass")
    return failed


def full_bitstrings(p, horizon, epsilons):
    failed = F(0)
    for bits in product((0, 1), repeat=horizon):
        mass = p**sum(bits)*(1-p)**(horizon-sum(bits))
        if any(abs(F(sum(bits[:n]), n)-p) > epsilons[n] for n in range(1, horizon+1)):
            failed += mass
    return failed


def choose_row(state, rule):
    n0, k0, n1, k1 = state
    if rule == "stop_on_first_one" and (k0+k1):
        return None
    if not n0:
        return 0
    if not n1:
        return 1
    if rule in ("alternate", "stop_on_first_one"):
        return int(n0 > n1)
    if rule == "higher_mean":
        return int(F(k1, n1) > F(k0, n0))
    if rule == "lower_mean":
        return int(F(k1, n1) < F(k0, n0))
    raise ValueError("unregistered sampler")


def adaptive_failure(laws, horizon, epsilons, rule):
    survivors = {(0, 0, 0, 0): F(1)}
    failed, stopped, states = F(0), F(0), 0
    for _ in range(horizon):
        nxt = defaultdict(F)
        for state, mass in survivors.items():
            states += 1
            r = choose_row(state, rule)
            if r is None:
                stopped += mass
                continue
            for bit, chance in ((0, 1-laws[r]), (1, laws[r])):
                new = list(state)
                new[2*r] += 1
                new[2*r+1] += bit
                weight = mass*chance
                n, k = new[2*r:2*r+2]
                if abs(F(k, n)-laws[r]) > epsilons[r][n]:
                    failed += weight
                else:
                    nxt[tuple(new)] += weight
        survivors = nxt
    if failed+stopped+sum(survivors.values()) != 1:
        raise ValueError("adaptive law lost probability mass")
    return failed, states


def optional_peek():
    p = F(3, 5)
    direct, repaired = F(0), F(0)
    for bits in product((0, 1), repeat=3):
        mass = p**sum(bits)*(1-p)**(3-sum(bits))
        if bits[:2] == (0, 0):
            direct += mass*(p > F(1, 2))
            repaired += mass*(p > F(2, 3))
        elif bits == (1, 1, 1):
            direct += mass*(p < F(5, 8))
            repaired += mass*(p < F(1, 2))
    return {"p": p, "fixed_look_nominal_error": F(1, 4),
            "optional_failure": direct, "repair_failure_at_p": repaired,
            "repair_uniform_union_upper": F(1, 9)+F(1, 8)}
