"""FunctionalMechanismContractV1 -- #214 section 2, frozen before FNA-1 implementation.

Every donor function must reduce to this contract before any mechanism is built, so that
the FUNCTION is separated from the implementation it was discovered in. The compact form
#214 gives is

    D = (I, O, S, L, C, F)

and this module adds the fields #214 section 2 lists alongside it: source identity,
information surface, strongest non-neural parent, candidate OCM realization, exact
authority boundary, and the causal-ablation gate.

Two rules are enforced here rather than left to prose, because both are ways this
programme has previously produced an unearned positive:

1. ``strongest_non_neural_parent`` may not be empty. #214 section 2: "If the function is
   already owned by a mature non-neural parent, absorb that parent rather than creating
   OCM-specific notation." A contract that names no parent has not looked.
2. A contract whose ownership is PARENT_OWNS_IT may not also declare an OCM realization.
   That combination is precisely the "invent OCM notation for a mechanism a parent already
   supplies" error, and it is refused at validation rather than reviewed later.

No mechanism in this module retrieves, ranks, learns or routes. It validates documents.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

SCHEMA = "ocm.fna.functional_mechanism_contract.v1"

#: The six-tuple of #214 section 2. Every one is required; an absent term is not "unknown",
#: it is an unfinished contract.
CORE_TERMS = ("input_contract_I", "output_contract_O", "state_transformation_S",
              "learning_update_rule_L", "resource_vector_C", "known_failure_modes_F")

REQUIRED = CORE_TERMS + (
    "name", "source_identity", "information_surface", "strongest_non_neural_parent",
    "ownership", "exact_authority_boundary", "causal_ablation_gate", "negative_terminal",
    "reopen_condition", "evidence_class",
)

#: Ownership dispositions. PARENT_OWNS_IT is a successful outcome, not a failure to build.
OWNERSHIP = ("PARENT_OWNS_IT", "PARENT_OWNS_IT_BUT_ABSENT_ON_MAIN", "ADAPT",
             "ADAPT_ABSENT_ON_MAIN", "BUILD", "REJECT", "OPEN",
             "NO_OBLIGATION_IN_AN_EXACT_SYSTEM")

#: An OCM realization is licensed only under these dispositions.
MAY_DECLARE_OCM_REALIZATION = ("ADAPT", "ADAPT_ABSENT_ON_MAIN", "BUILD",
                               "PARENT_OWNS_IT_BUT_ABSENT_ON_MAIN")

#: Registered #214 section 7 terminals. A contract may not name an unregistered one.
TERMINALS = (
    "NON_NEURAL_FUNCTIONAL_RECONSTRUCTION_SUPPORTED", "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE",
    "NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE", "PARENT_SUFFICIENT_FOR",
    "NO_FUNCTIONAL_PARITY", "NEURAL_DONOR_DOMINATES_AT_SCOPE", "STATE_SEARCH_COST_DOMINATES",
    "ACQUISITION_COST_DOMINATES", "REPRESENTATION_INSUFFICIENT", "APPROXIMATE_RETRIEVAL_NOT_SAFE",
    "NO_LIFETIME_PAYBACK",
)

#: Claims no collection of function-level positives may license (#214 section 7).
FORBIDDEN_CLAIMS = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "AGI", "GENERAL_SUPERIORITY")


class ContractError(ValueError):
    """A typed rejection at the contract boundary; ``code`` is the registered reason."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def registered_terminal(value: str) -> bool:
    """A registered terminal, or a bounded CANNOT_CHECK with a stated reason.

    A bare ``CANNOT_CHECK_`` is refused: an unbounded cannot-check is not a disposition,
    it is a blank. This mirrors the rule the #165 closure artifact already enforces.
    """
    if value.startswith("CANNOT_CHECK_"):
        return len(value) > len("CANNOT_CHECK_")
    return any(value == t or value.startswith(t + "_") for t in TERMINALS)


def validate(doc: Mapping[str, Any]) -> dict:
    """Validate one contract. Returns the document; raises ContractError on any breach."""
    problems: list[str] = []
    for key in REQUIRED:
        if key not in doc:
            problems.append(f"MISSING_FIELD:{key}")
        elif doc[key] in (None, "", [], {}) and key != "strongest_non_neural_parent":
            # An empty parent list has its own, more informative rejection below; reporting
            # it as a generic empty field would bury the rule that actually matters.
            problems.append(f"EMPTY_FIELD:{key}")
    if problems:
        raise ContractError("INCOMPLETE_CONTRACT", ", ".join(sorted(problems)))

    if doc["ownership"] not in OWNERSHIP:
        raise ContractError("UNREGISTERED_OWNERSHIP", str(doc["ownership"]))
    if not isinstance(doc["strongest_non_neural_parent"], (list, tuple)) or \
            not doc["strongest_non_neural_parent"]:
        raise ContractError("NO_PARENT_NAMED",
                            "section 2 requires the strongest non-neural parent; a contract "
                            "that names none has not given first refusal")
    if not registered_terminal(doc["negative_terminal"]):
        raise ContractError("UNREGISTERED_TERMINAL", str(doc["negative_terminal"]))

    realization = doc.get("candidate_ocm_realization")
    if realization and doc["ownership"] not in MAY_DECLARE_OCM_REALIZATION:
        raise ContractError(
            "OCM_NOTATION_FOR_A_PARENT_OWNED_FUNCTION",
            f"ownership={doc['ownership']} names a mature parent, so building an OCM "
            f"analogue ({realization!r}) is the error section 2 forbids")

    body = json.dumps(doc, sort_keys=True)
    for claim in FORBIDDEN_CLAIMS:
        if claim in body:
            raise ContractError("FORBIDDEN_CLAIM", claim)
    return dict(doc)


def validate_all(docs) -> list[dict]:
    return [validate(d) for d in docs]
