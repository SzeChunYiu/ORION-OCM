"""FC-5 exact microscopes, not a protected or whole-repository execution.

The numerical example is a source-derived rational projection of the disclosed
V4 lifecycle and V2 nuisance formulas at commit 858bb7f. It does not import the
repository implementation. Exact rational arithmetic slightly differs from its
floating arithmetic; the inequalities here have margins far above roundoff.
"""
from __future__ import annotations
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from gmi_closure_microscope import q, Exact


def compare_target_bounds(non_target: Exact, lower: Exact, witness: Exact) -> dict:
    """Conditional only: callers must separately justify the TARGET-CLASS lower bound.

    A supplied number is not evidence that the bound holds. Admissibility,
    matched accounting, target membership and bound provenance are external
    proof obligations, not established by this numerical function.
    """
    c, lo, upper = q(non_target), q(lower), q(witness)
    if lo > upper:
        raise ValueError('A valid lower bound cannot exceed an admissible witness upper bound')
    return {
        'beats_witness': c < upper,
        'beats_target_class_if_lower_bound_valid': c < lo,
        'ties_lower_bound': c == lo,
    }


def profile_value(seed: int, tag: str, lower: F, upper: F) -> F:
    h = int.from_bytes(sha256(f'{seed}:{tag}'.encode()).digest()[:8], 'big')
    return lower + (upper - lower) * F(h, 2**64 - 1)


def linear_candidate(low_rank: bool, verifier: bool) -> dict:
    """Three candidates inside the disclosed factor vocabulary, G1, scale 8.

    Width 1, affine capability, plus optional low_rank_revision/check gate.
    Positive linear admissibility is 1 in the cited score model for all three;
    this does NOT prove an actual executable program can realize the tags.
    """
    seed = 17
    reuse = profile_value(seed, 'linear:reuse', F(7, 10), F(27, 20))
    rank = profile_value(seed, 'linear:rank', F(1, 20), F(7, 20))
    checker = profile_value(seed, 'linear:check', F(3, 100), F(3, 10))
    n_caps = 1 + int(low_rank)
    tokens = 8 + n_caps + int(verifier)
    state = work = F(32)  # features = 4 * scale
    f = max(F(2, 25), min(F(1), 3 * rank)) if low_rank else F(1)
    cost = {
        'development_compute': (tokens + state * (F(1, 2) + F(3, 20) * n_caps)) / max(F(1, 4), reuse),
        'search_compute': F(tokens),
        'description_compiler_burden': (tokens + F(3, 20) * state) / max(F(1, 2), reuse),
        'state_storage': state * f,
        'serve_compute_latency': work,
        'update_retraining': state * f,
        'communication': F(3, 100) * work,
        'verification': F(3, 25) * work * checker if verifier else F(0),
        'human_external_intervention': F(0),
    }
    vector = {
        'state_scales_with': 'n_features', 'serve_scales_with': 'n_features',
        'update_locality': 'global', 'routing': 'none', 'sharing': 'shared',
        'retrieval': 'none', 'serve_iterations': 'one', 'stochastic_serve': False,
        'verifier_gated': verifier, 'external_authority': False,
    }
    return {'cost': sum(cost.values()), 'channels': cost, 'vector': vector,
            'cap_atoms': ('affine', 'low_rank_revision') if low_rank else ('affine',),
            'positive_linear_surrogate_score': F(1)}


def source_derived_receipt() -> dict:
    w = linear_candidate(False, False)
    t = linear_candidate(True, False)
    n = linear_candidate(True, True)
    return {
        'source_commit': '858bb7f6c67e4a17cc75027933b5d95346347c8b',
        'evidence_class': 'SOURCE_DERIVED_ALGEBRAIC_PROJECTION_NOT_REPOSITORY_EXECUTION',
        'development_seed': 17, 'grammar': 'G1_TENSOR_GRAPH', 'cell': 'w8',
        'canonical_target_witness_cost': float(w['cost']),
        'cheaper_same_target_cost': float(t['cost']),
        'non_target_cost_between_them': float(n['cost']),
        'exact_target_cost': str(t['cost']), 'exact_non_target_cost': str(n['cost']),
        'exact_witness_cost': str(w['cost']),
        'same_target_vector': w['vector'] == t['vector'],
        'competitor_has_different_vector': w['vector'] != n['vector'],
        'all_three_positive_surrogate_scores': [1, 1, 1],
        'strict_order_target_then_non_target_then_witness': t['cost'] < n['cost'] < w['cost'],
        'does_not_claim': ['actual run_cell returned these candidates',
                           'any of the 159 reported cells has been reclassified',
                           'the same-target candidate is globally optimal',
                           'these capability tags describe implemented machines'],
    }


def finite_bound_check() -> dict:
    checks = weak_inferences_refuted = 0
    # Two admissible target implementations, one admissible non-target.
    for w, t, n in product(range(6), repeat=3):
        optimum = min(w, t)
        comparison = compare_target_bounds(n, optimum, w)
        assert comparison['beats_target_class_if_lower_bound_valid'] == (n < w and n < t)
        weak_inferences_refuted += n < w and n >= optimum
        checks += 1
    return {'finite_class_bound_checks': checks, 'failures': 0,
            'beating_witness_without_beating_class': weak_inferences_refuted}
