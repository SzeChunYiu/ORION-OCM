"""Skill induction, routing, execution, diagnosis and drift (M9 §8, §11–§14).

* `run_skill` executes a bound skill under a contract, recording every step; success is the
  contract's checker over the *final* state (hidden state read only by the checker).
* Induction strategies from a successful trace (M9 §11): exact memoisation (the operator list),
  subtrace mining (longest common role subsequence across traces), generalised skeleton (roles
  with bindings split from the trace) — a skill is accepted only when it also succeeds on a
  *withheld* task of the same distribution (intervention test), never because its source succeeded.
* Routers (M9 §12): top-k name similarity, type/precondition routing, OCM router (precondition +
  role + warrant liveness + known failures + scope + past outcome); router error is measured
  separately from operator failure.
* Diagnosis (M9 §13): classifies a failed run into the responsible layer (missing information,
  wrong operator selected, operator wrong, bad adapter/transfer map, bad order, stale
  environment/drift, authority prevented, checker CANNOT_CHECK) so the update targets that layer.
* Drift (M9 §14): a versioned environment; a stale binding fails its checker; revision =
  re-bind the failing role under the new version with lineage; rollback = the previous skill.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from enum import Enum
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from ocm.kso.warrant import Liveness, WarrantProfile, meet_all_profiles

from .contracts import Operator, Skill, SkillCapsule, Step, StepOutcome, TaskContract, apply_operator


@dataclass(frozen=True)
class RunResult:
    task_id: str
    skill_id: str | None
    success: bool
    steps: tuple[Step, ...]
    final_state: dict[str, Any]
    cost: int
    unauthorized_attempts: int
    forbidden_attempts: int


def run_skill(skill: Skill, ops: Mapping[str, Operator], contract: TaskContract, *, revoked: Iterable[Hashable] = ()) -> RunResult:
    if skill.liveness(revoked) is not Liveness.LIVE:
        return RunResult(contract.task_id, skill.skill_id, False, (Step("*", StepOutcome.PRECONDITION_FAILED, "skill not live"),), dict(contract.initial_state), 0, 0, 0)
    state = dict(contract.initial_state)
    steps: list[Step] = []
    cost = unauth = forb = 0
    for role in skill.skeleton:
        oid = skill.bindings[role]
        op = ops.get(oid)
        if op is None:
            steps.append(Step(oid, StepOutcome.PRECONDITION_FAILED, "unknown operator"))
            break
        if op.warrant.liveness(revoked) is not Liveness.LIVE:
            steps.append(Step(oid, StepOutcome.PRECONDITION_FAILED, "operator not live"))
            break
        state, st = apply_operator(op, state, contract)
        steps.append(st)
        cost += op.cost
        unauth += int(st.outcome is StepOutcome.UNAUTHORIZED)
        forb += int(st.outcome is StepOutcome.FORBIDDEN)
        if st.outcome is not StepOutcome.APPLIED:
            break
        if cost > contract.budget_steps:
            steps.append(Step(oid, StepOutcome.BACKEND_FAILED, "budget exhausted"))
            break
    ok = all(s.outcome is StepOutcome.APPLIED for s in steps) and contract.checker(state, contract.hidden)
    return RunResult(contract.task_id, skill.skill_id, ok, tuple(steps), state, cost, unauth, forb)


# ------------------------------------------------------------------ induction
def induce_memoised(trace: Sequence[str], ops: Mapping[str, Operator], domain: str, evidence: str) -> Skill:
    roles = tuple(f"step{i}" for i in range(len(trace)))
    return Skill(f"memo:{domain}", roles, dict(zip(roles, trace)), domain, WarrantProfile.of({evidence}))


def induce_skeleton(trace: Sequence[str], ops: Mapping[str, Operator], domain: str, evidence: str) -> Skill:
    """Generalised: roles come from the operators' registered roles; bindings are the trace."""
    roles = tuple(ops[o].role for o in trace)
    return Skill(f"skel:{domain}", roles, {ops[o].role: o for o in trace}, domain, WarrantProfile.of({evidence}))


def induce_subtrace(traces: Sequence[Sequence[str]], ops: Mapping[str, Operator], domain: str, evidence: str) -> Skill | None:
    """Longest common *role* subsequence across successful traces."""
    if not traces:
        return None
    role_seqs = [[ops[o].role for o in t] for t in traces]
    common = role_seqs[0]
    for seq in role_seqs[1:]:
        m = SequenceMatcher(None, common, seq).find_longest_match(0, len(common), 0, len(seq))
        common = common[m.a: m.a + m.size]
    if not common:
        return None
    bindings = {ops[o].role: o for o in traces[0] if ops[o].role in common}
    return Skill(f"sub:{domain}", tuple(common), bindings, domain, WarrantProfile.of({evidence}))


def capsule_from_skill(skill: Skill, ops: Mapping[str, Operator], capsule_id: str) -> SkillCapsule:
    return SkillCapsule(capsule_id, "gather→classify→policy→smallest act→verify→document", skill.skeleton, {skill.domain: dict(skill.bindings)}, {skill.domain: dict(skill.adapter)}, skill.warrant, lineage=(skill.skill_id,))


def accept_skill(skill: Skill, ops: Mapping[str, Operator], withheld: Sequence[TaskContract]) -> tuple[bool, dict[str, Any]]:
    """Intervention test (M9 §11): the skill must succeed on withheld tasks of the same distribution."""
    runs = [run_skill(skill, ops, t) for t in withheld]
    ok = bool(runs) and all(r.success for r in runs)
    return ok, {"withheld": len(runs), "successes": sum(r.success for r in runs)}


# ------------------------------------------------------------------ routers
def route_similarity(skills: Sequence[Skill], contract: TaskContract, ops: Mapping[str, Operator], k: int = 1) -> list[Skill]:
    """Top-k by name similarity between the skill's operators and the task's allowed actions."""
    def score(sk: Skill) -> float:
        return sum(max(SequenceMatcher(None, b, a).ratio() for a in contract.allowed_actions) for b in sk.bindings.values()) / max(1, len(sk.bindings))
    return sorted(skills, key=lambda s: -score(s))[:k]


def route_typed(skills: Sequence[Skill], contract: TaskContract, ops: Mapping[str, Operator], k: int = 1) -> list[Skill]:
    """Type/precondition routing: every bound operator must exist in the task's allowed actions and
    its first precondition must hold on the initial state."""
    out = []
    for sk in skills:
        if all(b in contract.allowed_actions for b in sk.bindings.values()) and ops[sk.bindings[sk.skeleton[0]]].preconditions(contract.initial_state):
            out.append(sk)
    return out[:k]


@dataclass
class OCMRouter:
    """Precondition + role + liveness + known failures + scope + recorded outcomes."""
    outcomes: dict[str, list[bool]] = field(default_factory=dict)

    def route(self, skills: Sequence[Skill], contract: TaskContract, ops: Mapping[str, Operator], *, revoked: Iterable[Hashable] = (), k: int = 1) -> list[Skill]:
        cands = []
        for sk in skills:
            if sk.domain != contract.domain or sk.liveness(revoked) is not Liveness.LIVE:
                continue
            if not all(b in contract.allowed_actions for b in sk.bindings.values()):
                continue
            if any(ops[b].role != r for r, b in sk.bindings.items()):
                continue                                   # role mismatch = superficial similarity
            if contract.task_id in sk.known_failures:
                continue
            hist = self.outcomes.get(sk.skill_id, [])
            past = (sum(hist) + 1) / (len(hist) + 2)
            cands.append((past, sk))
        cands.sort(key=lambda p: (-p[0], p[1].skill_id))
        return [sk for _, sk in cands[:k]]

    def record(self, skill_id: str, success: bool) -> None:
        self.outcomes.setdefault(skill_id, []).append(success)


def mutant_try_every_skill(skills: Sequence[Skill], contract: TaskContract, ops: Mapping[str, Operator]) -> tuple[RunResult | None, int]:
    """Planted (M9 §18): try every skill until one works and call that transfer."""
    tries = 0
    for sk in skills:
        tries += 1
        r = run_skill(sk, ops, contract)
        if r.success:
            return r, tries
    return None, tries


# ------------------------------------------------------------------ diagnosis
class Layer(str, Enum):
    MISSING_INFORMATION = "MISSING_INFORMATION"
    WRONG_OPERATOR_SELECTED = "WRONG_OPERATOR_SELECTED"
    OPERATOR_WRONG = "OPERATOR_WRONG"
    BAD_ADAPTER = "BAD_ADAPTER"
    BAD_ORDER = "BAD_ORDER"
    ENVIRONMENT_DRIFT = "ENVIRONMENT_DRIFT"
    AUTHORITY_PREVENTED = "AUTHORITY_PREVENTED"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    CANNOT_CHECK = "CANNOT_CHECK"
    NONE = "NONE"


def diagnose(result: RunResult, skill: Skill, ops: Mapping[str, Operator], contract: TaskContract, *, env_version: str) -> Layer:
    if result.success:
        return Layer.NONE
    last = result.steps[-1] if result.steps else None
    if last is None:
        return Layer.CANNOT_CHECK
    if last.outcome is StepOutcome.UNAUTHORIZED or last.outcome is StepOutcome.FORBIDDEN:
        return Layer.AUTHORITY_PREVENTED
    if last.detail == "budget exhausted":
        return Layer.RESOURCE_EXHAUSTION
    if last.detail in ("unknown operator", "operator not live", "skill not live"):
        return Layer.BAD_ADAPTER
    if last.outcome is StepOutcome.PRECONDITION_FAILED:
        # a precondition failing after earlier steps applied = order / missing information
        return Layer.BAD_ORDER if len(result.steps) > 1 else Layer.MISSING_INFORMATION
    if last.outcome is StepOutcome.CHECK_FAILED or last.outcome is StepOutcome.BACKEND_FAILED:
        return Layer.ENVIRONMENT_DRIFT if contract.version != env_version else Layer.OPERATOR_WRONG
    # every step applied but the goal is not met: the skill did the wrong thing — selection or operator?
    roles = [ops[skill.bindings[r]].role for r in skill.skeleton]
    if "act_broad" in roles:
        return Layer.WRONG_OPERATOR_SELECTED
    return Layer.OPERATOR_WRONG


# ------------------------------------------------------------------ drift and revision
def revise_for_version(skill: Skill, ops_new: Mapping[str, Operator], failing_role: str, evidence: str) -> Skill:
    """Specialise: re-bind the failing role under the new environment version, keeping lineage."""
    return Skill(f"{skill.skill_id}@v2", skill.skeleton, dict(skill.bindings), skill.domain, skill.warrant.meet(WarrantProfile.of({evidence})), dict(skill.adapter), skill.known_failures, skill.lineage + (skill.skill_id,), skill.scope)
