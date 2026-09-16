#!/usr/bin/env python3
"""Exact finite developmental-potential and capital-separation witnesses for #908."""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path
from typing import Hashable, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = "GMI_833_FINITE_DEVELOPMENTAL_POTENTIAL_EVOLVABILITY_AND_CAPITAL_SEPARATION_AT_REGISTERED_SCOPE"
ZERO_MASS = "UNREACHABLE_ZERO_USEFUL_MASS"
FORBIDDEN_PROMOTIONS = (
    "UNIVERSAL_OPEN_ENDED_EVOLVABILITY",
    "HISTORY_ALWAYS_HELPS",
    "PROPOSAL_COUNT_EQUALS_WALL_CLOCK_OR_ENERGY",
    "EMPIRICAL_K2_ESTABLISHED",
    "CURRENT_CAPABILITY_IDENTIFIES_POTENTIAL",
    "FUTURE_TASK_PREDICTION_VALIDATED",
    "RECURSIVE_PRIMITIVE_INVENTION_ESTABLISHED",
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
        "morphcap",
        "research/gmi-833-morphcap-v1/RESULT_V1.json",
        "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a",
        "claim_ceiling",
        "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "axiom_core",
        "research/gmi-833-axiom-core-v1/RESULT_V1.json",
        "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9",
        "claim_ceiling",
        "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE",
    ),
    (
        "developmental_naturality",
        "research/gmi-833-developmental-naturality-v1/RESULT_V1.json",
        "04b35a9926cac10d51fe9175e231e943c52b178b",
        "claim_ceiling",
        "GMI_EXACT_DEVELOPMENTAL_NATURALITY_AT_REGISTERED_FINITE_DETERMINISTIC_SCOPE",
    ),
    (
        "useful_descendant",
        "research/gmi-useful-descendant-evolvability-v1/RESULT_V1.json",
        "4cbaa3d2f3d19927c5c678c02581055ade277d80",
        "claim_ceiling",
        "USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE",
    ),
    (
        "development_amortization",
        "research/gmi-development-amortization-v1/DEVELOPMENT_AMORTIZATION_V1.json",
        "567e6918fef13578a75f2cb43b4c8cccd6e642db",
        "claim_ceiling",
        "G2",
    ),
    (
        "developmental_capital",
        "research/gmi-developmental-capital-v1/DEVELOPMENTAL_CAPITAL_V1.md",
        "fcc44fbc2dd04bad1536f878fe2d34680d4118db",
        None,
        None,
    ),
)


def exact(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or type(value) not in (int, Fraction):
        raise ValueError("registered numeric values must be exact integers or Fractions")
    return Fraction(value)


def exact_vector(values: Sequence[int | Fraction], *, positive_total: bool = False) -> tuple[Fraction, ...]:
    vector = tuple(exact(value) for value in values)
    if not vector or any(value < 0 for value in vector):
        raise ValueError("resource vectors must be nonempty, aligned, and nonnegative")
    if positive_total and not any(value > 0 for value in vector):
        raise ValueError("at least one resource coordinate must be positive")
    return vector


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
        actual_blob = git_blob_sha(data)
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
                "actual_blob": actual_blob,
                "blob_ok": actual_blob == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def vector_leq(left: Sequence[Fraction], right: Sequence[Fraction]) -> bool:
    return len(left) == len(right) and all(x <= y for x, y in zip(left, right, strict=True))


def add_vectors(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    if len(left) != len(right):
        raise ValueError("resource vectors must align")
    return tuple(x + y for x, y in zip(left, right, strict=True))


def reachable_with_costs(
    states: Iterable[Hashable],
    initial: Hashable,
    edges: Sequence[tuple[Hashable, Hashable, Sequence[int | Fraction]]],
    budget: Sequence[int | Fraction],
) -> dict[Hashable, tuple[tuple[Fraction, ...], ...]]:
    carrier = tuple(states)
    if not carrier or len(set(carrier)) != len(carrier) or initial not in carrier:
        raise ValueError("developmental carrier must be nonempty/unique and contain the initial state")
    carrier_set = set(carrier)
    bound = exact_vector(budget)
    normalized_edges = []
    for source, target, raw_cost in edges:
        if source not in carrier_set or target not in carrier_set:
            raise ValueError("developmental edge must remain inside the carrier")
        cost = exact_vector(raw_cost)
        if len(cost) != len(bound):
            raise ValueError("edge costs and budget must align")
        normalized_edges.append((source, target, cost))

    labels: dict[Hashable, list[tuple[Fraction, ...]]] = {state: [] for state in carrier}
    zero = tuple(Fraction(0) for _ in bound)
    labels[initial].append(zero)
    queue = deque([(initial, zero)])
    while queue:
        state, cost_so_far = queue.popleft()
        if cost_so_far not in labels[state]:
            continue
        for source, target, edge_cost in normalized_edges:
            if source != state:
                continue
            candidate = add_vectors(cost_so_far, edge_cost)
            if not vector_leq(candidate, bound):
                continue
            if any(vector_leq(existing, candidate) for existing in labels[target]):
                continue
            labels[target] = [existing for existing in labels[target] if not vector_leq(candidate, existing)]
            labels[target].append(candidate)
            queue.append((target, candidate))
    return {
        state: tuple(sorted(costs))
        for state, costs in labels.items()
        if costs
    }


def developmental_potential(
    states: Iterable[Hashable],
    initial: Hashable,
    capabilities: Mapping[Hashable, int | Fraction],
    edges: Sequence[tuple[Hashable, Hashable, Sequence[int | Fraction]]],
    budget: Sequence[int | Fraction],
) -> dict[str, object]:
    carrier = tuple(states)
    if set(capabilities) != set(carrier):
        raise ValueError("every and only developmental states need a capability score")
    scores = {state: exact(capabilities[state]) for state in carrier}
    reachable = reachable_with_costs(carrier, initial, edges, budget)
    current = scores[initial]
    potential = max(scores[state] for state in reachable)
    return {
        "current_capability": current,
        "developmental_potential": potential,
        "headroom": potential - current,
        "reachable_states": tuple(state for state in carrier if state in reachable),
        "nondominated_path_costs": reachable,
    }


def validate_kernel(kernel: Mapping[Hashable, int | Fraction]) -> dict[Hashable, Fraction]:
    if not kernel:
        raise ValueError("proposal kernel must have a nonempty finite carrier")
    normalized = {item: exact(mass) for item, mass in kernel.items()}
    if any(mass < 0 for mass in normalized.values()) or sum(normalized.values(), Fraction(0)) != 1:
        raise ValueError("proposal kernel must be an exact normalized probability law")
    return normalized


def useful_descendant_mass(
    kernel: Mapping[Hashable, int | Fraction], useful: Iterable[Hashable]
) -> Fraction:
    normalized = validate_kernel(kernel)
    useful_set = set(useful)
    if not useful_set.issubset(normalized):
        raise ValueError("useful descendants must lie inside the kernel carrier")
    return sum((normalized[item] for item in useful_set), Fraction(0))


def iid_first_hit(mass: int | Fraction) -> dict[str, object]:
    probability = exact(mass)
    if probability < 0 or probability > 1:
        raise ValueError("useful-descendant mass must lie in [0,1]")
    if probability == 0:
        return {"status": ZERO_MASS, "expected_proposals": None}
    return {"status": "FINITE_EXPECTATION", "expected_proposals": 1 / probability}


def priced_burden(raw: Sequence[int | Fraction], prices: Sequence[int | Fraction]) -> Fraction:
    vector = exact_vector(raw)
    price_vector = exact_vector(prices, positive_total=True)
    if len(vector) != len(price_vector):
        raise ValueError("raw burden and registered prices must align")
    return sum((value * price for value, price in zip(vector, price_vector, strict=True)), Fraction(0))


def history_discovery_comparison(
    baseline_kernel: Mapping[Hashable, int | Fraction],
    history_kernel: Mapping[Hashable, int | Fraction],
    useful: Iterable[Hashable],
    stored_solutions: Iterable[Hashable],
    per_proposal_burden: Sequence[int | Fraction],
    history_overhead: Sequence[int | Fraction],
    prices: Sequence[int | Fraction],
) -> dict[str, object]:
    baseline = validate_kernel(baseline_kernel)
    history = validate_kernel(history_kernel)
    if set(baseline) != set(history):
        raise ValueError("baseline and history proposal laws must share one carrier")
    useful_set, stored_set = set(useful), set(stored_solutions)
    if not useful_set.issubset(baseline) or not stored_set.issubset(baseline):
        raise ValueError("useful/stored identifiers must lie inside the descendant carrier")
    if useful_set & stored_set:
        raise ValueError("search-policy assay must keep held-out useful descendants out of stored solutions")
    proposal = exact_vector(per_proposal_burden, positive_total=True)
    overhead = exact_vector(history_overhead)
    if len(proposal) != len(overhead):
        raise ValueError("proposal burden and history overhead must align")
    p0 = useful_descendant_mass(baseline, useful_set)
    ph = useful_descendant_mass(history, useful_set)
    c = priced_burden(proposal, prices)
    h = priced_burden(overhead, prices)
    if c <= 0:
        raise ValueError("registered price vector must assign positive burden to a proposal")

    base_cost = None if p0 == 0 else c / p0
    history_cost = None if ph == 0 else h + c / ph
    if base_cost is None and history_cost is None:
        verdict = "BOTH_UNREACHABLE"
    elif base_cost is None:
        verdict = "HISTORY_STRICTLY_IMPROVES"
    elif history_cost is None:
        verdict = "HISTORY_HARMS"
    elif history_cost < base_cost:
        verdict = "HISTORY_STRICTLY_IMPROVES"
    elif history_cost == base_cost:
        verdict = "TIE"
    else:
        verdict = "HISTORY_HARMS"
    positive_mass_iff = None
    if p0 > 0 and ph > 0:
        positive_mass_iff = (verdict == "HISTORY_STRICTLY_IMPROVES") == (h + c / ph < c / p0)
    return {
        "baseline_mass": p0,
        "history_mass": ph,
        "per_proposal_priced_burden": c,
        "history_priced_overhead": h,
        "baseline_expected_priced_burden": base_cost,
        "history_expected_priced_burden": history_cost,
        "verdict": verdict,
        "positive_mass_iff_holds": positive_mass_iff,
        "proposal_law_changed": baseline != history,
    }


def classify_capital(
    useful: Iterable[Hashable],
    stored_solutions: Iterable[Hashable],
    baseline_kernel: Mapping[Hashable, int | Fraction],
    history_kernel: Mapping[Hashable, int | Fraction],
    per_proposal_burden: Sequence[int | Fraction],
    history_overhead: Sequence[int | Fraction],
    prices: Sequence[int | Fraction],
) -> dict[str, object]:
    baseline = validate_kernel(baseline_kernel)
    history = validate_kernel(history_kernel)
    useful_set, stored_set = set(useful), set(stored_solutions)
    if not useful_set.issubset(baseline) or not stored_set.issubset(baseline) or set(baseline) != set(history):
        raise ValueError("capital assay objects must share one registered carrier")
    solution_capital = bool(useful_set & stored_set)
    law_changed = baseline != history
    if solution_capital:
        if law_changed:
            return {
                "solution_capital": True,
                "search_policy_capital": None,
                "policy_assay_status": "CANNOT_IDENTIFY_STORED_SOLUTION_CONTAMINATION",
                "proposal_law_changed": True,
            }
        return {
            "solution_capital": True,
            "search_policy_capital": False,
            "policy_assay_status": "SOLUTION_ONLY_UNCHANGED_POLICY",
            "proposal_law_changed": False,
        }
    comparison = history_discovery_comparison(
        baseline,
        history,
        useful_set,
        stored_set,
        per_proposal_burden,
        history_overhead,
        prices,
    )
    policy_capital = comparison["proposal_law_changed"] and comparison["verdict"] == "HISTORY_STRICTLY_IMPROVES"
    return {
        "solution_capital": False,
        "search_policy_capital": policy_capital,
        "policy_assay_status": comparison["verdict"],
        "proposal_law_changed": comparison["proposal_law_changed"],
    }


def exhaustive_census() -> dict[str, int]:
    potential_cases = 0
    for scores in product(range(3), repeat=3):
        for costs in product(range(1, 3), repeat=3):
            edges = (("s0", "s1", (costs[0],)), ("s1", "s2", (costs[1],)), ("s0", "s2", (costs[2],)))
            previous = None
            for budget in range(7):
                result = developmental_potential(("s0", "s1", "s2"), "s0", dict(zip(("s0", "s1", "s2"), scores)), edges, (budget,))
                if previous is not None and result["developmental_potential"] < previous:
                    raise ValueError("developmental potential decreased under budget expansion")
                if result["current_capability"] != scores[0] or result["headroom"] != result["developmental_potential"] - scores[0]:
                    raise ValueError("current/potential/headroom identity failed")
                previous = result["developmental_potential"]
                potential_cases += 1

    useful_mass_cases = 0
    carrier = ("a", "b", "c")
    for counts in product(range(5), repeat=3):
        if sum(counts) != 4:
            continue
        kernel = {item: Fraction(count, 4) for item, count in zip(carrier, counts, strict=True)}
        for mask in range(1, 8):
            useful = {item for index, item in enumerate(carrier) if mask & (1 << index)}
            mass = useful_descendant_mass(kernel, useful)
            hit = iid_first_hit(mass)
            if (mass == 0) != (hit["status"] == ZERO_MASS):
                raise ValueError("zero-mass first-hit typing failed")
            if mass > 0 and hit["expected_proposals"] != 1 / mass:
                raise ValueError("iid first-hit expectation failed")
            useful_mass_cases += 1

    history_cases = 0
    for base_count, history_count, proposal_cost, overhead in product(range(5), range(5), range(1, 4), range(4)):
        baseline = {"hit": Fraction(base_count, 4), "miss": Fraction(4 - base_count, 4)}
        history = {"hit": Fraction(history_count, 4), "miss": Fraction(4 - history_count, 4)}
        result = history_discovery_comparison(baseline, history, {"hit"}, set(), (proposal_cost,), (overhead,), (1,))
        if base_count > 0 and history_count > 0 and result["positive_mass_iff_holds"] is not True:
            raise ValueError("positive-mass history improvement iff failed")
        history_cases += 1

    capital_cases = 0
    for target_index in range(3):
        useful = {carrier[target_index]}
        for stored_mask in range(8):
            stored = {item for index, item in enumerate(carrier) if stored_mask & (1 << index)}
            result = classify_capital(
                useful,
                stored,
                {"a": Fraction(1, 3), "b": Fraction(1, 3), "c": Fraction(1, 3)},
                {"a": Fraction(1, 2), "b": Fraction(1, 4), "c": Fraction(1, 4)},
                (1,),
                (0,),
                (1,),
            )
            if bool(useful & stored) != result["solution_capital"]:
                raise ValueError("solution-capital classification failed")
            if result["solution_capital"] and result["search_policy_capital"]:
                raise ValueError("contaminated direct reuse was called policy capital")
            capital_cases += 1
    return {
        "budgeted_potential_cases": potential_cases,
        "useful_mass_first_hit_cases": useful_mass_cases,
        "history_discovery_cases": history_cases,
        "capital_separation_cases": capital_cases,
    }


def validate_ledgers() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {"id", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = data["claims"]
    if len(claims) != 5 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if any(not row["assumptions"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN":
        raise ValueError("independent-review gap must remain open")
    return {"claim_ledgers": 5, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"}


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_DEVELOPMENTAL_POTENTIAL_V1.json").read_text())
    expected_rows = {
        "- [ ] Formalize developmental potential separately from current capability.",
        "- [ ] Define evolvability quantitatively.",
        "- [ ] Derive conditions under which history improves future discovery rather than merely storing solutions.",
        "- [ ] Distinguish solution capital from search-policy improvement.",
    }
    replacements = reconciliation.get("replacements", [])
    manifest_ok = (
        manifest.get("issue") == 908
        and manifest.get("source_pr") == 909
        and manifest.get("parent_issue") == 833
        and manifest.get("freeze_commit") == "f7e3e07edd07a0edafbcb62d50f038cea6e11667"
        and manifest.get("frozen_main") == "9f90fc4ef961b7e9adccf7438488d1a64b9e68be"
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 4
        and manifest.get("total_exhaustive_cases") == 1941
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == 833
        and reconciliation.get("source_issue") == 908
        and reconciliation.get("source_pr") == 909
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and len(replacements) == 4
        and {row.get("old") for row in replacements} == expected_rows
        and all(row.get("anchor") == "# L. Development, morphogenesis, and evolvability" for row in replacements)
        and all(row.get("new", "").startswith("- [x]") and "PR #909 / #908" in row.get("new", "") for row in replacements)
    )
    return {
        "manifest_ok": manifest_ok,
        "reconciliation_ok": reconciliation_ok,
        "reconciliation_rows": len(replacements),
        "source_pr": reconciliation.get("source_pr"),
    }


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    graph = developmental_potential(
        ("now", "mid", "future"),
        "now",
        {"now": 1, "mid": 2, "future": 5},
        (("now", "mid", (1, 0)), ("mid", "future", (1, 1))),
        (2, 1),
    )
    low_budget = developmental_potential(
        ("now", "mid", "future"),
        "now",
        {"now": 1, "mid": 2, "future": 5},
        (("now", "mid", (1, 0)), ("mid", "future", (1, 1))),
        (1, 0),
    )
    high_now_low_headroom = developmental_potential(("x",), "x", {"x": 5}, (), (0,))
    low_now_high_headroom = graph
    kernel = {"u": Fraction(1, 4), "n": Fraction(3, 4)}
    mass, hit = useful_descendant_mass(kernel, {"u"}), iid_first_hit(Fraction(1, 4))
    zero_hit = iid_first_hit(0)
    beneficial = history_discovery_comparison(
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        {"u": Fraction(1, 2), "n": Fraction(1, 2)},
        {"u"}, set(), (2,), (1,), (1,),
    )
    tie = history_discovery_comparison(
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        {"u": Fraction(1, 2), "n": Fraction(1, 2)},
        {"u"}, set(), (2,), (4,), (1,),
    )
    harmful = history_discovery_comparison(
        {"u": Fraction(1, 2), "n": Fraction(1, 2)},
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        {"u"}, set(), (2,), (0,), (1,),
    )
    solution_only = classify_capital(
        {"u"}, {"u"},
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        (1,), (0,), (1,),
    )
    policy_only = classify_capital(
        {"u"}, set(),
        {"u": Fraction(1, 4), "n": Fraction(3, 4)},
        {"u": Fraction(1, 2), "n": Fraction(1, 2)},
        (2,), (1,), (1,),
    )
    census = exhaustive_census()
    ledgers = validate_ledgers()
    package_contracts = validate_package_contracts()
    expected_census = {
        "budgeted_potential_cases": 1512,
        "useful_mass_first_hit_cases": 105,
        "history_discovery_cases": 300,
        "capital_separation_cases": 24,
    }
    checks = {
        "parents_exactly_pinned": bool(parent_audit["all_ok"]),
        "current_and_potential_are_distinct": graph["current_capability"] == 1 and graph["developmental_potential"] == 5 and graph["headroom"] == 4,
        "budget_expansion_nondecreasing": low_budget["developmental_potential"] <= graph["developmental_potential"],
        "current_capability_does_not_identify_headroom": high_now_low_headroom["headroom"] == 0 and low_now_high_headroom["headroom"] == 4,
        "useful_mass_and_first_hit_exact": mass == Fraction(1, 4) and hit["expected_proposals"] == 4,
        "zero_mass_is_typed_unreachable": zero_hit == {"status": ZERO_MASS, "expected_proposals": None},
        "history_improvement_iff_with_overhead": beneficial["verdict"] == "HISTORY_STRICTLY_IMPROVES" and beneficial["positive_mass_iff_holds"] is True,
        "history_tie_and_harm_preserved": tie["verdict"] == "TIE" and harmful["verdict"] == "HISTORY_HARMS",
        "solution_only_is_not_policy_capital": solution_only["solution_capital"] and not solution_only["search_policy_capital"],
        "policy_only_is_not_solution_reuse": policy_only["search_policy_capital"] and not policy_only["solution_capital"],
        "bounded_censuses_complete": census == expected_census,
        "scientific_ledgers_complete": ledgers == {"claim_ledgers": 5, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        "manifest_and_reconciliation_exact": package_contracts == {
            "manifest_ok": True,
            "reconciliation_ok": True,
            "reconciliation_rows": 4,
            "source_pr": 909,
        },
    }
    return {
        "schema": "GMI833DevelopmentalPotentialEvolvabilityResultV1",
        "issue": 908,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "developmental_potential": graph,
            "low_budget": low_budget,
            "high_now_low_headroom": high_now_low_headroom,
            "useful_mass": mass,
            "first_hit": hit,
            "zero_mass_first_hit": zero_hit,
            "history_beneficial": beneficial,
            "history_tie": tie,
            "history_harmful": harmful,
            "solution_only": solution_only,
            "policy_only": policy_only,
        },
        "scientific_ledger": ledgers,
        "package_contracts": package_contracts,
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
