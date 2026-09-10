"""Mutation / crossover over OCMMorphologyGenomeV1 (direct E0 encoding).

All operators are seeded-RNG deterministic.  Structural mutations respect the
schema vocabularies; theta mutations stay within declared bounds.
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple

from morphology.schema import (FIELD_FAMILIES, LEARNING_FAMILIES, MEMORY_FAMILIES,
                               REVISION_FAMILIES, TOPOLOGY_FAMILIES, EXECUTIVE_FAMILIES,
                               UNIT_TYPES, OCMMorphologyGenomeV1, UnitSpec)
from morphology.direct_genome import DEFAULT_THETA, _make, operators_for
from morphology.gs_bound import GS_BOUND_V1

THETA_BOUNDS = {
    "queue_budget": (8.0, 64.0),
    "probe_budget": (1.0, 8.0),
    "expansion_cap": (16.0, 128.0),
    "consolidation_threshold": (0.1, 0.9),
    "index_build": (0.0, 1.0),
    "bidding_temperature": (0.1, 2.0),
}


def mutate(g: OCMMorphologyGenomeV1, rng: random.Random,
           p_struct: float = 0.7, p_theta: float = 0.3) -> OCMMorphologyGenomeV1:
    h = g.clone()
    if rng.random() < p_struct:
        kind = rng.choice(["unit", "field", "topology", "exec", "learn", "rev", "mem"])
        if kind == "unit":
            # amend-5: the mutated space is GS_BOUND_V1 — census maxima are
            # descriptive, never bounds.  (The old census-9 + hardcoded-3
            # union was the same set; this derives it from the declared
            # bound so a bound extension can never leave mutation behind.)
            types = list(GS_BOUND_V1["extra_units"])
            cur = [u.unit_type for u in h.U if u.unit_type != "fact_relation"]
            if cur and rng.random() < 0.5:
                cur.remove(rng.choice(cur))          # delete a unit
            elif len(cur) < 5:
                cand = [t for t in types if t not in cur]
                if cand:
                    cur.append(rng.choice(cand))      # add a unit
            h.U = [UnitSpec("u%02d_%s" % (i, t), t) for i, t in
                   enumerate(["fact_relation"] + sorted(cur))]
            unit_types = [u.unit_type for u in h.U]
            h.O_basis = operators_for(unit_types, h.L, h.K, h.R)
        elif kind == "field":
            h.F_arch = rng.choice(list(FIELD_FAMILIES))
        elif kind == "topology":
            h.T_family = rng.choice(list(TOPOLOGY_FAMILIES))
        elif kind == "exec":
            h.Pi_arch = rng.choice(list(EXECUTIVE_FAMILIES))
        elif kind == "learn":
            h.L = rng.choice(list(LEARNING_FAMILIES))
            unit_types = [u.unit_type for u in h.U]
            h.O_basis = operators_for(unit_types, h.L, h.K, h.R)
        elif kind == "rev":
            h.R = rng.choice(list(REVISION_FAMILIES))
            h.O_basis = tuple(op for op in h.O_basis if op != "revoke_reopen") + (
                ("revoke_reopen",) if h.R != "none" else ())
        else:
            h.K = rng.choice(list(MEMORY_FAMILIES))
            unit_types = [u.unit_type for u in h.U]
            h.O_basis = operators_for(unit_types, h.L, h.K, h.R)
    if rng.random() < p_theta:
        key = rng.choice(list(THETA_BOUNDS))
        lo, hi = THETA_BOUNDS[key]
        cur = float(h.theta.get(key, DEFAULT_THETA.get(key, (lo + hi) / 2)))
        h.theta[key] = round(min(hi, max(lo, cur + rng.gauss(0, (hi - lo) / 8))), 4)
    h.provenance = dict(h.provenance)
    h.provenance["origin"] = "mutation"
    h.provenance["parent"] = g.digest()[:16]
    return h


def crossover(a: OCMMorphologyGenomeV1, b: OCMMorphologyGenomeV1,
              rng: random.Random) -> OCMMorphologyGenomeV1:
    """Dimension-wise uniform crossover (families / unit set / theta)."""
    pick = lambda x, y: x if rng.random() < 0.5 else y  # noqa: E731
    child = OCMMorphologyGenomeV1(
        encoding=pick(a.encoding, b.encoding),
        F_arch=pick(a.F_arch, b.F_arch),
        U=sorted([u for u in pick(list(a.U), list(b.U))],
                 key=lambda u: u.unit_id) or a.U[:1],
        T_family=pick(a.T_family, b.T_family),
        O_basis=tuple(sorted(set(a.O_basis) | set(b.O_basis))),
        Pi_arch=pick(a.Pi_arch, b.Pi_arch),
        L=pick(a.L, b.L), R=pick(a.R, b.R), K=pick(a.K, b.K),
        theta=dict(sorted({**a.theta, **b.theta}.items())),
        provenance={"origin": "crossover",
                    "parents": [a.digest()[:16], b.digest()[:16]]})
    # repair operator basis against the child's own support
    unit_types = [u.unit_type for u in child.U]
    child.O_basis = operators_for(unit_types, child.L, child.K, child.R)
    return child
