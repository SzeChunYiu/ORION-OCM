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
    authority: Authority = field(default_factory=lambda: Authority.of(proposal=1))

    def adoptable_through_cognition(self) -> bool:
        """C6 constitutional proposals are recommendation packets only (M11 §6)."""
        return self.change_class is not ChangeClass.C6_CONSTITUTION

    def fingerprint(self) -> str:
        return hashlib.sha256(json.dumps({"id": self.proposal_id, "v": self.version, "target": self.target_component, "class": self.change_class.value, "change": self.change, "pred": self.prediction.digest(), "incumbent": self.incumbent_fingerprint}, sort_keys=True, default=str).encode()).hexdigest()[:16]


def minimum_class_for(layer: str) -> ChangeClass:
    return {"D0": ChangeClass.C0_PARAMETERS, "D1": ChangeClass.C1_ROUTER, "D2": ChangeClass.C2_OPERATOR, "D5": ChangeClass.C2_OPERATOR, "D6": ChangeClass.C4_LEARNING_POLICY, "D3": ChangeClass.C3_REPRESENTATION, "D4": ChangeClass.C3_REPRESENTATION, "D7": ChangeClass.C5_ORGANISATION, "D8": ChangeClass.C6_CONSTITUTION}[layer]


CLASS_ORDER = [ChangeClass.C0_PARAMETERS, ChangeClass.C1_ROUTER, ChangeClass.C2_OPERATOR, ChangeClass.C4_LEARNING_POLICY, ChangeClass.C3_REPRESENTATION, ChangeClass.C5_ORGANISATION, ChangeClass.C6_CONSTITUTION]


def is_minimum_sufficient(p: SelfChangeProposal, diagnosed_minimum_layer: str) -> bool:
    return CLASS_ORDER.index(p.change_class) <= CLASS_ORDER.index(minimum_class_for(diagnosed_minimum_layer))


def mutant_proposal_edits_evaluator(p: SelfChangeProposal) -> SelfChangeProposal:
    """Planted (M11 §18 hostile): a proposal whose change touches the evaluator/threshold."""
    return SelfChangeProposal(p.proposal_id + "#evil", p.version, p.trigger_evidence, "adoption.threshold", "D8", p.incumbent_fingerprint, ChangeClass.C0_PARAMETERS, {"adoption_margin": 1.0}, lambda a: a, p.prediction, p.preserved_capabilities, p.reopened_capabilities, p.discriminator, p.rollback_plan, p.scope, p.expiry, p.origin)


PROTECTED_TARGETS = ("adoption.", "assurance.", "constitution.", "meter.", "authority.")


def touches_protected_target(p: SelfChangeProposal) -> bool:
    return any(p.target_component.startswith(t) for t in PROTECTED_TARGETS) or any(str(k).startswith("adoption") or str(k).startswith("meter") for k in p.change)
