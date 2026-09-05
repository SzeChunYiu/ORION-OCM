"""SelfChangeProposal.v1, change classes and pre-outcome prediction (M11 §5–§8; batch 5 E4).

A proposal is a *candidate object* with proposal-only authority: it names its trigger evidence,
target component and layer, the incumbent fingerprint it replaces, the change class (C0
parameters … C5 whole organisation; C6 constitutional = recommendation packet only, never
adoptable through this path), predicted benefits and regressions on named *held-out* task
families, resource delta, preserved and reopened capabilities, a pre-registered discriminator,
rollback plan, scope/expiry, and its origin (existing alternative / transfer / recombination /
learned / ORION-V2 import / human) so imported fixes are never presented as autonomous invention.
`Prediction` is recorded *before* any protected outcome access and hashed; the proposal cannot
change its own status (`status` lives in the adoption ledger, not on the proposal).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, Sequence

from ocm.kso.types import Authority


class ChangeClass(str, Enum):
    C0_PARAMETERS = "C0"
    C1_ROUTER = "C1"
    C2_OPERATOR = "C2"
    C3_REPRESENTATION = "C3"
    C4_LEARNING_POLICY = "C4"
    C5_ORGANISATION = "C5"
    C6_CONSTITUTION = "C6"


class Origin(str, Enum):
    EXISTING_ALTERNATIVE = "existing_alternative"
    TRANSFER = "transfer"
    RECOMBINATION = "recombination"
    LEARNED = "learned"
    ORION_V2_IMPORT = "orion_v2_import"
    HUMAN = "human"


@dataclass(frozen=True)
class Prediction:
    """Pre-outcome prediction on held-out families (M11 §8): improve / regress / unchanged / reopen."""
    improve: tuple[str, ...]
    may_regress: tuple[str, ...]
    resource_delta: Mapping[str, float]
    invariants_unchanged: tuple[str, ...]
    must_reopen: tuple[str, ...]
    expected_failure_modes: tuple[str, ...]
    margin: float                                     # pre-registered tolerance for "matches"

    def digest(self) -> str:
        return hashlib.sha256(json.dumps({"i": self.improve, "r": self.may_regress, "d": dict(self.resource_delta), "u": self.invariants_unchanged, "o": self.must_reopen, "f": self.expected_failure_modes, "m": self.margin}, sort_keys=True).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class SelfChangeProposal:
    proposal_id: str
    version: str
    trigger_evidence: tuple[str, ...]
    target_component: str
    target_layer: str
    incumbent_fingerprint: str
    change_class: ChangeClass
    change: Mapping[str, Any]                         # the replacement / edit, declaratively
    apply: Callable[[Any], Any]                       # incumbent artifact → challenger artifact (pure)
    prediction: Prediction
    preserved_capabilities: tuple[str, ...]
    reopened_capabilities: tuple[str, ...]
    discriminator: str                                # pre-registered suite id
    rollback_plan: str
    scope: str
    expiry: str
    origin: Origin
    origin_ref: str = ""
    dev_tasks: tuple[str, ...] = ()                   # task ids the proposer saw while forming the change (E4 disjointness clause)
    authority: Authority = field(default_factory=lambda: Authority.of(proposal=1))

    def adoptable_through_cognition(self) -> bool:
        """C6 constitutional proposals are recommendation packets only (M11 §6)."""
        return self.change_class is not ChangeClass.C6_CONSTITUTION

    def fingerprint(self) -> str:
        # The external decision binds the complete declarative contract. The
        # host-supplied apply callback is deliberately not a code-identity proof.
        contract = {
            "schema": "ocm.self_change.declarative.v2", "id": self.proposal_id,
            "v": self.version, "trigger_evidence": self.trigger_evidence,
            "target": self.target_component, "target_layer": self.target_layer,
            "class": self.change_class.value, "change": self.change,
            "pred": self.prediction.digest(), "incumbent": self.incumbent_fingerprint,
            "preserved": self.preserved_capabilities, "reopened": self.reopened_capabilities,
            "discriminator": self.discriminator, "rollback_plan": self.rollback_plan,
            "scope": self.scope, "expiry": self.expiry, "origin": self.origin.value,
            "origin_ref": self.origin_ref, "dev_tasks": self.dev_tasks,
            "authority": self.authority.as_dict(), "implementation_identity": "HOST_SUPPLIED_UNVERIFIED",
        }
        return hashlib.sha256(json.dumps(contract, sort_keys=True, default=str).encode()).hexdigest()[:16]


def minimum_class_for(layer: str) -> ChangeClass:
    return {"D0": ChangeClass.C0_PARAMETERS, "D1": ChangeClass.C1_ROUTER, "D2": ChangeClass.C2_OPERATOR, "D5": ChangeClass.C2_OPERATOR, "D6": ChangeClass.C4_LEARNING_POLICY, "D3": ChangeClass.C3_REPRESENTATION, "D4": ChangeClass.C3_REPRESENTATION, "D7": ChangeClass.C5_ORGANISATION, "D8": ChangeClass.C6_CONSTITUTION}[layer]


CLASS_ORDER = [ChangeClass.C0_PARAMETERS, ChangeClass.C1_ROUTER, ChangeClass.C2_OPERATOR, ChangeClass.C4_LEARNING_POLICY, ChangeClass.C3_REPRESENTATION, ChangeClass.C5_ORGANISATION, ChangeClass.C6_CONSTITUTION]


def is_minimum_sufficient(p: SelfChangeProposal, diagnosed_minimum_layer: str) -> bool:
    return CLASS_ORDER.index(p.change_class) <= CLASS_ORDER.index(minimum_class_for(diagnosed_minimum_layer))


def mutant_proposal_edits_evaluator(p: SelfChangeProposal) -> SelfChangeProposal:
    """Planted (M11 §18 hostile): a proposal whose change touches the evaluator/threshold."""
    return SelfChangeProposal(p.proposal_id + "#evil", p.version, p.trigger_evidence, "adoption.threshold", "D8", p.incumbent_fingerprint, ChangeClass.C0_PARAMETERS, {"adoption_margin": 1.0}, lambda a: a, p.prediction, p.preserved_capabilities, p.reopened_capabilities, p.discriminator, p.rollback_plan, p.scope, p.expiry, p.origin)


PROTECTED_TARGETS = ("adoption.", "assurance.", "constitution.", "meter.", "authority.")
PROTECTED_TOKENS = ("adoption", "assurance", "constitution", "meter", "authority", "charge", "budget", "threshold", "evaluator")


def _walk(x):
    if isinstance(x, Mapping):
        for k, v in x.items():
            yield str(k)
            yield from _walk(v)
    elif isinstance(x, (list, tuple, set)):
        for v in x:
            yield from _walk(v)
    elif isinstance(x, str):
        yield x


def touches_protected_target(p: SelfChangeProposal) -> bool:
    """The meter, thresholds and the evaluator lie structurally outside every proposal's write set
    (batch 5 E7): any protected token anywhere in the change (keys or string values, nested) refuses."""
    if any(p.target_component.startswith(t) for t in PROTECTED_TARGETS):
        return True
    return any(any(tok in item.lower() for tok in PROTECTED_TOKENS) for item in _walk(p.change))


def mutant_nested_meter_edit(p: SelfChangeProposal) -> SelfChangeProposal:
    """Planted (E7 hostile): the meter reached through a nested key that a prefix test misses."""
    return SelfChangeProposal(p.proposal_id + "#nested", p.version, p.trigger_evidence, "router.policy", p.target_layer, p.incumbent_fingerprint, p.change_class, {"params": {"Meter": {"charge": 0.0}}}, lambda a: a, p.prediction, p.preserved_capabilities, p.reopened_capabilities, p.discriminator, p.rollback_plan, p.scope, p.expiry, p.origin)


def mutant_graded_on_dev_tasks(p: SelfChangeProposal, held_out: Sequence[str]) -> SelfChangeProposal:
    """Planted (E4 hostile): the proposer saw the held-out tasks while forming the change."""
    return SelfChangeProposal(p.proposal_id + "#dev", p.version, p.trigger_evidence, p.target_component, p.target_layer, p.incumbent_fingerprint, p.change_class, p.change, p.apply, p.prediction, p.preserved_capabilities, p.reopened_capabilities, p.discriminator, p.rollback_plan, p.scope, p.expiry, p.origin, dev_tasks=tuple(held_out))
