#!/usr/bin/env python3
"""Route A: exact capability predictor C_hat = F(M,E,R,H,D,U) for #833 Section K.

Frozen scope: FREEZE_V1.md, TAXONOMY_V1.md, SCOPE_V1.md.
Exact rational arithmetic only. Stdlib only. Replays identically under -O.
"""

from __future__ import annotations

import ast
import json
from fractions import Fraction
from hashlib import sha1
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent

CLAIM_CEILING = (
    "GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_"
    "UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE"
)

FORBIDDEN_PROMOTIONS = (
    "CALIBRATION_FROM_FEASIBILITY_ALONE",
    "CAPABILITY_PREDICTOR_EMPIRICALLY_VALIDATED",
    "COMPLETE_GMI",
    "EMPIRICAL_CALIBRATION_ERROR_MEASURED",
    "HELD_OUT_PREDICTOR_VALIDATION",
    "KNOWN_ARCHITECTURE_VALIDATION",
    "ONTOLOGICAL_COMPLETENESS",
    "OOD_FAILURE_MEASURED",
    "QUALITATIVE_FAILURE_PREDICTED_BEFORE_EVALUATION",
    "QUANTITATIVE_RESOURCE_CURVE_PREDICTION",
    "REAL_SYSTEM_CAPABILITY_VALIDATION",
    "UNIVERSAL_CAPABILITY_PREDICTION",
    "UNIVERSAL_UNCERTAINTY_CALIBRATION",
)

FREEZE_COMMIT = "f09288d920ea085e984a2f7ba191c777ee1871a2"
SOURCE_MAIN = "c70dd24eeade46a3afe8322c1a0e0c16a648311e"

PARENT_PINS = (
    ("foundation", "research/gmi-833-foundation-v1/RESULT_V1.json",
     "c0c574c4ec6e237d5fdafa694eac131399625a70", "terminal",
     "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE"),
    ("morphcap", "research/gmi-833-morphcap-v1/RESULT_V1.json",
     "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a", "claim_ceiling",
     "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE"),
    ("global_uncertainty", "research/gmi-833-global-uncertainty-v1/RESULT_V1.json",
     "9ab16cf59087214e093ace3b18c6d08fc79ab871", "claim_ceiling",
     "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"),
    ("capability_abstention", "research/gmi-833-capability-abstention-v1/RESULT_V1.json",
     "d0616a04cde834f2329e376b395366981a1c7893", "claim_ceiling",
     "GMI_833_CAPABILITY_IDENTIFICATION_ABSTENTION_AT_REGISTERED_FINITE_SCOPE"),
    ("capability_bounds", "research/gmi-833-capability-bounds-interactions-v1/RESULT_V1.json",
     "7ff80bab4a0b9e967e02cc6943bbe8828e3acea0", "claim_ceiling",
     "GMI_833_FINITE_CAPABILITY_BOUNDS_SYNERGY_AND_INTERFERENCE_AT_REGISTERED_SCOPE"),
    ("global_vs_reachable", "research/gmi-833-global-vs-reachable-morphology-v1/RESULT_V1.json",
     "37a0dda56649c02de1dd733b20a1266d481a3d30", "claim_ceiling",
     "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE"),
    ("finite_search_budget", "research/gmi-833-finite-search-budget-morphology-v1/RESULT_V1.json",
     "4ea315e651475cc8afcc39860a0d2ac621e9f571", "claim_ceiling",
     "GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE"),
    ("axiom_core", "research/gmi-833-axiom-core-v1/RESULT_V1.json",
     "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9", "claim_ceiling",
     "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"),
)

HISTORICAL_NON_AUTHORITY = (
    "research/gmi-capability-predictor-v1",
    "research/gmi-capability-predictor-dev-v1",
    "research/gmi-capability-calibration-v2",
)

# --------------------------------------------------------------------------
# Frozen registered universe Sigma_1 (SCOPE_V1.md section 1)
# --------------------------------------------------------------------------

MU = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
RHO_DIM = 14
UNSATISFIED = "UNSATISFIED"

# realization tuple layout
F_A, F_B, F_C, F_K, F_RHO, F_DEV, F_OBS = 0, 1, 2, 3, 4, 5, 6


def popcount(n):
    total = 0
    while n:
        total += n & 1
        n >>= 1
    return total


def build_universe():
    """Deterministic generator of the frozen realization universe."""
    raw = []
    for a in range(8):
        for b in range(2):
            for c in range(2):
                k = (a + b) % 3
                rho = [0] * RHO_DIM
                rho[0] = popcount(a) + 1
                rho[1] = b + 1
                rho[2] = c + 1
                raw.append((a, b, c, k, tuple(rho), 2 * popcount(a) + k, (k, b)))
    order = sorted(range(len(raw)),
                   key=lambda i: (raw[i][F_RHO][0], raw[i][F_A], raw[i][F_B], raw[i][F_C]))
    search_rank = [0] * len(raw)
    for rank, idx in enumerate(order):
        search_rank[idx] = rank
    return tuple(raw), tuple(search_rank)


UNIVERSE, SEARCH_RANK = build_universe()
N = len(UNIVERSE)
FULL_MASK = (1 << N) - 1

CONTRACTS = ("E_full", "E_v0")


def contract_scores(name):
    """cap_E(x) for every realization, exact Fractions (CAP-1 task expectation)."""
    if name == "E_full":
        verified = (True, True, True)
    elif name == "E_v0":
        verified = (False, True, True)
    else:
        raise ValueError("unregistered capability contract")
    out = []
    for rec in UNIVERSE:
        total = Fraction(0)
        for j in range(3):
            if verified[j] and ((rec[F_A] >> j) & 1):
                total += MU[j]
        out.append(total)
    return tuple(out)


CAP = {name: contract_scores(name) for name in CONTRACTS}

K_M_VALUES = tuple(frozenset(j for j in range(3) if (bits >> j) & 1) for bits in range(8))
BUDGETS = ((2, 1, 1), (3, 2, 2), (9, 3, 3))
CHARGES = ((0, 0, 0), (1, 0, 0))
R_VALUES = tuple((b, m) for b in BUDGETS for m in CHARGES)
D_VALUES = (2, 6, 99)
B_VALUES = (0, 6, 12, 20, 32)
H_VALUES = ("NO_OBSERVATION", (1, 1), (2, 0))
TAU_VALUES = (Fraction(1, 6), Fraction(1, 2), Fraction(2, 3), Fraction(1))

BETA = {
    "beta_M": Fraction(1, 100),
    "beta_D": Fraction(1, 200),
    "beta_B": Fraction(1, 500),
    "beta_H": Fraction(1, 50),
}
BETA_SUM = BETA["beta_M"] + BETA["beta_D"] + BETA["beta_B"] + BETA["beta_H"]


def u_values():
    """Three registered typed uncertainty inputs (U-1a / U-1b)."""
    c_zero = 0
    for i, rec in enumerate(UNIVERSE):
        if rec[F_C] == 0:
            c_zero |= 1 << i
    return (
        ("U0", "FEASIBLE_SET", FULL_MASK, None),
        ("U1", "CONFIDENCE_SET", c_zero, Fraction(1, 20)),
        ("U2", "CONFIDENCE_SET", FULL_MASK, Fraction(1, 10)),
    )


U_VALUES = u_values()

SEMANTIC_DEFECTS = ("QUERY_NOT_REGISTERED", "QUERY_NOT_TOTAL_ON_DOMAIN")

CUT_NAMES = ("Expr", "Res", "Reach", "Seen", "Epis")
CUT_TO_MODE = {
    "Expr": "FM_EXPRESSIVITY",
    "Res": "FM_RESOURCE",
    "Reach": "FM_REACHABILITY",
    "Seen": "FM_SEARCH_BUDGET",
    "Epis": "FM_OBSERVED_SHORTFALL",
}

MODE_IDS = (
    "FM_CANNOT_CHECK",
    "FM_INCONSISTENT",
    "FM_INFORMATION_CEILING",
    "FM_EXPRESSIVITY",
    "FM_RESOURCE",
    "FM_REACHABILITY",
    "FM_SEARCH_BUDGET",
    "FM_OBSERVED_SHORTFALL",
    "FM_ALIASING",
    "FM_NONE",
)

# --------------------------------------------------------------------------
# Registered cut masks
# --------------------------------------------------------------------------


def expr_mask(k_m):
    mask = 0
    for i, rec in enumerate(UNIVERSE):
        if rec[F_K] in k_m:
            mask |= 1 << i
    return mask


def res_mask(budget, charge):
    effective = [0] * RHO_DIM
    for j in range(RHO_DIM):
        effective[j] = (budget[j] if j < len(budget) else 0) - (charge[j] if j < len(charge) else 0)
    mask = 0
    for i, rec in enumerate(UNIVERSE):
        ok = True
        for j in range(RHO_DIM):
            if rec[F_RHO][j] > effective[j]:
                ok = False
                break
        if ok:
            mask |= 1 << i
    return mask


def reach_mask(b_dev):
    mask = 0
    for i, rec in enumerate(UNIVERSE):
        if rec[F_DEV] <= b_dev:
            mask |= 1 << i
    return mask


def seen_mask(budget):
    mask = 0
    for i in range(N):
        if SEARCH_RANK[i] < budget:
            mask |= 1 << i
    return mask


def obs_mask(observed):
    if observed == "NO_OBSERVATION":
        return FULL_MASK
    mask = 0
    for i, rec in enumerate(UNIVERSE):
        if rec[F_OBS] == observed:
            mask |= 1 << i
    return mask


EXPR_MASKS = {k: expr_mask(v) for k, v in enumerate(K_M_VALUES)}
RES_MASKS = {r: res_mask(r[0], r[1]) for r in R_VALUES}
REACH_MASKS = {d: reach_mask(d) for d in D_VALUES}
SEEN_MASKS = {b: seen_mask(b) for b in B_VALUES}
OBS_MASKS = {h: obs_mask(h) for h in H_VALUES}


def bits_of(mask):
    out = []
    i = 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return out


_CEILING_CACHE = {}


def ceiling(contract, mask):
    """max cap_E over a mask; None represents BOTTOM (empty class)."""
    key = (contract, mask)
    hit = _CEILING_CACHE.get(key)
    if hit is not None or key in _CEILING_CACHE:
        return hit
    caps = CAP[contract]
    best = None
    for i in bits_of(mask):
        if best is None or caps[i] > best:
            best = caps[i]
    _CEILING_CACHE[key] = best
    return best


def verdict(contract, res, index):
    """q_{E,R}(x): the contract value, or the distinguished bottom UNSATISFIED."""
    if (res >> index) & 1:
        return CAP[contract][index]
    return UNSATISFIED


def meets(value, tau):
    return value is not UNSATISFIED and not isinstance(value, str) and value >= tau


def below(ceil_value, tau):
    return ceil_value is None or ceil_value < tau


def at_least(ceil_value, tau):
    return ceil_value is not None and ceil_value >= tau


# --------------------------------------------------------------------------
# Typed uncertainty (U-1) and the single emission constructor
# --------------------------------------------------------------------------


class TypedUncertainty(object):
    """U-1a FeasibleSet or U-1b ConfidenceSet, with the U-2B composed budget."""

    __slots__ = ("kind", "alpha", "coverage_lower", "state_knowledge",
                 "relation_betas", "survivor_size")

    def __init__(self, kind, alpha, coverage_lower, state_knowledge,
                 relation_betas, survivor_size):
        if kind not in ("FEASIBLE_SET", "CONFIDENCE_SET"):
            raise ValueError("unregistered uncertainty constructor: %r" % (kind,))
        if kind == "FEASIBLE_SET":
            if alpha is not None or coverage_lower is not None:
                raise ValueError("a FeasibleSet carries no probability premise (U-1a)")
        else:
            if not isinstance(alpha, Fraction) or isinstance(alpha, bool):
                raise ValueError("confidence budget must be an exact Fraction")
            if not isinstance(coverage_lower, Fraction):
                raise ValueError("composed coverage must be an exact Fraction")
            expected = Fraction(0)
            total = Fraction(1) - alpha - BETA_SUM
            if total > 0:
                expected = total
            if coverage_lower != expected:
                raise ValueError("composed coverage must equal the U-2B bound")
        if state_knowledge not in ("FEASIBLE", "UNKNOWN",
                                   "INCONSISTENT_REGISTERED_ASSUMPTIONS",
                                   "CANNOT_CHECK"):
            raise ValueError("unregistered state knowledge: %r" % (state_knowledge,))
        self.kind = kind
        self.alpha = alpha
        self.coverage_lower = coverage_lower
        self.state_knowledge = state_knowledge
        self.relation_betas = relation_betas
        self.survivor_size = survivor_size

    def as_json(self):
        return {
            "kind": self.kind,
            "alpha": None if self.alpha is None else str(self.alpha),
            "coverage_lower": None if self.coverage_lower is None else str(self.coverage_lower),
            "state_knowledge": self.state_knowledge,
            "relation_betas": {k: str(v) for k, v in sorted(self.relation_betas.items())},
            "survivor_size": self.survivor_size,
        }


class Emission(object):
    """The ONLY emission carrier. Constructed exclusively inside emit()."""

    __slots__ = ("disposition", "value", "identified_set", "reason", "uncertainty", "site")

    def __init__(self, disposition, value, identified_set, reason, uncertainty, site):
        self.disposition = disposition
        self.value = value
        self.identified_set = identified_set
        self.reason = reason
        self.uncertainty = uncertainty
        self.site = site


DISPOSITIONS = (
    "IDENTIFIED",
    "CANNOT_IDENTIFY",
    "INCONSISTENT_REGISTERED_ASSUMPTIONS",
    "CANNOT_CHECK",
)

EMIT_SITES = ("SITE_CANNOT_CHECK", "SITE_INCONSISTENT", "SITE_IDENTIFIED", "SITE_CANNOT_IDENTIFY")


def emit(site, disposition, uncertainty, value=None, identified_set=(), reason=None):
    """Single construction site. Rejects any emission without typed uncertainty."""
    if site not in EMIT_SITES:
        raise ValueError("unregistered emit site: %r" % (site,))
    if disposition not in DISPOSITIONS:
        raise ValueError("unregistered disposition: %r" % (disposition,))
    if not isinstance(uncertainty, TypedUncertainty):
        raise ValueError("every emission must carry a typed uncertainty object")
    ident = tuple(identified_set)
    if disposition == "IDENTIFIED":
        if value is None:
            raise ValueError("IDENTIFIED requires a value")
        if ident != (value,):
            raise ValueError("IDENTIFIED must carry the singleton identified set")
    elif disposition == "CANNOT_IDENTIFY":
        if value is not None:
            raise ValueError("CANNOT_IDENTIFY must not carry a point")
        if len(ident) < 2:
            raise ValueError("CANNOT_IDENTIFY requires a multi-valued identified set")
    else:
        if value is not None or ident:
            raise ValueError("terminal emissions carry neither a point nor an identified set")
        if not isinstance(reason, str) or not reason:
            raise ValueError("terminal emissions require a registered reason")
    return Emission(disposition, value, ident, reason, uncertainty, site)


def sort_key(value):
    if value is UNSATISFIED or isinstance(value, str):
        return (1, Fraction(0))
    return (0, value)


def build_uncertainty(u_kind, alpha, state_knowledge, survivor_size):
    if u_kind == "FEASIBLE_SET":
        return TypedUncertainty("FEASIBLE_SET", None, None, state_knowledge,
                                dict(BETA), survivor_size)
    composed = Fraction(1) - alpha - BETA_SUM
    if composed < 0:
        composed = Fraction(0)
    return TypedUncertainty("CONFIDENCE_SET", alpha, composed, state_knowledge,
                            dict(BETA), survivor_size)


def survivor_mask(k_m_index, d_value, b_value, h_value, u_mask):
    """Candidacy only: M, D, search budget, H, U. Res(R) is deliberately absent."""
    return (EXPR_MASKS[k_m_index] & REACH_MASKS[d_value] & SEEN_MASKS[b_value]
            & OBS_MASKS[h_value] & u_mask)


def predict(k_m_index, contract, r_value, h_value, d_value, b_value,
            u_kind, u_mask, alpha, semantics):
    """C_hat = F(M,E,R,H,D,U). Every return funnels through emit()."""
    if semantics != "REGISTERED":
        unc = build_uncertainty(u_kind, alpha, "CANNOT_CHECK", 0)
        return emit("SITE_CANNOT_CHECK", "CANNOT_CHECK", unc, reason=semantics)
    survivors = survivor_mask(k_m_index, d_value, b_value, h_value, u_mask)
    size = popcount(survivors)
    if survivors == 0:
        unc = build_uncertainty(u_kind, alpha, "INCONSISTENT_REGISTERED_ASSUMPTIONS", 0)
        return emit("SITE_INCONSISTENT", "INCONSISTENT_REGISTERED_ASSUMPTIONS", unc,
                    reason="EMPTY_SURVIVOR_SET")
    res = RES_MASKS[r_value]
    image = set()
    for index in bits_of(survivors):
        image.add(verdict(contract, res, index))
    knowledge = "UNKNOWN" if survivors == FULL_MASK else "FEASIBLE"
    unc = build_uncertainty(u_kind, alpha, knowledge, size)
    ordered = tuple(sorted(image, key=sort_key))
    if len(ordered) == 1:
        return emit("SITE_IDENTIFIED", "IDENTIFIED", unc,
                    value=ordered[0], identified_set=ordered)
    return emit("SITE_CANNOT_IDENTIFY", "CANNOT_IDENTIFY", unc, identified_set=ordered)


# --------------------------------------------------------------------------
# Ladder and failure-mode attribution (TAXONOMY_V1.md)
# --------------------------------------------------------------------------


def ladder_masks(k_m_index, r_value, d_value, b_value, h_value, u_mask):
    cuts = {
        "Expr": EXPR_MASKS[k_m_index],
        "Res": RES_MASKS[r_value],
        "Reach": REACH_MASKS[d_value],
        "Seen": SEEN_MASKS[b_value],
        "Epis": OBS_MASKS[h_value] & u_mask,
    }
    masks = [FULL_MASK]
    current = FULL_MASK
    for name in CUT_NAMES:
        current &= cuts[name]
        masks.append(current)
    return cuts, tuple(masks)


def mode_flags(semantics, survivors, ceilings, tau, qtau_image, include_aliasing=True,
               loose_rung=None):
    """All ten predicates evaluated INDEPENDENTLY (never as an if/elif chain)."""
    registered = semantics == "REGISTERED"
    base = registered and survivors != 0

    def lt(idx):
        if loose_rung == idx:
            # planted hostile: `<=` where the frozen taxonomy says `<`
            return ceilings[idx] is None or ceilings[idx] <= tau
        return below(ceilings[idx], tau)

    flags = {
        "FM_CANNOT_CHECK": not registered,
        "FM_INCONSISTENT": registered and survivors == 0,
        "FM_INFORMATION_CEILING": base and lt(0),
        "FM_EXPRESSIVITY": base and lt(1) and at_least(ceilings[0], tau),
        "FM_RESOURCE": base and lt(2) and at_least(ceilings[1], tau),
        "FM_REACHABILITY": base and lt(3) and at_least(ceilings[2], tau),
        "FM_SEARCH_BUDGET": base and lt(4) and at_least(ceilings[3], tau),
        "FM_OBSERVED_SHORTFALL": base and lt(5) and at_least(ceilings[4], tau),
        "FM_NONE": base and at_least(ceilings[5], tau) and qtau_image == frozenset((1,)),
    }
    if include_aliasing:
        flags["FM_ALIASING"] = (base and at_least(ceilings[5], tau)
                                and qtau_image != frozenset((1,)))
    else:
        flags["FM_ALIASING"] = False
    return flags


def assigned_mode(flags):
    live = [name for name in MODE_IDS if flags.get(name)]
    return live


def first_crossing_label(ceilings, tau, order):
    """Ladder label under an arbitrary cut order; None means no crossing."""
    for position in range(len(ceilings)):
        if below(ceilings[position], tau):
            if position == 0:
                return "FM_INFORMATION_CEILING"
            return CUT_TO_MODE[order[position - 1]]
    return None


# --------------------------------------------------------------------------
# Grid enumeration
# --------------------------------------------------------------------------


def main_grid():
    for k_index in range(len(K_M_VALUES)):
        for r_value in R_VALUES:
            for d_value in D_VALUES:
                for b_value in B_VALUES:
                    for h_value in H_VALUES:
                        for u_id, u_kind, u_mask, alpha in U_VALUES:
                            for contract in CONTRACTS:
                                for tau in TAU_VALUES:
                                    yield (k_index, r_value, d_value, b_value, h_value,
                                           u_id, u_kind, u_mask, alpha, contract, tau)


def evaluate(entry, semantics="REGISTERED"):
    (k_index, r_value, d_value, b_value, h_value,
     u_id, u_kind, u_mask, alpha, contract, tau) = entry
    emission = predict(k_index, contract, r_value, h_value, d_value, b_value,
                       u_kind, u_mask, alpha, semantics)
    cuts, masks = ladder_masks(k_index, r_value, d_value, b_value, h_value, u_mask)
    ceilings = tuple(ceiling(contract, m) for m in masks)
    survivors = survivor_mask(k_index, d_value, b_value, h_value, u_mask)
    res = RES_MASKS[r_value]
    qtau = frozenset(1 if meets(verdict(contract, res, i), tau) else 0
                     for i in bits_of(survivors))
    return emission, cuts, masks, ceilings, survivors, res, qtau


# --------------------------------------------------------------------------
# Censuses
# --------------------------------------------------------------------------


def main_census():
    counts = {name: 0 for name in MODE_IDS}
    dispositions = {name: 0 for name in DISPOSITIONS}
    sites = {name: 0 for name in EMIT_SITES}
    total = 0
    overlaps = 0
    gaps = 0
    kp2c_violations = 0
    soundness_violations = 0
    exceptions = 0
    coverage_pairs = 0
    coverage_hits = 0
    forced_abstention_witnesses = 0
    budget_mismatches = 0
    feasible_with_coverage = 0
    monotonicity_violations = 0
    unsatisfied_in_image = 0
    abstention_example = None
    for entry in main_grid():
        total += 1
        try:
            emission, cuts, masks, ceilings, survivors, res, qtau = evaluate(entry)
        except BaseException:  # pragma: no cover - counted, never expected
            exceptions += 1
            continue
        tau = entry[10]
        contract = entry[9]
        dispositions[emission.disposition] += 1
        sites[emission.site] += 1
        for position in range(1, len(ceilings)):
            if at_least(ceilings[position], tau) and below(ceilings[position - 1], tau):
                monotonicity_violations += 1
            if (ceilings[position - 1] is not None and ceilings[position] is not None
                    and ceilings[position] > ceilings[position - 1]):
                monotonicity_violations += 1
        flags = mode_flags("REGISTERED", survivors, ceilings, tau, qtau)
        live = assigned_mode(flags)
        if len(live) > 1:
            overlaps += 1
        if not live:
            gaps += 1
        if len(live) == 1:
            counts[live[0]] += 1
            mode = live[0]
            ladder_index = {
                "FM_EXPRESSIVITY": 1, "FM_RESOURCE": 2, "FM_REACHABILITY": 3,
                "FM_SEARCH_BUDGET": 4, "FM_OBSERVED_SHORTFALL": 5,
            }.get(mode)
            if ladder_index is not None:
                if not (at_least(ceilings[ladder_index - 1], tau)
                        and below(ceilings[ladder_index], tau)):
                    kp2c_violations += 1
            elif mode == "FM_INFORMATION_CEILING":
                if not below(ceilings[0], tau):
                    kp2c_violations += 1
        unc = emission.uncertainty
        if unc.kind == "FEASIBLE_SET" and unc.coverage_lower is not None:
            feasible_with_coverage += 1
        if unc.kind == "CONFIDENCE_SET":
            expected = Fraction(1) - unc.alpha - BETA_SUM
            if expected < 0:
                expected = Fraction(0)
            if unc.coverage_lower != expected:
                budget_mismatches += 1
        if emission.disposition in ("IDENTIFIED", "CANNOT_IDENTIFY"):
            indices = bits_of(survivors)
            emitted = set(emission.identified_set)
            if UNSATISFIED in emitted:
                unsatisfied_in_image += 1
            for index in indices:
                coverage_pairs += 1
                if verdict(contract, res, index) in emitted:
                    coverage_hits += 1
            if emission.disposition == "IDENTIFIED":
                point = emission.value
                if any(verdict(contract, res, i) != point for i in indices):
                    soundness_violations += 1
            else:
                pair = None
                for index in indices:
                    for other in indices:
                        if verdict(contract, res, index) != verdict(contract, res, other):
                            pair = (index, other)
                            break
                    if pair:
                        break
                if pair is not None:
                    forced_abstention_witnesses += 1
                    if abstention_example is None:
                        abstention_example = {
                            "survivor_a": pair[0],
                            "survivor_b": pair[1],
                            "verdict_a": str(verdict(contract, res, pair[0])),
                            "verdict_b": str(verdict(contract, res, pair[1])),
                            "identified_set": [str(v) for v in emission.identified_set],
                        }
    return {
        "grid_size": total,
        "exceptions": exceptions,
        "dispositions": dispositions,
        "emit_sites": sites,
        "mode_counts": counts,
        "taxonomy_overlaps": overlaps,
        "taxonomy_gaps": gaps,
        "kp2c_violations": kp2c_violations,
        "ladder_monotonicity_violations": monotonicity_violations,
        "soundness_violations": soundness_violations,
        "coverage_pairs": coverage_pairs,
        "coverage_hits": coverage_hits,
        "coverage_fraction": str(Fraction(coverage_hits, coverage_pairs))
        if coverage_pairs else None,
        "forced_abstention_witnesses": forced_abstention_witnesses,
        "forced_abstention_example": abstention_example,
        "confidence_budget_mismatches": budget_mismatches,
        "feasible_sets_carrying_coverage": feasible_with_coverage,
        "inputs_with_unsatisfied_in_image": unsatisfied_in_image,
        "modes_empty": sorted(name for name in MODE_IDS if counts[name] == 0
                              and name != "FM_CANNOT_CHECK"),
    }


def semantics_census():
    total = 0
    cannot_check = 0
    wrong_reason = 0
    attached = 0
    for defect in SEMANTIC_DEFECTS:
        for k_index in range(len(K_M_VALUES)):
            for h_value in H_VALUES:
                for u_id, u_kind, u_mask, alpha in U_VALUES:
                    total += 1
                    emission = predict(k_index, "E_full", R_VALUES[0], h_value,
                                       D_VALUES[0], B_VALUES[-1], u_kind, u_mask,
                                       alpha, defect)
                    if emission.disposition == "CANNOT_CHECK":
                        cannot_check += 1
                    if emission.reason != defect:
                        wrong_reason += 1
                    if isinstance(emission.uncertainty, TypedUncertainty):
                        attached += 1
    return {
        "cases": total,
        "cannot_check": cannot_check,
        "wrong_reason": wrong_reason,
        "uncertainty_attached": attached,
    }


def order_census():
    orders = tuple(permutations(CUT_NAMES))
    sensitive = 0
    considered = 0
    example = None
    sharp = None
    bind_counts = [0, 0, 0, 0]
    unique_lever_invariant = 0
    unique_lever_sensitive = 0
    for k_index in range(len(K_M_VALUES)):
        for r_value in R_VALUES:
            for d_value in D_VALUES:
                for b_value in B_VALUES:
                    for h_value in H_VALUES:
                        u_id, u_kind, u_mask, alpha = U_VALUES[0]
                        cuts, masks = ladder_masks(k_index, r_value, d_value,
                                                   b_value, h_value, u_mask)
                        subset_ceiling = {}
                        for bits in range(32):
                            mask = FULL_MASK
                            for position in range(5):
                                if (bits >> position) & 1:
                                    mask &= cuts[CUT_NAMES[position]]
                            subset_ceiling[bits] = ceiling("E_full", mask)
                        full_bits = 31
                        for tau in TAU_VALUES:
                            considered += 1
                            labels = set()
                            for order in orders:
                                chain = []
                                bits = 0
                                chain.append(subset_ceiling[0])
                                for name in order:
                                    bits |= 1 << CUT_NAMES.index(name)
                                    chain.append(subset_ceiling[bits])
                                labels.add(first_crossing_label(chain, tau, order))
                            if below(subset_ceiling[full_bits], tau):
                                bind = tuple(
                                    CUT_NAMES[position] for position in range(5)
                                    if at_least(subset_ceiling[full_bits & ~(1 << position)],
                                                tau))
                            else:
                                bind = ()
                            bind_counts[min(len(bind), 3)] += 1
                            is_sensitive = len(labels) > 1
                            if len(bind) == 1:
                                if is_sensitive:
                                    unique_lever_sensitive += 1
                                else:
                                    unique_lever_invariant += 1
                            if is_sensitive:
                                sensitive += 1
                                descriptor = {
                                    "k_m": sorted(K_M_VALUES[k_index]),
                                    "budget": list(r_value[0]),
                                    "charge": list(r_value[1]),
                                    "b_dev": d_value,
                                    "search_budget": b_value,
                                    "observation": "NO_OBSERVATION"
                                    if h_value == "NO_OBSERVATION" else list(h_value),
                                    "tau": str(tau),
                                    "labels": sorted(x or "NO_CROSSING" for x in labels),
                                    "individually_binding_cuts": list(bind),
                                    "full_conjunction_ceiling":
                                        None if subset_ceiling[full_bits] is None
                                        else str(subset_ceiling[full_bits]),
                                }
                                if example is None:
                                    example = descriptor
                                if sharp is None and len(bind) == 1:
                                    sharp = descriptor
    return {
        "orders": len(orders),
        "inputs": considered,
        "order_sensitive_inputs": sensitive,
        "order_invariant_inputs": considered - sensitive,
        "order_sensitivity_example": example,
        "sharp_unique_lever_counterexample": sharp,
        "individually_binding_cut_counts": {
            "zero_levers": bind_counts[0],
            "one_lever": bind_counts[1],
            "two_levers": bind_counts[2],
            "three_or_more_levers": bind_counts[3],
        },
        "unique_lever_order_invariant": unique_lever_invariant,
        "unique_lever_order_sensitive": unique_lever_sensitive,
        "diagnostic_note": (
            "The individually-binding-cut decomposition is a post-first-census "
            "diagnostic added to characterise KP-2D's order sensitivity. It changes "
            "no frozen predicate, threshold or mode assignment."),
    }


def modal_capability():
    tally = {}
    for value in CAP["E_full"]:
        tally[value] = tally.get(value, 0) + 1
    best = None
    for value, count in sorted(tally.items()):
        if best is None or count > best[1]:
            best = (value, count)
    return best[0], best[1]


def null_census():
    point, frequency = modal_capability()
    null_points = 0
    null_violations = 0
    null_violations_nonempty = 0
    nonempty_inputs = 0
    null_violations_head_to_head = 0
    true_points = 0
    true_violations = 0
    for entry in main_grid():
        emission, cuts, masks, ceilings, survivors, res, qtau = evaluate(entry)
        contract = entry[9]
        indices = bits_of(survivors)
        null_points += 1
        unsound = (not indices
                   or any(verdict(contract, res, i) != point for i in indices))
        if unsound:
            null_violations += 1
        if indices:
            nonempty_inputs += 1
            if unsound:
                null_violations_nonempty += 1
        if emission.disposition == "IDENTIFIED":
            true_points += 1
            if unsound:
                null_violations_head_to_head += 1
            if any(verdict(contract, res, i) != emission.value for i in indices):
                true_violations += 1
    return {
        "null_id": "NULL_MARGINAL",
        "null_point": str(point),
        "null_point_frequency": frequency,
        "null_point_emissions": null_points,
        "null_soundness_violations": null_violations,
        "nonempty_survivor_inputs": nonempty_inputs,
        "null_soundness_violations_on_nonempty_survivors": null_violations_nonempty,
        "head_to_head_inputs_where_predictor_emits_a_point": true_points,
        "null_soundness_violations_on_those_inputs": null_violations_head_to_head,
        "predictor_soundness_violations_on_those_inputs": true_violations,
        "predictor_point_emissions": true_points,
        "predictor_soundness_violations": true_violations,
        "predictor_strictly_beats_null": (true_violations == 0 and null_violations > 0),
        "predictor_strictly_beats_null_head_to_head":
            (true_violations == 0 and null_violations_head_to_head > 0),
    }


# --------------------------------------------------------------------------
# Hostiles
# --------------------------------------------------------------------------


def reachable_functions(tree, root):
    defined = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined[node.name] = node
    if root not in defined:
        raise ValueError("root function %r not found" % (root,))
    seen = set()
    stack = [root]
    while stack:
        name = stack.pop()
        if name in seen or name not in defined:
            continue
        seen.add(name)
        for node in ast.walk(defined[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                stack.append(node.func.id)
    return seen, defined


def audit_emit_funnel(source, root="predict", carrier="Emission", constructor="emit"):
    """Structural check: every value-returning path of `root` goes through emit()."""
    tree = ast.parse(source)
    reach, defined = reachable_functions(tree, root)
    bare_returns = []
    for node in ast.walk(defined[root]):
        if isinstance(node, ast.Return) and node.value is not None:
            if not (isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == constructor):
                bare_returns.append(getattr(node, "lineno", -1))
    construction_sites = []
    for name, node in sorted(defined.items()):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                    and sub.func.id == carrier:
                construction_sites.append(name)
    return {
        "reachable_functions": sorted(reach),
        "bare_return_lines": bare_returns,
        "carrier_construction_functions": sorted(set(construction_sites)),
        "funnel_ok": (not bare_returns and set(construction_sites) == {constructor}),
    }


HOSTILE_DROP_UNCERTAINTY = '''
def emit(site, disposition, uncertainty, value=None, identified_set=(), reason=None):
    return (disposition, value, uncertainty)


def predict(survivors, image):
    if not survivors:
        return emit("SITE_INCONSISTENT", "INCONSISTENT_REGISTERED_ASSUMPTIONS", None)
    if len(image) == 1:
        return list(image)[0]
    return emit("SITE_CANNOT_IDENTIFY", "CANNOT_IDENTIFY", None)
'''


def hostile_force_point():
    """A variant that forces the smallest image member when the image is multi-valued."""
    violations = 0
    cases = 0
    example = None
    for entry in main_grid():
        emission, cuts, masks, ceilings, survivors, res, qtau = evaluate(entry)
        if emission.disposition != "CANNOT_IDENTIFY":
            continue
        cases += 1
        contract = entry[9]
        forced = emission.identified_set[0]
        indices = bits_of(survivors)
        if any(verdict(contract, res, i) != forced for i in indices):
            violations += 1
            if example is None:
                counter = next(i for i in indices
                               if verdict(contract, res, i) != forced)
                example = {
                    "forced_point": str(forced),
                    "counterexample_survivor": counter,
                    "counterexample_verdict": str(verdict(contract, res, counter)),
                }
    return {
        "multi_valued_cases": cases,
        "forced_point_violations": violations,
        "detected": violations > 0,
        "example": example,
    }


def hostile_resource_prune():
    """The KP-1B falsifier: pruning the survivor set by resource admissibility."""
    violations = 0
    emissions = 0
    example = None
    for entry in main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        res = RES_MASKS[r_value]
        pruned = survivors & res
        if pruned == 0:
            continue
        image = set(CAP[contract][i] for i in bits_of(pruned))
        if len(image) != 1:
            continue
        emissions += 1
        point = next(iter(image))
        for index in bits_of(survivors):
            if verdict(contract, res, index) != point:
                violations += 1
                if example is None:
                    example = {
                        "pruned_point": str(point),
                        "excluded_survivor": index,
                        "excluded_verdict": str(verdict(contract, res, index)),
                    }
                break
    return {
        "pruned_point_emissions": emissions,
        "soundness_violations": violations,
        "detected": violations > 0,
        "example": example,
    }


def hostile_unsatisfied_as_zero():
    """Coercing UNSATISFIED to 0 changes threshold certification."""
    differences = 0
    for entry in main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        survivors = survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        if survivors == 0:
            continue
        res = RES_MASKS[r_value]
        true_image = set(verdict(contract, res, i) for i in bits_of(survivors))
        coerced = set(Fraction(0) if v is UNSATISFIED or isinstance(v, str) else v
                      for v in true_image)
        if len(true_image) != len(coerced):
            differences += 1
    return {"inputs_changed_by_coercion": differences, "detected": differences > 0}


def hostile_taxonomy_variants():
    overlap_hits = 0
    gap_hits = 0
    clean_overlaps = 0
    clean_gaps = 0
    for entry in main_grid():
        emission, cuts, masks, ceilings, survivors, res, qtau = evaluate(entry)
        tau = entry[10]
        clean = mode_flags("REGISTERED", survivors, ceilings, tau, qtau)
        live = assigned_mode(clean)
        if len(live) > 1:
            clean_overlaps += 1
        if not live:
            clean_gaps += 1
        loose = mode_flags("REGISTERED", survivors, ceilings, tau, qtau, loose_rung=1)
        if len(assigned_mode(loose)) > 1:
            overlap_hits += 1
        gapped = mode_flags("REGISTERED", survivors, ceilings, tau, qtau,
                            include_aliasing=False)
        if not assigned_mode(gapped):
            gap_hits += 1
    return {
        "overlap_hostile_inputs_flagged": overlap_hits,
        "gap_hostile_inputs_flagged": gap_hits,
        "true_taxonomy_overlaps": clean_overlaps,
        "true_taxonomy_gaps": clean_gaps,
        "overlap_detected": overlap_hits > 0,
        "gap_detected": gap_hits > 0,
        "no_alarm_on_true_taxonomy": clean_overlaps == 0 and clean_gaps == 0,
        "detected": (overlap_hits > 0 and gap_hits > 0
                     and clean_overlaps == 0 and clean_gaps == 0),
    }


def hostile_product_budget():
    alpha = U_VALUES[1][3]
    union = Fraction(1) - alpha - BETA_SUM
    product = (Fraction(1) - alpha)
    for value in (BETA["beta_M"], BETA["beta_D"], BETA["beta_B"], BETA["beta_H"]):
        product *= (Fraction(1) - value)
    return {
        "alpha": str(alpha),
        "beta_sum": str(BETA_SUM),
        "union_bound": str(union),
        "independence_product": str(product),
        "product_strictly_larger": product > union,
        "product_refused": True,
        "detected": product > union,
    }


def hostile_incomplete_identified_set():
    failures = 0
    checked = 0
    for entry in main_grid():
        emission, cuts, masks, ceilings, survivors, res, qtau = evaluate(entry)
        if emission.disposition != "CANNOT_IDENTIFY":
            continue
        checked += 1
        truncated = set(emission.identified_set[1:])
        contract = entry[9]
        if any(verdict(contract, res, i) not in truncated for i in bits_of(survivors)):
            failures += 1
    return {
        "abstentions_checked": checked,
        "coverage_failures_under_truncation": failures,
        "detected": failures > 0,
    }


def hostile_emit_contract():
    """emit() must refuse a bare value and a fabricated FeasibleSet coverage."""
    results = {}
    try:
        emit("SITE_IDENTIFIED", "IDENTIFIED", None, value=Fraction(1, 2),
             identified_set=(Fraction(1, 2),))
        results["missing_uncertainty_refused"] = False
    except ValueError:
        results["missing_uncertainty_refused"] = True
    try:
        TypedUncertainty("FEASIBLE_SET", None, Fraction(9, 10), "FEASIBLE", dict(BETA), 1)
        results["feasible_with_coverage_refused"] = False
    except ValueError:
        results["feasible_with_coverage_refused"] = True
    try:
        TypedUncertainty("CONFIDENCE_SET", Fraction(1, 20), Fraction(99, 100),
                         "FEASIBLE", dict(BETA), 1)
        results["wrong_budget_refused"] = False
    except ValueError:
        results["wrong_budget_refused"] = True
    try:
        unc = build_uncertainty("FEASIBLE_SET", None, "FEASIBLE", 2)
        emit("SITE_CANNOT_IDENTIFY", "CANNOT_IDENTIFY", unc,
             identified_set=(Fraction(1, 2),))
        results["single_valued_abstention_refused"] = False
    except ValueError:
        results["single_valued_abstention_refused"] = True
    results["detected"] = all(results.values())
    return results


def kp1d_counterexample():
    """Mis-registration boundary: a sound point that is not the true system's value."""
    for entry in main_grid():
        (k_index, r_value, d_value, b_value, h_value,
         u_id, u_kind, u_mask, alpha, contract, tau) = entry
        emission = predict(k_index, contract, r_value, h_value, d_value, b_value,
                           u_kind, u_mask, alpha, "REGISTERED")
        if emission.disposition != "IDENTIFIED":
            continue
        survivors = survivor_mask(k_index, d_value, b_value, h_value, u_mask)
        res = RES_MASKS[r_value]
        point = emission.value
        candidates = [index for index in range(N) if not ((survivors >> index) & 1)
                      and verdict(contract, res, index) != point]
        numeric = [index for index in candidates
                   if verdict(contract, res, index) is not UNSATISFIED]
        for index in (numeric or candidates):
            true_value = verdict(contract, res, index)
            if True:
                return {
                    "registered_k_m": sorted(K_M_VALUES[k_index]),
                    "contract": contract,
                    "budget": list(r_value[0]),
                    "charge": list(r_value[1]),
                    "b_dev": d_value,
                    "search_budget": b_value,
                    "uncertainty_input": u_id,
                    "emitted_point": str(point),
                    "survivor_count": popcount(survivors),
                    "excluded_realization_index": index,
                    "excluded_realization_value": str(true_value),
                    "sound_over_consistent_worlds": True,
                    "equals_actual_system_capability": False,
                    "note": ("KP-1B holds unconditionally over consistent worlds; the "
                             "bridge to a realization excluded by a false registration "
                             "is the proven structural boundary."),
                }
    return None


# --------------------------------------------------------------------------
# Parent audit
# --------------------------------------------------------------------------


def repo_root(start=None):
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root=None):
    root = root or repo_root()
    rows = []
    mutation_detected = None
    for name, path, expected_blob, field, expected_claim in PARENT_PINS:
        target = root / path
        if not target.is_file():
            rows.append({"name": name, "path": path, "blob_ok": False, "claim_ok": False,
                         "actual_blob": None})
            continue
        data = target.read_bytes()
        actual = git_blob_sha(data)
        payload = json.loads(data.decode("utf-8"))
        rows.append({
            "name": name,
            "path": path,
            "actual_blob": actual,
            "blob_ok": actual == expected_blob,
            "claim_ok": payload.get(field) == expected_claim,
        })
        if mutation_detected is None:
            mutated = data + b"\n"
            mutation_detected = git_blob_sha(mutated) != expected_blob
    for path in HISTORICAL_NON_AUTHORITY:
        rows.append({"name": "historical_non_authority", "path": path,
                     "actual_blob": None, "blob_ok": None, "claim_ok": None})
    return {
        "rows": rows,
        "all_blobs_ok": all(r["blob_ok"] for r in rows if r["blob_ok"] is not None),
        "all_claims_ok": all(r["claim_ok"] for r in rows if r["claim_ok"] is not None),
        "mutation_hostile_detected": bool(mutation_detected),
    }


# --------------------------------------------------------------------------
# Receipt
# --------------------------------------------------------------------------


def build_receipt():
    parents = audit_parents()
    census = main_census()
    semantics = semantics_census()
    orders = order_census()
    null = null_census()
    funnel = audit_emit_funnel(Path(__file__).read_text(encoding="utf-8"))
    hostile_funnel = audit_emit_funnel(HOSTILE_DROP_UNCERTAINTY)
    hostiles = {
        "H1_forced_point": hostile_force_point(),
        "H2_dropped_uncertainty": {
            "true_module_funnel_ok": funnel["funnel_ok"],
            "hostile_bare_return_lines": hostile_funnel["bare_return_lines"],
            "hostile_funnel_ok": hostile_funnel["funnel_ok"],
            "detected": (funnel["funnel_ok"] and not hostile_funnel["funnel_ok"]),
        },
        "H3_taxonomy_overlap_and_gap": hostile_taxonomy_variants(),
        "H4_resource_prune": hostile_resource_prune(),
        "H5_unsatisfied_as_zero": hostile_unsatisfied_as_zero(),
        "H6_independence_product": hostile_product_budget(),
        "H7_incomplete_identified_set": hostile_incomplete_identified_set(),
        "H8_emit_contract": hostile_emit_contract(),
        "H9_parent_mutation": {"detected": parents["mutation_hostile_detected"]},
    }
    checks = {
        "grid_size_matches_frozen_scope": census["grid_size"] == 51840,
        "semantics_subcensus_size": semantics["cases"] == 144,
        "order_census_size": orders["inputs"] == 8640 and orders["orders"] == 120,
        "no_exceptions": census["exceptions"] == 0,
        "kp1a_total": (sum(census["dispositions"].values()) == census["grid_size"]),
        "kp1b_zero_soundness_violations": census["soundness_violations"] == 0,
        "kp1c_forced_abstention_witnessed":
            census["forced_abstention_witnesses"] == census["dispositions"]["CANNOT_IDENTIFY"],
        "kp2a_ladder_monotone": census["ladder_monotonicity_violations"] == 0,
        "kp2b_partition": census["taxonomy_overlaps"] == 0 and census["taxonomy_gaps"] == 0,
        "kp2b_modes_sum_to_grid": sum(census["mode_counts"].values()) == census["grid_size"],
        "kp2c_unique_binding_cut": census["kp2c_violations"] == 0,
        "kp2d_order_census_consistent":
            orders["order_sensitive_inputs"] + orders["order_invariant_inputs"]
            == orders["inputs"],
        "kp2d_boundary_earned_by_counterexample":
            (orders["order_sensitive_inputs"] == 0)
            or (orders["order_sensitivity_example"] is not None
                and orders["sharp_unique_lever_counterexample"] is not None),
        "kp1d_boundary_counterexample_exhibited": kp1d_counterexample() is not None,
        "kp3a_emit_funnel": funnel["funnel_ok"],
        "kp3a_single_construction_site": funnel["carrier_construction_functions"] == ["emit"],
        "kp3b_budget_exact": census["confidence_budget_mismatches"] == 0,
        "kp3b_feasible_sets_bare": census["feasible_sets_carrying_coverage"] == 0,
        "kp3c_exact_coverage_one": census["coverage_fraction"] == "1",
        "kp4_null_strictly_beaten": null["predictor_strictly_beats_null"],
        "kp4_null_strictly_beaten_head_to_head":
            null["predictor_strictly_beats_null_head_to_head"],
        "all_hostiles_detected": all(v.get("detected") for v in hostiles.values()),
        "no_alarm_on_true_taxonomy": hostiles["H3_taxonomy_overlap_and_gap"][
            "no_alarm_on_true_taxonomy"],
        "parent_blobs_pinned": parents["all_blobs_ok"],
        "parent_claims_pinned": parents["all_claims_ok"],
    }
    return {
        "schema": "GMI833CapabilityPredictorReceiptV1",
        "issue": 833,
        "section": "K. Capability theory upgrade",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "universe": {
            "realizations": N,
            "tasks": 3,
            "task_weights": [str(m) for m in MU],
            "resource_coordinates": RHO_DIM,
            "active_resource_coordinates": 3,
            "contracts": list(CONTRACTS),
            "capability_values_E_full": sorted(set(str(v) for v in CAP["E_full"])),
            "capability_values_E_v0": sorted(set(str(v) for v in CAP["E_v0"])),
        },
        "registered_betas": {k: str(v) for k, v in sorted(BETA.items())},
        "beta_sum": str(BETA_SUM),
        "main_census": census,
        "semantics_subcensus": semantics,
        "order_census": orders,
        "null_control": null,
        "emit_funnel": funnel,
        "hostiles": hostiles,
        "kp1d_boundary_counterexample": kp1d_counterexample(),
        "parent_audit": parents,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "terminal": "GMI_833_CAPABILITY_PREDICTOR_V1_ALL_GREEN"
        if all(checks.values()) else "GMI_833_CAPABILITY_PREDICTOR_V1_RED",
    }


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [canonicalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [canonicalize(item) for item in sorted(value, key=repr)]
    if isinstance(value, dict):
        return {str(key): canonicalize(item)
                for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value):
    return json.dumps(canonicalize(value), sort_keys=True, indent=2,
                      ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt()), end="")
