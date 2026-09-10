"""Is the micro-Earth trajectory observable permutation invariant?

MULTISET enumeration is only a legitimate quotient of FULL enumeration if
permuting the initial population leaves the trajectory signature unchanged.
That is a claim about the frozen dynamics, so it gets tested, not assumed.

The frozen _social picks its donor with max(), whose tie-break is list order,
and _birthdeath iterates in list order under a population cap. Either can
break the symmetry. A single counterexample forbids the quotient.
"""
from __future__ import annotations

import itertools
import random

import worlds as W

HOLDS = "PERMUTATION_INVARIANT"
BREAKS = "PERMUTATION_SYMMETRY_BROKEN"
CANNOT = "CANNOT_CHECK_NO_PERMUTATIONS_TESTED"


def permutations_of(spec: W.WorldSpec, limit: int, rng: random.Random):
    pairs = list(zip(spec.genomes, spec.methods))
    seen = set()
    idx = list(range(len(pairs)))
    all_perms = itertools.permutations(idx)
    for k, perm in enumerate(all_perms):
        if k >= limit:
            break
        g = tuple(pairs[i][0] for i in perm)
        m = tuple(pairs[i][1] for i in perm)
        if (g, m) in seen:
            continue
        seen.add((g, m))
        yield W.WorldSpec(spec.n, g, m, spec.social, spec.leak,
                          spec.regime, spec.kernel_id, spec.seed)


def probe(me_mod, specs, ticks: int = W.DEFAULT_TICKS,
          perm_limit: int = 24, seed: int = 0) -> dict:
    rng = random.Random(seed)
    n_tested, n_perm, counterexamples = 0, 0, []
    for spec in specs:
        base = W.signature(me_mod, spec, ticks)
        n_tested += 1
        for alt in permutations_of(spec, perm_limit, rng):
            n_perm += 1
            sig = W.signature(me_mod, alt, ticks)
            if sig != base:
                if len(counterexamples) < 5:
                    counterexamples.append({
                        "base": spec.key(), "permuted": alt.key(),
                        "base_sig": base, "permuted_sig": sig})
                break
    if n_perm == 0:
        status = CANNOT
    elif counterexamples:
        status = BREAKS
    else:
        status = HOLDS
    return {
        "instrument": "permutation_invariance_probe",
        "n_base_specs": n_tested, "n_permutations": n_perm,
        "n_counterexamples": len(counterexamples),
        "counterexamples": counterexamples,
        "status": status,
        "multiset_quotient_licensed": status == HOLDS,
        "can_fail": True,
        "consequence": (
            "MULTISET enumeration is a sound quotient of FULL only when this "
            "row is PERMUTATION_INVARIANT. Otherwise the exhaustive claim must "
            "be made over FULL, at |cells|^n rather than C(|cells|+n-1, n)."),
    }
