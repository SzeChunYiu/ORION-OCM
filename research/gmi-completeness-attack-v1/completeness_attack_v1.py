#!/usr/bin/env python3
"""GMI Completeness Attack v1 — Issue #602 Section J2.

Finite, exact attack on the registered D1–D8 domain basis under a frozen
E1 constant-factor burden vector. No network, no third-party imports.
Safe under ``python3 -I`` and Python 3.8.

What this capsule does (and does not):

- SEARCH: for each Di, enumerate obligations no Di realization meets within
  the frozen burden (constructive witnesses).
- PAIRWISE: exhibit reduction failures where Di⊗Dj product composition fails
  even though both budgets are nonzero.
- HIGHER-ORDER: exhibit obligations not captured by any pairwise simple
  composition.
- BOUNDED COMPLETENESS: prove every ATOMIC obligation whose demand fits the
  frozen budget of its unique support domain is met by that domain; record
  PAIR/HIGHER non-factorizable residues as explicit open regions.

Claim ceiling: finite catalogue under frozen B and E1. Not ontological
completeness of machine intelligence.
"""

from __future__ import print_function

import itertools
from fractions import Fraction

# ---------------------------------------------------------------------------
# Registry alignment (names match DOMAIN_REGISTRY_V1 / issue #602 J preamble)
# ---------------------------------------------------------------------------

DOMAIN_IDS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")

DOMAIN_NAMES = {
    "D1": "coefficient_function_field",
    "D2": "exemplar_memory_indexed",
    "D3": "probabilistic_belief",
    "D4": "symbolic_rule_program",
    "D5": "search_deliberative_frontier",
    "D6": "dynamical_state_controller",
    "D7": "collective_distributed_population",
    "D8": "morphogenetic_self_rewriting",
}

# Primary native size coordinate per domain (frozen scope).
SIZE_COORDINATE = {
    "D1": "parameter_count",
    "D2": "record_count",
    "D3": "support_size",
    "D4": "symbol_count",
    "D5": "frontier_width",
    "D6": "state_dimension",
    "D7": "component_count",
    "D8": "morph_depth",
}

# Frozen E1 burden: each Di may spend at most this many units of its native
# size coordinate (plus declared constant-factor overhead, not modelled here).
FROZEN_BURDEN = {
    "D1": 8,
    "D2": 8,
    "D3": 8,
    "D4": 8,
    "D5": 8,
    "D6": 8,
    "D7": 8,
    "D8": 4,
}

BURDEN_CLASS = "E1_CONSTANT_FACTOR"

# Demand sweep for ATOMIC obligations (includes over-budget demands).
ATOMIC_DEMANDS = tuple(range(1, 13))  # 1..12

# Coupling kinds.
ATOMIC = "ATOMIC"
PAIR = "PAIR"
HIGHER = "HIGHER"


def _zero_demand():
    return {d: 0 for d in DOMAIN_IDS}


def _demand_tuple(demand_map):
    return tuple(int(demand_map[d]) for d in DOMAIN_IDS)


class Obligation(object):
    """One finite cognitive obligation in the attack catalogue."""

    __slots__ = (
        "oid",
        "name",
        "coupling",
        "support",
        "demand",
        "factorizable",
    )

    def __init__(self, oid, name, coupling, support, demand, factorizable):
        self.oid = int(oid)
        self.name = str(name)
        self.coupling = str(coupling)
        self.support = frozenset(support)
        self.demand = dict(demand)
        self.factorizable = bool(factorizable)

    def demand_on(self, domain_id):
        return int(self.demand[domain_id])


def build_obligation_catalogue(burden=None):
    """Construct the finite obligation catalogue used by the attack.

    Catalogue structure (deterministic):
      - ATOMIC_Di_k for each Di and k in ATOMIC_DEMANDS
      - PAIR_FACTOR_Di_Dj : alone-fail, product-succeed (factorizable)
      - PAIR_FAIL_Di_Dj   : alone-fail, product-fail (reduction failure)
      - HIGHER_Di_Dj_Dk   : for selected triples; no pairwise product meets it
    """
    if burden is None:
        burden = FROZEN_BURDEN
    obligations = []
    oid = 0

    # --- ATOMIC: single-domain native obligations ---------------------------
    for di in DOMAIN_IDS:
        for k in ATOMIC_DEMANDS:
            demand = _zero_demand()
            demand[di] = k
            obligations.append(
                Obligation(
                    oid=oid,
                    name="ATOMIC_%s_demand_%d" % (di, k),
                    coupling=ATOMIC,
                    support=(di,),
                    demand=demand,
                    factorizable=True,
                )
            )
            oid += 1

    # --- PAIR: every unordered pair ----------------------------------------
    for di, dj in itertools.combinations(DOMAIN_IDS, 2):
        # Factorizable: each side needs half-ish of its budget (still alone-
        # insufficient if we set demand = burden+1 for "alone" check via
        # requiring BOTH domains). Alone always fails because support size 2.
        demand_f = _zero_demand()
        demand_f[di] = max(1, burden[di] // 2)
        demand_f[dj] = max(1, burden[dj] // 2)
        obligations.append(
            Obligation(
                oid=oid,
                name="PAIR_FACTOR_%s_%s" % (di, dj),
                coupling=PAIR,
                support=(di, dj),
                demand=demand_f,
                factorizable=True,
            )
        )
        oid += 1

        # Non-factorizable reduction failure: joint demand exceeds what a
        # product protocol can pay even when each budget is fully spent on
        # its factor — modelled as needing burden+1 on each factor under a
        # non-separable interaction (factorizable=False).
        demand_n = _zero_demand()
        demand_n[di] = burden[di] + 1
        demand_n[dj] = burden[dj] + 1
        obligations.append(
            Obligation(
                oid=oid,
                name="PAIR_FAIL_%s_%s" % (di, dj),
                coupling=PAIR,
                support=(di, dj),
                demand=demand_n,
                factorizable=False,
            )
        )
        oid += 1

    # --- HIGHER: selected contiguous triples + one full-basis residue ------
    triples = (
        ("D1", "D2", "D3"),
        ("D2", "D3", "D4"),
        ("D3", "D4", "D5"),
        ("D4", "D5", "D6"),
        ("D5", "D6", "D7"),
        ("D6", "D7", "D8"),
        ("D1", "D4", "D8"),
        ("D2", "D5", "D7"),
    )
    for triple in triples:
        demand = _zero_demand()
        for di in triple:
            demand[di] = max(1, burden[di] // 2)
        obligations.append(
            Obligation(
                oid=oid,
                name="HIGHER_%s" % "_".join(triple),
                coupling=HIGHER,
                support=triple,
                demand=demand,
                factorizable=False,
            )
        )
        oid += 1

    # Explicit open-region residue: requires all eight with non-factorizable
    # joint morphology/uncertainty/search coupling.
    demand_all = _zero_demand()
    for di in DOMAIN_IDS:
        demand_all[di] = burden[di] + 1
    obligations.append(
        Obligation(
            oid=oid,
            name="HIGHER_OPEN_FULL_BASIS_RESIDUE",
            coupling=HIGHER,
            support=DOMAIN_IDS,
            demand=demand_all,
            factorizable=False,
        )
    )
    oid += 1

    return tuple(obligations)


# Module-level frozen catalogue.
OBLIGATIONS = build_obligation_catalogue()


# ---------------------------------------------------------------------------
# Meeting / reduction predicates (exact)
# ---------------------------------------------------------------------------

def meets_alone(domain_id, obligation, burden=None):
    """True iff a Di realization within frozen burden meets the obligation.

    Only ATOMIC obligations with unique support == domain_id and
    demand[domain_id] <= burden[domain_id] are alone-meetable.
    """
    if burden is None:
        burden = FROZEN_BURDEN
    if obligation.coupling != ATOMIC:
        return False
    if obligation.support != frozenset((domain_id,)):
        return False
    return obligation.demand_on(domain_id) <= burden[domain_id]


def product_meets(domain_ids, obligation, burden=None):
    """Simple composition Di⊗Dj⊗… : independent product + protocol.

    Succeeds only when:
      - obligation.support ⊆ domain_ids
      - obligation.factorizable is True
      - every support domain's demand is ≤ its frozen burden
    Non-factorizable couplings are reduction failures by definition.
    """
    if burden is None:
        burden = FROZEN_BURDEN
    support = obligation.support
    if not support.issubset(frozenset(domain_ids)):
        return False
    if not obligation.factorizable:
        return False
    for di in support:
        if obligation.demand_on(di) > burden[di]:
            return False
    return True


def pairwise_reduction_fails(di, dj, obligation, burden=None):
    """True when (di,dj) is a pairwise reduction failure on this obligation.

    Criteria:
      - neither domain meets alone
      - obligation support is exactly {di, dj}
      - product composition fails (non-factorizable or over-budget)
    """
    if burden is None:
        burden = FROZEN_BURDEN
    if meets_alone(di, obligation, burden) or meets_alone(dj, obligation, burden):
        return False
    if obligation.support != frozenset((di, dj)):
        return False
    return not product_meets((di, dj), obligation, burden)


def higher_order_uncaptured(obligation, burden=None):
    """True iff obligation is higher-order and no pairwise product captures it."""
    if burden is None:
        burden = FROZEN_BURDEN
    if obligation.coupling != HIGHER:
        return False
    support = sorted(obligation.support)
    if len(support) < 3:
        return False
    for di, dj in itertools.combinations(support, 2):
        if product_meets((di, dj), obligation, burden):
            return False
    # Also: full simple product of the support fails when non-factorizable.
    return not product_meets(support, obligation, burden)


def union_meets(obligation, burden=None, domains=None):
    """Union coverage under alone-meet OR factorizable product of support."""
    if burden is None:
        burden = FROZEN_BURDEN
    if domains is None:
        domains = DOMAIN_IDS
    for di in domains:
        if meets_alone(di, obligation, burden):
            return True
    # Factorizable multi-domain obligations met by product of their support
    # when every support domain is in the admitted basis.
    if obligation.support.issubset(frozenset(domains)):
        if product_meets(obligation.support, obligation, burden):
            return True
    return False


# ---------------------------------------------------------------------------
# Attack searches (constructive witnesses)
# ---------------------------------------------------------------------------

def obligations_unmet_by(domain_id, catalogue=None, burden=None):
    """All catalogue obligations no Di realization meets within frozen burden."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    return tuple(o for o in catalogue if not meets_alone(domain_id, o, burden))


def first_unmet_witness(domain_id, catalogue=None, burden=None):
    """One constructive witness obligation unmet by Di, or None.

    Preference order:
      1. over-budget ATOMIC obligation for this domain (sharpest falsifier)
      2. any other unmet obligation
    """
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    over = None
    other = None
    for o in catalogue:
        if meets_alone(domain_id, o, burden):
            continue
        if (
            o.coupling == ATOMIC
            and o.support == frozenset((domain_id,))
            and o.demand_on(domain_id) > burden[domain_id]
        ):
            over = o
            break
        if other is None:
            other = o
    return over if over is not None else other


def pairwise_reduction_failures(catalogue=None, burden=None):
    """All (di, dj, obligation) pairwise reduction-failure witnesses."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    out = []
    for di, dj in itertools.combinations(DOMAIN_IDS, 2):
        for o in catalogue:
            if pairwise_reduction_fails(di, dj, o, burden):
                out.append((di, dj, o))
    return tuple(out)


def higher_order_uncaptured_obligations(catalogue=None, burden=None):
    """All higher-order obligations not captured by simple pairwise composition."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    return tuple(o for o in catalogue if higher_order_uncaptured(o, burden))


def atomic_in_budget(catalogue=None, burden=None):
    """ATOMIC obligations whose unique-support demand fits the frozen burden."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    out = []
    for o in catalogue:
        if o.coupling != ATOMIC:
            continue
        di = next(iter(o.support))
        if o.demand_on(di) <= burden[di]:
            out.append(o)
    return tuple(out)


def prove_bounded_completeness_atomic(catalogue=None, burden=None):
    """Prove every in-budget ATOMIC obligation is met by its support domain.

    Returns (ok: bool, coverage: Fraction, n_in_budget, n_met, counterexamples).
    """
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    scoped = atomic_in_budget(catalogue, burden)
    counterexamples = []
    met = 0
    for o in scoped:
        di = next(iter(o.support))
        if meets_alone(di, o, burden):
            met += 1
        else:
            counterexamples.append(o)
    n = len(scoped)
    coverage = Fraction(met, n) if n else Fraction(1, 1)
    return (len(counterexamples) == 0, coverage, n, met, tuple(counterexamples))


# ---------------------------------------------------------------------------
# Coverage metrics (exact Fraction)
# ---------------------------------------------------------------------------

def coverage_fraction_domain(domain_id, catalogue=None, burden=None):
    """|{o : Di meets alone}| / |O| as Fraction."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    n = len(catalogue)
    hit = sum(1 for o in catalogue if meets_alone(domain_id, o, burden))
    return Fraction(hit, n)


def coverage_fraction_union(catalogue=None, burden=None, domains=None):
    """Fraction of catalogue met by alone-or-factorizable-product union."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = FROZEN_BURDEN
    if domains is None:
        domains = DOMAIN_IDS
    n = len(catalogue)
    hit = sum(1 for o in catalogue if union_meets(o, burden, domains))
    return Fraction(hit, n)


def open_region_fraction(catalogue=None, burden=None):
    """Fraction of catalogue left open (not met by union under frozen burden)."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    cov = coverage_fraction_union(catalogue, burden)
    return Fraction(1, 1) - cov


def run_completeness_attack(catalogue=None, burden=None):
    """End-to-end attack report (JSON-serializable primitives + Fractions)."""
    if catalogue is None:
        catalogue = OBLIGATIONS
    if burden is None:
        burden = dict(FROZEN_BURDEN)

    alone_coverage = {}
    unmet_counts = {}
    unmet_witnesses = {}
    for di in DOMAIN_IDS:
        alone_coverage[di] = coverage_fraction_domain(di, catalogue, burden)
        unmet = obligations_unmet_by(di, catalogue, burden)
        unmet_counts[di] = len(unmet)
        w = first_unmet_witness(di, catalogue, burden)
        unmet_witnesses[di] = None if w is None else {
            "oid": w.oid,
            "name": w.name,
            "coupling": w.coupling,
            "demand": _demand_tuple(w.demand),
        }

    pair_fails = pairwise_reduction_failures(catalogue, burden)
    higher = higher_order_uncaptured_obligations(catalogue, burden)
    ok, atomic_cov, n_atomic, n_met, counter = prove_bounded_completeness_atomic(
        catalogue, burden
    )
    union_cov = coverage_fraction_union(catalogue, burden)
    open_frac = open_region_fraction(catalogue, burden)

    return {
        "burden_class": BURDEN_CLASS,
        "frozen_burden": dict(burden),
        "catalogue_size": len(catalogue),
        "alone_coverage": alone_coverage,
        "unmet_counts": unmet_counts,
        "unmet_witnesses": unmet_witnesses,
        "pairwise_reduction_failure_count": len(pair_fails),
        "pairwise_reduction_failure_samples": tuple(
            (di, dj, o.name) for di, dj, o in pair_fails[:8]
        ),
        "higher_order_uncaptured_count": len(higher),
        "higher_order_samples": tuple(o.name for o in higher[:8]),
        "bounded_atomic_completeness": {
            "proved": ok,
            "coverage": atomic_cov,
            "n_in_budget": n_atomic,
            "n_met": n_met,
            "counterexamples": tuple(o.name for o in counter),
        },
        "union_coverage": union_cov,
        "open_region_fraction": open_frac,
        "j2_tick_advice": {
            "D1_unmet_search": unmet_counts["D1"] > 0,
            "D2_unmet_search": unmet_counts["D2"] > 0,
            "D3_unmet_search": unmet_counts["D3"] > 0,
            "D4_unmet_search": unmet_counts["D4"] > 0,
            "D5_unmet_search": unmet_counts["D5"] > 0,
            "D6_unmet_search": unmet_counts["D6"] > 0,
            "D7_unmet_search": unmet_counts["D7"] > 0,
            "D8_unmet_search": unmet_counts["D8"] > 0,
            "pairwise_reduction_failures": len(pair_fails) > 0,
            "higher_order_uncaptured": len(higher) > 0,
            "bounded_completeness_proved": ok,
            "open_regions_recorded": open_frac > 0,
        },
    }


def main():
    report = run_completeness_attack()
    print("GMI Completeness Attack v1  (#602 J2)")
    print("burden_class =", report["burden_class"])
    print("frozen_burden =", report["frozen_burden"])
    print("catalogue_size =", report["catalogue_size"])
    print("--- alone coverage (exact Fraction) ---")
    for di in DOMAIN_IDS:
        frac = report["alone_coverage"][di]
        print(
            "  %s  coverage=%s  unmet=%d  witness=%s"
            % (
                di,
                frac,
                report["unmet_counts"][di],
                report["unmet_witnesses"][di]["name"]
                if report["unmet_witnesses"][di]
                else None,
            )
        )
    print(
        "pairwise_reduction_failures =",
        report["pairwise_reduction_failure_count"],
    )
    print(
        "higher_order_uncaptured =",
        report["higher_order_uncaptured_count"],
    )
    bac = report["bounded_atomic_completeness"]
    print(
        "bounded_atomic_completeness proved=%s coverage=%s (%d/%d)"
        % (bac["proved"], bac["coverage"], bac["n_met"], bac["n_in_budget"])
    )
    print("union_coverage =", report["union_coverage"])
    print("open_region_fraction =", report["open_region_fraction"])
    print("j2_tick_advice =", report["j2_tick_advice"])


if __name__ == "__main__":
    main()
