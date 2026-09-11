import copy
import json
from pathlib import Path

from validate_gmi_e3_domains import RESOURCE_ID, validate_contract


def fixture():
    path = Path(__file__).resolve().parent / "GMI_E3_DOMAIN_SPECIALIZATIONS_V1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_contract_is_green():
    assert validate_contract(fixture()) == []


def test_domain_cannot_change_shared_resource_semantics():
    data = fixture()
    data = copy.deepcopy(data)
    data["domains"]["FORMAL_MATHEMATICS_LEAN"]["rho_resource_semantics_id"] = "MATH_ONLY_COST"
    errors = validate_contract(data)
    assert any(RESOURCE_ID in error for error in errors)


def test_k2_cannot_disappear_from_one_common_capital_ladder():
    data = fixture()
    data = copy.deepcopy(data)
    data["common_theory_fields"]["developmental_capital"] = ["K0", "K1", "K3"]
    errors = validate_contract(data)
    assert any("K0,K1,K2,K3" in error for error in errors)


def test_verifier_remains_external_field():
    data = fixture()
    data = copy.deepcopy(data)
    data["common_theory_fields"]["external_contract"] = [
        "constitution_identity",
        "development_protocol_id",
        "intervention_probe_class_id",
    ]
    errors = validate_contract(data)
    assert any("external contract field set changed" in error for error in errors)


def test_math_and_code_domains_are_both_mandatory():
    data = fixture()
    data = copy.deepcopy(data)
    del data["domains"]["EXECUTION_VERIFIED_CODE"]
    errors = validate_contract(data)
    assert any("domains must be exactly" in error for error in errors)
