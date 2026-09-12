import json
from pathlib import Path

from gmi_k5_bh_experiments import run

HERE=Path(__file__).resolve().parent
SCORE=json.loads((HERE/"GMI_K5_BH_SCORING_FREEZE_V1.json").read_text())
ADM=json.loads((HERE/"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json").read_text())
EXEC=json.loads((HERE/"GMI_K5_BH_EXECUTION_FREEZE_V5.json").read_text())


def test_admissibility_addendum_changes_no_numerical_quality_threshold():
    assert SCORE["quality_thresholds"]=={
        "B_SPECIALIZATION_max_test_mse":0.50,
        "C_FEATURE_LEARNING_max_test_error":0.18,
        "E_CONTROL_min_normalized_return":0.80,
        "F_CONTINUAL_min_old_accuracy":0.95,
        "F_CONTINUAL_min_new_accuracy":0.90,
    }
    assert "quality_threshold" not in json.dumps(ADM).lower()
    assert ADM["no_threshold_change"].startswith("All numerical quality thresholds remain exactly")


def test_all_development_smoke_results_report_self_consistent_admissible_set():
    # Development-only seeds: this validates the runner contract, not protected scientific predictions.
    for i,lane in enumerate(sorted(EXEC["final_task_plan"])):
        vals=EXEC["final_task_plan"][lane]["values"]
        for j,value in enumerate(vals):
            r=run(lane,0xA50000+i*17+j,value)
            assert isinstance(r.get("admissible"),list), (lane,value,r)
            assert r["observed_winner"]=="NONE" or r["observed_winner"] in r["admissible"], (lane,value,r)
            assert "predicted_winner" in r and "prediction_margin" in r and "observables" in r


def test_v5_continual_grid_is_the_pre_execution_corrected_grid():
    assert EXEC["final_task_plan"]["F_CONTINUAL"]["values"]==[0.0,0.60,0.90,0.98]


def test_addendum_makes_predicted_inadmissibility_non_green_by_definition():
    text=json.dumps(ADM,sort_keys=True)
    assert ">=6/8" in text or "6/8" in text
    assert "PREDICTED_INADMISSIBLE" in text
    assert "INCONCLUSIVE" in text and "THEORY_RED" in text
