"""R0-D2: ``SelectionPolicyContractV1``.

Issue #152 is explicit that checker validity is not selection safety: the runtime
preserves supplied operator order as policy, and reordering two individually
valid operators can change which accepted result is chosen.  A counterfactual
comparison is therefore meaningless until the compared transformation is declared
admissible against a contract.

Three contracts are registered here, and they differ only in what they protect.
That is the point: whether a transformation is safe is not a property of the
transformation, it is a property of the contract, and this study reports its
answer under each rather than choosing one and calling it the answer.

``C1_ANSWER_EQUIVALENCE``
    protects the decision, the answer mapping and the chosen operator identity.
    Permits early exit at the first passing candidate in the supplied order,
    because ``decide`` returns exactly that candidate. Does NOT permit reordering
    when more than one candidate passes, because the chosen operator would change.

``C2_TRACE_EQUIVALENCE``
    protects everything C1 does, plus the full solve trace including the verdict
    map for every examined candidate. Permits nothing that changes which
    candidates are examined, so it permits neither early exit nor reordering.

``C3_ANSWER_EQUIVALENCE_WITH_UNIQUE_PASS``
    protects what C1 does, and additionally applies only on queries where at most
    one candidate passes. There reordering is answer-safe, because the identity of
    the passing candidate does not depend on order.

No contract here permits speculation with irreversible side effects, and none
permits inferring an untried operator's outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SelectionPolicyContract:
    contract_id: str
    scope: str
    admissible_set_identity: str
    protected_output_coordinates: tuple[str, ...]
    output_equivalence: str
    allowed_transformations: tuple[str, ...]
    optimization_coordinates: tuple[str, ...]
    speculation_budget: str
    fallback_policy: str
    side_effect_class: str
    commit_authority_boundary: str
    applies_when: str = "every eligible query"

    def permits(self, transformation: str) -> bool:
        return transformation in self.allowed_transformations


_COMMON = dict(
    scope="ocm.runtime.solve compose/check/decide over a supplied OperatorSpec sequence",
    admissible_set_identity=(
        "A^E is the ordered sequence compose_stage actually composes: structurally "
        "applicable under the reacting subgraph, operator warrant live, every input atom "
        "live. Preconditions are enforced by the registry path; the solve path checks "
        "warrant and input liveness."),
    optimization_coordinates=("composition_work", "verification_calls"),
    speculation_budget="none; this study proposes no speculative execution",
    fallback_policy="the incumbent supplied-order policy, unchanged",
    side_effect_class=(
        "backends are invoked by the incumbent already; this study invokes nothing extra "
        "and re-executes no candidate, so its own side-effect class is READ_ONLY"),
    commit_authority_boundary=(
        "unchanged; commitment remains behind _finish_commitment and no contract here "
        "touches it"),
)

C1_ANSWER_EQUIVALENCE = SelectionPolicyContract(
    contract_id="C1_ANSWER_EQUIVALENCE",
    protected_output_coordinates=("decision", "answer", "chosen_operator_id"),
    output_equivalence=(
        "two runs are equivalent when the decision, the answer mapping and the chosen "
        "operator identity are equal"),
    allowed_transformations=("early_exit_at_first_pass_in_supplied_order",),
    **_COMMON)

C2_TRACE_EQUIVALENCE = SelectionPolicyContract(
    contract_id="C2_TRACE_EQUIVALENCE",
    protected_output_coordinates=("decision", "answer", "chosen_operator_id",
                                  "examined_candidate_set", "verdict_map"),
    output_equivalence=(
        "two runs are equivalent when C1 holds AND the same candidates were examined with "
        "the same verdicts, so the trace a reviewer reads is unchanged"),
    allowed_transformations=(),
    **_COMMON)

C3_ANSWER_EQUIVALENCE_WITH_UNIQUE_PASS = SelectionPolicyContract(
    contract_id="C3_ANSWER_EQUIVALENCE_WITH_UNIQUE_PASS",
    protected_output_coordinates=("decision", "answer", "chosen_operator_id"),
    output_equivalence="as C1",
    allowed_transformations=("early_exit_at_first_pass_in_supplied_order",
                             "reorder_admissible_candidates"),
    applies_when="queries on which at most one admissible candidate passes",
    **_COMMON)

CONTRACTS: Mapping[str, SelectionPolicyContract] = {
    c.contract_id: c for c in
    (C1_ANSWER_EQUIVALENCE, C2_TRACE_EQUIVALENCE, C3_ANSWER_EQUIVALENCE_WITH_UNIQUE_PASS)}


def reorder_is_answer_safe(passing_count: int) -> bool:
    """Reordering preserves the chosen operator only when the passing set is a singleton.

    ``decide`` returns ``passed[0]``. With two passing candidates a permutation can
    change which one that is, so the chosen operator identity -- a protected
    coordinate under every contract here -- is not preserved. With one, order
    cannot change it. With none, there is no answer to preserve and the decision
    is determined by the unordered verdict multiset.
    """
    return passing_count <= 1
