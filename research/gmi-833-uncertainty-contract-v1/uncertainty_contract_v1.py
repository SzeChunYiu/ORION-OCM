#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import hashlib
import json

CLAIM_CEILING = "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "UNIVERSAL_UNCERTAINTY_CALIBRATION",
    "INDEPENDENCE_PROVED",
    "ALL_REAL_WORLD_CONFIDENCE_VALID",
    "UNIVERSAL_POSTERIOR_CORRECTNESS",
    "REAL_SCALE_UNCERTAINTY_VALIDATION",
    "COMPLETE_GMI",
]

PARENT_PINS = (
    {
        "path": "research/gmi-dependency-aware-uncertainty-composition-v1/RESULT_V1.json",
        "blob": "d5253d8b77f45a3dfc9f96ddf66eef427acb1bf9",
        "claim_ceiling": "DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE",
        "semantic_key": ("shared_ancestor_hostile", "strict", True),
    },
    {
        "path": "research/gmi-developmental-uncertainty-transport-v1/RESULT_V1.json",
        "blob": "49df3257c9181c64bae63b53c503e302ca887fe8",
        "claim_ceiling": "SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE",
        "semantic_key": ("target_evidence_noninheritance", None, True),
    },
    {
        "path": "research/gmi-epistemic-aleatoric-separation-v1/RESULT_V1.json",
        "blob": "e422a880c7e1f49cd80260cc679c31e056a4046d",
        "claim_ceiling": "EXACT_EPISTEMIC_ALEATORIC_SEPARATION_FOR_REGISTERED_FINITE_LATENT_MODELS",
        "semantic_key": ("no_latent_semantics", None, "CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS"),
    },
    {
        "path": "research/gmi-capability-calibration-v2/RESULT_V2.json",
        "blob": "278845962ef2a573d3664fc3a400591e440ed313",
        "claim_ceiling": "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME",
        "semantic_key": ("abstention_accounting_control", "abstentions_counted_as_correct", False),
    },
)


def _frozen(values):
    return frozenset(values)


def _validate_domain(domain, candidates):
    if not domain:
        raise ValueError("registered domain must be nonempty")
    if not candidates.issubset(domain):
        raise ValueError("candidate set must be a subset of its registered domain")


@dataclass(frozen=True)
class FeasibleSet:
    domain: frozenset
    candidates: frozenset
    version: int
    provenance: str

    def __post_init__(self):
        domain = _frozen(self.domain)
        candidates = _frozen(self.candidates)
        _validate_domain(domain, candidates)
        if self.version < 0 or not self.provenance:
            raise ValueError("version/provenance must be registered")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "candidates", candidates)


@dataclass(frozen=True)
class ConfidenceSet:
    domain: frozenset
    candidates: frozenset
    alpha: Fraction
    target: str
    version: int
    provenance: str
    raw_evidence_count: int = 0

    def __post_init__(self):
        domain = _frozen(self.domain)
        candidates = _frozen(self.candidates)
        _validate_domain(domain, candidates)
        alpha = Fraction(self.alpha)
        if alpha < 0 or alpha > 1:
            raise ValueError("failure budget alpha must lie in [0,1]")
        if self.version < 0 or self.raw_evidence_count < 0:
            raise ValueError("version/evidence count must be nonnegative")
        if not self.target or not self.provenance:
            raise ValueError("confidence target/provenance must be registered")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(self, "alpha", alpha)

    @property
    def coverage_lower_bound(self):
        return 1 - self.alpha


@dataclass(frozen=True)
class PredictiveLaw:
    probabilities: tuple
    version: int
    provenance: str

    def __post_init__(self):
        probs = tuple((y, Fraction(p)) for y, p in self.probabilities)
        if not probs or any(p < 0 for _, p in probs) or sum((p for _, p in probs), Fraction(0)) != 1:
            raise ValueError("predictive law must be a normalized finite probability law")
        if len({y for y, _ in probs}) != len(probs):
            raise ValueError("predictive-law outcomes must be unique")
        if self.version < 0 or not self.provenance:
            raise ValueError("version/provenance must be registered")
        object.__setattr__(self, "probabilities", tuple(sorted(probs, key=lambda row: repr(row[0]))))


@dataclass(frozen=True)
class LatentPredictiveModel:
    weights: tuple
    kernels: tuple
    version: int
    provenance: str

    def __post_init__(self):
        weights = tuple((theta, Fraction(p)) for theta, p in self.weights)
        if not weights or any(p < 0 for _, p in weights) or sum((p for _, p in weights), Fraction(0)) != 1:
            raise ValueError("latent weights must form a normalized finite probability law")
        weight_ids = tuple(theta for theta, _ in weights)
        if len(weight_ids) != len(set(weight_ids)):
            raise ValueError("latent identifiers in weights must be unique")
        kernel_rows = tuple(self.kernels)
        kernel_ids = tuple(theta for theta, _ in kernel_rows)
        if len(kernel_ids) != len(set(kernel_ids)):
            raise ValueError("latent kernel identifiers must be unique")
        kernel_map = {}
        for theta, law in kernel_rows:
            converted = tuple((y, Fraction(p)) for y, p in law)
            if len({y for y, _ in converted}) != len(converted):
                raise ValueError("latent-kernel outcomes must be unique")
            if not converted or any(p < 0 for _, p in converted) or sum((p for _, p in converted), Fraction(0)) != 1:
                raise ValueError("every latent kernel must be normalized")
            kernel_map[theta] = converted
        if set(kernel_map) != set(weight_ids):
            raise ValueError("every registered latent state needs exactly one kernel")
        if self.version < 0 or not self.provenance:
            raise ValueError("version/provenance must be registered")
        object.__setattr__(self, "weights", tuple(sorted(weights, key=lambda row: repr(row[0]))))
        object.__setattr__(
            self,
            "kernels",
            tuple(sorted(((theta, tuple(sorted(law, key=lambda row: repr(row[0])))) for theta, law in kernel_map.items()), key=lambda row: repr(row[0]))),
        )


@dataclass(frozen=True)
class SelectivePrediction:
    value_set: frozenset
    upper_error: Fraction
    determinate_coverage: Fraction
    scope: str
    provenance: str
    abstentions_counted_as_correct: bool = False

    def __post_init__(self):
        upper = Fraction(self.upper_error)
        coverage = Fraction(self.determinate_coverage)
        if upper < 0 or upper > 1 or coverage < 0 or coverage > 1:
            raise ValueError("risk/coverage coordinates must lie in [0,1]")
        if self.abstentions_counted_as_correct:
            raise ValueError("abstentions may not be counted as correct predictions")
        if not self.scope or not self.provenance:
            raise ValueError("selective prediction needs scope/provenance")
        object.__setattr__(self, "value_set", _frozen(self.value_set))
        object.__setattr__(self, "upper_error", upper)
        object.__setattr__(self, "determinate_coverage", coverage)


@dataclass(frozen=True)
class QueryResult:
    terminal: str
    values: tuple = ()
    reason: str | None = None


@dataclass(frozen=True)
class TransportResult:
    terminal: str
    confidence: ConfidenceSet | None
    reason: str | None = None


def is_unknown(obj):
    return isinstance(obj, (FeasibleSet, ConfidenceSet)) and obj.candidates == obj.domain


def identified_set(obj, query):
    if obj is None:
        return QueryResult("CANNOT_CHECK", reason="UNCERTAINTY_OBJECT_MISSING")
    if query is None:
        return QueryResult("CANNOT_CHECK", reason="QUERY_NOT_REGISTERED")
    if not isinstance(obj, (FeasibleSet, ConfidenceSet)):
        return QueryResult("CANNOT_CHECK", reason="QUERY_REQUIRES_SET_VALUED_OBJECT")
    if not obj.candidates:
        return QueryResult("INCONSISTENT_REGISTERED_ASSUMPTIONS")
    values = tuple(sorted({query(x) for x in obj.candidates}, key=repr))
    if len(values) == 1:
        return QueryResult("IDENTIFIED", values=values)
    return QueryResult("CANNOT_IDENTIFY", values=values)


def relation_image(candidates, relation):
    c = set(candidates)
    return frozenset(y for x, y in relation if x in c)


def complete_relation(source_domain, target_domain):
    return frozenset((x, y) for x in source_domain for y in target_domain)


def transport_confidence(source, target_domain, relation, beta, target_version, provenance):
    if not isinstance(source, ConfidenceSet):
        return TransportResult("CANNOT_CHECK", None, "SOURCE_CONFIDENCE_OBJECT_REQUIRED")
    if target_domain is None:
        return TransportResult("CANNOT_CHECK", None, "TARGET_DOMAIN_NOT_REGISTERED")
    target_domain = _frozen(target_domain)
    if not target_domain:
        return TransportResult("CANNOT_CHECK", None, "TARGET_DOMAIN_EMPTY_OR_UNREGISTERED")
    beta = Fraction(beta)
    if beta < 0 or beta > 1:
        raise ValueError("relation failure budget beta must lie in [0,1]")
    missing = relation is None
    if missing:
        relation = complete_relation(source.domain, target_domain)
    else:
        relation = frozenset(relation)
        if any(x not in source.domain or y not in target_domain for x, y in relation):
            raise ValueError("registered relation leaves declared source/target domain")
    candidates = relation_image(source.candidates, relation)
    raw_alpha = min(Fraction(1), source.alpha + beta)
    inconsistent = not candidates
    alpha = Fraction(1) if inconsistent else raw_alpha
    confidence = ConfidenceSet(
        domain=target_domain,
        candidates=candidates,
        alpha=alpha,
        target=source.target,
        version=target_version,
        provenance=provenance,
        raw_evidence_count=0,
    )
    if inconsistent:
        return TransportResult("INCONSISTENT_REGISTERED_ASSUMPTIONS", confidence)
    terminal = "TRANSPORTED_UNKNOWN_RELATION" if missing else "TRANSPORTED"
    return TransportResult(terminal, confidence)


def chain_transport(source, stages):
    current = source
    terminals = []
    for stage in stages:
        result = transport_confidence(current, **stage)
        terminals.append(result.terminal)
        if result.confidence is None or result.terminal == "INCONSISTENT_REGISTERED_ASSUMPTIONS":
            return result, tuple(terminals)
        current = result.confidence
    return TransportResult("TRANSPORTED_CHAIN", current), tuple(terminals)


def dependence_hostile():
    marginal_good = Fraction(3, 4)
    true_joint = Fraction(1, 2)
    union_lower = 1 - (Fraction(1, 4) + Fraction(1, 4))
    independence_product = marginal_good * marginal_good
    return {
        "marginal_good_each": marginal_good,
        "true_joint_good": true_joint,
        "union_lower": union_lower,
        "independence_product": independence_product,
        "product_unsound": independence_product > true_joint,
        "union_attained": union_lower == true_joint,
    }


def shared_ancestor_hostile():
    xs = (-1, 1)
    global_assignments = tuple((x, x, x, x - x) for x in xs)
    global_y = frozenset(row[3] for row in global_assignments)
    local_a = frozenset(xs)
    local_b = frozenset(xs)
    local_y = frozenset(a - b for a in local_a for b in local_b)
    return {"global_y": global_y, "local_y": local_y, "strict": global_y < local_y}


def marginal_from_latent(model):
    if not isinstance(model, LatentPredictiveModel):
        raise TypeError("latent model required")
    weights = dict(model.weights)
    kernels = {theta: dict(law) for theta, law in model.kernels}
    outcomes = sorted({y for law in kernels.values() for y in law}, key=repr)
    return tuple(
        (y, sum((weights[theta] * kernels[theta].get(y, Fraction(0)) for theta in weights), Fraction(0)))
        for y in outcomes
    )


def decompose_latent(model):
    if isinstance(model, PredictiveLaw):
        return {"terminal": "CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS"}
    if not isinstance(model, LatentPredictiveModel):
        return {"terminal": "CANNOT_CHECK", "reason": "LATENT_MODEL_NOT_REGISTERED"}
    weights = dict(model.weights)
    kernels = {theta: dict(law) for theta, law in model.kernels}
    means = {}
    variances = {}
    for theta, law in kernels.items():
        mean = sum((Fraction(y) * p for y, p in law.items()), Fraction(0))
        variance = sum((p * (Fraction(y) - mean) ** 2 for y, p in law.items()), Fraction(0))
        means[theta] = mean
        variances[theta] = variance
    mean = sum((weights[theta] * means[theta] for theta in weights), Fraction(0))
    aleatoric = sum((weights[theta] * variances[theta] for theta in weights), Fraction(0))
    epistemic_mean = sum((weights[theta] * (means[theta] - mean) ** 2 for theta in weights), Fraction(0))
    total = aleatoric + epistemic_mean
    return {
        "terminal": "DECOMPOSED_WITH_REGISTERED_LATENT_SEMANTICS",
        "mean": mean,
        "aleatoric": aleatoric,
        "epistemic_mean": epistemic_mean,
        "total": total,
        "marginal": marginal_from_latent(model),
    }


def epistemic_aleatoric_hostile():
    pure_aleatoric = LatentPredictiveModel(
        weights=(("single", 1),),
        kernels=(("single", ((-1, Fraction(1, 2)), (1, Fraction(1, 2)))),),
        version=0,
        provenance="PURE_ALEATORIC",
    )
    pure_epistemic = LatentPredictiveModel(
        weights=(("left", Fraction(1, 2)), ("right", Fraction(1, 2))),
        kernels=(("left", ((-1, 1),)), ("right", ((1, 1),))),
        version=0,
        provenance="PURE_EPISTEMIC_MEAN",
    )
    a = decompose_latent(pure_aleatoric)
    e = decompose_latent(pure_epistemic)
    predictive = PredictiveLaw(probabilities=a["marginal"], version=0, provenance="MARGINAL_ONLY")
    rejected = decompose_latent(predictive)
    return {
        "same_marginal": a["marginal"] == e["marginal"],
        "different_decomposition": (a["aleatoric"], a["epistemic_mean"]) != (e["aleatoric"], e["epistemic_mean"]),
        "pure_aleatoric": (a["aleatoric"], a["epistemic_mean"], a["total"]),
        "pure_epistemic": (e["aleatoric"], e["epistemic_mean"], e["total"]),
        "marginal_only_terminal": rejected["terminal"],
    }


def _git_blob_sha(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def audit_parent_files(repo_root):
    root = Path(repo_root)
    rows = []
    for pin in PARENT_PINS:
        path = root / pin["path"]
        data = path.read_bytes()
        parsed = json.loads(data)
        actual_blob = _git_blob_sha(data)
        outer, inner, expected = pin["semantic_key"]
        actual_semantic = parsed.get(outer) if inner is None else parsed.get(outer, {}).get(inner)
        row = {
            "path": pin["path"],
            "expected_blob": pin["blob"],
            "actual_blob": actual_blob,
            "blob_ok": actual_blob == pin["blob"],
            "claim_ceiling_ok": parsed.get("claim_ceiling") == pin["claim_ceiling"],
            "semantic_ok": actual_semantic == expected,
        }
        rows.append(row)
    return {
        "rows": rows,
        "all_ok": all(row["blob_ok"] and row["claim_ceiling_ok"] and row["semantic_ok"] for row in rows),
    }


def source_chain_witness():
    source = ConfidenceSet(
        domain={0, 1},
        candidates={0, 1},
        alpha=Fraction(1, 20),
        target="theta",
        version=0,
        provenance="SOURCE",
        raw_evidence_count=2048,
    )
    stages = (
        {
            "target_domain": {"a", "b"},
            "relation": {(0, "a"), (1, "b")},
            "beta": Fraction(1, 100),
            "target_version": 1,
            "provenance": "R1",
        },
        {
            "target_domain": {10, 20},
            "relation": {("a", 10), ("b", 20)},
            "beta": Fraction(1, 200),
            "target_version": 2,
            "provenance": "R2",
        },
    )
    result, terminals = chain_transport(source, stages)
    return source, result, terminals


def missing_empty_query_witness():
    source = ConfidenceSet(
        domain={0, 1},
        candidates={0, 1},
        alpha=Fraction(1, 20),
        target="theta",
        version=0,
        provenance="SOURCE",
        raw_evidence_count=10,
    )
    missing = transport_confidence(source, {0, 1, 2}, None, 0, 1, "MISSING_RELATION")
    empty = transport_confidence(source, {0, 1, 2}, frozenset(), 0, 1, "EMPTY_RELATION")
    no_domain = transport_confidence(source, None, None, 0, 1, "NO_DOMAIN")
    return {
        "missing_terminal": missing.terminal,
        "missing_unknown": is_unknown(missing.confidence),
        "missing_candidates": missing.confidence.candidates,
        "identity_query": identified_set(missing.confidence, lambda x: x),
        "constant_query": identified_set(missing.confidence, lambda x: "same"),
        "empty_relation_transport_terminal": empty.terminal,
        "empty_relation_coverage_lower": empty.confidence.coverage_lower_bound,
        "empty_relation_query": identified_set(empty.confidence, lambda x: x),
        "no_domain_terminal": no_domain.terminal,
        "no_domain_reason": no_domain.reason,
        "no_query": identified_set(missing.confidence, None),
    }


def jsonable(obj):
    if isinstance(obj, Fraction):
        return f"{obj.numerator}/{obj.denominator}"
    if isinstance(obj, QueryResult):
        return {"terminal": obj.terminal, "values": jsonable(obj.values), "reason": obj.reason}
    if isinstance(obj, TransportResult):
        return {"terminal": obj.terminal, "reason": obj.reason}
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return [jsonable(v) for v in sorted(obj, key=repr)]
    return obj


def build_receipt(parent_audit):
    source, chain, chain_terminals = source_chain_witness()
    final = chain.confidence
    dep = dependence_hostile()
    shared = shared_ancestor_hostile()
    q = missing_empty_query_witness()
    kind = epistemic_aleatoric_hostile()
    selective = SelectivePrediction(
        value_set={"memory_exact"},
        upper_error=Fraction(3, 64),
        determinate_coverage=Fraction(1, 16),
        scope="REGISTERED_DETERMINATE_FRAME",
        provenance="PARENT_766",
        abstentions_counted_as_correct=False,
    )
    checks = {
        "parent_evidence_exactly_pinned": parent_audit["all_ok"],
        "chain_failure_budget_exact": final.alpha == Fraction(13, 200),
        "chain_coverage_lower_exact": final.coverage_lower_bound == Fraction(187, 200),
        "developmental_raw_evidence_not_inherited": source.raw_evidence_count == 2048 and final.raw_evidence_count == 0,
        "developmental_version_advanced": source.version == 0 and final.version == 2,
        "no_independence_product": dep["product_unsound"] and dep["union_attained"],
        "shared_ancestor_dependency_loss_exercised": shared["strict"] and shared["global_y"] == frozenset({0}) and shared["local_y"] == frozenset({-2, 0, 2}),
        "missing_relation_becomes_unknown": q["missing_terminal"] == "TRANSPORTED_UNKNOWN_RELATION" and q["missing_unknown"],
        "unknown_nonconstant_query_abstains": q["identity_query"].terminal == "CANNOT_IDENTIFY",
        "unknown_constant_query_identified": q["constant_query"].terminal == "IDENTIFIED" and q["constant_query"].values == ("same",),
        "empty_relation_transport_is_inconsistent": q["empty_relation_transport_terminal"] == "INCONSISTENT_REGISTERED_ASSUMPTIONS",
        "empty_relation_zero_guaranteed_coverage": q["empty_relation_coverage_lower"] == 0,
        "empty_relation_query_is_inconsistent": q["empty_relation_query"].terminal == "INCONSISTENT_REGISTERED_ASSUMPTIONS",
        "missing_domain_is_cannot_check": q["no_domain_terminal"] == "CANNOT_CHECK",
        "missing_query_is_cannot_check": q["no_query"].terminal == "CANNOT_CHECK",
        "same_marginal_different_decomposition": kind["same_marginal"] and kind["different_decomposition"],
        "marginal_only_decomposition_rejected": kind["marginal_only_terminal"] == "CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS",
        "selective_abstentions_not_success": not selective.abstentions_counted_as_correct,
    }
    return jsonable({
        "schema": "GMI_833_GLOBAL_UNCERTAINTY_CONTRACT_RESULT_V1",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "checks": checks,
        "chain": {
            "source_failure_budget": source.alpha,
            "stage_terminals": chain_terminals,
            "final_failure_budget": final.alpha,
            "final_coverage_lower": final.coverage_lower_bound,
            "final_candidates": final.candidates,
            "source_raw_evidence_count": source.raw_evidence_count,
            "target_raw_evidence_count": final.raw_evidence_count,
            "target_version": final.version,
        },
        "dependence_hostile": dep,
        "shared_ancestor_hostile": shared,
        "query_semantics": q,
        "uncertainty_kind_hostile": kind,
        "selective_prediction": {
            "value_set": selective.value_set,
            "upper_error": selective.upper_error,
            "determinate_coverage": selective.determinate_coverage,
            "abstentions_counted_as_correct": selective.abstentions_counted_as_correct,
        },
    })


def canonical_json(receipt):
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def repo_root():
    return Path(__file__).resolve().parents[2]


def main():
    audit = audit_parent_files(repo_root())
    receipt = build_receipt(audit)
    print(canonical_json(receipt), end="")
    return 0 if receipt["verdict"] == "GREEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
