#!/usr/bin/env python3
"""Fail-closed independent-authorship / benchmark-circularity policy (#165 §16).

The intended cause of a diagnosis/benchmark item must not be labelled from the
task generator's planting intent. Independent recovery is the only admissible
truth source when a cause is the target. If recovery is not exact and cheap,
the truth label is CANNOT_CHECK. Generator intent is retained as an audit field
only.
"""
from __future__ import annotations

from typing import Any, Mapping

CANNOT_CHECK = "CANNOT_CHECK"
GENERATOR_INTENT = "GENERATOR_INTENT"
INDEPENDENT_RECOVERY = "INDEPENDENT_RECOVERY"

CAUSE_TARGETS = frozenset({
    "cause",
    "diagnosis",
    "true_layer",
    "true_class",
    "planted_cause",
    "minimum_sufficient_cause",
    "root_cause",
})


class PolicyViolation(ValueError):
    """Raised when a caller tries to use generator intent as cause truth."""


def label_truth(
    *,
    target: str,
    recovered: Mapping[str, Any] | None,
    planted: Mapping[str, Any] | None = None,
    independently_authored: bool = False,
    evidence_class: str = "E2",
) -> dict[str, Any]:
    """Return the only admissible truth record for ``target``.

    Fail-closed rules:
    - If ``target`` is a cause/diagnosis field, never copy planted/generator intent.
    - If independent recovery did not succeed, emit CANNOT_CHECK.
    - E3+ records require independently authored families; otherwise CANNOT_CHECK
      for confirmatory use (exploratory E0–E2 may still keep a generator-intent audit).
    """
    planted = dict(planted or {})
    audit = {
        "generator_intent": planted,
        "generator_intent_role": "AUDIT_ONLY",
        "independently_authored": independently_authored,
        "evidence_class": evidence_class,
    }
    if target in CAUSE_TARGETS:
        if recovered is None or recovered.get("status") != "RECOVERED":
            reason = (recovered or {}).get("reason", "independent recovery unavailable")
            return {
                "target": target,
                "source": CANNOT_CHECK,
                "truth": None,
                "reason": reason,
                "policy": "do_not_label_cause_from_generator_intent",
                **audit,
            }
        truth = dict(recovered.get("truth") or {})
        if "planted_family" in truth or "planted_cause" in truth or "true_layer" in truth:
            raise PolicyViolation("recovered truth must not carry generator-intent fields")
        return {
            "target": target,
            "source": INDEPENDENT_RECOVERY,
            "truth": truth,
            "reason": None,
            "policy": "independent_min_sufficient_cause",
            **audit,
        }
    if evidence_class in {"E3", "E4", "E5"} and not independently_authored:
        return {
            "target": target,
            "source": CANNOT_CHECK,
            "truth": None,
            "reason": "E3+ requires independently authored world/task families",
            "policy": "no_internal_worlds_substitute_for_independent_authorship",
            **audit,
        }
    return {
        "target": target,
        "source": INDEPENDENT_RECOVERY if recovered and recovered.get("status") == "RECOVERED" else CANNOT_CHECK,
        "truth": (recovered or {}).get("truth") if recovered and recovered.get("status") == "RECOVERED" else None,
        "reason": None if recovered and recovered.get("status") == "RECOVERED" else "recovery required",
        "policy": "non_cause_target",
        **audit,
    }


def refuse_generator_intent_as_cause(label: Mapping[str, Any]) -> None:
    if label.get("target") in CAUSE_TARGETS and label.get("source") == GENERATOR_INTENT:
        raise PolicyViolation("generator intent cannot label a cause target")
    truth = label.get("truth") or {}
    if label.get("target") in CAUSE_TARGETS and label.get("source") != CANNOT_CHECK:
        if any(k in truth for k in ("planted_family", "planted_cause", "true_layer")):
            raise PolicyViolation("cause truth still contains generator-intent fields")


def artifact_explained_positive_is_negative(agreement_reason: str) -> bool:
    """Shared-taxonomy or rejection-sampled agreement is not independent recovery."""
    return agreement_reason in {
        "REJECTION_SAMPLED_TO_MATCH_PLANTED",
        "SHARED_MECHANISM_TAXONOMY",
        "GENERATOR_FILTERED_BY_ORACLE_INVARIANT",
        "AUTHOR_PLANTED_METHOD",
    }
