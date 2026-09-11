import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "GMI_REALIZATION_THEOREM_REGISTRY_V1.json"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_theorem_ids_are_unique_and_ordered():
    registry = load_registry()
    ids = [row["id"] for row in registry["rows"]]
    assert len(ids) == len(set(ids))
    assert ids == [f"GMI-RP{i}" for i in range(1, 19)]


def test_new_semantic_and_bias_rows_are_present():
    registry = load_registry()
    by_id = {row["id"]: row for row in registry["rows"]}
    assert by_id["GMI-RP12"]["status"] == "SPECIFIED_AND_EXHAUSTIVELY_CALIBRATED"
    assert by_id["GMI-RP13"]["status"] == "SPECIFIED_AND_EXHAUSTIVELY_CALIBRATED"
    assert by_id["GMI-RP16"]["status"] == "PROVED_BY_ALGEBRA_AND_EXHAUSTIVELY_CALIBRATED"
    assert by_id["GMI-RP18"]["status"] == "SPECIFIED_EMPIRICAL_BRIDGE"


def test_registry_forbids_architecture_label_shortcuts():
    registry = load_registry()
    forbidden = "\n".join(registry["forbidden_inference"]).lower()
    assert "architecture family label" in forbidden
    assert "neural network uniquely implied" in forbidden
    assert "rank or code length converted to probability" in forbidden
    assert "k1 inferred from final success" in forbidden


def test_registry_keeps_real_cross_paradigm_work_open():
    registry = load_registry()
    open_targets = set(registry["open_theory_targets"])
    assert "prospective family-held-out semantic proposal-geometry transfer" in open_targets
    assert "real code/math semantic proposal geometry under common E3 receipts" in open_targets
    assert "neural-family semantic proposal geometry with frozen held-out targets" in open_targets
    assert registry["claim_ceiling"] == "FORMAL_SYNTHESIS_PLUS_FINITE_EXACT_CROSS_PARADIGM_CALIBRATION_ONLY"
