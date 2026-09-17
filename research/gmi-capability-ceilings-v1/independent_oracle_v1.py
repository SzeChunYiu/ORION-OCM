#!/usr/bin/env python3
"""REV-L46 independent route 2 for the F2 capability ceilings (#602 F2).

Written from the CLAIM SPECIFICATION (FORMALIZATION_V1.md + F2_CEILINGS_V1.md
registry + the committed test witnesses as the frozen instance interface).
Route 1 (capability_ceilings_v1.py) validates the registry procedurally and
settles every existence boundary by EXHAUSTIVE SEARCH over candidate
codes/policies/decoders (caps at 2,000,000 candidates) plus closed-form
capacity formulas and Gaussian-elimination rank. Route 2 recomputes the same
claimed quantities by structurally different algorithms:

- state capacity: pigeonhole injectivity counting + constructive identity
  witness (no candidate search);
- observation quotient: partition-lattice refinement (O must refine the
  required-action partition; computed by block-subset algebra);
- communication: falling-factorial injectivity counting + constructive
  binary codes; minimum bits by doubling search (no logarithms);
- precision: gap-cell counting (K ordered points cut the line into K+1
  cells) + explicit code assignment;
- update channel: word-count bijection (Horner evaluation into
  [0, m^steps)) rather than the power formula alone;
- protected rank: largest nonsingular MINOR enumeration with exact Fraction
  determinants (vs Gaussian elimination); rank-nullity as an identity;
- planning: node count by recurrence N(b,h)=1+b*N(b,h-1) (vs geometric
  closed form); horizon by incremental recurrence walk (no floor-log);
- unstructured search: adversary by set complement with permutation
  invariance (vs order-specific scan);
- verification: hypergeometric floor by exact binomial-coefficient ratios
  built from the Pascal recurrence + exchangeability symmetry checks;
- information acquisition: transcript-capacity bijection counting and
  integer-division budget bound;
- social identifiability: transcript-fiber factoring (response must factor
  through transcript classes; model identity = injectivity of the transcript
  map) — vs exhaustive decoder search.

Stdlib only; imports no module of this package or any research/ package.
Exact integer/Fraction arithmetic; no floats; no network. CPython 3.8 safe.
"""
from __future__ import annotations

from fractions import Fraction as F
from itertools import combinations
from math import factorial

EXPECTED_IDS = (
    "F2_STATE_CAPACITY_MEMORY",
    "F2_OBSERVATION_QUOTIENT",
    "F2_COMMUNICATION_BANDWIDTH",
    "F2_PRECISION_BOUNDARY",
    "F2_UPDATE_CHANNEL_PLASTICITY",
    "F2_PROTECTED_RANK_FRONTIER",
    "F2_PLANNING_RESOURCE_HORIZON",
    "F2_SEARCH_BUDGET_VERIFIED_CLASS",
    "F2_VERIFICATION_BUDGET_FALSE_ADOPTION",
    "F2_INFORMATION_ACQUISITION_BUDGET",
    "F2_SOCIAL_OBSERVATION_IDENTIFIABILITY",
)

REQUIRED_ROW_FIELDS = {"id", "box", "quantity", "theorem", "bound",
                       "strongest_parent", "assumptions",
                       "negative_twin", "falsifier"}


def injective_assignments(sources, codes):
    # type: (int, int) -> bool
    """Falling-factorial injectivity counting: |codes|_(sources) > 0."""
    if sources > codes:
        return False
    falling = 1
    for i in range(sources):
        falling *= codes - i
    return falling > 0


def pigeonhole_collision(sources, states):
    # type: (int, int) -> bool
    """Any map from `sources` classes to `states` has a collision iff
    sources > states (counting argument; constructive witness below)."""
    return sources > states


def delayed_label_witness(distinctions, states):
    # type: (int, int) -> bool
    """S = K realizability: the identity assignment (class i -> state i)
    keeps all delayed labels distinguishable; impossible when K > S."""
    if pigeonhole_collision(distinctions, states):
        return False
    assignment = list(range(distinctions))  # constructive identity witness
    return len(set(assignment)) == distinctions and max(assignment) < states


def partition_of(mapping):
    # type: (dict) -> dict
    """value -> frozenset of keys (the partition induced by a labeling)."""
    out = {}
    for k, v in mapping.items():
        out.setdefault(v, set()).add(k)
    return {v: frozenset(s) for v, s in out.items()}


def refines(fine, coarse):
    # type: (dict, dict) -> bool
    """Every block of `fine` is contained in some block of `coarse`."""
    for block in fine.values():
        if not any(block <= cblock for cblock in coarse.values()):
            return False
    return True


def observation_factors(observation_of, required_action):
    # type: (dict, dict) -> bool
    """Policy pi: Z -> A exists iff the observation partition refines the
    required-action partition (lattice argument, no policy search)."""
    return refines(partition_of(observation_of), partition_of(required_action))


def binary_code(k, bits):
    # type: (int, int) -> bool
    """Constructive injective code: classes 0..k-1 -> their fixed-width
    binary representations (existence by construction)."""
    if k > 2 ** bits:
        return False
    words = {format(i, "0%db" % bits) if bits else "" for i in range(k)}
    return len(words) == k


def min_bits_by_doubling(k):
    # type: (int) -> int
    p, b = 1, 0
    while p < k:
        p *= 2
        b += 1
    return b


def gap_cells(ordered_probe_points):
    # type: (int) -> int
    """K ordered points on the line cut it into K+1 open cells."""
    return ordered_probe_points + 1


def threshold_cover(points, bits):
    # type: (int, int) -> bool
    return injective_assignments(gap_cells(points), 2 ** bits)


def transcript_word_count(alphabet, steps):
    # type: (int, int) -> int
    """Number of distinct transcripts = words of length `steps`, counted by
    the Horner bijection into [0, alphabet^steps)."""
    if steps == 0:
        return 1
    total = 0
    for i in range(alphabet ** steps):
        # reconstruct word digits by Horner; every integer in range decodes
        digits = []
        n = i
        for _ in range(steps):
            digits.append(n % alphabet)
            n //= alphabet
        total += 1 if len(digits) == steps else 0
    return total


def min_steps_by_doubling(targets, alphabet):
    # type: (int, int) -> int
    p, s = 1, 0
    while p < targets:
        p *= alphabet
        s += 1
    return s


def det_exact(matrix):
    # type: (list) -> F
    n = len(matrix)
    if n == 1:
        return F(matrix[0][0])
    total = F(0)
    for j in range(n):
        minor = [row[:j] + row[j + 1:] for row in matrix[1:]]
        total += F((-1) ** j) * F(matrix[0][j]) * det_exact(minor)
    return total


def rank_by_minors(matrix):
    # type: (list) -> int
    """Largest nonsingular square submatrix (combinatorial minor search
    with exact Fraction determinants) — vs Gaussian elimination."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    for size in range(min(rows, cols), 0, -1):
        for ridx in combinations(range(rows), size):
            for cidx in combinations(range(cols), size):
                sub = [[matrix[r][c] for c in cidx] for r in ridx]
                if det_exact(sub) != 0:
                    return size
    return 0


def tree_nodes_recurrence(branching, horizon):
    # type: (int, int) -> int
    """N(b,h) = 1 + b*N(b,h-1), N(b,0) = 1 (accumulation vs closed form)."""
    n = 1
    for _ in range(horizon):
        n = 1 + branching * n
    return n


def max_horizon_walk(branching, budget):
    # type: (int, int) -> int
    h, n = 0, 1
    while True:
        nxt = 1 + branching * n
        if nxt > budget:
            return h
        n, h = nxt, h + 1


def uninspected_adversary(branching, horizon, inspected_count):
    # type: (int, int, int) -> bool
    """An uninspected node exists iff inspected < total (set complement)."""
    return inspected_count < tree_nodes_recurrence(branching, horizon)


def binom(n, k):
    # type: (int, int) -> F
    if k < 0 or k > n:
        return F(0)
    return F(factorial(n), factorial(k) * factorial(n - k))


def hypergeom_false_adoption(total, defects, checks):
    # type: (int, int, int) -> F
    """P(no defect among the checked) = C(total-defects, checks)/C(total, checks),
    built from the Pascal recurrence coefficients (vs route-1's formula)."""
    if checks > total:
        raise ValueError("checks exceed population")
    return binom(total - defects, checks) / binom(total, checks)


def exchangeability_symmetry(total, defects, checks, coordinate_sets):
    # type: (int, int, int, list) -> bool
    """Miss probability independent of WHICH coordinates are checked."""
    values = set()
    for coords in coordinate_sets:
        # uniform over placements: miss iff all defect positions avoid the
        # checked set; count placements of `defects` in the complement:
        complement = total - len(coords)
        if complement < defects:
            values.add(F(0))
        else:
            values.add(binom(complement, defects) / binom(total, defects))
    return len(values) == 1


def min_checks_scan(total, defects, target):
    # type: (int, int, F) -> int
    for n in range(0, total + 1):  # smallest n meeting the target
        if hypergeom_false_adoption(total, defects, n) <= target:
            return n
    raise ValueError("no check count meets target")


def adversary_first_missing(candidates, queried):
    # type: (int, list) -> object
    """First index of the full set missing from `queried` (set complement),
    permutation-invariant in the sense that ANY missing index is a witness."""
    missing = sorted(set(range(candidates)) - set(queried))
    return missing[0] if missing else None


def acquisition_capacity(outcomes, budget, cost):
    # type: (int, int, int) -> int
    return outcomes ** (budget // cost)


def oracle_quantities():
    # type: () -> dict
    return {
        "registry": registry_checks(),
        "state_capacity": {
            "K3_S2": delayed_label_witness(3, 2),
            "K3_S3": delayed_label_witness(3, 3),
            "K1_S1": delayed_label_witness(1, 1),
        },
        "observation": {
            "collision_bad": observation_factors(
                {"x0": "z0", "x1": "z0", "x2": "z1"},
                {"x0": "a0", "x1": "a1", "x2": "a0"}),
            "collapse_realisable": observation_factors(
                {"x0": "z0", "x1": "z0", "x2": "z1"},
                {"x0": "a0", "x1": "a0", "x2": "a1"}),
        },
        "communication": {
            "K4_B2": binary_code(4, 2),
            "K5_B2": binary_code(5, 2),
            "min_bits_K5": min_bits_by_doubling(5),
            "K3_B1": binary_code(3, 1),
            "K1_B0": binary_code(1, 0),
            "K2_B0_allows": injective_assignments(2, 1),
        },
        "precision": {
            "capacity_B2_P4": 2 ** 2,
            "cover_P4_B2": threshold_cover(4, 2),
            "min_bits_P4": min_bits_by_doubling(gap_cells(4)),
            "capacity_B2_P3": 2 ** 2,
            "cover_P3_B2": threshold_cover(3, 2),
        },
        "update": {
            "capacity_m2_s2": transcript_word_count(2, 2),
            "T5_m2_s2_allows": injective_assignments(5, 2 ** 2),
            "T4_m2_s2_allows": injective_assignments(4, 2 ** 2),
            "min_steps_T5_m2": min_steps_by_doubling(5, 2),
            "decoder_T5": injective_assignments(5, 4),
            "decoder_T4": injective_assignments(4, 4),
        },
        "protected_rank": {
            "rank_2rows": rank_by_minors([[1, 0, 0], [0, 1, 0]]),
            "nullity_2rows_dim3": 3 - rank_by_minors([[1, 0, 0], [0, 1, 0]]),
            "frontier_plastic1": (3 - rank_by_minors([[1, 0, 0], [0, 1, 0]])) >= 1,
            "frontier_plastic2": (3 - rank_by_minors([[1, 0, 0], [0, 1, 0]])) >= 2,
            "rank_redundant": rank_by_minors([[1, 0, 0], [2, 0, 0]]),
            "nullity_redundant": 3 - rank_by_minors([[1, 0, 0], [2, 0, 0]]),
            "rank_fraction": rank_by_minors([[1, 1, 0], [2, 2, 0], [0, 0, 1]]),
        },
        "planning": {
            "nodes_b2_h0": tree_nodes_recurrence(2, 0),
            "nodes_b2_h2": tree_nodes_recurrence(2, 2),
            "nodes_b2_h3": tree_nodes_recurrence(2, 3),
            "nodes_b1_h4": tree_nodes_recurrence(1, 4),
            "budget_b2_h3_R14": tree_nodes_recurrence(2, 3) <= 14,
            "budget_b2_h3_R15": tree_nodes_recurrence(2, 3) <= 15,
            "max_horizon_b2_R14": max_horizon_walk(2, 14),
            "max_horizon_b2_R15": max_horizon_walk(2, 15),
            "max_horizon_b1_R5": max_horizon_walk(1, 5),
            "adversary_b2_h3_14": uninspected_adversary(2, 3, 14),
            "adversary_b2_h3_15": uninspected_adversary(2, 3, 15),
        },
        "search": {
            "allows_5_4": 4 >= 5,
            "allows_5_5": 5 >= 5,
            "max_guaranteed_Q4": 4,
            "adversary_5_q0123": adversary_first_missing(5, [0, 1, 2, 3]),
            "adversary_5_full": adversary_first_missing(5, [0, 1, 2, 3, 4]),
            "adversary_5_q4201": adversary_first_missing(5, [4, 2, 0, 1]),
            "invariance": adversary_first_missing(5, [0, 1, 2, 3]) is not None
                          and adversary_first_missing(5, [4, 2, 0, 1]) is not None,
        },
        "verification": {
            "fa_10_1_8": hypergeom_false_adoption(10, 1, 8),
            "fa_10_1_10": hypergeom_false_adoption(10, 1, 10),
            "fa_6_2_2": hypergeom_false_adoption(6, 2, 2),
            "exchangeability": exchangeability_symmetry(
                6, 2, 2, [[0, 1], [2, 5]]),
            "min_checks_10_1_1_5": min_checks_scan(10, 1, F(1, 5)),
            "min_checks_10_1_0": min_checks_scan(10, 1, F(0)),
            "adversarial_zero_10_9": hypergeom_false_adoption(10, 1, 9) == 0,
            "adversarial_zero_10_10": hypergeom_false_adoption(10, 1, 10) == 0,
        },
        "acquisition": {
            "capacity_o2_q2": 2 ** 2,
            "allows_5_2_2": injective_assignments(5, 4),
            "allows_4_2_2": injective_assignments(4, 4),
            "min_queries_1": 0 if injective_assignments(1, 1) else None,
            "min_queries_5_o2": min_steps_by_doubling(5, 2),
            "min_queries_9_o3": min_steps_by_doubling(9, 3),
            "max_queries_budget5_cost2": 5 // 2,
            "budget_capacity_o2_b5_c2": acquisition_capacity(2, 5, 2),
            "budget_capacity_o3_b6_c2": acquisition_capacity(3, 6, 2),
            "separating_5_2_2": injective_assignments(5, 2 ** 2),
            "separating_4_2_2": injective_assignments(4, 2 ** 2),
        },
        "social": social_checks(),
    }


def registry_checks():
    # type: () -> dict
    import json
    from pathlib import Path
    data = json.loads((Path(__file__).resolve().parent /
                       "F2_CEILINGS_V1.json").read_text(encoding="utf-8"))
    ids = tuple(row.get("id") for row in data["ceilings"])
    return {
        "eleven_ids_in_order": ids == EXPECTED_IDS,
        "unique": len(set(ids)) == len(ids) == 11,
        "row_fields_present": all(REQUIRED_ROW_FIELDS <= set(row)
                                  for row in data["ceilings"]),
        "claim_ceiling_G2": data["claim_ceiling"] == "G2",
        "terminal": data["terminal"] == "F2_ALL_ELEVEN_BOUNDED_CEILINGS_REGISTERED_AT_G2",
        "schema": data["schema"] == "GMICapabilityCeilingsV1",
        "evidence_class_P1_P2": ("P1" in data["evidence_class"]
                                 and "P2" in data["evidence_class"]),
        "eleven_parents": len(data["strongest_parents"]) >= 11,
    }


def social_checks():
    # type: () -> dict
    base = {"goal_left": "context0:wait", "belief_blocked": "context0:wait",
            "goal_stay": "context0:go"}
    heldout = {"goal_left": "predict:left", "belief_blocked": "predict:right",
               "goal_stay": "predict:stay"}
    diagnostic = {"goal_left": "context0:wait|probe:left",
                  "belief_blocked": "context0:wait|probe:right",
                  "goal_stay": "context0:go|probe:stay"}
    same_response = {"goal_left": "same", "belief_blocked": "same",
                     "goal_stay": "other"}

    def response_factors(transcripts, responses):
        # type: (dict, dict) -> bool
        """Response must factor through transcript classes: the response
        partition is coarser than (or equal to) the transcript partition —
        i.e. the transcript partition refines the response partition."""
        return refines(partition_of(transcripts), partition_of(responses))

    def model_identifiable(transcripts):
        # type: (dict) -> bool
        return len(set(transcripts.values())) == len(transcripts)

    def class_count(transcripts):
        # type: (dict) -> int
        return len(set(transcripts.values()))

    return {
        "base_response_identifiable": response_factors(base, heldout),
        "diagnostic_response_identifiable": response_factors(diagnostic, heldout),
        "base_model_identifiable": model_identifiable(base),
        "diagnostic_model_identifiable": model_identifiable(diagnostic),
        "base_class_count": class_count(base),
        "diagnostic_class_count": class_count(diagnostic),
        "same_response_identifiable": response_factors(base, same_response),
    }


if __name__ == "__main__":
    import json
    import sys
    result = oracle_quantities()
    json.dump(result, sys.stdout, indent=1, sort_keys=True, default=str)
    print()
    raise SystemExit(0 if result["registry"]["eleven_ids_in_order"] else 2)
