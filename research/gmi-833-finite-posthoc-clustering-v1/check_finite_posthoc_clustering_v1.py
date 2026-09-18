#!/usr/bin/env python3
"""Exact replay and artifact builder for the finite clustering quartet."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
SOURCE_MAIN = "5aaebc5a7bab7825f30c007d9fd5cd4e34f5118e"
FREEZE_COMMIT = "9ae830c41eb773445b630af8303afa51ce59a083"
SOURCE_ISSUE = 998
SOURCE_PR = 999
PARENT_ISSUE = 833
CLAIM_CEILING = "FINITE_POSTHOC_CLUSTERING_BLIND_REFERENCE_MAPPING_UNKNOWN_AND_STABILITY_AT_REGISTERED_966_984_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "LARGE_SCALE_CLUSTERING_VALIDITY",
    "UNIVERSAL_NATURAL_UNIQUE_OR_UNBIASED_TAXONOMY",
    "KNOWN_FAMILY_RECOVERY_BEYOND_FOUR_SUPPLIED_FINGERPRINTS",
    "LITERAL_HISTORICAL_IGNORANCE",
    "ARCHITECTURE_PRIOR_FREE_DISCOVERY",
    "CLUSTER_TRUTH_OR_UNIQUENESS",
    "ARBITRARY_THRESHOLD_METRIC_OR_GRAMMAR_ROBUSTNESS",
    "MORPHOLOGY_ZOO_COMPLETION",
    "NEURAL_FAMILY_CLOSURE",
    "NEW_FORM_OF_INTELLIGENCE",
    "COMPLETE_GMI",
    "ONTOLOGICAL_COMPLETENESS",
)
PARENT_PINS = (
    (
        "finite_candidate_space",
        "research/gmi-833-finite-candidate-space-v1/RESULT_V1.json",
        "4086d6bea440d626e48d92eb35d39267a010589e",
        "claim_ceiling",
        "GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE",
    ),
    (
        "finite_morphology_metrics",
        "research/gmi-833-finite-morphology-metrics-v1/RESULT_V1.json",
        "b5bafc0ac9460de87723a27fe1a307ae7d06751b",
        "claim_ceiling",
        "GMI_833_FINITE_COLLAPSE_AND_SEMANTIC_RESOURCE_DEVELOPMENTAL_METRICS_AT_REGISTERED_SCOPE",
    ),
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C = _load("gmi833_f3_cluster_core", HERE / "finite_posthoc_clustering_v1.py")
P = _load("gmi833_f3_posthoc_mapper", HERE / "posthoc_mapper_v1.py")
O = _load("gmi833_f3_component_oracle", HERE / "independent_component_oracle_v1.py")
M = C.M
F = C.F


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def repo_root() -> Path:
    current = HERE
    while current.parent != current:
        if (current / "research").is_dir() and (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("repository root not found")


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents() -> dict[str, object]:
    root = repo_root()
    rows = []
    for name, relative, expected_blob, field, expected_claim in PARENT_PINS:
        path = root / relative
        data = path.read_bytes() if path.is_file() else b""
        actual = git_blob_sha(data) if data else None
        try:
            claim_ok = json.loads(data).get(field) == expected_claim
        except (json.JSONDecodeError, UnicodeDecodeError):
            claim_ok = False
        rows.append(
            {
                "name": name,
                "path": relative,
                "actual_blob": actual,
                "blob_ok": actual == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def freeze_custody() -> dict[str, object]:
    root = repo_root()
    rows = []
    for name in ("FREEZE_V1.md", "PROTOCOL_V1.json"):
        current = (HERE / name).read_bytes()
        frozen = subprocess.run(
            ["git", "show", f"{FREEZE_COMMIT}:research/gmi-833-finite-posthoc-clustering-v1/{name}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        rows.append({"path": name, "unchanged_since_freeze": current == frozen})
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"], cwd=root, check=False
    ).returncode == 0
    return {"freeze_commit_is_ancestor": ancestor, "rows": rows, "all_ok": ancestor and all(row["unchanged_since_freeze"] for row in rows)}


def component_signature(clusters) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted(tuple(sorted(C.record_digest(row) for row in cluster.members)) for cluster in clusters))


def cluster_lookup(clusters) -> dict[object, object]:
    return {record: cluster for cluster in clusters for record in cluster.members}


def candidate_and_cluster_census() -> tuple[dict[str, object], dict[str, object], tuple[object, ...], tuple[object, ...]]:
    snapshots = C.generate_evaluate_retain()
    records = C.distinct_records(snapshots)
    clusters = C.cluster_records(records)
    record_index = {record: f"M{index:04d}" for index, record in enumerate(records, 1)}
    cluster_by_record = cluster_lookup(clusters)
    labels = {cluster.cluster_id: P.map_fingerprint(cluster.medoid.observations) for cluster in clusters}

    candidate_rows = []
    for snapshot in snapshots:
        cluster = cluster_by_record[snapshot.record]
        candidate_rows.append(
            {
                "candidate_id": snapshot.candidate_id,
                "canonical_code": snapshot.canonical_code,
                "morphology_id": record_index[snapshot.record],
                "morphology_digest": C.record_digest(snapshot.record),
                "cluster_id": cluster.cluster_id,
                "posthoc_label": labels[cluster.cluster_id],
            }
        )
    ledger = {
        "schema": "GMI_833_FINITE_POSTHOC_CLUSTERING_CANDIDATE_MEMBERSHIP_V1",
        "issue": SOURCE_ISSUE,
        "source_pr": SOURCE_PR,
        "parent_issue": PARENT_ISSUE,
        "generation_evaluation_completed_before_clustering": True,
        "presentation_count": len(candidate_rows),
        "distinct_morphology_count": len(records),
        "cluster_count": len(clusters),
        "rows": candidate_rows,
    }
    if len({row["candidate_id"] for row in candidate_rows}) != len(snapshots):
        raise AssertionError("candidate ledger duplicated an identifier")
    if len({json.dumps(row["canonical_code"]) for row in candidate_rows}) != len(snapshots):
        raise AssertionError("candidate ledger did not retain every presentation")

    cluster_rows = []
    for cluster in clusters:
        presentation_count = sum(snapshot.record in cluster.members for snapshot in snapshots)
        cluster_rows.append(
            {
                "cluster_id": cluster.cluster_id,
                "morphology_count": len(cluster.members),
                "presentation_count": presentation_count,
                "medoid_digest": C.record_digest(cluster.medoid),
                "medoid_component_totals": list(cluster.medoid_component_totals),
                "posthoc_label": labels[cluster.cluster_id],
            }
        )
    census = {
        "generation_then_evaluation_then_clustering": True,
        "all_presentations_retained": True,
        "presentation_count": len(snapshots),
        "distinct_morphology_count": len(records),
        "threshold": fraction_text(C.EDGE_THRESHOLD),
        "threshold_edge_count": len(C.threshold_edges(records)),
        "cluster_count": len(clusters),
        "morphology_cluster_size_histogram": {
            str(size): count for size, count in sorted(Counter(len(row.members) for row in clusters).items())
        },
        "presentation_membership_total": sum(row["presentation_count"] for row in cluster_rows),
        "clusters": cluster_rows,
    }
    return census, ledger, snapshots, clusters


def independent_oracle_census(clusters, records) -> dict[str, object]:
    ordered = tuple(sorted(records, key=C.record_key))
    matrix = tuple(
        tuple(M.morphology_distance(left, right) for right in ordered)
        for left in ordered
    )
    oracle = O.threshold_components(matrix, C.EDGE_THRESHOLD)
    oracle_signature = tuple(
        sorted(tuple(sorted(C.record_digest(ordered[index]) for index in component)) for component in oracle)
    )
    primary = component_signature(clusters)
    return {
        "distance_matrix_entries": len(ordered) ** 2,
        "independent_component_count": len(oracle),
        "exact_partition_match": oracle_signature == primary,
    }


def posthoc_census(clusters) -> dict[str, object]:
    source = (HERE / "finite_posthoc_clustering_v1.py").read_text(encoding="utf-8")
    forbidden_core_tokens = (
        "posthoc_mapper_v1",
        "INPUT_GATED_STUTTER",
        "QUIESCENT_TERMINATOR",
        "ZERO_STREAM_LOOP",
        "ZERO_EMITTING_TERMINATOR",
        '"UNKNOWN"',
    )
    if any(token in source for token in forbidden_core_tokens):
        raise ValueError("causal clustering core contains a post-hoc registry token")
    labels = [P.map_fingerprint(cluster.medoid.observations) for cluster in clusters]
    known = sorted(label for label in labels if label != P.UNKNOWN)
    if len(known) != 4 or len(labels) - len(known) != 8:
        raise ValueError("frozen reference/UNKNOWN outcome drifted")

    unmatched = (("HALTED", (9,)), ("HALTED", (9,)), ("HALTED", (9,)))
    if P.map_fingerprint(unmatched, P.load_registry()) != P.UNKNOWN:
        raise ValueError("unmatched fingerprint was forced into a known reference")
    matched = P.load_registry()[0]
    ambiguous_registry = (
        matched,
        {"family": "DUPLICATE_REFERENCE", "observations": matched["observations"]},
    )
    if P.map_fingerprint(matched["observations"], ambiguous_registry) != P.UNKNOWN:
        raise ValueError("ambiguous fingerprint was forced into a known reference")
    return {
        "mapping_loaded_only_after_clusters_complete": True,
        "causal_core_registry_token_hits": 0,
        "supplied_reference_count": len(P.load_registry()),
        "known_mapped_cluster_count": len(known),
        "unknown_cluster_count": labels.count(P.UNKNOWN),
        "known_label_histogram": dict(sorted(Counter(known).items())),
        "unmatched_returns_UNKNOWN": True,
        "ambiguous_returns_UNKNOWN": True,
        "nearest_label_fallback": False,
    }


def remint_census(snapshots, clusters) -> dict[str, object]:
    programs = F.enumerate_candidates(F.StructuralBudget(2, 2))
    baseline_index = C.record_cluster_index(clusters)
    token_bank = ("u0", "u1", "u2", "u3", "u4")
    checks = 0
    for permuted in permutations(token_bank):
        remint = dict(zip(F.SEMANTIC_OPS, permuted))
        for program, snapshot in zip(programs, snapshots):
            decoded = F.decode_reminted(F.remint_program(program, remint), remint)
            record = M.morphology_record(decoded)
            if record != snapshot.record or baseline_index[record] != baseline_index[snapshot.record]:
                raise ValueError("certified remint changed candidate cluster membership")
            checks += 1

    hostile_original = F.CandidateProgram(1, (F.Instruction("INC", 0, 0),))
    honest = dict(zip(F.SEMANTIC_OPS, token_bank))
    dishonest = dict(honest)
    dishonest["INC"], dishonest["READ"] = dishonest["READ"], dishonest["INC"]
    hostile_changed = F.decode_reminted(F.remint_program(hostile_original, honest), dishonest)
    hostile_distance = M.morphology_distance(
        M.morphology_record(hostile_original), M.morphology_record(hostile_changed)
    )
    if hostile_distance <= 0:
        raise ValueError("semantics-changing pseudo-remint was accepted")
    return {
        "certified_surface_remint_count": 120,
        "candidate_membership_equivariance_checks": checks,
        "all_candidate_memberships_invariant": True,
        "semantics_changing_pseudo_remint_detected": True,
        "pseudo_remint_morphology_distance": fraction_text(hostile_distance),
    }


def metric_stability_census(records, base_clusters) -> dict[str, object]:
    changed_clusters = C.cluster_records(records, M.PERTURBED_WEIGHTS)
    base_edges = set(C.threshold_edges(records, M.BASE_WEIGHTS))
    changed_edges = set(C.threshold_edges(records, M.PERTURBED_WEIGHTS))
    pair_count = 0
    minimum_margin = None
    edge_decision_checks = 0
    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            base = M.morphology_distance(records[left], records[right], M.BASE_WEIGHTS)
            changed = M.morphology_distance(records[left], records[right], M.PERTURBED_WEIGHTS)
            margin = abs(base - C.EDGE_THRESHOLD)
            minimum_margin = margin if minimum_margin is None else min(minimum_margin, margin)
            pair_count += 1
            if abs(base - changed) > M.UNIFORM_PERTURBATION_BOUND:
                raise ValueError("pair exceeded parent perturbation bound")
            edge_decision_checks += 1
            if (base <= C.EDGE_THRESHOLD) != (changed <= C.EDGE_THRESHOLD):
                raise ValueError("certified perturbation changed a threshold edge")
    if minimum_margin is None or minimum_margin <= M.UNIFORM_PERTURBATION_BOUND:
        raise ValueError("edge stability lacks a strict parent-bound margin")
    if base_edges != changed_edges or component_signature(base_clusters) != component_signature(changed_clusters):
        raise ValueError("certified metric perturbation changed the partition")

    changed_by_members = {
        tuple(sorted(C.record_digest(row) for row in cluster.members)): cluster
        for cluster in changed_clusters
    }
    medoid_rows = []
    for cluster in base_clusters:
        key = tuple(sorted(C.record_digest(row) for row in cluster.members))
        changed_cluster = changed_by_members[key]
        ranked = []
        for candidate in cluster.members:
            vector = C.component_totals(candidate, cluster.members)
            ranked.append((C.weighted_total(vector, M.BASE_WEIGHTS), vector, C.record_key(candidate), candidate))
        best = min(row[0] for row in ranked)
        minimizers = [row for row in ranked if row[0] == best]
        if len({row[1] for row in minimizers}) != 1:
            raise ValueError("a base medoid tie is not componentwise exact")
        nonminimum = [row[0] for row in ranked if row[0] > best]
        aggregate_bound = 2 * (len(cluster.members) - 1) * M.UNIFORM_PERTURBATION_BOUND
        gap = min(nonminimum) - best if nonminimum else None
        if gap is not None and gap <= aggregate_bound:
            raise ValueError("medoid nonminimum exclusion lacks perturbation margin")
        if cluster.medoid != changed_cluster.medoid:
            raise ValueError("certified metric perturbation changed a deterministic medoid")
        medoid_rows.append(
            {
                "cluster_id": cluster.cluster_id,
                "base_minimizer_count": len(minimizers),
                "base_minimizers_componentwise_tied": True,
                "next_cost_gap": None if gap is None else fraction_text(gap),
                "two_sided_aggregate_bound": fraction_text(aggregate_bound),
                "deterministic_medoid_preserved": True,
            }
        )

    base_labels = [P.map_fingerprint(row.medoid.observations) for row in base_clusters]
    changed_labels = [P.map_fingerprint(row.medoid.observations) for row in changed_clusters]
    if base_labels != changed_labels:
        raise ValueError("certified perturbation changed post-hoc labels")

    hostile_weights = M.MetricWeights(Fraction(6), Fraction(3), Fraction(2))
    hostile_clusters = C.cluster_records(records, hostile_weights)
    hostile_edge_changes = len(base_edges.symmetric_difference(set(C.threshold_edges(records, hostile_weights))))
    if component_signature(hostile_clusters) == component_signature(base_clusters):
        raise ValueError("out-of-bound metric hostile did not change the partition")
    return {
        "distinct_pair_checks": pair_count,
        "edge_decision_checks": edge_decision_checks,
        "parent_pairwise_change_bound": fraction_text(M.UNIFORM_PERTURBATION_BOUND),
        "minimum_base_threshold_margin": fraction_text(minimum_margin),
        "base_edge_count": len(base_edges),
        "perturbed_edge_count": len(changed_edges),
        "edge_set_preserved": True,
        "partition_preserved": True,
        "medoid_rows": medoid_rows,
        "all_deterministic_medoids_preserved": True,
        "all_posthoc_labels_and_UNKNOWN_preserved": True,
        "out_of_bound_hostile_weights": ["6/1", "3/1", "2/1"],
        "out_of_bound_hostile_edge_changes": hostile_edge_changes,
        "out_of_bound_hostile_cluster_count": len(hostile_clusters),
        "out_of_bound_hostile_partition_change_detected": True,
    }


def validate_ledgers_and_contracts() -> dict[str, object]:
    scientific = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
    reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_FINITE_POSTHOC_CLUSTERING_V1.json").read_text(encoding="utf-8"))
    required = {"id", "statement", "scope", "assumptions", "dependencies", "falsifiers", "strongest_parent", "counterexample_methods", "limits"}
    claims = scientific.get("claims", [])
    if len(claims) != 5 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema/count drifted")
    if tuple(row["id"] for row in claims) != ("ORDER-1", "CLUSTER-1", "MAP-1", "UNKNOWN-1", "STABLE-1"):
        raise ValueError("scientific claim IDs drifted")
    if any(not row["scope"] or not row["falsifiers"] or not row["limits"] for row in claims):
        raise ValueError("scientific claim discipline field is empty")
    manifest_ok = (
        manifest.get("schema") == "GMI_833_FINITE_POSTHOC_CLUSTERING_MANIFEST_V1"
        and manifest.get("issue") == SOURCE_ISSUE
        and manifest.get("source_pr") == SOURCE_PR
        and manifest.get("parent_issue") == PARENT_ISSUE
        and manifest.get("source_main") == SOURCE_MAIN
        and manifest.get("freeze_commit") == FREEZE_COMMIT
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and manifest.get("target_rows") == 4
    )
    expected_old = (
        "- [ ] Cluster candidates only after generation/evaluation.",
        "- [ ] Blindly map recovered clusters to known architecture families after the fact.",
        "- [ ] Maintain an `UNKNOWN` cluster class; do not force every candidate into a known taxonomy.",
        "- [ ] Validate clustering stability under grammar remints and metric perturbations.",
    )
    replacements = reconciliation.get("replacements", [])
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == PARENT_ISSUE
        and reconciliation.get("source_issue") == SOURCE_ISSUE
        and reconciliation.get("source_pr") == SOURCE_PR
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
        and tuple(row.get("old") for row in replacements) == expected_old
        and all(row.get("anchor") == "# F. Intelligence-space generator" for row in replacements)
        and all(row.get("new", "").startswith("- [x]") and "PR #999 / #998" in row.get("new", "") for row in replacements)
    )
    return {
        "scientific_claim_count": len(claims),
        "open_gap_count": len(scientific.get("open_gaps", [])),
        "manifest_ok": manifest_ok,
        "reconciliation_ok": reconciliation_ok,
        "reconciliation_rows": len(replacements),
    }


def build_artifacts() -> tuple[dict[str, object], dict[str, object]]:
    clustering, ledger, snapshots, clusters = candidate_and_cluster_census()
    records = C.distinct_records(snapshots)
    parent = audit_parents()
    custody = freeze_custody()
    oracle = independent_oracle_census(clusters, records)
    posthoc = posthoc_census(clusters)
    remint = remint_census(snapshots, clusters)
    stability = metric_stability_census(records, clusters)
    contracts = validate_ledgers_and_contracts()
    checks = {
        "parents_exactly_pinned": parent["all_ok"],
        "freeze_custody_intact": custody["all_ok"],
        "generation_evaluation_precede_clustering": clustering["generation_then_evaluation_then_clustering"],
        "all_presentations_retained": clustering["all_presentations_retained"],
        "independent_component_oracle_exact": oracle["exact_partition_match"],
        "causal_core_taxonomy_blind": posthoc["causal_core_registry_token_hits"] == 0,
        "posthoc_mapping_separated": posthoc["mapping_loaded_only_after_clusters_complete"],
        "UNKNOWN_is_explicit_and_total": posthoc["unmatched_returns_UNKNOWN"] and posthoc["ambiguous_returns_UNKNOWN"],
        "all_certified_remints_equivariant": remint["all_candidate_memberships_invariant"],
        "metric_perturbation_partition_stable": stability["partition_preserved"],
        "metric_perturbation_medoids_stable": stability["all_deterministic_medoids_preserved"],
        "hostiles_detected": remint["semantics_changing_pseudo_remint_detected"] and stability["out_of_bound_hostile_partition_change_detected"],
        "package_contracts_valid": contracts["manifest_ok"] and contracts["reconciliation_ok"],
    }
    if not all(checks.values()):
        raise ValueError(f"one or more exact checks failed: {checks}")
    result = {
        "schema": "GMI_833_FINITE_POSTHOC_CLUSTERING_RESULT_V1",
        "issue": SOURCE_ISSUE,
        "source_pr": SOURCE_PR,
        "parent_issue": PARENT_ISSUE,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "checks": checks,
        "parent_audit": parent,
        "freeze_custody": custody,
        "clustering_census": clustering,
        "independent_oracle": oracle,
        "posthoc_mapping": posthoc,
        "remint_stability": remint,
        "metric_perturbation_stability": stability,
        "package_contracts": contracts,
        "candidate_ledger_sha256": sha256(artifact_text(ledger).encode("utf-8")).hexdigest(),
        "verdict": "GREEN",
    }
    return result, ledger


def artifact_text(value: dict[str, object]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    write = "--write" in sys.argv[1:]
    if any(arg != "--write" for arg in sys.argv[1:]):
        raise SystemExit("usage: check_finite_posthoc_clustering_v1.py [--write]")
    result, ledger = build_artifacts()
    paths = (
        (HERE / "RESULT_V1.json", artifact_text(result)),
        (HERE / "CANDIDATE_MEMBERSHIP_V1.json", artifact_text(ledger)),
    )
    if write:
        for path, text in paths:
            path.write_text(text, encoding="utf-8")
    else:
        for path, expected in paths:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                raise ValueError(f"artifact drift: {path.name}")
    print(artifact_text(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
