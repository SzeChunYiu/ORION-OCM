from __future__ import annotations

from decimal import Decimal as D

import r0c_scheduler_residual_audit as R


def _d(obj: dict) -> D:
    return D(obj["exact_decimal"])


def test_merged_native_donor_is_source_custodied_and_pairwise_exact():
    receipt = R.build_receipt()
    assert receipt["source"]["git_blob_sha1"] == R.EXPECTED_SOURCE_BLOB
    assert receipt["source"]["donor_terminal"] == "EXACT_FINITE_PARITY_WITH_MIXED_OBSERVED_COST"
    assert len(receipt["cells"]) == 4
    assert all(cell["best_whole_process_scheduler"] == cell["best_search_scheduler"]
               for cell in receipt["cells"])
    assert {cell["best_whole_process_scheduler"] for cell in receipt["cells"]} == {"layered", "indexed"}


def test_free_cell_oracle_has_only_0p285_percent_whole_process_residual():
    receipt = R.build_receipt()
    whole = receipt["aggregate"]["whole_process_wall_seconds"]
    assert whole["best_static_scheduler"] == "indexed"
    assert _d(whole["static_totals"]["layered"]) == D("18.513788321")
    assert _d(whole["static_totals"]["indexed"]) == D("18.315104110")
    assert _d(whole["free_cell_identity_oracle_total"]) == D("18.262926388")
    assert _d(whole["oracle_improvement_over_best_static_fraction"]) == D(
        "0.002848890275841298507366224302614679485980"
    )
    assert _d(whole["oracle_improvement_over_best_static_percent"]) < D("0.285")


def test_search_local_residual_is_larger_but_still_oracle_only():
    receipt = R.build_receipt()
    search = receipt["aggregate"]["search_seconds"]
    whole = receipt["aggregate"]["whole_process_wall_seconds"]
    assert search["best_static_scheduler"] == "indexed"
    assert _d(search["static_totals"]["layered"]) == D("1.426318450")
    assert _d(search["static_totals"]["indexed"]) == D("1.282425732")
    assert _d(search["free_cell_identity_oracle_total"]) == D("1.243620865")
    assert D("3.02") < _d(search["oracle_improvement_over_best_static_percent"]) < D("3.03")
    assert (_d(search["oracle_improvement_over_best_static_fraction"])
            > _d(whole["oracle_improvement_over_best_static_fraction"]))


def test_outcome_label_is_explicitly_forbidden_as_selector_feature():
    receipt = R.build_receipt()
    assert receipt["ml_authorized"] is False
    assert receipt["terminal"] == "R0C_DONOR_ORACLE_BOUND_ONLY_NO_SELECTION_POPULATION"
    assert any("positive/false is an outcome label" in item for item in receipt["claim_boundary"])
    assert any("only four authored" in item for item in receipt["claim_boundary"])
    assert receipt["findings"]["whole_process_oracle_residual_below_half_percent"] is True
