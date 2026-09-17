from __future__ import annotations

import argparse
import json
import math
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

HERE = Path(__file__).resolve().parent

POLICIES: Dict[str, Tuple[int, int]] = {
    "C0": (0, 0),
    "C1": (1, 1),
    "ID": (0, 1),
    "NOT": (1, 0),
}

PROVENANCE_TAGS = (
    "INITIAL_OR_INHERITED_ORGANIZATION",
    "EXTERNAL_OBSERVATION",
    "REWARD_OR_EVALUATOR_SIGNAL",
    "ENDOGENOUS_COMPUTE",
    "STOCHASTIC_VARIATION",
    "ORACLE_ADVICE_OR_TOOL",
    "SOCIAL_OR_CULTURAL_TRANSFER",
    "PHYSICAL_OR_ENVIRONMENTAL_SIGNAL",
)

TARGET_CORRELATED_IMPORT_TAGS = (
    "INITIAL_OR_INHERITED_ORGANIZATION",
    "EXTERNAL_OBSERVATION",
    "REWARD_OR_EVALUATOR_SIGNAL",
    "ORACLE_ADVICE_OR_TOOL",
    "SOCIAL_OR_CULTURAL_TRANSFER",
    "PHYSICAL_OR_ENVIRONMENTAL_SIGNAL",
)

NULL_CONDITION_HIERARCHY = (
    {
        "id": "NO_SENSORY_OBSERVATIONS",
        "forbidden_channels": ("EXTERNAL_OBSERVATION",),
        "reading": "no sensory/environment observation channel is admitted; other declared channels remain visible",
    },
    {
        "id": "NO_REWARD_OR_EVALUATOR_FEEDBACK",
        "forbidden_channels": ("REWARD_OR_EVALUATOR_SIGNAL",),
        "reading": "no reward/evaluator feedback enters development",
    },
    {
        "id": "NO_TASK_SPECIFIC_DATA",
        "forbidden_channels": ("EXTERNAL_OBSERVATION", "REWARD_OR_EVALUATOR_SIGNAL"),
        "reading": "no task-specific observational or evaluator data are supplied; task-independent initialization may remain",
    },
    {
        "id": "NO_EXTERNAL_INTERACTION",
        "forbidden_channels": (
            "EXTERNAL_OBSERVATION",
            "REWARD_OR_EVALUATOR_SIGNAL",
            "ORACLE_ADVICE_OR_TOOL",
            "SOCIAL_OR_CULTURAL_TRANSFER",
            "PHYSICAL_OR_ENVIRONMENTAL_SIGNAL",
        ),
        "reading": "no external interaction channel enters after initialization",
    },
    {
        "id": "NO_ENDOGENOUS_RANDOMNESS",
        "forbidden_channels": ("STOCHASTIC_VARIATION",),
        "reading": "development is deterministic conditional on the remaining declared state/channels",
    },
    {
        "id": "NO_TASK_SPECIFIC_INITIALIZATION",
        "forbidden_channels": (),
        "reading": "initial organization may exist but must be independent of the registered target/task variable",
    },
    {
        "id": "ABSOLUTE_REGISTERED_NULL_EXCEPT_SUBSTRATE_AND_DYNAMICS",
        "forbidden_channels": (
            "EXTERNAL_OBSERVATION",
            "REWARD_OR_EVALUATOR_SIGNAL",
            "STOCHASTIC_VARIATION",
            "ORACLE_ADVICE_OR_TOOL",
            "SOCIAL_OR_CULTURAL_TRANSFER",
            "PHYSICAL_OR_ENVIRONMENTAL_SIGNAL",
        ),
        "reading": "only registered substrate/dynamics and target-independent initial organization remain; no imported target-correlated channel is licensed",
    },
)

HSG_ISSUE_COMMENT_AUTHORITIES = {
    "HSG_V2_CLOSURE_AMENDMENT": {
        "issue": 233,
        "comment_id": 5609406015,
        "updated_at": "2026-09-09T22:07:34Z",
        "required_heading": "HSG-T51 — Closed-computable novelty information bound",
    }
}

BARRIER_STATUSES = (
    "DECIDABLE",
    "SEMI_DECIDABLE",
    "CERTIFIABLE",
    "SOUND_INCOMPLETE_APPROXIMATION",
    "PROBABILISTIC_APPROXIMATION",
    "IDENTIFIABLE_IN_LIMIT",
    "NOT_IDENTIFIABLE_AT_SCOPE",
    "UNDECIDABLE_RELATIVE_TO_S",
    "RESOURCE_INFEASIBLE_AT_SCOPE",
    "PHYSICAL_STATUS_UNKNOWN",
)

TRANSITION_CLASSES = (
    "DOMAIN_RESTRICTION",
    "PROMISE_PROBLEM",
    "APPROXIMATION",
    "SEMIDECISION",
    "ABSTENTION",
    "LIST_OR_SET_OUTPUT",
    "CERTIFICATE",
    "INTERACTION_OR_QUERY",
    "ORACLE_OR_ADVICE",
    "RANDOMNESS",
    "RESOURCE_RELAXATION",
    "SUBSTRATE_EXPANSION",
    "LITERAL_CONTRADICTION",
)

FORBIDDEN_TERMINALS = (
    "BROKE_TURING",
    "BROKE_RICE",
    "BROKE_GODEL",
    "BROKE_NFL",
    "BROKE_BLUM",
    "CREATED_INFORMATION_FROM_NOTHING",
    "UNIVERSAL_RESOURCE_MONOTONICITY",
    "UNIVERSAL_SELF_IMPROVEMENT",
    "PHYSICAL_CHURCH_TURING_FALSIFIED",
    "ALL_BARRIERS_SOLVED",
    "SOLVED_FOREVER",
    "COMPLETE_GMI",
)

EXPECTED_PARENT_PINS = {
    "HST_THEOREM_REGISTRY_V1": {
        "path": "research/heritable-search-transformation-v1/HST_THEOREM_REGISTRY_V1.json",
        "blob_sha": "5b94d66a8d8d2196a518fd7ac8d1da83663e42a4",
    },
    "FREEZE_HST_V1": {
        "path": "research/heritable-search-transformation-v1/FREEZE_HST_V1.json",
        "blob_sha": "8723baf57ac16878edb4dfff45bd7decfa15b6be",
    },
    "HSG_FREEZE_V1": {
        "path": "research/heritable-search-geometry-v1/HSG_FREEZE_V1.json",
        "blob_sha": "0116c6bc81f49db982abdc9446c0c6519133ced6",
    },
    "HSG_ATOM_TABLE_V1": {
        "path": "research/heritable-search-geometry-v1/HSG_ATOM_TABLE_V1.json",
        "blob_sha": "b102b6fa3dad12e8c5ea7205b76a8340a69e751f",
    },
    "AJ6_AJ8_THEORY": {
        "path": "research/gmi-833-aj6-aj8-development-value-intelligence-v1/THEORY.md",
        "blob_sha": "2396ddcd5eb8d1b47968c9c0a291fceacb45ba8b",
    },
    "AJ6_AJ8_CHECKER": {
        "path": "research/gmi-833-aj6-aj8-development-value-intelligence-v1/check_aj6_aj8.py",
        "blob_sha": "3b550a8dd5c60013bc9603d93e2e4f764ac1e964",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def score(policy: str, target: str = "ID") -> Tuple[int, int]:
    p = POLICIES[policy]
    t = POLICIES[target]
    correct = sum(int(p[x] == t[x]) for x in (0, 1))
    return correct, 2


def score_string(policy: str, target: str = "ID") -> str:
    n, d = score(policy, target)
    return f"{n}/{d}" if n not in (0, d) else str(n // d)


def reachable(start: str, transitions: Mapping[str, Sequence[Tuple[str, str]]]) -> Dict[str, Tuple[str, ...]]:
    require(start in POLICIES, "unknown start policy")
    out: Dict[str, Tuple[str, ...]] = {start: ()}
    q: deque[str] = deque([start])
    while q:
        cur = q.popleft()
        for action, nxt in transitions.get(cur, ()):
            require(nxt in POLICIES, f"unknown policy {nxt}")
            if nxt not in out:
                out[nxt] = out[cur] + (action,)
                q.append(nxt)
    return out


def gamma_profiles(
    start: str,
    transitions: Mapping[str, Sequence[Tuple[str, str]]],
    action_provenance: Mapping[str, Sequence[str]],
    target: str = "ID",
) -> List[dict]:
    paths = reachable(start, transitions)
    profiles: List[dict] = []
    for machine, actions in sorted(paths.items()):
        provenance = {"INITIAL_OR_INHERITED_ORGANIZATION"}
        for action in actions:
            tags = tuple(action_provenance.get(action, ()))
            require(tags, f"missing provenance for development action {action}")
            unknown = sorted(set(tags) - set(PROVENANCE_TAGS))
            require(not unknown, f"unregistered provenance tags: {unknown}")
            provenance.update(tags)
        profiles.append(
            {
                "machine": machine,
                "capability": {f"{target}_TASK": score_string(machine, target)},
                "resources": {
                    "development_steps": len(actions),
                    "external_observations": int("EXTERNAL_OBSERVATION" in provenance),
                    "oracle_queries": int("ORACLE_ADVICE_OR_TOOL" in provenance),
                },
                "provenance": sorted(provenance),
                "history": list(actions),
            }
        )
    return profiles


def profile_capability_set(profiles: Iterable[dict], task: str = "ID_TASK") -> List[str]:
    return sorted({p["capability"][task] for p in profiles})


def entropy_bits(distribution: Mapping[object, float]) -> float:
    total = sum(distribution.values())
    require(abs(total - 1.0) < 1e-12, "distribution must sum to one")
    h = 0.0
    for p in distribution.values():
        require(p >= 0.0, "negative probability")
        if p:
            h -= p * math.log2(p)
    return round(h, 12)


def mutual_information_bits(joint: Mapping[Tuple[object, object], float]) -> float:
    total = sum(joint.values())
    require(abs(total - 1.0) < 1e-12, "joint must sum to one")
    px: Dict[object, float] = {}
    py: Dict[object, float] = {}
    for (x, y), p in joint.items():
        require(p >= 0.0, "negative probability")
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    mi = 0.0
    for (x, y), p in joint.items():
        if p:
            mi += p * math.log2(p / (px[x] * py[y]))
    return round(mi, 12)


def classify_information_case(
    *,
    target_correlated_import: bool,
    initial_target_information: bool,
    random_novelty: bool,
    capability_gain: bool,
    consumed_provenance: Sequence[str],
) -> str:
    unknown = sorted(set(consumed_provenance) - set(PROVENANCE_TAGS))
    require(not unknown, f"unregistered provenance tags: {unknown}")
    if target_correlated_import:
        require(
            any(tag in consumed_provenance for tag in TARGET_CORRELATED_IMPORT_TAGS),
            "target-correlated import omitted from provenance",
        )
        if "ORACLE_ADVICE_OR_TOOL" in consumed_provenance:
            return "IMPORTED_ORACLE_OR_ADVICE_POWER"
        return "IMPORTED_INFORMATION_OR_ADVICE"
    if initial_target_information and capability_gain:
        require("ENDOGENOUS_COMPUTE" in consumed_provenance, "compute unfolding missing ENDOGENOUS_COMPUTE provenance")
        return "COMPUTATIONAL_UNFOLDING_WITHOUT_EXTERNAL_DATA"
    if random_novelty:
        require("STOCHASTIC_VARIATION" in consumed_provenance, "random novelty missing STOCHASTIC_VARIATION provenance")
        return "RANDOM_NOVELTY_WITHOUT_TARGET_ALIGNMENT"
    if capability_gain:
        return "UNEXERCISED_CAPABILITY"
    return "NO_TARGET_INFORMATION_ACQUIRED"


@dataclass(frozen=True)
class BarrierContext:
    S: str
    Pi: Tuple[str, ...]
    Q: str
    R: Tuple[str, ...]
    H: str
    eps: str
    delta: str
    V: str

    def as_dict(self) -> dict:
        return {
            "S": self.S,
            "Pi": list(self.Pi),
            "Q": self.Q,
            "R": list(self.R),
            "H": self.H,
            "eps": self.eps,
            "delta": self.delta,
            "V": self.V,
        }


def validate_barrier_transition(record: Mapping[str, object]) -> None:
    source_status = str(record.get("source_status", ""))
    target_status = str(record.get("target_status", ""))
    require(source_status in BARRIER_STATUSES, f"unknown source status: {source_status}")
    require(target_status in BARRIER_STATUSES, f"unknown target status: {target_status}")
    classes = tuple(record.get("transition_classes", ()))
    require(classes, "transition classification missing")
    require(all(c in TRANSITION_CLASSES for c in classes), "unknown transition class")
    changed_axes = tuple(record.get("changed_axes", ()))
    require(changed_axes, "changed axis missing")
    original = set(record.get("original_premises", ()))
    retained = set(record.get("retained_premises", ()))
    require(original, "original premises missing")
    require(retained.issubset(original), "retained premises must be a subset of original premises")
    require(bool(record.get("nearest_residual_barrier")), "nearest residual barrier missing")
    terminal = str(record.get("terminal", ""))
    require(terminal != "SOLVED_FOREVER", "SOLVED_FOREVER is forbidden")
    require(terminal not in FORBIDDEN_TERMINALS, f"forbidden terminal: {terminal}")
    broke_claim = terminal.startswith("BROKE_") or bool(record.get("claims_literal_contradiction", False))
    if broke_claim:
        require(original == retained, "BROKE_* requires every original premise to be retained")
        require(bool(record.get("same_problem_contract", False)), "BROKE_* requires unchanged problem contract")
        require(bool(record.get("same_output_contract", False)), "BROKE_* requires unchanged output contract")
        require(bool(record.get("contradiction_verified", False)), "BROKE_* requires a verified contradiction")
        require(classes == ("LITERAL_CONTRADICTION",), "BROKE_* requires literal-contradiction classification")
    else:
        require("LITERAL_CONTRADICTION" not in classes, "literal contradiction class requires contradiction claim")


def validate_parent_ledger(path: Path) -> None:
    obj = json.loads(path.read_text())
    pins = obj.get("repository_pins", {})
    require(pins == EXPECTED_PARENT_PINS, "parent pin drift")
    authorities = obj.get("issue_comment_authorities", {})
    require(authorities == HSG_ISSUE_COMMENT_AUTHORITIES, "issue-comment parent authority drift")
    rows = obj.get("rows", [])
    require(rows, "parent ledger must contain rows")
    require(obj.get("parent_census") == len(rows), "parent census mismatch")
    required = {"parent_id", "theorem_or_result", "assumptions", "conclusion", "relaxations", "strongest_source", "af_residual"}
    for row in rows:
        missing = sorted(required - set(row))
        require(not missing, f"parent row missing fields: {missing}")
        require(row["assumptions"], f"parent {row.get('parent_id')} missing assumptions")
        require(row["conclusion"], f"parent {row.get('parent_id')} missing conclusion")
        require(row["af_residual"], f"parent {row.get('parent_id')} missing AF residual")


def make_transition_records() -> List[dict]:
    verification_exact_ctx = BarrierContext(
        "EFFECTIVE_COMPUTATION", (), "UNRESTRICTED_SEMANTIC_PROPERTY_DECISION",
        ("FINITE_TIME",), "UNBOUNDED_PROGRAM_SET", "0", "0", "EXACT_TOTAL_DECISION"
    )
    abstract_ctx = BarrierContext(
        "EFFECTIVE_COMPUTATION", (), "UNRESTRICTED_SEMANTIC_PROPERTY_DECISION",
        ("FINITE_ANALYSIS",), "UNBOUNDED_PROGRAM_SET", "0", "0", "SOUND_ABSTRACT_CERTIFICATE"
    )
    finite_ctx = BarrierContext(
        "FINITE_PROMISE_SLICE", (), "UNRESTRICTED_SEMANTIC_PROPERTY_DECISION",
        ("FINITE_ENUMERATION",), "FINITE_PROMISE_SET", "0", "0", "EXACT_TOTAL_DECISION"
    )
    single_id_ctx = BarrierContext(
        "EFFECTIVE_LEARNER", ("POSITIVE_TEXT",), "LANGUAGE_IDENTIFICATION",
        ("UNBOUNDED_TIME",), "LIMIT", "0", "0", "SINGLE_ANSWER_OUTPUT"
    )
    list_ctx = BarrierContext(
        "EFFECTIVE_LEARNER", ("POSITIVE_TEXT",), "LANGUAGE_IDENTIFICATION",
        ("UNBOUNDED_TIME",), "LIMIT", "0", "0", "FINITE_LIST_OUTPUT"
    )
    base_halting_ctx = BarrierContext(
        "BASE_EFFECTIVE_COMPUTATION", (), "BASE_HALTING_DECISION",
        ("FINITE_EFFECTIVE_COMPUTE",), "UNBOUNDED_PROGRAM_SET", "0", "0", "EXACT_TOTAL_DECISION"
    )
    oracle_ctx = BarrierContext(
        "BASE_PLUS_HALTING_ORACLE", ("ORACLE_A",), "BASE_HALTING_DECISION",
        ("ORACLE_QUERY",), "UNBOUNDED_PROGRAM_SET", "0", "0", "EXACT_TOTAL_DECISION"
    )
    return [
        {
            "id": "F7_ABSTRACT_INTERPRETATION",
            "source_context": verification_exact_ctx.as_dict(),
            "target_context": abstract_ctx.as_dict(),
            "source_status": "UNDECIDABLE_RELATIVE_TO_S",
            "target_status": "SOUND_INCOMPLETE_APPROXIMATION",
            "changed_axes": ["R", "V"],
            "original_premises": ["UNBOUNDED_PROGRAM_CLASS", "EXACT_TOTAL_DECISION"],
            "retained_premises": ["UNBOUNDED_PROGRAM_CLASS"],
            "extra_power_or_weakened_requirement": "replace exact total decision by sound over-approximate certification",
            "nearest_residual_barrier": "false alarms / incompleteness remain possible; unrestricted exact total decision remains unavailable",
            "transition_classes": ["APPROXIMATION", "CERTIFICATE"],
            "same_problem_contract": True,
            "same_output_contract": False,
            "contradiction_verified": False,
            "terminal": "BARRIER_DISPLACED_BY_SOUND_INCOMPLETE_APPROXIMATION",
        },
        {
            "id": "F7_FINITE_PROMISE",
            "source_context": verification_exact_ctx.as_dict(),
            "target_context": finite_ctx.as_dict(),
            "source_status": "UNDECIDABLE_RELATIVE_TO_S",
            "target_status": "DECIDABLE",
            "changed_axes": ["S", "H"],
            "original_premises": ["UNBOUNDED_PROGRAM_CLASS", "EXACT_TOTAL_DECISION"],
            "retained_premises": ["EXACT_TOTAL_DECISION"],
            "extra_power_or_weakened_requirement": "restrict domain to a finite promised slice",
            "nearest_residual_barrier": "the unrestricted class remains outside the finite promise",
            "transition_classes": ["DOMAIN_RESTRICTION", "PROMISE_PROBLEM"],
            "same_problem_contract": False,
            "same_output_contract": True,
            "contradiction_verified": False,
            "terminal": "DECIDABLE_ONLY_ON_FINITE_PROMISE_SLICE",
        },
        {
            "id": "F7_LIST_OUTPUT",
            "source_context": single_id_ctx.as_dict(),
            "target_context": list_ctx.as_dict(),
            "source_status": "NOT_IDENTIFIABLE_AT_SCOPE",
            "target_status": "IDENTIFIABLE_IN_LIMIT",
            "changed_axes": ["V"],
            "original_premises": ["SINGLE_ANSWER_OUTPUT", "TARGET_CLASS_SCOPE"],
            "retained_premises": ["TARGET_CLASS_SCOPE"],
            "extra_power_or_weakened_requirement": "allow a registered finite list of guesses in the limit",
            "nearest_residual_barrier": "single-answer identification is not thereby established",
            "transition_classes": ["LIST_OR_SET_OUTPUT"],
            "same_problem_contract": True,
            "same_output_contract": False,
            "contradiction_verified": False,
            "terminal": "OUTPUT_CONTRACT_WEAKENED_TO_LIST_IDENTIFICATION",
        },
        {
            "id": "F7_ORACLE_RELATIVIZATION",
            "source_context": base_halting_ctx.as_dict(),
            "target_context": oracle_ctx.as_dict(),
            "source_status": "UNDECIDABLE_RELATIVE_TO_S",
            "target_status": "DECIDABLE",
            "changed_axes": ["S", "Pi", "R"],
            "original_premises": ["NO_ORACLE", "BASE_EFFECTIVE_SUBSTRATE"],
            "retained_premises": [],
            "extra_power_or_weakened_requirement": "add an explicitly charged oracle channel deciding the base halting set",
            "nearest_residual_barrier": "decidability is relative to the stronger oracle substrate; its relative halting problem remains above it",
            "transition_classes": ["ORACLE_OR_ADVICE", "SUBSTRATE_EXPANSION"],
            "same_problem_contract": True,
            "same_output_contract": True,
            "contradiction_verified": False,
            "terminal": "RELATIVE_DECIDABILITY_WITH_IMPORTED_ORACLE_POWER",
        },
    ]
