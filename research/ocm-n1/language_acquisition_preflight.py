"""Preflight the N1 'learning how to learn language' measurement.

The historical M5 aligned-demonstration construction task is excellent for
checking version-space correctness, but it may be too low-entropy for the much
stronger #52/#53 meta-learning claim.  In a fully aligned S/V/O demonstration,
all three semantic roles are observed, so one example can identify the word
order from the six registered permutations.  If the cold-start floor is already
one demonstration, a later family cannot show a 100->30->10->3 style decline on
that endpoint.

This module measures that floor on the frozen M5 transitive task and registers
the design consequence.  It is DEVELOPMENT_CALIBRATION_ONLY and reads no N1
protected outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ocm.evaluation import m5_acquisition_eval as M5
from ocm.language import acquisition as AQ
from ocm.language import microworld as W


@dataclass(frozen=True)
class AcquisitionFloor:
    family: str
    hypothesis_count: int
    first_pass_demos: int | None
    statuses: tuple[tuple[int, str], ...]


def transitive_aligned_demo_floor(max_demos: int = 6) -> AcquisitionFloor:
    if max_demos < 1:
        raise ValueError("max_demos must be positive")
    _, seed = M5.frozen_inventory()
    lexicon = M5.frozen_lexicon()
    examples = W.generate()
    dev = [
        (e.utterance, e.meaning)
        for e in examples
        if e.split == "dev" and e.family == "transitive"
    ]
    family = M5.transitive_family(seed, [u for u, _ in dev])
    statuses = []
    first_pass = None
    for k in range(1, min(max_demos, len(dev)) + 1):
        demos = [
            AQ.Demonstration(u, meaning, f"preflight:demo:{i + 1}")
            for i, (u, meaning) in enumerate(dev[:k])
        ]
        proposal = AQ.acquire(family, lexicon, demos)
        statuses.append((k, proposal.status.value))
        if proposal.status.value == "PASS" and first_pass is None:
            first_pass = k
    return AcquisitionFloor(
        family.family,
        len(family.hypotheses),
        first_pass,
        tuple(statuses),
    )


def run() -> dict[str, Any]:
    floor = transitive_aligned_demo_floor()
    if floor.first_pass_demos == 1:
        terminal = "CURRENT_ALIGNED_CONSTRUCTION_TASK_HAS_ONE_DEMO_FLOOR"
        consequence = (
            "Do not use the inherited aligned S/V/O family as the primary N1 meta-learning endpoint. "
            "Register harder families with latent/partial structure or staged evidence so cold-start acquisition "
            "requires multiple discriminating observations; preserve one-shot families as correctness controls."
        )
    elif floor.first_pass_demos is None:
        terminal = "CURRENT_TASK_DOES_NOT_REACH_PASS"
        consequence = "Repair or replace the task before using it in an acquisition-cost curve."
    else:
        terminal = "CURRENT_TASK_HAS_MEASURABLE_MULTI_DEMO_RANGE"
        consequence = "It may be retained as one candidate family, subject to difficulty/order matching."
    return {
        "receipt": "N1_LANGUAGE_ACQUISITION_PREFLIGHT_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "family": floor.family,
        "hypothesis_count": floor.hypothesis_count,
        "first_pass_demos": floor.first_pass_demos,
        "statuses": [{"demos": n, "status": status} for n, status in floor.statuses],
        "terminal": terminal,
        "design_consequence": consequence,
        "registered_n1_primary_endpoint_requirements": [
            "cold-start family acquisition must have a non-trivial multi-observation range",
            "family difficulty must be frozen independently of curriculum order",
            "related/unrelated/harmful-transfer families must be declared before outcomes",
            "each later saving must identify reused learned objects or acquisition procedures",
            "persistent grammar/skill-memory and continual-adaptation parents receive the same prior information",
            "one-shot correctness families remain secondary controls, not the meta-learning headline",
        ],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
