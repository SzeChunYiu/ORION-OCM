"""Canonical forms, phenotype digest and isomorphism-ish collapse.

Genotype digest: exact bytes of the canonical genome JSON (includes inactive genes).
Phenotype digest: digest over the *behaviorally relevant* compiled structure —
unit multiset (by type), families, operators that are actually executable given
topology/executive.  Two genotypes with the same phenotype digest are duplicates
for capability analysis (#221 E2 checklist; hostile test 'genotype diversity
collapses to same phenotype').
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List

from morphology.schema import OCMMorphologyGenomeV1


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def genotype_digest(g: OCMMorphologyGenomeV1) -> str:
    return g.digest()


def phenotype_obj(g: OCMMorphologyGenomeV1, active_unit_types: Iterable[str],
                  active_operators: Iterable[str]) -> Dict[str, Any]:
    """Behaviorally relevant projection.  ``active_*`` come from compile.py."""
    return {
        "F_arch": g.F_arch,
        "unit_types": sorted(active_unit_types),
        "T_family": g.T_family,
        "O_active": sorted(active_operators),
        "Pi_arch": g.Pi_arch,
        "L": g.L,
        "R": g.R,
        "K": g.K,
        "theta_phenotypic": {k: round(float(v), 6) for k, v in sorted(g.theta.items())
                             if k in _PHENOTYPIC_THETA},
    }


_PHENOTYPIC_THETA = frozenset({
    "queue_budget", "probe_budget", "expansion_cap", "consolidation_threshold",
    "index_build", "bidding_temperature",
})


def phenotype_digest(g: OCMMorphologyGenomeV1, active_unit_types: Iterable[str],
                     active_operators: Iterable[str]) -> str:
    return hashlib.sha256(
        canonical_json(phenotype_obj(g, active_unit_types, active_operators))
        .encode("utf-8")).hexdigest()


def collapse_duplicates(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """Exact duplicate/isomorphism-ish collapse by ``key`` (e.g. phenotype digest).

    Order-preserving; each survivor records how many genotypes collapsed into it.
    """
    seen: Dict[str, Dict[str, Any]] = {}
    order: List[Dict[str, Any]] = []
    for it in items:
        k = it[key]
        if k in seen:
            seen[k]["collapsed_genotypes"] = seen[k].get("collapsed_genotypes", 1) + 1
        else:
            copy = dict(it)
            copy["collapsed_genotypes"] = 1
            seen[k] = copy
            order.append(copy)
    return order
