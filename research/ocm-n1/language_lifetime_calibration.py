"""Exact synthetic lifetime-language calibration for #52/#53.

This is deliberately harder than the inherited one-demo M5 construction task.
Each task is a finite permutation version space.  Teacher observations are
pairwise order constraints.  Related later tasks strictly extend an earlier role
set, so a persistent learner may reuse *previously justified order constraints*
when they are in scope.  Reset arms cannot.

This demonstrates one precise mechanism for acquisition amortization:
reusable structured competence reduces the later search/information burden.
It does NOT establish a Machine-Epistemics residual: an equally informed
persistent grammar/skill-library parent receives the same reusable constraints
and is expected to match the curve.

Harmful transfer is fail-closed.  Borrowed constraints are provisional for the
new family.  If observed evidence empties the borrowed version space, the learner
restarts from the full family using the already-seen observations and does not
promote the conflicting family into the broader scope.
"""
from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Iterable, Mapping, Sequence


Constraint = tuple[str, str]  # a must occur before b
Order = tuple[str, ...]


@dataclass(frozen=True)
class OrderTask:
    task_id: str
    scope: str
    roles: tuple[str, ...]
    gold: Order
    observations: tuple[Constraint, ...]
    related: bool

    def __post_init__(self) -> None:
        if set(self.roles) != set(self.gold) or len(self.roles) != len(self.gold):
            raise ValueError("gold order must be a permutation of roles")
        if any(a not in self.roles or b not in self.roles or a == b for a, b in self.observations):
            raise ValueError("observation refers to invalid roles")
        if not all(before(self.gold, c) for c in self.observations):
            raise ValueError("teacher observation contradicts registered gold")


@dataclass(frozen=True)
class SolveReceipt:
    task_id: str
    scope: str
    full_hypotheses: int
    initial_hypotheses_after_reuse: int
    observations_consumed: int
    reused_constraints: tuple[Constraint, ...]
    borrowed_rejected: bool
    surviving_order: Order
    promoted_constraints: tuple[Constraint, ...]


@dataclass
class ConstraintMemory:
    by_scope: dict[str, set[Constraint]]

    def __init__(self) -> None:
        self.by_scope = {}

    def reusable_for(self, scope: str, roles: Iterable[str]) -> tuple[Constraint, ...]:
        role_set = set(roles)
        return tuple(sorted(c for c in self.by_scope.get(scope, set()) if c[0] in role_set and c[1] in role_set))

    def promote_order(self, scope: str, order: Order) -> tuple[Constraint, ...]:
        constraints = tuple((order[i], order[j]) for i in range(len(order)) for j in range(i + 1, len(order)))
        self.by_scope.setdefault(scope, set()).update(constraints)
        return constraints


def before(order: Order, constraint: Constraint) -> bool:
    a, b = constraint
    return order.index(a) < order.index(b)


def hypotheses(roles: Sequence[str]) -> tuple[Order, ...]:
    return tuple(itertools.permutations(tuple(roles)))


def filter_constraints(space: Iterable[Order], constraints: Iterable[Constraint]) -> tuple[Order, ...]:
    cs = tuple(constraints)
    return tuple(order for order in space if all(before(order, c) for c in cs))


def solve(task: OrderTask, memory: ConstraintMemory | None, *, promote: bool = True) -> SolveReceipt:
    full = hypotheses(task.roles)
    borrowed = () if memory is None else memory.reusable_for(task.scope, task.roles)
    space = filter_constraints(full, borrowed)
    initial = len(space)
    if not space:
        # Corrupt memory is a hard failure rather than a hidden reset.
        raise ValueError("persistent constraint memory is internally inconsistent")

    seen: list[Constraint] = []
    borrowed_rejected = False
    for observation in task.observations:
        seen.append(observation)
        candidate = filter_constraints(space, (observation,))
        if not candidate and borrowed and not borrowed_rejected:
            # New evidence falsifies transfer.  Re-open from the declared full
            # family, replaying exactly the observations already paid for.
            borrowed_rejected = True
            candidate = filter_constraints(full, seen)
        space = candidate
        if not space:
            raise ValueError(f"registered observations are inconsistent for {task.task_id}")
        if len(space) == 1:
            break
    if len(space) != 1:
        raise ValueError(f"observations do not identify a unique order for {task.task_id}: {len(space)} survive")
    chosen = space[0]
    if chosen != task.gold:
        raise AssertionError("unique learned order differs from registered gold")

    promoted: tuple[Constraint, ...] = ()
    # A family whose transfer was contradicted is treated as a scope exception.
    # It is learned for this task but not generalized into the broader scope.
    if promote and memory is not None and not borrowed_rejected:
        promoted = memory.promote_order(task.scope, chosen)
    return SolveReceipt(
        task.task_id,
        task.scope,
        len(full),
        initial,
        len(seen),
        borrowed,
        borrowed_rejected,
        chosen,
        promoted,
    )


def registered_tasks() -> tuple[OrderTask, ...]:
    return (
        OrderTask(
            "L1_basic_SVO",
            "lang-a",
            ("S", "V", "O"),
            ("S", "V", "O"),
            (("S", "V"), ("V", "O")),
            True,
        ),
        OrderTask(
            "L2_add_modifier",
            "lang-a",
            ("S", "V", "O", "M"),
            ("S", "V", "O", "M"),
            (("O", "M"), ("S", "V"), ("V", "O")),
            True,
        ),
        OrderTask(
            "L3_add_question_marker",
            "lang-a",
            ("S", "V", "O", "M", "Q"),
            ("S", "V", "O", "M", "Q"),
            (("M", "Q"), ("O", "M"), ("V", "O"), ("S", "V")),
            True,
        ),
        OrderTask(
            "U1_unrelated_SOV_language",
            "lang-b",
            ("S", "O", "V"),
            ("S", "O", "V"),
            (("S", "O"), ("O", "V")),
            False,
        ),
        OrderTask(
            "H1_conflicting_order_same_scope",
            "lang-a",
            ("S", "V", "O"),
            ("S", "O", "V"),
            (("O", "V"), ("S", "O")),
            False,
        ),
    )


def run_arm(*, persistent: bool) -> list[SolveReceipt]:
    memory = ConstraintMemory() if persistent else None
    receipts = []
    for task in registered_tasks():
        receipts.append(solve(task, memory, promote=persistent))
    return receipts


def serialize(receipts: Sequence[SolveReceipt]) -> list[dict]:
    return [
        {
            "task_id": r.task_id,
            "scope": r.scope,
            "full_hypotheses": r.full_hypotheses,
            "initial_hypotheses_after_reuse": r.initial_hypotheses_after_reuse,
            "observations_consumed": r.observations_consumed,
            "reused_constraints": [list(c) for c in r.reused_constraints],
            "borrowed_rejected": r.borrowed_rejected,
            "surviving_order": list(r.surviving_order),
            "promoted_constraint_count": len(r.promoted_constraints),
        }
        for r in receipts
    ]


def run() -> dict:
    ocm = run_arm(persistent=True)
    # Strongest isolated parent gets exactly the same scoped persistent grammar
    # constraint memory.  Equality is a required calibration property.
    skill_parent = run_arm(persistent=True)
    reset = run_arm(persistent=False)
    related_ids = {t.task_id for t in registered_tasks() if t.related}
    ocm_related = [r.observations_consumed for r in ocm if r.task_id in related_ids]
    reset_related = [r.observations_consumed for r in reset if r.task_id in related_ids]
    harmful = next(r for r in ocm if r.task_id.startswith("H1_"))
    unrelated = next(r for r in ocm if r.task_id.startswith("U1_"))
    return {
        "receipt": "N1_LANGUAGE_LIFETIME_CALIBRATION_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "mechanism": "scoped reusable pairwise order constraints over nested construction families",
        "ocm": serialize(ocm),
        "persistent_skill_grammar_parent": serialize(skill_parent),
        "reset_between_families": serialize(reset),
        "related_observation_curve_ocm": ocm_related,
        "related_observation_curve_reset": reset_related,
        "amortization_present_vs_reset": sum(ocm_related) < sum(reset_related),
        "strong_parent_matches_exactly": serialize(ocm) == serialize(skill_parent),
        "unrelated_scope_reuse_count": len(unrelated.reused_constraints),
        "harmful_transfer_rejected": harmful.borrowed_rejected,
        "harmful_task_cost_equals_reset": harmful.observations_consumed == next(
            r.observations_consumed for r in reset if r.task_id == harmful.task_id
        ),
        "isolated_terminal": "PARENT_SUFFICIENT",
        "meta_learning_terminal": "NO_META_LEARNING_CLAIM_FROM_CONSTRAINT_REUSE",
        "interpretation": (
            "The nested related families exhibit real acquisition amortization relative to reset because previously learned "
            "order constraints shrink later version spaces.  The equally informed persistent grammar/skill parent matches "
            "exactly, so this is evidence that the measurement/hostiles work, not evidence of a unique Machine-Epistemics mechanism."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
