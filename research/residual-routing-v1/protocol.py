"""R0-D5: the frozen R0 protocol.

#152 requires the protocol to be frozen before scored execution, and a pilot to
be kept separate from it.  Both apply here and both are recorded.

The pilot
---------

Two pilot runs preceded this freeze and neither is scored evidence:

1. ``tests/m2`` under the instrument, which established that the wrapper records
   real selection points and restores the runtime afterwards. It reported 94
   selection points, 22 of them with more than one admissible candidate.
2. a full-suite run under the same instrument, which validated the instrument at
   population scale and revealed that per-candidate work was not being recorded,
   leaving the BEFORE/CHOSEN split as a bound rather than an exact figure. The
   instrument was repaired for that and the pilot's numbers are not used.

That is exactly the repair-and-separate the issue permits. The scored execution
below runs after this plan's digest exists.

Why the test suite is the population
------------------------------------

#152 requires real current repository workloads and forbids inventing a
favourable synthetic routing world. The repository's own test suite is the only
place the runtime is exercised on real tasks at volume: it is what the project
actually runs, it covers every module that reaches ``solve``, and no part of it
was written for this study. Its weakness is declared rather than argued away --
tests are chosen to exercise behaviour, not to represent a task ecology's
frequency distribution, so ``rho_R`` here is a rate over exercised selection
points and not over a deployment workload.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

import contract
import frontier
import identifiability

R0_PLAN: Mapping[str, Any] = {
    "study_id": "RESIDUAL_ROUTING_OPPORTUNITY_V1",
    "issue": "SzeChunYiu/ORION-OCM#152",
    "unlocks": "SzeChunYiu/ORION-OCM#71",
    "authority": "EVIDENCE_ONLY. No ML, NN, bandit or router is implemented, proposed as "
                 "code, or run. The study reads and counts the existing exact policy.",
    "population": {
        "definition": "every invocation of ocm.runtime.solve.compose_stage reached by the "
                      "repository's own test suite at the frozen commit",
        "command": "python -m pytest tests -q -p harvest_plugin",
        "unit": "one selection point = one compose_stage call = one query q",
        "independent_units": "the test node id that produced the record; several selection "
                             "points may share one node and are not independent",
        "exclusions": [
            "research/ scripts that construct their own operators outside the runtime path "
            "-- they are not the deployed selection surface",
            "tests/test_distribution.py, which errors at collection on this commit for "
            "reasons predating this study (wheel build environment) and reaches no "
            "selection point",
            "the mechanical-proof and proof-runtime lanes, which supply a single operator "
            "per solve and therefore register |A^E| <= 1 rows rather than routing rows",
        ],
    },
    "resource_coordinates": ["composition_work", "verification_calls"],
    "noninferiority": "a transformation is admissible only if it preserves every protected "
                      "coordinate of its contract exactly; there is no tolerance margin",
    "selection_contracts": [c for c in contract.CONTRACTS],
    "counterfactual_identification_route": identifiability.ROUTE,
    "safe_speculation_budget": "none used; no candidate is executed by this study",
    "primary_terminal_rule": (
        "If a material fraction of queries has |A^E| > 1 AND a router could recover work "
        "that an exact policy cannot AND that recovery is answer-safe AND it survives the "
        "lifetime inequality, the terminal is RESIDUAL_ROUTING_OPPORTUNITY_CONFIRMED. If "
        "the recoverable work is entirely available to an exact early-exit policy, the "
        "terminal is EXACT_POLICY_SUFFICIENT. If no query admits more than one candidate, "
        "NO_RESIDUAL_ROUTING_OPPORTUNITY. If candidate outcomes are unobserved, "
        "CANNOT_CHECK_COUNTERFACTUAL_OPERATOR_OUTCOMES. If reordering cannot be shown to "
        "preserve the chosen operator, SELECTION_POLICY_EQUIVALENCE_NOT_ESTABLISHED. If a "
        "routing residual exists but cannot repay a learner's per-use cost, "
        "RESIDUAL_TOO_SMALL_TO_AMORTIZE_ANY_LEARNER."),
    "negative_terminals": [
        "NO_RESIDUAL_ROUTING_OPPORTUNITY", "EXACT_POLICY_SUFFICIENT",
        "GUARDED_REPRESENTATION_SUFFICIENT", "COUNTERFACTUAL_VALUE_NOT_IDENTIFIABLE",
        "SELECTION_POLICY_EQUIVALENCE_NOT_ESTABLISHED",
        "RESIDUAL_TOO_SMALL_TO_AMORTIZE_ANY_LEARNER", "ROUTING_DEMAND_TOO_LOW",
        "REPRESENTATION_CHANNEL_INSUFFICIENT",
        "CANNOT_CHECK_COUNTERFACTUAL_OPERATOR_OUTCOMES",
    ],
    "predictions_frozen_before_scored_execution": {
        "F1": "A material fraction of selection points has |A^E| > 1, so the trivial "
              "theorem region of #152 does not settle the question by itself.",
        "F2": "Incumbent work is invariant under any reordering of the admissible "
              "sequence, because compose and check have no early exit. Δ(q) under pure "
              "reordering is therefore identically zero.",
        "F3": "Work IS recoverable by stopping at the first passing candidate, and that "
              "policy is exact, needs no learner, and preserves decision, answer and "
              "chosen operator under contract C1.",
        "F4": "The residual specific to ROUTING -- work spent on non-passing candidates "
              "BEFORE the answer, recoverable only by knowing which candidate passes -- is "
              "small relative to the early-exit recovery.",
        "F5": "On queries with more than one passing candidate, reordering changes the "
              "chosen operator and is therefore outside every contract registered here.",
    },
    "kill_criterion": (
        "If the routing-specific residual is large, answer-safe, repeatedly demanded and "
        "repays a learner's per-use cost, this study must return "
        "RESIDUAL_ROUTING_OPPORTUNITY_CONFIRMED even though every prior expectation in this "
        "repository points the other way. The study stops there and does not proceed into "
        "learned routing."),
    "frontier": frontier.inventory(),
}


#: Fields of ``R0_PLAN["frontier"]`` that describe WHERE the plan was evaluated
#: rather than WHAT it says. They change with every commit.
VOLATILE_FRONTIER_FIELDS = ("commit", "branch", "tree_is_clean_for_bound_sources")


def commitment() -> str:
    """The digest as originally published, environment included.

    DEFECT, recorded rather than repaired: this hashes ``frontier.inventory()``,
    which embeds ``git rev-parse HEAD``. The digest therefore changes on every
    subsequent commit and can only be reproduced at the exact commit that
    produced the receipt. A frozen commitment whose whole purpose is later
    re-verification must not depend on when it is re-verified.

    The function is left exactly as it was so the published digest stays
    explicable. ``plan_commitment`` is the re-verifiable form, and the check that
    actually carries scientific weight -- did the bound runtime sources change --
    is ``bound_sources_match``.
    """
    body = json.dumps(R0_PLAN, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


def plan_commitment() -> str:
    """The digest of what the plan SAYS, stable across commits.

    Identical to ``commitment`` except that the volatile environment fields are
    dropped. The bound-source hashes are KEPT, because a plan evaluated against
    different runtime files is a different plan.
    """
    plan = dict(R0_PLAN)
    frontier_view = {k: v for k, v in plan["frontier"].items()
                     if k not in VOLATILE_FRONTIER_FIELDS}
    plan["frontier"] = frontier_view
    body = json.dumps(plan, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


def bound_sources_match(receipt: Mapping[str, Any]) -> dict:
    """Do the files this study made claims about still have the same bytes?

    This is the load-bearing check and it was not being made. The published
    receipt records a sha256 per bound source; this recomputes them from the
    working tree and reports any drift by name. If a bound source has changed,
    every terminal in the receipt is a statement about a runtime that no longer
    exists, and that must surface as a failure rather than as a stale digest.
    """
    stored = receipt["protocol"]["frontier"]["bound_sources"]
    current = {rel: frontier.sha256(frontier.REPO / rel) for rel in stored}
    drifted = sorted(rel for rel in stored if stored[rel] != current[rel])
    return {"checked": sorted(stored), "drifted": drifted,
            "all_match": not drifted, "current": current}
