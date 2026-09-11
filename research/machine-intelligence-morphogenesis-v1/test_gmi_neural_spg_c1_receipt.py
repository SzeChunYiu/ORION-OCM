import json
from pathlib import Path
from statistics import median


HERE = Path(__file__).resolve().parent
GRID = HERE / "GMI_NEURAL_SPG_C1_PRIMARY_GRID_V1.json"
RECEIPT = HERE / "GMI_NEURAL_SPG_C1_RECEIPT_V1.json"


def flatten(matrix):
    return [value for row in matrix for value in row]


def test_primary_grid_recomputes_receipt_headlines():
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    for ecology in ("A1", "A2"):
        matched = flatten(grid[ecology]["matched_gain_bits"])
        cross = flatten(grid[ecology]["cross_gain_bits"])
        assert len(matched) == 48
        assert len(cross) == 48
        positive = sum(value > 0 for value in matched)
        median_matched = median(matched)
        median_cross = median(cross)
        specificity = median_matched - median_cross
        out = receipt["results"][ecology]
        assert positive == out["positive_matched_rows"] == 40
        assert abs(median_matched - out["median_matched_gain_bits"]) < 1e-8
        assert abs(median_cross - out["median_cross_gain_bits"]) < 1e-8
        assert abs(specificity - out["median_specificity_gap_bits"]) < 1e-8


def test_every_registered_prediction_is_green():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["prediction_results"]
    assert all(receipt["prediction_results"].values())
    assert receipt["terminal"] == (
        "NEURAL_K1_SEMANTIC_PROPOSAL_GEOMETRY_SUPPORTED_AT_REGISTERED_SYNTHETIC_SCOPE"
    )


def test_result_remains_k1_and_parent_owned():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["candidate_capital_level"] == "K1"
    assert receipt["k2_status"] == "NOT_TESTED"
    assert receipt["parent_disposition"] == (
        "MULTITASK_REPRESENTATION_TRANSFER_LEARNING_PARENT_OWNS_MECHANISM_CLASS"
    )
    ceiling = receipt["claim_ceiling"].lower()
    assert "not k2" in ceiling
    assert "not" in ceiling and "universal gmi law" in ceiling


def test_freeze_precedes_execution_source_commit():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["protocol"]["freeze_commit"] == "6449fcf940796315949603662151bcf05edde5f4"
    assert receipt["executable"]["commit_before_registered_execution"] == (
        "0b04c791188c97f282ccc3c2edf3aa834c301247"
    )
