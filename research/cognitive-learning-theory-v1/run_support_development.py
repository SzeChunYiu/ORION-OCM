"""E2 actual-source support-retention study. Refuses an unfrozen registration.

Each arm runs in its own process. Source donor code remains unchanged. This
driver is not an M11 generation change and cannot execute protected ecology.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from dataclasses import asdict

from support_effects import Cost, SupportLearner, canonical, monotone_tables, sha

HERE = Path(__file__).resolve().parent
DONORS = HERE.parent / "self-evolution-v1" / "donor_runtime"
ARMS = ("active_monotone", "antichain_parent", "eager_table", "lazy_cache", "loo_ablation")


def rule_record(rule):
    return None if rule is None else {"q": rule.preperiod, "p": rule.period, "v": list(rule.values)}


def semantic_id(context, mask):
    # A receipt acquired while measuring a contract does not change that
    # contract's content identity or create an unseen mask.
    semantic_context = {key: value for key, value in context.items() if key != "baseline_witness"}
    return sha({"context": semantic_context, "mask": mask})


def block_occurrence_id(block, manifest):
    """Opaque source occurrence identity; equal payloads are still distinct evidence."""
    return sha({"source_manifest": manifest, "source_block_occurrence": block.block_id,
                "observations": list(block.observations)})


def independent_induce(language, observations):
    """Scorer-only alternate shape traversal: first feasible fixed-ranked shape.

    No source .induce, _slot_constraints or dependency oracle calls. This checks
    the donor result, not a second independent mathematical model of cognition.
    """
    shapes = sorted((q + p, p, q) for q in range(language.max_preperiod + 1)
                    for p in range(1, language.max_period + 1))
    for _, p, q in shapes:
        slots = [None] * (q + p)
        valid = True
        for position, value in observations:
            index = position if position < q else q + (position - q) % p
            if not 0 <= value < language.max_value or (slots[index] is not None and slots[index] != value):
                valid = False
                break
            slots[index] = value
        if valid:
            return {"q": q, "p": p, "v": [0 if value is None else value for value in slots]}
    return None


class ObservationReads:
    def __init__(self, values, cost):
        self.values, self.cost = values, cost

    def __iter__(self):
        for value in self.values:
            self.cost.source_observation_reads += 1
            yield value

    def __len__(self):
        return len(self.values)


def worker(arm: str, out: Path, registration: dict):
    start_wall, start_cpu = time.perf_counter_ns(), time.process_time_ns()
    sys.path.insert(0, str(DONORS))
    import depend as source
    from games import Work
    out.mkdir(parents=True, exist_ok=False)
    catalogue = source.build_catalogue(1)
    if source.LANGUAGE.max_value <= 1 or len(catalogue.families) != 16:
        raise ValueError("source rank/family scope differs from registered donor")
    cost = Cost()
    basis = monotone_tables(4, cost) if arm == "active_monotone" else ()
    basis_bytes = len(canonical(basis).encode())
    basis_cost = asdict(cost)
    rows, raw_probes = [], []
    seen_method_occurrences, seen_semantic_contracts = set(), set()
    for family in catalogue.families:
        # Opaque ordering is content-bound and fixed; no role or diagnostic
        # label enters the learner. Four-block membership remains a given.
        blocks = sorted(family.blocks, key=lambda block: block_occurrence_id(block, registration["donor_manifest_sha256"]))
        block_data = [list(map(list, block.observations)) for block in blocks]
        block_ids = [block_occurrence_id(block, registration["donor_manifest_sha256"]) for block in blocks]
        method_occurrence = sha({"source_manifest": registration["donor_manifest_sha256"],
                                 "source_method_occurrence": family.method_id})
        if len(set(block_ids)) != 4 or method_occurrence in seen_method_occurrences:
            raise ValueError("source occurrence identities collide or are duplicated")
        seen_method_occurrences.add(method_occurrence)
        method_identity = sha({"source_method_occurrence": method_occurrence,
                               "blocks": block_data, "block_occurrences": block_ids,
                               "language": source.LANGUAGE.language_id,
                               "baseline": rule_record(family.rule)})
        context = {"source_manifest": registration["donor_manifest_sha256"],
                   "language": source.LANGUAGE.language_id,
                   "method_identity": method_identity,
                   "source_method_occurrence": method_occurrence,
                   "evidence_content_hash": sha(block_data),
                   "block_ids": block_ids,
                   "baseline_representation": rule_record(family.rule),
                   "scope": "subsets of these four original blocks; exact baseline representation identity"}
        contract_ids = {semantic_id(context, mask) for mask in range(16)}
        if len(contract_ids) != 16 or contract_ids & seen_semantic_contracts:
            raise ValueError("distinct registered occurrence contracts share an identity")
        seen_semantic_contracts.update(contract_ids)

        def oracle(mask, phase="acquisition"):
            observations = sorted({tuple(observation) for bit, data in enumerate(block_data)
                                   if mask & (1 << bit) for observation in data})
            cost.source_observation_reads += sum(len(data) for bit, data in enumerate(block_data)
                                                 if mask & (1 << bit))
            work = Work()
            induced = source.LANGUAGE.induce(ObservationReads(observations, cost), work=work)
            cost.source_shape_checks += work.expansions
            retained = induced == family.rule
            raw_probes.append({"semantic_id": semantic_id(context, mask),
                               "method_identity": method_identity, "mask": mask, "phase": phase,
                               "retained": retained, "induced_representation": rule_record(induced),
                               "source_shape_checks": work.expansions})
            # Keep even the failing method's last actually observed probe.
            (out / "raw-probes.json").write_text(canonical(raw_probes) + "\n")
            return retained

        # Baseline knowledge is actually checked and charged for every arm.
        cost.query_calls += 1
        baseline = oracle(15, "baseline-witness")
        if not baseline or any(family.rule.grundy(n) != value for data in block_data for n, value in data):
            raise ValueError("BASELINE_CONSISTENCY_FAILED")
        context["baseline_witness"] = sha(raw_probes[-1])
        # Context excludes phase/arm/display IDs. A new display name cannot
        # create an unqueried support configuration.
        learner = SupportLearner(arm, 4, context, cost, basis)
        before = asdict(cost)
        learner.acquire(oracle)
        acquisition = asdict(cost)
        probed_masks = sorted(learner.observations)
        path = out / (method_identity + ".json")
        snapshot_sha = learner.persist(path)
        persisted_bytes = path.stat().st_size
        # Removal arm keeps acquired exact observations; removes only learned
        # extrapolation, so it does not compare against an artificially reset cache.
        removal_cost = Cost()
        removal = SupportLearner.restart(path, expected_hash=snapshot_sha,
                                         expected_context=context, cost=removal_cost)
        learner = SupportLearner.restart(path, expected_hash=snapshot_sha,
                                         expected_context=context, cost=cost)
        service = []
        for mask in sorted(range(16), key=lambda m: sha({"method": method_identity, "mask": m})):
            calls_before = cost.query_calls
            prediction_before = learner.predict(mask)
            answer, inferred = learner.answer(mask, lambda m: oracle(m, "restart-service"))
            # Removal query uses the real source implementation and an isolated
            # counterfactual ledger: its execution is never credited to treatment.
            if removal.predict(mask, generalize=False) is None:
                removal_cost.query_calls += 1
                observations = sorted({tuple(observation) for bit, data in enumerate(block_data)
                                       if mask & (1 << bit) for observation in data})
                removal_cost.source_observation_reads += sum(len(data) for bit, data in enumerate(block_data)
                                                             if mask & (1 << bit))
                work = Work()
                induced = source.LANGUAGE.induce(ObservationReads(observations, removal_cost), work=work)
                removal_cost.source_shape_checks += work.expansions
                removal.observations[mask] = induced == family.rule
            removed_answer = removal.observations[mask]
            service.append({"mask": mask, "semantic_id": semantic_id(context, mask),
                            "unqueried_at_restart": mask not in probed_masks,
                            "pre_query_prediction": prediction_before, "answer": answer,
                            "inferred_unqueried": inferred,
                            "fallback_queries": cost.query_calls - calls_before,
                            "removal_answer": removed_answer})
        rows.append({"method_identity": method_identity, "context": context,
                     "probe_order": learner.probe_order, "probed_masks_at_restart": probed_masks,
                     "cost_before_acquisition": before, "cost_after_acquisition": acquisition,
                     "snapshot_sha256": snapshot_sha, "snapshot_bytes": persisted_bytes,
                     "service": service, "removal_cost": asdict(removal_cost),
                     "post_service_record": learner.record()})
        # Write observations/predictions before scorer access, and preserve
        # completed methods if a later method or scorer falsifies assumptions.
        (out / "raw-probes.json").write_text(canonical(raw_probes) + "\n")
        (out / "learning-receipt.json").write_text(json.dumps({"status": "PARTIAL_LEARNING_RECEIPT",
            "arm": arm, "cost": asdict(cost), "rows": rows}, indent=2, sort_keys=True) + "\n")
    learning_end_wall, learning_end_cpu = time.perf_counter_ns(), time.process_time_ns()
    # The independent scorer sees full masks ONLY after every arm-local
    # acquisition/prediction is finished. No scorer outcomes train the learner.
    scorer_start = time.perf_counter_ns()
    scorer_mismatches = []
    monotonicity_failures = []
    for row, family in zip(rows, catalogue.families):
        blocks = sorted(family.blocks, key=lambda block: block_occurrence_id(block, registration["donor_manifest_sha256"]))
        truth = {}
        for mask in range(16):
            observations = sorted({obs for bit, block in enumerate(blocks)
                                   if mask & (1 << bit) for obs in block.observations})
            expected = independent_induce(source.LANGUAGE, observations)
            truth[mask] = expected == rule_record(family.rule)
            source_result = rule_record(source.LANGUAGE.induce(observations))
            if expected != source_result:
                scorer_mismatches.append({"method": row["method_identity"], "mask": mask})
        violations = [(a, b) for a in range(16) for b in range(16)
                      if a & b == a and truth[a] and not truth[b]]
        row["monotonicity_violations"] = violations
        row["stale_retention_predictions"] = sum(s["answer"] and not truth[s["mask"]] for s in row["service"])
        row["collateral_reopen_predictions"] = sum(not s["answer"] and truth[s["mask"]] for s in row["service"])
        row["correct"] = sum(s["answer"] == truth[s["mask"]] for s in row["service"])
        row["truth_retention"] = {str(mask): value for mask, value in truth.items()}
        if violations:
            monotonicity_failures.append({"method": row["method_identity"], "violations": violations})
    result = {"schema": "ocm.support_effects.development_result.v1", "arm": arm,
              "ecology": "development", "generation_changes": 0,
              "claim_ceiling": "parent-owned learning of retention on already exposed source families; supplied block grouping",
              "cost": asdict(cost), "counted_operations": cost.counted_operations,
              "generic_version_space_cost": basis_cost, "generic_version_space_bytes": basis_bytes,
              "persistent_snapshot_bytes": sum(row["snapshot_bytes"] for row in rows),
              "unique_source_method_occurrences": len(seen_method_occurrences),
              "unique_semantic_contracts": len(seen_semantic_contracts),
              "learning_and_removal_wall_ns": learning_end_wall - start_wall,
              "learning_and_removal_cpu_ns": learning_end_cpu - start_cpu,
              "scorer_wall_ns": time.perf_counter_ns() - scorer_start,
              "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "correct": sum(row["correct"] for row in rows), "n": 16 * len(rows),
              "independent_scorer_agrees": not scorer_mismatches,
              "scorer_mismatches": scorer_mismatches,
              "monotonicity_failures": monotonicity_failures, "rows": rows}
    (out / "raw-probes.json").write_text(canonical(raw_probes) + "\n")
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if monotonicity_failures or scorer_mismatches:
        raise ValueError("MODEL_OR_SCORER_REFUTED: retained complete result.json and learning-receipt.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, default=HERE / "SUPPORT_DEVELOPMENT_REGISTRATION_V1.json")
    parser.add_argument("--registration-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker", choices=ARMS)
    args = parser.parse_args()
    raw = args.registration.read_bytes()
    registration = json.loads(raw)
    if hashlib.sha256(raw).hexdigest() != args.registration_sha256:
        raise ValueError("registration digest mismatch")
    if registration["status"] != "FROZEN_FOR_E2_DEVELOPMENT" or registration["ecology"] != "development":
        raise PermissionError("review and freeze required; protected execution not supported")
    for name, expected in registration["executable_sha256"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != expected:
            raise ValueError("frozen executable changed: " + name)
    manifest = HERE.parent / "self-evolution-v1" / "DONOR_MANIFEST.json"
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != registration["donor_manifest_sha256"]:
        raise ValueError("donor manifest changed")
    for row in json.loads(manifest.read_text())["rows"]:
        path = HERE.parent.parent / row["local_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("donor source changed: " + str(path))
    if args.worker:
        worker(args.worker, args.out, registration)
        return
    args.out.mkdir(parents=True, exist_ok=False)
    summaries = []
    for arm in registration["arms"]:
        start = time.perf_counter_ns()
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
            "--registration", str(args.registration.resolve()), "--registration-sha256", args.registration_sha256,
            "--out", str((args.out / arm).resolve()), "--worker", arm], capture_output=True, text=True)
        receipt = {"arm": arm, "process_wall_ns": time.perf_counter_ns() - start,
                   "exit_code": completed.returncode, "stderr": completed.stderr,
                   "stdout": completed.stdout}
        (args.out / (arm + "-process.json")).write_text(json.dumps(receipt, indent=2) + "\n")
        if completed.returncode:
            raise RuntimeError("arm failed; retained process receipt: " + arm)
        result = json.loads((args.out / arm / "result.json").read_text())
        summaries.append({**receipt, "correct": result["correct"], "n": result["n"],
                          "cost": result["cost"], "counted_operations": result["counted_operations"],
                          "snapshot_bytes": result["persistent_snapshot_bytes"],
                          "peak_rss_kib": result["peak_process_rss_kib"]})
    summary = {"registration_sha256": args.registration_sha256, "ecology": "development",
               "status": "E2_EXACT_SOURCE_MASK_CENSUS", "arms": summaries,
               "statistical_unit": "whole original method lifecycle; masks correlated; no inferential p-values",
               "novel_mechanism_claim": False, "new_ocm_generations": 0}
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
