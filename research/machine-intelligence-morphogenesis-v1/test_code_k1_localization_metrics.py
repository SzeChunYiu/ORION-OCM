import math

import pytest

from code_k1_localization_metrics import (
    canonical_repo_path,
    localization_metrics,
    localization_rank_shift,
    paired_localization_rows,
)


def test_single_fault_file_localized_after_one_irrelevant_event():
    row = localization_metrics(
        ["docs/readme.md", "src/cache.py", "src/other.py"],
        ["src/cache.py"],
        event_budget=10,
    )
    assert row.event_rank == 2
    assert row.localization_censored is False
    assert row.irrelevant_inspection_events_before_cover == 1
    assert row.irrelevant_unique_files_before_cover == 1
    assert row.repeated_inspection_events_before_cover == 0


def test_multi_file_fault_requires_all_causal_files():
    row = localization_metrics(
        ["src/a.py", "src/noise.py", "src/b.py"],
        ["src/a.py", "src/b.py"],
    )
    assert row.event_rank == 3
    assert row.fault_files_seen == 2
    assert row.irrelevant_inspection_events_before_cover == 1


def test_repeated_inspection_counts_as_search_event():
    row = localization_metrics(
        ["src/noise.py", "src/noise.py", "src/fault.py"],
        ["src/fault.py"],
    )
    assert row.event_rank == 3
    assert row.irrelevant_inspection_events_before_cover == 2
    assert row.irrelevant_unique_files_before_cover == 1
    assert row.repeated_inspection_events_before_cover == 1


def test_censored_rank_is_budget_plus_one():
    row = localization_metrics(
        ["src/a.py", "src/noise.py"],
        ["src/missing.py"],
        event_budget=7,
    )
    assert row.localization_censored is True
    assert row.event_rank == 8
    assert row.fault_files_seen == 0


def test_positive_shift_means_treatment_localized_earlier():
    shift = localization_rank_shift(reset_rank=15, treatment_rank=3)
    assert shift == pytest.approx(2.0)


def test_equal_ranks_have_zero_shift():
    assert localization_rank_shift(5, 5) == 0.0


def test_paired_rows_preserve_censor_flags():
    reset = localization_metrics(["a.py"], ["fault.py"], event_budget=4)
    treatment = localization_metrics(["fault.py"], ["fault.py"], event_budget=4)
    rows = paired_localization_rows([reset], [treatment])
    assert len(rows) == 1
    assert rows[0]["reset_censored"] is True
    assert rows[0]["treatment_censored"] is False
    assert rows[0]["delta_I_loc_bits"] > 0


def test_gold_or_reference_patch_is_not_an_input_to_metric():
    # The function signature deliberately requires only inspection trace + planted
    # causal fault files; no repair patch appears in the scoring API.
    row = localization_metrics(["src/fault.py"], ["src/fault.py"])
    assert row.event_rank == 1


def test_paths_are_repository_relative_and_canonical():
    assert canonical_repo_path("./src\\module.py") == "src/module.py"
    with pytest.raises(ValueError):
        canonical_repo_path("../secret.py")
    with pytest.raises(ValueError):
        canonical_repo_path("/tmp/secret.py")


def test_duplicate_fault_files_are_rejected():
    with pytest.raises(ValueError, match="duplicates"):
        localization_metrics(["a.py"], ["a.py", "./a.py"])


def test_event_budget_cannot_be_smaller_than_observed_trace():
    with pytest.raises(ValueError, match="cannot be smaller"):
        localization_metrics(["a.py", "b.py"], ["b.py"], event_budget=1)
