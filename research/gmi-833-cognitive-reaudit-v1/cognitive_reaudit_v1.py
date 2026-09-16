#!/usr/bin/env python3
"""Exact finite witnesses for the #917 cognitive-function re-audit."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha1
from itertools import combinations, product
import json
from pathlib import Path
from typing import Hashable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = (
    "GMI_833_COGNITIVE_REAUDIT_FUNCTIONAL_DIFFERENTIATION_"
    "RESOURCE_RATIONAL_SELECTION_AND_STATIC_QUOTIENT_WITH_ABSTENTION"
)
CANNOT_IDENTIFY = "CANNOT_IDENTIFY_FROM_PARTIAL_INTERFACE"
FORBIDDEN_PROMOTIONS = (
    "MEMORY_ANATOMY_IDENTIFIED",
    "UNIQUE_FOUR_STORE_ARCHITECTURE_DERIVED",
    "COST_LEGALIZES_INEXACT_ATTENTION",
    "UNIVERSAL_ATTENTION_ARCHITECTURE",
    "PARTIAL_SAMPLES_IDENTIFY_CONCEPT",
    "AMORTIZATION_CREATES_SEMANTICS",
    "GENERAL_CONCEPT_LEARNING_SOLVED",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "foundation",
        "research/gmi-833-foundation-v1/RESULT_V1.json",
        "c0c574c4ec6e237d5fdafa694eac131399625a70",
        "terminal",
        "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE",
    ),
    (
        "axiom_core",
        "research/gmi-833-axiom-core-v1/RESULT_V1.json",
        "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9",
        "claim_ceiling",
        "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE",
    ),
    (
        "historical_memory_theorem",
        "research/machine-intelligence-morphogenesis-v1/GMI_MEMORY_REGIME_PARTITION_V1.md",
        "25c6b3c88c07a8cff84d65e573cddbac12781034",
        None,
        None,
    ),
    (
        "historical_memory_witness",
        "research/machine-intelligence-morphogenesis-v1/gmi_microscope/memory_regime_witness.py",
        "10390cefbcc6978c0fb1a006aef5c9687ba3ef37",
        None,
        None,
    ),
    (
        "attention_corrigendum",
        "research/gmi-attention-sequence-v1/ATTENTION_SEQUENCE_THEOREM_V1.md",
        "ed000be608435bc48ca46ea787cc9ca665b8a477",
        None,
        None,
    ),
    (
        "attention_witness",
        "research/gmi-attention-sequence-v1/attention_witness.py",
        "66ab7caeb12d383f3aa25cce3a5c6c9139755ede",
        None,
        None,
    ),
    (
        "concept_admission_theorem",
        "research/gmi-concept-subgoal-repair-v1/CONCEPT_ADMISSION_THEOREM_V1.md",
        "4f77c968a3a83061dbc48201ed31b119c1c015b4",
        None,
        None,
    ),
    (
        "concept_implementation",
        "research/gmi-concept-subgoal-repair-v1/concept_v1.py",
        "ba5993d11c0a1a8616c686cc33509f60f65e4bb1",
        None,
        None,
    ),
)


def exact(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or type(value) not in (int, Fraction):
        raise ValueError("registered values must be exact integers or Fractions")
    return Fraction(value)


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows = []
    for name, path, expected_blob, field, expected_claim in PARENT_PINS:
        target = root / path
        if not target.is_file():
            rows.append({"name": name, "path": path, "actual_blob": None, "blob_ok": False, "claim_ok": False})
            continue
        data = target.read_bytes()
        claim_ok = True
        if field is not None:
            try:
                claim_ok = json.loads(data).get(field) == expected_claim
            except (UnicodeDecodeError, json.JSONDecodeError):
                claim_ok = False
        rows.append(
            {
                "name": name,
                "path": path,
                "actual_blob": git_blob_sha(data),
                "blob_ok": git_blob_sha(data) == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


# MEMORY-1: operational signatures, not anatomical labels.
PROBE_NAMES = (
    "within_event_carry",
    "cross_event_survival",
    "event_identity_recall",
    "class_response_recall",
    "repeat_execution_saving",
)
REGISTERED_MEMORY_PROFILES = {
    "working": (1, 0, 0, 0, 0),
    "episodic": (0, 1, 1, 0, 0),
    "semantic": (0, 1, 0, 1, 0),
    "procedural": (0, 1, 0, 0, 1),
}


def normalize_profile(profile: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(profile)
    if len(normalized) != len(PROBE_NAMES) or any(type(value) is not int or value not in (0, 1) for value in normalized):
        raise ValueError("a memory profile must contain one binary response per registered probe")
    return normalized


def profile_distinction(left: Sequence[int], right: Sequence[int]) -> dict[str, object]:
    a, b = normalize_profile(left), normalize_profile(right)
    # ``normalize_profile`` has already proved equal lengths; avoid
    # ``zip(..., strict=True)`` so the frozen witness also replays on Python 3.9.
    witnesses = tuple(name for name, x, y in zip(PROBE_NAMES, a, b) if x != y)
    return {"distinguishable": bool(witnesses), "separating_probes": witnesses}


def audit_registered_memory_roles() -> dict[str, object]:
    pairs = {}
    for left, right in combinations(REGISTERED_MEMORY_PROFILES, 2):
        pairs[f"{left}/{right}"] = profile_distinction(
            REGISTERED_MEMORY_PROFILES[left], REGISTERED_MEMORY_PROFILES[right]
        )
    return {"pairs": pairs, "all_pairwise_distinct": all(row["distinguishable"] for row in pairs.values())}


def memory_partition_nonidentification_hostile() -> dict[str, object]:
    protected_profile = {
        "responses": ("current", "episode-7", "class-blue", "action-ok"),
        "charged_trace": (4, 3, 2, 1),
    }
    implementations = {
        "four_separated_stores": protected_profile,
        "one_tagged_unified_store": protected_profile,
    }
    return {
        "implementations": implementations,
        "protected_profiles_equal": len({repr(value) for value in implementations.values()}) == 1,
        "physical_partition_identifiable": False,
        "terminal": "FUNCTIONAL_ROLES_DISTINCT__PHYSICAL_PARTITION_NOT_IDENTIFIED",
    }


# ATTENTION-1: sufficiency precedes resource comparison.
def attention_comparison(
    item_count: int,
    relevant: Sequence[int],
    selected: Sequence[int],
    materialization_cost: int | Fraction,
    full_discovery_cost: int | Fraction = 0,
    selective_discovery_cost: int | Fraction = 0,
) -> dict[str, object]:
    if isinstance(item_count, bool) or type(item_count) is not int or item_count <= 0:
        raise ValueError("item_count must be a positive integer")
    legal = set(range(item_count))
    relevant_set, selected_set = set(relevant), set(selected)
    if not relevant_set or not relevant_set <= legal or not selected_set <= legal:
        raise ValueError("relevant must be nonempty and both sets must use legal item indices")
    c = exact(materialization_cost)
    full_d, selective_d = exact(full_discovery_cost), exact(selective_discovery_cost)
    if c <= 0 or full_d < 0 or selective_d < 0:
        raise ValueError("materialization cost must be positive and discovery costs nonnegative")
    sufficient = relevant_set <= selected_set
    full_cost = item_count * c + full_d
    selective_cost = len(selected_set) * c + selective_d
    premium = selective_d - full_d
    avoided = (item_count - len(selected_set)) * c
    strict_win = sufficient and selective_cost < full_cost
    return {
        "sufficient": sufficient,
        "full_cost": full_cost,
        "selective_cost": selective_cost,
        "discovery_premium": premium,
        "avoided_materialization": avoided,
        "selective_strictly_rational": strict_win,
        "strict_iff": strict_win == (sufficient and premium < avoided),
        "decision": "SELECTIVE" if strict_win else "FULL_OR_TIE" if sufficient else "INADMISSIBLE_SELECTION",
    }


def minimum_sufficient_selection(item_count: int, relevant: Sequence[int]) -> dict[str, object]:
    result = attention_comparison(item_count, relevant, relevant, 1)
    relevant_set = set(relevant)
    exact_subsets = []
    for mask in range(1 << item_count):
        selected = {index for index in range(item_count) if mask & (1 << index)}
        if relevant_set <= selected:
            exact_subsets.append(selected)
    minimum = min(len(row) for row in exact_subsets)
    minimizers = [row for row in exact_subsets if len(row) == minimum]
    return {
        "relevant": tuple(sorted(relevant_set)),
        "minimum_size": minimum,
        "unique_minimizer": tuple(sorted(next(iter(minimizers)))),
        "unique": len(minimizers) == 1,
        "witness_sufficient": result["sufficient"],
    }


def blind_selection_hostile(item_count: int, fixed_selection_size: int) -> dict[str, object]:
    if (
        isinstance(item_count, bool)
        or isinstance(fixed_selection_size, bool)
        or type(item_count) is not int
        or type(fixed_selection_size) is not int
        or item_count < 2
        or not 0 <= fixed_selection_size < item_count
    ):
        raise ValueError("hostile requires 0 <= fixed_selection_size < item_count and item_count >= 2")
    selected = tuple(range(fixed_selection_size))
    successes = sum(
        attention_comparison(item_count, (query,), selected, 1)["sufficient"] for query in range(item_count)
    )
    return {
        "queries": item_count,
        "successes": successes,
        "exact_fraction": Fraction(successes, item_count),
        "universally_exact": successes == item_count,
    }


# CONCEPT-1: static response-row quotient and fail-closed partial observation.
def normalize_table(table: Sequence[Sequence[Hashable]]) -> tuple[tuple[Hashable, ...], ...]:
    rows = tuple(tuple(row) for row in table)
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("response table must be nonempty and rectangular with at least one query")
    return rows


def response_row_quotient(table: Sequence[Sequence[Hashable]]) -> dict[str, object]:
    rows = normalize_table(table)
    label_by_row: dict[tuple[Hashable, ...], int] = {}
    labels = []
    for row in rows:
        if row not in label_by_row:
            label_by_row[row] = len(label_by_row)
        labels.append(label_by_row[row])
    return {"labels": tuple(labels), "class_count": len(label_by_row), "rows": tuple(label_by_row)}


def encoding_is_exact(table: Sequence[Sequence[Hashable]], encoding: Sequence[Hashable]) -> bool:
    rows = normalize_table(table)
    codes = tuple(encoding)
    if len(codes) != len(rows):
        raise ValueError("encoding must assign exactly one code to every experience")
    return all(codes[i] != codes[j] or rows[i] == rows[j] for i in range(len(rows)) for j in range(i + 1, len(rows)))


def quotient_minimality(table: Sequence[Sequence[Hashable]]) -> dict[str, object]:
    rows = normalize_table(table)
    quotient = response_row_quotient(rows)
    exact_encodings = []
    for encoding in product(range(len(rows)), repeat=len(rows)):
        if encoding_is_exact(rows, encoding):
            exact_encodings.append(encoding)
    minimum = min(len(set(encoding)) for encoding in exact_encodings)
    return {
        "quotient_classes": quotient["class_count"],
        "minimum_exact_codes": minimum,
        "quotient_is_exact": encoding_is_exact(rows, quotient["labels"]),
        "coarsest_exact": minimum == quotient["class_count"],
    }


def equivalence_signature(table: Sequence[Sequence[Hashable]]) -> tuple[bool, ...]:
    rows = normalize_table(table)
    return tuple(rows[i] == rows[j] for i in range(len(rows)) for j in range(i + 1, len(rows)))


def partial_interface_identifiability(
    completions: Sequence[Sequence[Sequence[Hashable]]], observed_queries: Sequence[int]
) -> dict[str, object]:
    normalized = tuple(normalize_table(table) for table in completions)
    if not normalized:
        raise ValueError("at least one completion is required")
    shape = (len(normalized[0]), len(normalized[0][0]))
    if any((len(table), len(table[0])) != shape for table in normalized):
        raise ValueError("all completions must share one finite interface")
    observed = tuple(observed_queries)
    if not observed or len(set(observed)) != len(observed) or any(type(q) is not int or not 0 <= q < shape[1] for q in observed):
        raise ValueError("observed queries must be a nonempty duplicate-free legal subset")
    observed_views = {
        tuple(tuple(row[q] for q in observed) for row in table)
        for table in normalized
    }
    if len(observed_views) != 1:
        raise ValueError("hostile completions must agree on every observed response")
    signatures = {equivalence_signature(table) for table in normalized}
    identifiable = len(signatures) == 1
    return {
        "completion_count": len(normalized),
        "quotient_signatures": tuple(sorted(signatures)),
        "identifiable": identifiable,
        "status": "IDENTIFIED_AT_SUPPLIED_COMPLETIONS" if identifiable else CANNOT_IDENTIFY,
    }


def partial_interface_hostile() -> dict[str, object]:
    return partial_interface_identifiability(
        (
            ((0, 0), (0, 0)),
            ((0, 0), (0, 1)),
        ),
        (0,),
    )


def verified_abstraction_adoption(
    reuse_count: int,
    fresh_cost: int | Fraction,
    installation_cost: int | Fraction,
    lookup_cost: int | Fraction,
) -> dict[str, object]:
    if isinstance(reuse_count, bool) or type(reuse_count) is not int or reuse_count < 1:
        raise ValueError("reuse_count must be a positive integer")
    fresh, install, lookup = exact(fresh_cost), exact(installation_cost), exact(lookup_cost)
    if fresh < 0 or install < 0 or lookup < 0:
        raise ValueError("costs must be nonnegative")
    fresh_total = reuse_count * fresh
    retained_total = fresh + install + (reuse_count - 1) * lookup
    gain = (reuse_count - 1) * (fresh - lookup) - install
    return {
        "fresh_total": fresh_total,
        "retained_total": retained_total,
        "gain": gain,
        "strictly_adopt": retained_total < fresh_total,
        "strict_iff": (retained_total < fresh_total) == (gain > 0),
        "semantics_created": False,
        "requires_verified_quotient": True,
    }


def exhaustive_census() -> dict[str, int]:
    memory_profile_pairs = 0
    profiles = tuple(product((0, 1), repeat=len(PROBE_NAMES)))
    for left, right in combinations(profiles, 2):
        result = profile_distinction(left, right)
        if not result["distinguishable"]:
            raise ValueError("distinct operational profiles were not separated")
        memory_profile_pairs += 1

    attention_comparisons = 0
    minimum_selection_cases = 0
    for n in range(1, 6):
        for relevant_mask in range(1, 1 << n):
            relevant = tuple(i for i in range(n) if relevant_mask & (1 << i))
            minimum = minimum_sufficient_selection(n, relevant)
            if not minimum["unique"] or minimum["unique_minimizer"] != relevant:
                raise ValueError("minimum sufficient selection theorem failed")
            minimum_selection_cases += 1
            for selected_mask in range(1 << n):
                selected = tuple(i for i in range(n) if selected_mask & (1 << i))
                for c, full_d, selective_d in product(range(1, 4), range(3), range(6)):
                    result = attention_comparison(n, relevant, selected, c, full_d, selective_d)
                    if not result["strict_iff"]:
                        raise ValueError("attention phase identity failed")
                    attention_comparisons += 1

    blind_attention_cases = 0
    for n in range(2, 9):
        for size in range(n):
            hostile = blind_selection_hostile(n, size)
            if hostile["universally_exact"] or hostile["exact_fraction"] != Fraction(size, n):
                raise ValueError("blind-selection hostile failed")
            blind_attention_cases += 1

    quotient_tables = 0
    encoding_checks = 0
    for experience_count in range(1, 5):
        for query_count in range(1, 3):
            for flat in product((0, 1), repeat=experience_count * query_count):
                table = tuple(
                    flat[index * query_count : (index + 1) * query_count]
                    for index in range(experience_count)
                )
                minimality = quotient_minimality(table)
                if not minimality["quotient_is_exact"] or not minimality["coarsest_exact"]:
                    raise ValueError("response-row quotient minimality failed")
                quotient_tables += 1
                encoding_checks += experience_count ** experience_count

    adoption_cases = 0
    for reuse, fresh, install, lookup in product(range(1, 9), range(5), range(5), range(5)):
        if not verified_abstraction_adoption(reuse, fresh, install, lookup)["strict_iff"]:
            raise ValueError("abstraction adoption identity failed")
        adoption_cases += 1

    return {
        "memory_profile_pairs": memory_profile_pairs,
        "attention_comparisons": attention_comparisons,
        "minimum_selection_cases": minimum_selection_cases,
        "blind_attention_cases": blind_attention_cases,
        "quotient_tables": quotient_tables,
        "encoding_checks": encoding_checks,
        "adoption_cases": adoption_cases,
    }


def validate_ledgers() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {"id", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = data["claims"]
    if len(claims) != 4 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN":
        raise ValueError("independent-review gap must remain open")
    return {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_COGNITIVE_REAUDIT_V1.json").read_text())
    expected_rows = {
        "- [ ] Re-audit memory differentiation under the upgraded foundation.",
        "- [ ] Re-audit attention as resource-rational selective processing.",
        "- [ ] Re-audit concept formation/abstraction.",
    }
    replacements = reconciliation.get("replacements", [])
    manifest_ok = (
        manifest.get("issue") == 917
        and manifest.get("source_pr") == 919
        and manifest.get("parent_issue") == 833
        and manifest.get("freeze_commit") == "4ca2ecd71bc177c2855d47bc1a5eb87d5c0ef48d"
        and manifest.get("frozen_main") == "36064c956ba24bd85949960dd23d6326656ba3e6"
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 3
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == 833
        and reconciliation.get("source_issue") == 917
        and reconciliation.get("source_pr") == 919
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and len(replacements) == 3
        and {row.get("old") for row in replacements} == expected_rows
        and all(row.get("anchor") == "# M. Cognitive-function derivation upgrade" for row in replacements)
        and all(row.get("new", "").startswith("- [x]") and "PR #919 / #917" in row.get("new", "") for row in replacements)
    )
    return {
        "manifest_ok": manifest_ok,
        "reconciliation_ok": reconciliation_ok,
        "reconciliation_rows": len(replacements),
        "source_pr": reconciliation.get("source_pr"),
    }


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    roles = audit_registered_memory_roles()
    partition_hostile = memory_partition_nonidentification_hostile()
    attention_positive = attention_comparison(4, (1,), (1,), 2, 0, 1)
    attention_high_discovery = attention_comparison(4, (1,), (1,), 2, 0, 7)
    blind = blind_selection_hostile(4, 1)
    quotient = quotient_minimality(((0, 1), (0, 1), (1, 0)))
    partial = partial_interface_hostile()
    adoption = verified_abstraction_adoption(4, 5, 3, 1)
    adoption_no_gain = verified_abstraction_adoption(2, 1, 1, 2)
    census = exhaustive_census()
    ledgers = validate_ledgers()
    package = validate_package_contracts()
    expected_census = {
        "memory_profile_pairs": 496,
        "attention_comparisons": 70308,
        "minimum_selection_cases": 57,
        "blind_attention_cases": 35,
        "quotient_tables": 370,
        "encoding_checks": 71662,
        "adoption_cases": 1000,
    }
    checks = {
        "parents_exactly_pinned": bool(parent_audit["all_ok"]),
        "registered_memory_roles_pairwise_distinct": roles["all_pairwise_distinct"],
        "memory_partition_not_identified": partition_hostile["protected_profiles_equal"] and not partition_hostile["physical_partition_identifiable"],
        "attention_positive_obeys_phase_law": attention_positive["sufficient"] and attention_positive["selective_strictly_rational"] and attention_positive["strict_iff"],
        "high_discovery_restores_full_processing": attention_high_discovery["sufficient"] and not attention_high_discovery["selective_strictly_rational"] and attention_high_discovery["strict_iff"],
        "blind_equal_size_selection_is_inexact": not blind["universally_exact"] and blind["exact_fraction"] == Fraction(1, 4),
        "response_row_quotient_is_coarsest_exact": quotient["quotient_is_exact"] and quotient["coarsest_exact"],
        "partial_interface_requires_abstention": not partial["identifiable"] and partial["status"] == CANNOT_IDENTIFY,
        "adoption_threshold_is_exact_but_not_formation": adoption["strictly_adopt"] and adoption["strict_iff"] and not adoption["semantics_created"],
        "bad_adoption_control_rejected": not adoption_no_gain["strictly_adopt"] and adoption_no_gain["strict_iff"],
        "exhaustive_census_complete": census == expected_census,
        "scientific_ledgers_complete": ledgers == {"claim_ledgers": 4, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        "manifest_and_reconciliation_exact": package == {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 3, "source_pr": 919},
    }
    return {
        "schema": "GMI833CognitiveReauditResultV1",
        "issue": 917,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "memory_roles": roles,
            "memory_partition_hostile": partition_hostile,
            "attention_positive": attention_positive,
            "attention_high_discovery_twin": attention_high_discovery,
            "attention_blind_twin": blind,
            "static_quotient": quotient,
            "partial_interface_hostile": partial,
            "verified_abstraction_adoption": adoption,
            "adoption_no_gain_control": adoption_no_gain,
        },
        "scientific_ledger": ledgers,
        "package_contracts": package,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))}
    return value


def canonical_json(value) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt(audit_parents())), end="")
