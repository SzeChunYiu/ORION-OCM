#!/usr/bin/env python3
"""Exact finite witnesses for Warranted Lifecycle Learning (WLL).

WLL distinguishes current behavior from future behavior induced by evidence,
scope, authority and verifier changes. This checker validates finite
calibration theorems and does not assert literature novelty.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class WarrantWorld:
    skill_count: int
    contexts_per_skill: int
    backup_support: tuple[int, ...]

    def __post_init__(self) -> None:
        expected = self.skill_count * self.contexts_per_skill
        if len(self.backup_support) != expected:
            raise ValueError("backup-support length mismatch")
        if any(bit not in (0, 1) for bit in self.backup_support):
            raise ValueError("backup-support state must be binary")

    def current_behavior(self) -> tuple[int, ...]:
        return (1,) * self.skill_count

    def post_primary_revocation(self, skill: int, context: int) -> int:
        if not 0 <= skill < self.skill_count:
            raise IndexError("skill out of range")
        if not 0 <= context < self.contexts_per_skill:
            raise IndexError("context out of range")
        return self.backup_support[skill * self.contexts_per_skill + context]

    def lifecycle_profile(self) -> tuple[int, ...]:
        return tuple(
            self.post_primary_revocation(skill, context)
            for skill in range(self.skill_count)
            for context in range(self.contexts_per_skill)
        )


def enumerate_worlds(skill_count: int, contexts_per_skill: int):
    width = skill_count * contexts_per_skill
    return tuple(
        WarrantWorld(skill_count, contexts_per_skill, bits)
        for bits in itertools.product((0, 1), repeat=width)
    )


def profile_partition(
    worlds: Iterable[WarrantWorld],
    *,
    lifecycle: bool,
    drop_challenge: int | None = None,
):
    partition: dict[tuple[int, ...], list[WarrantWorld]] = {}
    for world in worlds:
        profile = world.lifecycle_profile() if lifecycle else world.current_behavior()
        if drop_challenge is not None:
            index = drop_challenge
            if index < 0:
                index += len(profile)
            if not 0 <= index < len(profile):
                raise IndexError("challenge out of range")
            profile = profile[:index] + profile[index + 1 :]
        partition.setdefault(profile, []).append(world)
    return partition


def authority_scope(component_scopes: tuple[frozenset[int], ...]) -> frozenset[int]:
    if not component_scopes:
        raise ValueError("at least one component is required")
    scope = set(component_scopes[0])
    for component in component_scopes[1:]:
        scope.intersection_update(component)
    return frozenset(scope)


def union_scope_is_unsound(component_scopes: tuple[frozenset[int], ...]):
    safe = authority_scope(component_scopes)
    proposed = frozenset().union(*component_scopes)
    extra = sorted(proposed - safe)
    if not extra:
        return None
    context = extra[0]
    failing_component = next(
        index for index, scope in enumerate(component_scopes) if context not in scope
    )
    return {
        "context": context,
        "failing_component": failing_component,
        "component_scopes": [sorted(scope) for scope in component_scopes],
        "intersection_scope": sorted(safe),
        "union_scope": sorted(proposed),
        "countermodel": (
            "All components are correct inside their declared scopes; the identified "
            "component is wrong in the extra context. Union authorization therefore "
            "admits an unsupported composite output."
        ),
    }


def exact_unlearning_without_warrant() -> dict[str, object]:
    retrained_behavior = 1
    unlearned_behavior = 1
    live_claim = True
    valid_support_after_revocation = False
    return {
        "exact_behavioral_unlearning": unlearned_behavior == retrained_behavior,
        "warrant_correctness": not (live_claim and not valid_support_after_revocation),
        "witness": {
            "retrained_behavior": retrained_behavior,
            "unlearned_behavior": unlearned_behavior,
            "live_claim": live_claim,
            "valid_support_after_revocation": valid_support_after_revocation,
        },
    }


def warrant_without_exact_unlearning() -> dict[str, object]:
    retrained_raw_model_bit = 0
    updated_raw_model_bit = 1
    authorized_output = "ABSTAIN"
    unsupported_live_output = False
    return {
        "warrant_correctness": (
            authorized_output == "ABSTAIN" and not unsupported_live_output
        ),
        "exact_model_unlearning": updated_raw_model_bit == retrained_raw_model_bit,
        "witness": {
            "retrained_raw_model_bit": retrained_raw_model_bit,
            "updated_raw_model_bit": updated_raw_model_bit,
            "authorized_output": authorized_output,
        },
    }


def run_exact_calibration() -> dict[str, object]:
    skill_count = 3
    contexts_per_skill = 2
    worlds = enumerate_worlds(skill_count, contexts_per_skill)
    current = profile_partition(worlds, lifecycle=False)
    lifecycle = profile_partition(worlds, lifecycle=True)
    dropped = profile_partition(worlds, lifecycle=True, drop_challenge=-1)

    if len(worlds) != 64:
        raise AssertionError("world-count drift")
    if len(current) != 1:
        raise AssertionError("worlds should be currently behaviorally equivalent")
    if len(lifecycle) != 64 or any(len(group) != 1 for group in lifecycle.values()):
        raise AssertionError("lifecycle profiles should distinguish all worlds")
    if len(dropped) != 32 or any(len(group) != 2 for group in dropped.values()):
        raise AssertionError("planted challenge deletion did not create paired collisions")

    unlearning_only = exact_unlearning_without_warrant()
    warrant_only = warrant_without_exact_unlearning()
    if not unlearning_only["exact_behavioral_unlearning"]:
        raise AssertionError("unlearning positive witness failed")
    if unlearning_only["warrant_correctness"]:
        raise AssertionError("unlearning witness should violate warrant correctness")
    if not warrant_only["warrant_correctness"]:
        raise AssertionError("warrant positive witness failed")
    if warrant_only["exact_model_unlearning"]:
        raise AssertionError("warrant witness should fail exact unlearning")

    universe = frozenset(range(3))
    nonempty_scopes = tuple(
        frozenset(i for i in universe if (mask >> i) & 1)
        for mask in range(1, 1 << len(universe))
    )
    checked = 0
    countermodels = 0
    no_alarm = 0
    example = None
    for scopes in itertools.product(nonempty_scopes, repeat=3):
        checked += 1
        safe = authority_scope(scopes)
        if any(context not in scope for scope in scopes for context in safe):
            raise AssertionError("intersection scope is not sound")
        countermodel = union_scope_is_unsound(scopes)
        if countermodel is None:
            no_alarm += 1
        else:
            countermodels += 1
            if example is None:
                example = countermodel
    if countermodels == 0 or no_alarm == 0:
        raise AssertionError("scope checker lacks positive/no-alarm coverage")

    dimension = skill_count * contexts_per_skill
    return {
        "schema": "orion.ocm.warranted-lifecycle.exact-results.v1",
        "terminal": "PASS_FINITE_CALIBRATION_ONLY",
        "warrant_lift": {
            "skills": skill_count,
            "contexts_per_skill": contexts_per_skill,
            "warrant_bits": dimension,
            "latent_worlds": len(worlds),
            "current_behavior_classes": len(current),
            "lifecycle_equivalence_classes": len(lifecycle),
            "classes_after_planted_challenge_drop": len(dropped),
            "worlds_per_planted_collision": 2,
            "extra_exact_lifecycle_bits_required_without_queries_or_abstention": (
                math.ceil(math.log2(len(lifecycle) / len(current)))
            ),
        },
        "theorems_checked": {
            "lifecycle_equivalence_refines_current_behavior": True,
            "refinement_is_strict": len(lifecycle) > len(current),
            "behavioral_unlearning_does_not_imply_warrant_correctness": True,
            "warrant_correctness_does_not_imply_exact_model_unlearning": True,
            "composite_authority_scope_is_bounded_by_component_intersection": True,
        },
        "unlearning_incomparability": {
            "exact_unlearning_without_warrant": unlearning_only,
            "warrant_without_exact_unlearning": warrant_only,
        },
        "authority_scope": {
            "component_scope_tuples_checked": checked,
            "union_overauthorization_countermodels": countermodels,
            "no_alarm_equal_scope_cases": no_alarm,
            "example_union_countermodel": example,
        },
        "authority": {
            "finite_calibration": True,
            "literature_priority": False,
            "architecture_separation": False,
            "machine_unlearning_guarantee": False,
            "publication_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = run_exact_calibration()
    except (AssertionError, ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "error": str(exc)}, indent=2))
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        lift = result["warrant_lift"]
        print(
            "PASS: "
            f"{lift['latent_worlds']} currently equivalent worlds split into "
            f"{lift['lifecycle_equivalence_classes']} lifecycle classes; "
            f"planted drop leaves {lift['classes_after_planted_challenge_drop']} classes."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
