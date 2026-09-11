from cross_rep_phase_4bit import run


def test_registered_class_and_ecology_sizes():
    result = run()
    assert result["class_sizes"] == {"H_T": 980, "H_P": 882}
    assert result["ecology_sizes"] == {
        "E_T_ONLY": 718,
        "E_P_ONLY": 620,
        "E_OVERLAP": 262,
    }


def test_frozen_predictions_preserve_the_negative():
    result = run()
    assert result["frozen_predictions"]["CR_P1_threshold_region"] is True
    assert result["frozen_predictions"]["CR_P2_program_region"] is False
    assert result["frozen_predictions"]["CR_P4_reversal"] is False


def test_program_morphology_abstention_exposes_identifiability_failure():
    result = run()
    assert result["results"]["E_P_ONLY"]["H_P"]["abstain_rate"] == 1.0
    assert result["results"]["E_T_ONLY"]["H_P"]["abstain_rate"] == 1.0
    assert result["results"]["E_OVERLAP"]["H_P"]["abstain_rate"] == 1.0
    assert result["results"]["E_P_ONLY"]["H_T"]["mean_cost"] < 1.0
