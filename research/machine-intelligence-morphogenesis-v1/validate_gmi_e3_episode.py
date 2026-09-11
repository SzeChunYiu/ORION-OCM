"""Validate concrete GMI E3 real-cognition episode instances.

The validator checks theory invariants and attribution preconditions only.
It does not decide whether an empirical causal claim is statistically true.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


REQUIRED_TOP_LEVEL = {
    "schema",
    "episode_identity",
    "task_contract",
    "starting_developmental_situation",
    "morphology_realization",
    "external_verification",
    "pre_solution_trace",
    "outcome",
    "resource_vector",
    "ending_developmental_situation",
    "developmental_attribution",
}

REQUIRED_RESOURCES = {
    "foundation_model_calls",
    "foundation_model_input_tokens",
    "foundation_model_output_tokens",
    "candidate_generation_count",
    "search_expansions",
    "tool_calls",
    "verifier_calls",
    "failed_attempts",
    "cpu_time",
    "gpu_time",
    "wall_time",
    "peak_memory",
    "persistent_bytes_read",
    "persistent_bytes_written",
    "index_or_library_maintenance_work",
    "development_update_work",
    "human_interventions",
    "other_domain_specific_raw_receipts",
}

REQUIRED_SITUATION = {
    "machine_configuration_digest",
    "registered_history_digest",
    "public_ecology_authority_context_digest",
}

REQUIRED_MORPHOLOGY = {
    "F_factorization_identity",
    "Theta_mutable_state_digest",
    "K_execution_kernel_identity",
    "U_update_law_identity",
    "Gamma_morphogenesis_identity_or_none",
    "kappa_semantic_adapter_identity",
    "rho_resource_semantics_id",
}

REQUIRED_ATTRIBUTION = {
    "solution_was_absent_from_relevant_history",
    "pre_solution_mediator_observed",
    "matched_reset_result_ref",
    "strongest_parent_result_ref",
    "shuffle_or_cross_history_result_ref_or_na",
    "candidate_capital_level",
    "causal_attribution_terminal",
}

ALLOWED_CAPITAL = {"NONE_CALIBRATION", "K0", "K1", "K2", "K3"}
DOMAINS = {"FORMAL_MATHEMATICS_LEAN", "EXECUTION_VERIFIED_CODE"}


def _mapping(value: Any, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be a mapping")
        return {}
    return value


def validate_episode(episode: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    missing_top = REQUIRED_TOP_LEVEL - set(episode)
    if missing_top:
        errors.append(f"missing top-level groups: {sorted(missing_top)}")

    if episode.get("schema") != "GMIRealCognitionEpisodeV1.instance":
        errors.append("unexpected episode schema")

    identity = _mapping(episode.get("episode_identity"), "episode_identity", errors)
    domain = identity.get("domain")
    if domain not in DOMAINS:
        errors.append(f"unsupported domain {domain!r}")

    start = _mapping(
        episode.get("starting_developmental_situation"),
        "starting_developmental_situation",
        errors,
    )
    missing_start = REQUIRED_SITUATION - set(start)
    if missing_start:
        errors.append(f"starting situation missing {sorted(missing_start)}")

    ending = _mapping(
        episode.get("ending_developmental_situation"),
        "ending_developmental_situation",
        errors,
    )
    missing_end = REQUIRED_SITUATION - set(ending)
    if missing_end:
        errors.append(f"ending situation missing {sorted(missing_end)}")

    morphology = _mapping(episode.get("morphology_realization"), "morphology_realization", errors)
    missing_morph = REQUIRED_MORPHOLOGY - set(morphology)
    if missing_morph:
        errors.append(f"morphology missing {sorted(missing_morph)}")
    if morphology.get("rho_resource_semantics_id") != "GMI_E3_RAW_RESOURCES_V1":
        errors.append("episode must use GMI_E3_RAW_RESOURCES_V1")

    verifier = _mapping(episode.get("external_verification"), "external_verification", errors)
    verifier_type = str(verifier.get("verifier_type", ""))
    if domain == "FORMAL_MATHEMATICS_LEAN" and "FORMAL" not in verifier_type:
        errors.append("Lean mathematics episode must use a formal verifier class")
    if domain == "EXECUTION_VERIFIED_CODE" and not any(
        token in verifier_type for token in ("EXECUTION", "FORMAL_SPEC")
    ):
        errors.append("code episode must use execution/formal-spec verifier class")

    resources = _mapping(episode.get("resource_vector"), "resource_vector", errors)
    missing_resources = REQUIRED_RESOURCES - set(resources)
    if missing_resources:
        errors.append(f"resource vector missing {sorted(missing_resources)}")

    outcome = _mapping(episode.get("outcome"), "outcome", errors)
    if outcome.get("admissible_result") is True and outcome.get("all_required_checks_complete") is not True:
        errors.append("admissible_result=true requires all_required_checks_complete=true")

    attribution = _mapping(
        episode.get("developmental_attribution"), "developmental_attribution", errors
    )
    missing_attr = REQUIRED_ATTRIBUTION - set(attribution)
    if missing_attr:
        errors.append(f"developmental attribution missing {sorted(missing_attr)}")

    capital = attribution.get("candidate_capital_level")
    if capital not in ALLOWED_CAPITAL:
        errors.append(f"unknown candidate_capital_level {capital!r}")

    # K1+ claims require a genuinely fresh target and an observed pre-solution mediator.
    if capital in {"K1", "K2", "K3"}:
        if attribution.get("solution_was_absent_from_relevant_history") is not True:
            errors.append(f"{capital} requires solution absent from relevant history")
        if attribution.get("pre_solution_mediator_observed") is not True:
            errors.append(f"{capital} requires a pre-solution mediator")
        if not attribution.get("matched_reset_result_ref"):
            errors.append(f"{capital} requires matched reset evidence")

    # K2/K3 additionally require actual developmental update work/evidence rather than fixed replay.
    if capital in {"K2", "K3"}:
        if morphology.get("U_update_law_identity") in {None, "IDENTITY_NO_LEARNING"}:
            errors.append(f"{capital} cannot be claimed under identity/no-learning update")
        if resources.get("development_update_work") == 0:
            errors.append(f"{capital} cannot have measured zero development_update_work")

    # Calibration receipt must never masquerade as a developmental positive.
    if morphology.get("U_update_law_identity") == "IDENTITY_NO_LEARNING" and capital in {"K1", "K2", "K3"}:
        errors.append("identity/no-learning episode cannot claim developmental capital")

    return errors


def load_and_validate(path: str | Path) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        episode = json.load(handle)
    return validate_episode(episode)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path)
    args = parser.parse_args()
    errors = load_and_validate(args.episode)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("GMI_E3_EPISODE_SCHEMA_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
