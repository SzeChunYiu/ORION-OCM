from math import isclose

import pytest

from gmi_realization_demand_calibration import (
    DemandWorld,
    calibration_receipt,
    compositional_parity,
    horizon_crossover,
    materialized_table,
    winner,
)


def test_no_drift_r4_crossover_is_four():
    assert isclose(horizon_crossover(4, 0), 4.0)
    assert winner(DemandWorld(4, 2, 0)) == ("COMPOSITIONAL_PARITY",)
    assert winner(DemandWorld(4, 8, 0)) == ("MATERIALIZED_TABLE",)


def test_drift_pushes_materialization_crossover_outward():
    assert isclose(horizon_crossover(4, 2), 14.0)
    assert winner(DemandWorld(4, 8, 2)) == ("COMPOSITIONAL_PARITY",)
    assert winner(DemandWorld(4, 20, 2)) == ("MATERIALIZED_TABLE",)


def test_both_realizations_compute_same_registered_obligation_cost_model():
    world = DemandWorld(3, 5, 1)
    table = materialized_table(world)
    comp = compositional_parity(world)
    assert table.morphology == "MATERIALIZED_TABLE"
    assert comp.morphology == "COMPOSITIONAL_PARITY"
    assert table.build == 8
    assert comp.build == 3
    assert table.total == 21
    assert comp.total == 19


def test_one_bit_case_has_parallel_per_query_cost_and_no_unique_crossover():
    assert horizon_crossover(1, 0) is None
    assert horizon_crossover(1, 5) is None


def test_invalid_world_coordinates_fail_closed():
    with pytest.raises(ValueError):
        DemandWorld(0, 1, 0)
    with pytest.raises(ValueError):
        DemandWorld(2, -1, 0)
    with pytest.raises(ValueError):
        horizon_crossover(3, -1)


def test_receipt_has_parent_owned_claim_boundary():
    receipt = calibration_receipt()
    assert receipt["r4_no_drift_crossover"] == 4.0
    assert receipt["r4_u2_crossover"] == 14.0
    assert receipt["cases"]["no_drift_short"]["winner"] == ("COMPOSITIONAL_PARITY",)
    assert receipt["cases"]["no_drift_long"]["winner"] == ("MATERIALIZED_TABLE",)
    assert receipt["cases"]["drift_mid"]["winner"] == ("COMPOSITIONAL_PARITY",)
    assert receipt["cases"]["drift_long"]["winner"] == ("MATERIALIZED_TABLE",)
    assert receipt["terminal"] == "REALIZATION_DEMAND_SIGNATURE_SUPPORTED_AT_FINITE_CALIBRATION_SCOPE"
    assert "parent-owned" in receipt["claim_boundary"]
