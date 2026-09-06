"""Lean theorem subview over the canonical production KnowledgeSpace.

No parallel math store is introduced here. Goals/claims/proofs/procedures are normal KSO atoms;
planning reductions stay UNKNOWN, while checked proof support carries exact checker evidence.
"""
from __future__ import annotations

from typing import Any, Mapping

from flt_contract import AttemptStatus, EnvironmentIdentity, statement_identity
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.operators.registry import BackendKind, Candidate, OperatorSpec, compose_candidate


def _meta(**items: Any) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(items.items()))


def empty_space() -> KnowledgeSpace:
    return KnowledgeSpace((), ())


def open_obligation(*, theorem_name: str, statement: str, environment: EnvironmentIdentity) -> Atom:
    sid = statement_identity(statement, environment)
    return Atom(
        atom_id=f"theorem-goal:{sid}",
        atom_type="goal",
        warrant=WarrantProfile.partial(()),
        content_ref=f"lean-statement:{sid}",
        meta=_meta(
            theorem_name=theorem_name,
            statement=statement,
            statement_identity=sid,
            environment_digest=environment.digest,
            status=AttemptStatus.OPEN.value,
            desired_certificate="LEAN_KERNEL_PROOF",
            truth_warrant="NONE",
        ),
    )


def failed_attempt(*, attempt_id: str, goal_atom_id: str, terminal: str, budget: Mapping[str, int]) -> Atom:
    # Failure is an observation about this search episode, never a warrant that the theorem is false.
    return Atom(
        atom_id=f"proof-attempt:{attempt_id}",
        atom_type="observation",
        warrant=WarrantProfile.of((f"attempt-receipt:{attempt_id}",), complete=True),
        content_ref=f"proof-attempt:{attempt_id}",
        meta=_meta(goal_atom_id=goal_atom_id, status=AttemptStatus.FAILED_UNDER_BUDGET.value, terminal=terminal, budget=dict(budget)),
    )


def proposed_reduction(*, edge_id: str, dependencies: tuple[str, ...], goal_atom_id: str, method_ref: str) -> Hyperedge:
    # A proposed search/planning relation is deliberately UNKNOWN. It is not theorem support.
    return Hyperedge(
        edge_id=edge_id,
        tails=dependencies,
        heads=(goal_atom_id,),
        relation_type="COMPOSITION",
        warrant=WarrantProfile.partial(()),
        executable_ref=method_ref,
        meta=_meta(status=AttemptStatus.PROPOSED.value, semantics="WOULD_FOLLOW_FROM_NOT_PROVED_BY"),
    )


def proof_operator(*, goal_atom_id: str, backend, dependencies: tuple[str, ...] = ()) -> OperatorSpec:
    # The OPEN goal is the object being solved, not an epistemic premise. Only already-verified
    # dependencies belong in input_atoms; otherwise the goal's UNKNOWN warrant would make even an
    # exact checker result UNKNOWN. The goal identity travels in the candidate output/receipt.
    return OperatorSpec(
        operator_id="math.lean.native-proof-search",
        version="flt-kso-v1",
        kind=BackendKind.PROOF,
        backend=backend,
        input_atoms=dependencies,
        output_type="proof",
        known_failures=("FAILED_UNDER_BUDGET", "CANNOT_CHECK_PINNED_FLT_ENVIRONMENT"),
        lineage=("issue-38", "issue-62", "issue-115"),
    )


def compose_proof_candidate(
    ks: KnowledgeSpace,
    op: OperatorSpec,
    output: Mapping[str, Any],
    *,
    checker_evidence: str | None,
) -> Candidate:
    return compose_candidate(ks, op, output, exact_certificate_evidence=checker_evidence)


def admit_checked_proof(
    ks: KnowledgeSpace,
    *,
    goal: Atom,
    candidate: Candidate,
    proof_source_hash: str,
    checker_evidence: str,
) -> KnowledgeSpace:
    if candidate.certificate != "EXACT_CHECKER" or candidate.liveness(()) is not Liveness.LIVE:
        raise ValueError("only an exact live checker candidate can be admitted")
    proof_id = f"checked-proof:{proof_source_hash}"
    proof = Atom(
        atom_id=proof_id,
        atom_type="proof",
        warrant=candidate.warrant,
        authority=candidate.authority,
        scope=candidate.scope,
        content_ref=f"sha256:{proof_source_hash}",
        meta=_meta(status=AttemptStatus.PROVED.value, checker_evidence=checker_evidence, certificate="EXACT_CHECKER"),
    )
    claim_id = goal.atom_id.replace("theorem-goal:", "theorem-claim:", 1)
    previous = ks.atom_map().get(claim_id)
    claim_warrant = candidate.warrant if previous is None else previous.warrant.join(candidate.warrant)
    claim = Atom(
        atom_id=claim_id,
        atom_type="claim",
        warrant=claim_warrant,
        authority=candidate.authority if previous is None else previous.authority.meet(candidate.authority),
        scope=candidate.scope if previous is None else previous.scope.intersect(candidate.scope),
        content_ref=goal.content_ref,
        meta=_meta(status=AttemptStatus.PROVED.value, goal_atom_id=goal.atom_id, support_routes=(1 if previous is None else 2)),
    )
    # The OPEN goal itself is UNKNOWN by construction, so using it as a tail would incorrectly keep
    # support UNKNOWN. The checked proof is the sufficient route; verified dependency atoms are
    # conjunctive tails, while multiple proof edges provide alternative (OR) routes to the claim.
    edge = Hyperedge(
        edge_id=f"support:{proof_source_hash}",
        tails=tuple((*candidate.operator.input_atoms, proof_id)),
        heads=(claim_id,),
        relation_type="SUPPORT",
        warrant=proof.warrant,
        executable_ref="lean-kernel",
        meta=_meta(goal_atom_id=goal.atom_id, semantics="CHECKED_PROOF_SUPPORT", checker_evidence=checker_evidence),
    )
    out = ks.with_atoms(proof)
    out = out.with_atoms(claim) if previous is None else out.replace_atom(claim)
    return out.with_edges(edge)
