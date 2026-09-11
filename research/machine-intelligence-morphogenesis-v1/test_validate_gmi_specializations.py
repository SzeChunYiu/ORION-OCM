import json
from pathlib import Path

from validate_gmi_specializations import validate


def _data():
    here = Path(__file__).resolve().parent
    return json.loads((here / "GMI_SPECIALIZATION_CONTRACTS_V1.json").read_text())


def test_all_material_families_use_one_schema():
    receipt = validate(_data())
    assert receipt["families"] >= 6
    assert receipt["required_material_families_present"] is True
    assert receipt["terminal"] == "GMI_SPECIALIZATION_SCHEMA_STATIC_CHECK_GREEN"


def test_verifier_and_constitution_remain_external_fields():
    data = _data()
    assert set(data["external_fields"]) == {
        "V_external",
        "C_external",
        "development_protocol_D",
    }
    assert "V_external" not in set(data["canonical_morphology_fields"])
    assert "C_external" not in set(data["canonical_morphology_fields"])
