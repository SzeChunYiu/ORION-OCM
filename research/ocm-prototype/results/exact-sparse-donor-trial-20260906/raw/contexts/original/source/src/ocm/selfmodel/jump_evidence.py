"""Evidence-derived Jump assessment (theory batch 6 consequence 7).

`ocm.kso.jump` is a frozen parent-owned module (M0 dependency audit) whose `assess_jump` takes
`lower_level_sufficient` from the caller and whose `minimum_level` returns the lowest *admissible*
proposal.  This OCM-owned module derives both from the diagnosis instead: the minimum-sufficient
layer computed from ablation evidence is local ⇒ no Jump; UNKNOWN (no restoring ablation) or a
non-local layer without a valid obstruction certificate ⇒ insufficiency not identified; and the
minimum proposal is the lowest complete one at or above the evidence's minimum-sufficient level.
"""
from __future__ import annotations

from ocm.kso.jump import JumpAssessment, JumpProposal


def assess_jump_from_evidence(proposal: JumpProposal, *, minimum_sufficient_local: bool | None, certificate_valid: bool, donor_product_ties: bool, registered_class: tuple[str, ...] | None = ()) -> JumpAssessment:
    """Batch 7 G1: the Jump level is relative to the registered class of maps/tools; a J4/J5 proposal
    without a registered class is JUMP_PROPOSAL_INCOMPLETE (no uniform ceiling exists)."""
    if registered_class is None:
        return JumpAssessment.JUMP_PROPOSAL_INCOMPLETE
    if minimum_sufficient_local is None or not proposal.trigger.is_admissible:
        return JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    if minimum_sufficient_local:
        return JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    if not certificate_valid:
        return JumpAssessment.INCUMBENT_INSUFFICIENCY_NOT_IDENTIFIED
    if donor_product_ties:
        return JumpAssessment.DONOR_SUBSUMES_JUMP
    if not proposal.is_formally_complete:
        return JumpAssessment.JUMP_PROPOSAL_INCOMPLETE
    return JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION


def minimum_sufficient_proposal(proposals: tuple[JumpProposal, ...], minimum_sufficient_level: int) -> JumpProposal:
    admissible = [p for p in proposals if p.is_formally_complete and int(p.level) >= minimum_sufficient_level]
    if not admissible:
        raise ValueError("no complete admissible jump proposal at or above the minimum sufficient level")
    return min(admissible, key=lambda p: int(p.level))
