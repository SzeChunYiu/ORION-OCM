"""Static validator for GMI E3 math/code specialization contracts.

This validates theory-schema invariance only.  It does not run Lean, code tests,
models, or developmental experiments.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


REQUIRED_COMMON_GROUPS = {
    "developmental_situation",
    "morphology",
    "external_contract",
    "developmental_capital",
    "burden_semantics",
    "generality_semantics",
}

REQUIRED_MORPHOLOGY_FIELDS = {
    "F_factorization_identity",
    "Theta_mutable_state_digest",
    "K_execution_kernel_identity",
    "U_update_law_identity",
    "Gamma_morphogenesis_identity_or_none",
    "kappa_semantic_adapter_identity",
    "rho_resource_semantics_id",
}

REQUIRED_EXTERNAL_FIELDS = {
    "verifier_identity",
    "constitution_identity",
    "development_protocol_id",
    "intervention_probe_class_id",
}

REQUIRED_DOMAIN_FIELDS = (
    REQUIRED_MORPHOLOGY_FIELDS
    | REQUIRED_EXTERNAL_FIELDS
    | {
        "capability_coordinates",
        "family_native_pre_solution_mediators",
        "external_verifier_class",
        "allowed_domain_specific_fields",
    }
)

REQUIRED_DOMAINS = {"FORMAL_MATHEMATICS_LEAN", "EXECUTION_VERIFIED_CODE"}
REQUIRED_CAPITAL_LEVELS = ["K0", "K1", "K2", "K3"]
RESOURCE_ID = "GMI_E3_RAW_RESOURCES_V1"


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def validate_contract(data: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    common = data.get("common_theory_fields")
    if not isinstance(common, Mapping):
        return ["common_theory_fields missing or not a mapping"]

    missing_common = REQUIRED_COMMON_GROUPS - set(common)
    if missing_common:
        errors.append(f"missing common theory groups: {sorted(missing_common)}")

    if common.get("developmental_capital") != REQUIRED_CAPITAL_LEVELS:
        errors.append("developmental_capital must be exactly K0,K1,K2,K3 in order")

    morphology_fields = set(common.get("morphology", []))
    if morphology_fields != REQUIRED_MORPHOLOGY_FIELDS:
        errors.append(
            "common morphology field set changed: "
            f"expected {sorted(REQUIRED_MORPHOLOGY_FIELDS)}, got {sorted(morphology_fields)}"
        )

    external_fields = set(common.get("external_contract", []))
    if external_fields != REQUIRED_EXTERNAL_FIELDS:
        errors.append(
            "common external contract field set changed: "
            f"expected {sorted(REQUIRED_EXTERNAL_FIELDS)}, got {sorted(external_fields)}"
        )

    domains = data.get("domains")
    if not isinstance(domains, Mapping):
        return errors + ["domains missing or not a mapping"]

    if set(domains) != REQUIRED_DOMAINS:
        errors.append(
            f"domains must be exactly {sorted(REQUIRED_DOMAINS)}, got {sorted(domains)}"
        )

    for domain_name, domain in domains.items():
        if not isinstance(domain, Mapping):
            errors.append(f"{domain_name}: domain contract is not a mapping")
            continue

        missing = REQUIRED_DOMAIN_FIELDS - set(domain)
        if missing:
            errors.append(f"{domain_name}: missing fields {sorted(missing)}")

        for field in REQUIRED_DOMAIN_FIELDS:
            if field in domain and not _nonempty(domain[field]):
                errors.append(f"{domain_name}: empty field {field}")

        if domain.get("rho_resource_semantics_id") != RESOURCE_ID:
            errors.append(
                f"{domain_name}: must use shared resource semantics {RESOURCE_ID}"
            )

        # External authority/checking must not be smuggled into morphology field names.
        for morphology_field in REQUIRED_MORPHOLOGY_FIELDS:
            text = str(domain.get(morphology_field, "")).lower()
            if morphology_field not in {"kappa_semantic_adapter_identity"} and (
                "owns verifier" in text or "changes verifier" in text
            ):
                errors.append(
                    f"{domain_name}: morphology field {morphology_field} claims verifier authority"
                )

        capability = domain.get("capability_coordinates", [])
        mediators = domain.get("family_native_pre_solution_mediators", [])
        domain_specific = domain.get("allowed_domain_specific_fields", [])
        if len(set(capability)) != len(capability):
            errors.append(f"{domain_name}: duplicate capability coordinate")
        if len(set(mediators)) != len(mediators):
            errors.append(f"{domain_name}: duplicate pre-solution mediator")
        if len(set(domain_specific)) != len(domain_specific):
            errors.append(f"{domain_name}: duplicate domain-specific field")

    invariants = data.get("invariance_requirements")
    if not isinstance(invariants, list) or len(invariants) < 6:
        errors.append("invariance_requirements missing or too small")

    if data.get("terminal_if_valid") != "GMI_E3_STATIC_DOMAIN_SCHEMA_TRANSFER_GREEN":
        errors.append("unexpected valid terminal")

    return errors


def load_and_validate(path: str | Path) -> list[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return validate_contract(data)


def main() -> int:
    here = Path(__file__).resolve().parent
    path = here / "GMI_E3_DOMAIN_SPECIALIZATIONS_V1.json"
    errors = load_and_validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("GMI_E3_STATIC_DOMAIN_SCHEMA_TRANSFER_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
