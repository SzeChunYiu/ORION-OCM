"""§15 freeze-box catalog for publication-constitution v2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
V1_PROTOCOL = HERE.parent / "publication-constitution-v1" / "PROTOCOL.json"

# Issue #165 §15 — before protected confirmatory execution.
FREEZE_KEYS = (
    "decisive_question",
    "contribution_level",
    "strongest_parent",
    "causal_ablation",
    "prior_information_manifest",
    "task_family_generator",
    "protected_splits",
    "comparator_versions",
    "prompts_configs",
    "budgets",
    "resource_meters",
    "analysis",
    "stopping_exclusion",
    "non_inferiority_margins",
    "negative_terminals",
    "independent_unit",
    "power_precision",
    "multiplicity",
    "leakage_audit",
    "parent_favouring_controls",
    "independent_validation_subset",
)

AFTER_KEYS = (
    "raw_traces",
    "failures",
    "crashes_timeouts",
    "machine_readable_receipts",
    "raw_cost_vectors",
    "immutable_figure_tables",
    "exclusions_with_reasons",
    "checksum_manifest",
    "fresh_host_rerun",
    "disjoint_replication",
    "independent_scorer_checker",
    "red_team_reviewer_simulation",
    "claim_result_correspondence_review",
)

FORBIDDEN_EVIDENCE = frozenset({"E4", "E5"})
MISSING_PREFIXES = ("MISSING",)
CANNOT_CHECK_PREFIXES = ("CANNOT_CHECK",)


def load_protocol(path: Path | None = None) -> dict[str, Any]:
    target = path or (HERE / "PROTOCOL.json")
    return json.loads(target.read_text())


def _text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value or "").strip()


def is_missing(value: Any) -> bool:
    text = _text(value)
    return not text or text.startswith(MISSING_PREFIXES)


def is_cannot_check(value: Any) -> bool:
    return _text(value).startswith(CANNOT_CHECK_PREFIXES)


def is_filled(value: Any) -> bool:
    return not is_missing(value)


def classify(protocol: dict[str, Any] | None = None) -> dict[str, Any]:
    proto = protocol or load_protocol()
    studies = proto["studies"]
    freeze_complete: list[str] = []
    freeze_missing: list[str] = []
    freeze_cannot_check: list[str] = []
    for key in FREEZE_KEYS:
        values = [study.get(key) for study in studies.values()]
        if all(is_filled(value) for value in values):
            freeze_complete.append(key)
        elif all(is_cannot_check(value) or is_missing(value) for value in values) and any(
            is_cannot_check(value) for value in values
        ):
            freeze_cannot_check.append(key)
        else:
            freeze_missing.append(key)

    after = proto["section15"]["after_execution"]
    after_complete: list[str] = []
    after_missing: list[str] = []
    after_cannot_check: list[str] = []
    for key in AFTER_KEYS:
        status = _text(after[key]["status"] if isinstance(after[key], dict) else after[key])
        if status == "FREEZE_COMPLETE":
            after_complete.append(key)
        elif status.startswith("CANNOT_CHECK"):
            after_cannot_check.append(key)
        else:
            after_missing.append(key)

    return {
        "freeze_complete": freeze_complete,
        "freeze_missing": freeze_missing,
        "freeze_cannot_check": freeze_cannot_check,
        "after_complete": after_complete,
        "after_missing": after_missing,
        "after_cannot_check": after_cannot_check,
        "closes_issue_144": bool(proto.get("closes_issue_144")),
        "terminal": proto["terminal"],
        "invented_e4": any(
            str(study.get("evidence_class") or "") in FORBIDDEN_EVIDENCE for study in studies.values()
        ),
    }


def v1_exists_unoverwritten() -> bool:
    return V1_PROTOCOL.is_file() and "publication-constitution.protocol.v1" in V1_PROTOCOL.read_text()
