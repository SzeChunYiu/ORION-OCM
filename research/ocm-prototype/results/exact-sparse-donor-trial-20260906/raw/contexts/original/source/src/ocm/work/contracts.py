"""TaskContract.v1, generic Operator, SkillCapsule.v1, TransferMap.v1 (M9 §1–§4).

* `TaskContract` — everything an arm receives: initial observable state, goal/success condition,
  allowed and forbidden actions, available information, hidden protected state (never shown to
  the arm; only the checker reads it), budgets, authority scope, checker, side-effect policy,
  rollback semantics.
* `Operator` — representation-neutral: preconditions over an observable state, a backend that
  transforms state (may raise), expected effects, termination, checker, resource model, warrant,
  known failures, dependencies, lineage.  A method is a composition of operators (`Skill`).
* `SkillCapsule.v1` — the split that enables *partial* transfer: an invariant procedure skeleton
  (a sequence of abstract steps naming *roles*), domain bindings (role → concrete operator id in a
  domain), and an environment adapter (state accessors).  Applying a capsule in a new domain
  requires bindings for every role; a missing binding is `ADAPTER_REQUIRED`, never a guess.
* `TransferMap.v1` — source skill → target domain: role mapping, shared preconditions, the
  invariant core, discarded components, adapter, predicted gain, required tests, observed
  gain/harm, warrant = Λ(source) ⊗ Λ(correspondence) (never stronger), scope.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.types import Authority, Scope
from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles

State = dict[str, Any]


@dataclass(frozen=True)
class TaskContract:
    task_id: str
    version: str
    domain: str
    initial_state: Mapping[str, Any]
    goal: str
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    information: tuple[str, ...]                    # observable keys
    hidden: Mapping[str, Any]                       # protected; checker-only
    budget_steps: int
    budget_interactions: int
    authority: Authority
    checker: Callable[[Mapping[str, Any], Mapping[str, Any]], bool]   # (final observable state, hidden) → success
    side_effect_policy: str = "sandboxed"
    rollback: str = "snapshot"

    def observable(self, state: Mapping[str, Any]) -> dict[str, Any]:
        return {k: state[k] for k in self.information if k in state}


@dataclass(frozen=True)
class Operator:
    operator_id: str
    version: str
    domain: str
    preconditions: Callable[[Mapping[str, Any]], bool]
    backend: Callable[[dict[str, Any]], dict[str, Any]]       # returns the new state (pure)
    expected_effects: tuple[str, ...]
    terminates: Callable[[Mapping[str, Any]], bool]
    checker: Callable[[Mapping[str, Any]], bool]              # post-condition on the observable state
    cost: int = 1
    warrant: WarrantProfile = field(default_factory=WarrantProfile.one)
    authority: Authority = field(default_factory=Authority)
    scope: Scope = field(default_factory=Scope.universal)
    known_failures: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    role: str = ""                                            # abstract role this operator can fill


class StepOutcome(str, Enum):
    APPLIED = "APPLIED"
    PRECONDITION_FAILED = "PRECONDITION_FAILED"
    BACKEND_FAILED = "BACKEND_FAILED"
    CHECK_FAILED = "CHECK_FAILED"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class Step:
    operator_id: str
    outcome: StepOutcome
    detail: str = ""


def apply_operator(op: Operator, state: dict[str, Any], contract: TaskContract) -> tuple[dict[str, Any], Step]:
    """Every action passes the contract: forbidden actions and authority are refused before the
    backend runs (M9 §15: a high score with unauthorized side effects is not success)."""
    if op.operator_id in contract.forbidden_actions or (contract.allowed_actions and op.operator_id not in contract.allowed_actions):
        return state, Step(op.operator_id, StepOutcome.FORBIDDEN)
    if not (op.authority <= contract.authority):
        return state, Step(op.operator_id, StepOutcome.UNAUTHORIZED)
    try:
        precondition = op.preconditions(deepcopy(state))
        if type(precondition) is not bool:
            return state, Step(op.operator_id, StepOutcome.CANNOT_CHECK, "precondition returned no boolean verdict")
        if not precondition:
            return state, Step(op.operator_id, StepOutcome.PRECONDITION_FAILED)
    except Exception as exc:
        return state, Step(op.operator_id, StepOutcome.CANNOT_CHECK, f"precondition unavailable: {type(exc).__name__}")
    try:
        new = op.backend(deepcopy(state))
    except Exception as exc:  # noqa: BLE001
        return state, Step(op.operator_id, StepOutcome.BACKEND_FAILED, f"{type(exc).__name__}: {exc}")
    if type(new) is not dict:
        return state, Step(op.operator_id, StepOutcome.BACKEND_FAILED, "backend returned no state")
    try:
        checked = op.checker(deepcopy(new))
        if type(checked) is not bool:
            return state, Step(op.operator_id, StepOutcome.CANNOT_CHECK, "checker returned no boolean verdict")
    except Exception as exc:
        return state, Step(op.operator_id, StepOutcome.CANNOT_CHECK, f"checker unavailable: {type(exc).__name__}")
    if not checked:
        return state, Step(op.operator_id, StepOutcome.CHECK_FAILED)
    return new, Step(op.operator_id, StepOutcome.APPLIED)


# ------------------------------------------------------------------ skills
@dataclass(frozen=True)
class Skill:
    """A method = ordered composition of roles with optional guards; concrete only with bindings."""
    skill_id: str
    skeleton: tuple[str, ...]                                 # abstract roles in order
    bindings: Mapping[str, str]                               # role → operator id (this domain)
    domain: str
    warrant: WarrantProfile
    adapter: Mapping[str, str] = field(default_factory=dict)  # state-key correspondence used by the bindings
    known_failures: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    scope: Scope = field(default_factory=Scope.universal)

    def liveness(self, revoked: Iterable[Hashable]) -> Liveness:
        return self.warrant.liveness(revoked)


@dataclass(frozen=True)
class SkillCapsule:
    """SkillCapsule.v1: invariant skeleton + domain bindings + environment adapter (M9 §3)."""
    capsule_id: str
    signature: str                                            # semantic signature (what it accomplishes)
    skeleton: tuple[str, ...]
    domain_bindings: Mapping[str, Mapping[str, str]]          # domain → role → operator id
    adapters: Mapping[str, Mapping[str, str]]                 # domain → state-key correspondence
    warrant: WarrantProfile
    expected_effects: tuple[str, ...] = ()
    known_failures: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()

    def instantiate(self, domain: str, *, extra_warrant: WarrantProfile | None = None) -> Skill | None:
        b = self.domain_bindings.get(domain)
        if b is None or any(r not in b for r in self.skeleton):
            return None                                       # ADAPTER_REQUIRED
        w = self.warrant if extra_warrant is None else self.warrant.meet(extra_warrant)
        return Skill(f"{self.capsule_id}@{domain}", self.skeleton, dict(b), domain, w, dict(self.adapters.get(domain, {})), self.known_failures, self.lineage + (self.capsule_id,))


class TransferVerdict(str, Enum):
    TRANSFER = "TRANSFER"
    ADAPTER_REQUIRED = "ADAPTER_REQUIRED"
    REFUSE_TRANSFER = "REFUSE_TRANSFER"
    REFINE_REQUIRED = "REFINE_REQUIRED"
    LEARN_NEW = "LEARN_NEW"


@dataclass(frozen=True)
class TransferMap:
    transfer_id: str
    source_skill: str
    target_domain: str
    role_mapping: Mapping[str, str]                           # source role → target operator id
    shared_preconditions: tuple[str, ...]
    invariant_core: tuple[str, ...]                           # roles that transfer unchanged
    discarded: tuple[str, ...]                                # source components dropped
    adapter: Mapping[str, str]
    predicted_gain: float
    required_tests: tuple[str, ...]
    correspondence_warrant: WarrantProfile
    scope: Scope = field(default_factory=Scope.universal)
    observed_gain: float | None = None
    observed_harm: float | None = None
    failure_modes: tuple[str, ...] = ()

    def warrant(self, source: Skill) -> WarrantProfile:
        """Λ(transported) = Λ(source) ⊗ Λ(correspondence) — never stronger than either (M9 §4)."""
        return source.warrant.meet(self.correspondence_warrant)


def transported_skill(source: Skill, tm: TransferMap, target_ops: Mapping[str, Operator]) -> tuple[TransferVerdict, Skill | None, str]:
    """Build the target skill from a transfer map; refuse when the correspondence is dead, when a
    role has no target binding (adapter required), or when a target operator's *semantics*
    (expected effects) contradicts the role (superficial similarity, T7)."""
    if tm.correspondence_warrant.liveness(()) is Liveness.DEAD:
        return TransferVerdict.REFUSE_TRANSFER, None, "correspondence dead"
    bindings: dict[str, str] = {}
    for role in source.skeleton:
        tgt = tm.role_mapping.get(role)
        if tgt is None:
            return TransferVerdict.ADAPTER_REQUIRED, None, f"no binding for role {role}"
        op = target_ops.get(tgt)
        if op is None:
            return TransferVerdict.ADAPTER_REQUIRED, None, f"unknown target operator {tgt}"
        if op.role and op.role != role:
            return TransferVerdict.REFUSE_TRANSFER, None, f"{tgt} has role {op.role}, not {role} (superficial similarity)"
        bindings[role] = tgt
    return TransferVerdict.TRANSFER, Skill(f"{source.skill_id}->{tm.target_domain}", source.skeleton, bindings, tm.target_domain, tm.warrant(source), dict(tm.adapter), source.known_failures, source.lineage + (tm.transfer_id,), tm.scope), "ok"


def mutant_similarity_transfer(source: Skill, target_domain: str, target_ops: Mapping[str, Operator], similarity: float) -> Skill | None:
    """Planted (M9 §4 / §18): transfer because the operator *names* look alike; keeps the source
    warrant untouched (no correspondence factor)."""
    if similarity < 0.5:
        return None
    ops = list(target_ops)
    bindings = {role: next((o for o in ops if role.split("_")[0] in o), ops[0]) for role in source.skeleton}
    return Skill(f"{source.skill_id}~>{target_domain}", source.skeleton, bindings, target_domain, source.warrant)
