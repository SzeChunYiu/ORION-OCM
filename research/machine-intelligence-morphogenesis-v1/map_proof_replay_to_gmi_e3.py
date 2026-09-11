"""Map the existing fixed Lean proof-replay receipt into GMI E3 episode semantics.

This adapter is intentionally conservative:
- it does not run Lean;
- it does not grant informal statement correspondence;
- it does not claim learning, generalization, K1 or K2;
- it preserves the source receipt's claim ceiling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


INPUT_SCHEMA = "ocm.fixed-proof-replay.receipt.v1"
OUTPUT_SCHEMA = "GMIRealCognitionEpisodeV1.instance"


def _digest_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _null_resource_vector() -> dict[str, Any]:
    return {
        "foundation_model_calls": None,
        "foundation_model_input_tokens": None,
        "foundation_model_output_tokens": None,
        "candidate_generation_count": 0,
        "search_expansions": 0,
        "tool_calls": None,
        "verifier_calls": None,
        "failed_attempts": None,
        "cpu_time": None,
        "gpu_time": None,
        "wall_time": None,
        "peak_memory": None,
        "persistent_bytes_read": None,
        "persistent_bytes_written": None,
        "index_or_library_maintenance_work": 0,
        "development_update_work": 0,
        "human_interventions": 0,
        "other_domain_specific_raw_receipts": {
            "fixed_theorem_count": 9,
            "search_or_training_performed": False,
        },
    }


def map_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if receipt.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"expected input schema {INPUT_SCHEMA!r}")

    terminal = receipt.get("terminal")
    if terminal not in {"FIXED_PROOF_REPLAY_PASS", "CANNOT_CHECK", "FAIL"}:
        raise ValueError(f"unexpected proof-replay terminal: {terminal!r}")

    manifest_digest = receipt.get("manifest_sha256") or "UNKNOWN"
    claims = receipt.get("claims", {})
    correspondence = claims.get("informal_correspondence", "NOT_OBTAINED")
    learned_methods = claims.get("learned_proof_methods", "NOT_EVALUATED")
    unseen_generalization = claims.get("unseen_proof_generalization", "NOT_EVALUATED")

    formal_pass = terminal == "FIXED_PROOF_REPLAY_PASS"

    capability = {
        "statement_correspondence": "UNKNOWN" if correspondence == "NOT_OBTAINED" else correspondence,
        "target_kernel_verified": formal_pass,
        "registered_partial_lemmas_verified": formal_pass,
        "dependency_closure_valid": formal_pass,
        "forbidden_axiom_or_sorry_free": formal_pass,
    }

    if formal_pass:
        episode_terminal = "FORMAL_KERNEL_VERIFIED_FIXED_REPLAY_ONLY"
        semantic_claim_ceiling = (
            "Nine fixed authored formal theorems kernel-replayed under the pinned package; "
            "no informal correspondence, unseen proof generalization, learned proof method, K1 or K2 claim."
        )
    elif terminal == "CANNOT_CHECK":
        episode_terminal = "CANNOT_CHECK"
        semantic_claim_ceiling = "Proof replay infrastructure could not establish the fixed formal receipt."
    else:
        episode_terminal = "VERIFIER_REJECTION_OR_CUSTODY_FAILURE"
        semantic_claim_ceiling = "Fixed proof replay did not pass; no positive formal claim."

    starting = {
        "machine_configuration_digest": _digest_json(
            {
                "manifest": manifest_digest,
                "toolchain": receipt.get("toolchain"),
                "archive": receipt.get("archive_sha256"),
                "lean_binary": receipt.get("lean_binary_sha256"),
            }
        ),
        "registered_history_digest": "NO_DEVELOPMENTAL_HISTORY__FIXED_REPLAY_CALIBRATION",
        "public_ecology_authority_context_digest": _digest_json(
            {
                "statement_scope": receipt.get("statement_scope"),
                "claims": claims,
            }
        ),
        "morphology_identity": "FIXED_PROOF_REPLAY_NO_SEARCH_NO_LEARNING",
        "development_protocol_id": "IDENTITY_UPDATE__NO_LEARNING",
        "intervention_probe_class_id": "FIXED_REPLAY_ONLY",
    }

    episode = {
        "schema": OUTPUT_SCHEMA,
        "episode_identity": {
            "episode_id": f"proof-replay:{manifest_digest}",
            "domain": "FORMAL_MATHEMATICS_LEAN",
            "task_family_id": "proof-replay-v1-fixed-authored-theorems",
            "task_id": "nine-fixed-formal-theorems",
            "run_id": _digest_json(receipt),
            "arm_id": "FIXED_REPLAY_CALIBRATION",
            "protocol_version": "GMI_E3_V1",
        },
        "task_contract": {
            "raw_task_digest": manifest_digest,
            "semantic_task_digest": _digest_json(receipt.get("statement_scope")),
            "goal_obligations": ["replay exactly the registered fixed formal theorems"],
            "constraints": ["pinned Lean package", "no search", "no training", "no arbitrary candidate execution"],
            "allowed_tools_actions": ["registered fixed replay pipeline"],
            "disallowed_tools_actions": ["target editing", "new proof search", "foundation-model proof proposal"],
            "success_contract_id": "FIXED_PROOF_REPLAY_PASS",
            "resource_budget_id": "FIXED_REPLAY_EXISTING_PACKAGE",
            "protected_information_policy": "KNOWN_AUTHORED_FIXTURES__CALIBRATION_ONLY",
        },
        "starting_developmental_situation": starting,
        "morphology_realization": {
            "F_factorization_identity": "fixed formal proof package",
            "Theta_mutable_state_digest": "IMMUTABLE_FOR_EPISODE",
            "K_execution_kernel_identity": "direct fixed replay/compile/check",
            "U_update_law_identity": "IDENTITY_NO_LEARNING",
            "Gamma_morphogenesis_identity_or_none": None,
            "kappa_semantic_adapter_identity": "proof-replay-v1 formal receipt adapter",
            "rho_resource_semantics_id": "GMI_E3_RAW_RESOURCES_V1",
        },
        "external_verification": {
            "verifier_type": "FORMAL_KERNEL_VERIFIED",
            "verifier_identity": receipt.get("toolchain") or "LEAN_4_19_PINNED_BY_SOURCE_RECEIPT",
            "verifier_version_digest": _digest_json(
                {
                    "toolchain": receipt.get("toolchain"),
                    "archive": receipt.get("archive_sha256"),
                    "lean_binary": receipt.get("lean_binary_sha256"),
                }
            ),
            "admissibility_rule_digest": _digest_json("FIXED_PROOF_REPLAY_PASS"),
            "statement_or_spec_correspondence_rule": "NOT_OBTAINED_FOR_INFORMAL_STATEMENT",
            "verifier_strength_claim": "FORMAL_FIXED_STATEMENT_KERNEL_REPLAY_ONLY",
            "known_verifier_limitations": list(receipt.get("limitations", [])),
        },
        "pre_solution_trace": {
            "proposal_events": 0,
            "retrieval_events": 0,
            "search_expansions": 0,
            "tool_calls": None,
            "verification_calls": None,
            "failure_events": [],
            "retrieved_assets": [],
            "consumed_assets": [],
            "pre_solution_geometry_metrics": {
                "status": "NOT_APPLICABLE_FIXED_REPLAY_NO_SEARCH",
            },
        },
        "outcome": {
            "terminal": episode_terminal,
            "admissible_result": formal_pass,
            "capability_vector": capability,
            "partial_certificate_or_none": None,
            "semantic_claim_ceiling": semantic_claim_ceiling,
            "all_required_checks_complete": formal_pass,
        },
        "resource_vector": _null_resource_vector(),
        "ending_developmental_situation": {
            **starting,
            "new_persistent_objects": [],
            "revoked_or_retired_objects": [],
            "post_task_update_receipts": [],
        },
        "developmental_attribution": {
            "solution_was_absent_from_relevant_history": False,
            "pre_solution_mediator_observed": False,
            "matched_reset_result_ref": None,
            "strongest_parent_result_ref": None,
            "shuffle_or_cross_history_result_ref_or_na": "NA_FIXED_REPLAY_CALIBRATION",
            "candidate_capital_level": "NONE_CALIBRATION",
            "causal_attribution_terminal": "NO_DEVELOPMENTAL_CLAIM_FIXED_REPLAY",
        },
        "source_boundary": {
            "source_schema": INPUT_SCHEMA,
            "source_terminal": terminal,
            "source_claims": claims,
            "learned_proof_methods": learned_methods,
            "unseen_proof_generalization": unseen_generalization,
        },
    }
    return episode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.receipt.read_text(encoding="utf-8"))
    mapped = map_receipt(source)
    if args.out.exists():
        raise SystemExit("refusing to overwrite existing output")
    args.out.write_text(json.dumps(mapped, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(mapped["outcome"]["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
