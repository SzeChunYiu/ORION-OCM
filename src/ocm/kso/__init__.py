"""Canonical KnowledgeSpace (KSO) core — M1 consolidation of the inherited substrate.

Modules: ``warrant`` (antichain semiring, three-valued liveness) · ``ids`` · ``types`` (type
registry, authority lattice, scope) · ``space`` (one object model) · ``navigation`` (frozen-
denominator restart walk, surprise, four-valued outcome) · ``firing`` · ``revocation`` (prune
equivalence, impact cone, reopening) · ``extraction`` · ``admission`` (channels, compose, genome)
· ``abstraction`` (lumpability ∧ measurability, summaries) · ``resources`` · ``jump`` (byte-
identical parent copy) · ``obligations`` (theorem registry) · ``checks`` (M1 self-check CLI).
"""

from .jump import JumpAssessment, JumpLevel, JumpProposal, JumpTrigger, TriggerKind, assess_jump, minimum_level
from .space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from .types import Authority, Scope, TypeRegistry
from .warrant import CannotCheck, Liveness, WarrantProfile

__all__ = [
    "JumpAssessment", "JumpLevel", "JumpProposal", "JumpTrigger", "TriggerKind", "assess_jump", "minimum_level",
    "Atom", "Hyperedge", "KnowledgeSpace", "TypedRejection", "Authority", "Scope", "TypeRegistry",
    "CannotCheck", "Liveness", "WarrantProfile",
]
