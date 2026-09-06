from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ComparabilityStatus(str, Enum):
    COMPARABLE = "COMPARABLE"; PARTIALLY_COMPARABLE = "PARTIALLY_COMPARABLE"; NONCOMPARABLE = "NONCOMPARABLE"; CANNOT_CHECK = "CANNOT_CHECK"

@dataclass(frozen=True, slots=True)
class Anchor:
    anchor_id: str; old_object_id: str; new_object_id: str; invariant_ids: tuple[str, ...]; uncertainty: float = 0.0
    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.anchor_id, self.old_object_id, self.new_object_id)): raise ValueError("anchor identities must be non-blank")
        if not self.invariant_ids or any(not value.strip() for value in self.invariant_ids): raise ValueError("anchors require invariant identities")
        if self.uncertainty < 0: raise ValueError("anchor uncertainty must be non-negative")

@dataclass(frozen=True, slots=True)
class ComparabilityCertificate:
    certificate_id: str; old_epoch: str; new_epoch: str; target_context_id: str; mapping_ids: tuple[str, ...]; anchors: tuple[Anchor, ...]; required_invariant_ids: tuple[str, ...]; violated_invariant_ids: tuple[str, ...] = (); unresolved_invariant_ids: tuple[str, ...] = (); accumulated_uncertainty: float = 0.0; tolerance: float = 0.0; semantic_mapping_recoverable: bool = True; authority_granted: bool = False
    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.certificate_id, self.old_epoch, self.new_epoch, self.target_context_id)): raise ValueError("certificate identities must be non-blank")
        if self.old_epoch == self.new_epoch: raise ValueError("comparability certificates require distinct epochs")
        if any(not value.strip() for value in self.mapping_ids): raise ValueError("mapping_ids may not contain blanks")
        if self.accumulated_uncertainty < 0 or self.tolerance < 0: raise ValueError("uncertainty and tolerance must be non-negative")
        if self.authority_granted: raise ValueError("comparability certificates do not grant adoption authority")
    @property
    def status(self) -> ComparabilityStatus:
        if self.violated_invariant_ids or not self.semantic_mapping_recoverable: return ComparabilityStatus.NONCOMPARABLE
        if not self.mapping_ids or not self.anchors or self.unresolved_invariant_ids: return ComparabilityStatus.CANNOT_CHECK
        observed = {invariant for anchor in self.anchors for invariant in anchor.invariant_ids}
        if not set(self.required_invariant_ids) <= observed: return ComparabilityStatus.CANNOT_CHECK
        if self.accumulated_uncertainty > self.tolerance: return ComparabilityStatus.PARTIALLY_COMPARABLE
        return ComparabilityStatus.COMPARABLE
