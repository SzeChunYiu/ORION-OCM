"""Explicit bridge from persistent dialogue commitments into the General Epistemic Field.

The dialogue workspace remains a compact/materialized conversation view.  This adapter promotes no
world truth and performs no reference inference.  A caller must provide explicit meaning-node ->
persistent field-object bindings.  The adapter reuses the commitment's actual evidence record,
authority and scope, then delegates to :mod:`ocm.language.field_bridge`.

Consequences:

* speaker commitment authority stays speaker authority;
* retraction/supersession revokes the same evidence id, so the field representation reopens through
  the ordinary #102 warrant lifecycle;
* positive and negative commitments remain distinct because polarity is restored into the bound
  meaning before canonicalisation;
* dialogue JSON is not treated as a second truth store: only an ACTIVE, live commitment with an
  evidence record can be bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ocm.kso.space import TypedRejection
from ocm.kso.warrant import Liveness
from ocm.language.field_bridge import MeaningFieldBindingReceipt, bind_meaning
from ocm.language.meaning import MEdge, MeaningGraph

from .workspace import CommitmentStatus, DialogueWorkspace


@dataclass(frozen=True, slots=True)
class DialogueFieldBindingReceipt:
    commitment_id: str
    evidence_id: str
    negated: bool
    field_binding: MeaningFieldBindingReceipt

    def as_dict(self) -> dict:
        return {
            "commitment_id": self.commitment_id,
            "evidence_id": self.evidence_id,
            "negated": self.negated,
            "field_binding": self.field_binding.as_dict(),
        }


def commitment_meaning(workspace: DialogueWorkspace, commitment_id: str) -> MeaningGraph:
    """Reconstruct the exact semantic proposition represented by a dialogue commitment.

    ``DialogueWorkspace`` stores the positive canonical proposition plus a separate polarity bit.
    The field identity must restore that bit; otherwise ``p`` and ``not p`` could collapse to the
    same persistent representation.
    """
    commitment = workspace.commitments.get(commitment_id)
    if commitment is None:
        raise TypedRejection("UNKNOWN_COMMITMENT", commitment_id)
    graph = MeaningGraph.from_dict(commitment.meaning)
    if not commitment.negated:
        return graph
    if graph.root is None:
        raise TypedRejection("NEGATED_MEANING_WITHOUT_ROOT", commitment_id)
    if any(edge.relation == "NEGATES" for edge in graph.edges):
        raise TypedRejection(
            "POLARITY_ENCODING_CONFLICT",
            "commitment negated flag is set but stored positive meaning already contains NEGATES",
        )
    return MeaningGraph(
        graph.nodes,
        graph.edges + (MEdge("NEGATES", (graph.root,), (graph.root,)),),
        graph.root,
    )


def bind_commitment(
    workspace: DialogueWorkspace,
    commitment_id: str,
    bindings: Mapping[str, str],
) -> DialogueFieldBindingReceipt:
    """Bind one ACTIVE, live dialogue commitment to persistent field identities.

    No identity matching is attempted here.  ``bindings`` is an explicit correspondence supplied by
    an upstream resolver/checker.  The evidence record is authoritative for the representation's
    correspondence warrant, authority, scope and certificate kind.
    """
    commitment = workspace.commitments.get(commitment_id)
    if commitment is None:
        raise TypedRejection("UNKNOWN_COMMITMENT", commitment_id)
    if commitment.status is not CommitmentStatus.ACTIVE:
        raise TypedRejection("COMMITMENT_NOT_ACTIVE", commitment_id)

    runtime = workspace.runtime
    record = runtime.state.evidence.records.get(commitment.evidence_id)
    if record is None:
        raise TypedRejection("COMMITMENT_EVIDENCE_MISSING", commitment.evidence_id)
    if record.warrant.liveness(runtime.state.revoked) is not Liveness.LIVE:
        raise TypedRejection("COMMITMENT_EVIDENCE_NOT_LIVE", commitment.evidence_id)

    meaning = commitment_meaning(workspace, commitment_id)
    field_receipt = bind_meaning(
        runtime,
        meaning,
        bindings,
        warrant=record.warrant,
        certificate=record.channel.certificate,
        authority=record.authority,
        scope=record.scope,
        support_evidence_id=commitment.evidence_id,
    )
    return DialogueFieldBindingReceipt(
        commitment_id,
        commitment.evidence_id,
        commitment.negated,
        field_receipt,
    )
