"""Guards on the RV-377-180 B6 adjudicator.

Pins the three false-green paths found while validating the scorer against the
seed-0 receipts. Each of these returned a pass (or a scored verdict) on evidence
that could not support one, which is the failure mode a checker must never have.
"""
import json
import os

import pytest

from gmi_microscope import b6_adjudicate as A


def _receipt(tmp, pair, arm, seed, b_morph, final_best, klass="KVSTORE",
             b_dense=None, final_best_dense=None, origin=("seed", 1)):
    d = {
        "first_admissible": {"found": b_morph is not None, "B_morph": b_morph,
                             "carrier_atrophied": klass, "origin": list(origin)},
        "first_dense_admissible": {"found": b_dense is not None, "B_morph": b_dense},
        "final_best_capability_standard": final_best,
        "final_best_by_carrier": {"DENSE": final_best_dense},
    }
    p = os.path.join(tmp, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_t.json")
    json.dump(d, open(p, "w"))
    return p


@pytest.fixture
def res(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "RES", str(tmp_path))
    return str(tmp_path)


def test_refuses_a_seed_set_the_freeze_does_not_quantify_over(res):
    """The freeze says '>= 2 of 3 seeds'. One seed cannot evaluate that."""
    with pytest.raises(SystemExit):
        A.adjudicate("t", seeds=(0,))


def test_partial_run_never_emits_a_scored_verdict(res):
    """A partial set printed FAILED for a quantifier it cannot evaluate."""
    _receipt(res, "SAME", "CONTINUED", 0, 278, 0.9062)
    _receipt(res, "SAME", "RESET", 0, 11283, 0.8958)
    _receipt(res, "SAME", "TWIN", 0, 560, 0.9062)
    out = A.adjudicate("t", seeds=(0,), validation_only=True)
    verdicts = {k: v["verdict"] for k, v in out["predictions"].items()}
    assert all(v == "NOT_SCORED__PARTIAL_SEED_SET" for v in verdicts.values()), verdicts
    assert out["terminal"] == "VALIDATION_ONLY__NOT_AN_ADJUDICATION"
    # the underlying booleans must still be right
    assert out["predictions"]["D1b"]["per_seed"]["0"] is True


def test_d4_rollup_is_not_green_when_no_pair_was_scored(res):
    """D4 rolled up to HELD while every pair was unscored."""
    _receipt(res, "SAME", "CONTINUED", 0, 278, 0.9062)
    _receipt(res, "SAME", "RESET", 0, 11283, 0.8958)
    out = A.adjudicate("t", seeds=(0,), validation_only=True)
    assert out["predictions"]["D4"]["verdict"] != "HELD"


def test_d2d_pass_on_absent_data_is_labelled_vacuous(res):
    """The freeze's 'or UNDETERMINED' wording passes D2d with no determined seed.
    That is a pass satisfied by absence of evidence and must say so."""
    for s in (0, 1, 2):
        _receipt(res, "SAME", "CONTINUED", s, 278, 0.9062)
        _receipt(res, "SAME", "RESET", s, 11283, 0.8958)
        _receipt(res, "SAME", "TWIN", s, 560, 0.9062)
        _receipt(res, "CROSS", "CONTINUED", s, 142, 0.9115, klass="TABLE", final_best_dense=0.79)
        _receipt(res, "CROSS", "RESET", s, 596, 0.9115, final_best_dense=0.91)
        _receipt(res, "CROSS", "TWIN", s, 7906, 0.974)
        _receipt(res, "DISJ", "CONTINUED", s, 400, 0.90)
        _receipt(res, "DISJ", "TWIN", s, 420, 0.90)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["predictions"]["D2d"]["verdict"] == "HELD_VACUOUSLY__NO_DETERMINED_SEED"


def test_a_vacuous_d2d_cannot_rescue_a_failed_load_bearing_d1b(res):
    """PARENT_SUFFICIENT_OOPS must be reachable: if the residual D1b fails, a D2d
    that passed only because nothing was determined must not buy the positive."""
    for s in (0, 1, 2):
        # TWIN beats CONTINUED -> D1b fails on every seed
        _receipt(res, "SAME", "CONTINUED", s, 900, 0.9062)
        _receipt(res, "SAME", "RESET", s, 11283, 0.8958)
        _receipt(res, "SAME", "TWIN", s, 560, 0.9062)
        _receipt(res, "CROSS", "CONTINUED", s, 142, 0.9115, klass="TABLE", final_best_dense=0.79)
        _receipt(res, "CROSS", "RESET", s, 596, 0.9115, final_best_dense=0.91)
        _receipt(res, "CROSS", "TWIN", s, 7906, 0.974)
        _receipt(res, "DISJ", "CONTINUED", s, 400, 0.90)
        _receipt(res, "DISJ", "TWIN", s, 420, 0.90)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["predictions"]["D1b"]["verdict"] == "FAILED"
    assert out["terminal"] == "PARENT_SUFFICIENT_OOPS"


def test_missing_units_block_any_adjudication(res):
    _receipt(res, "SAME", "CONTINUED", 0, 278, 0.9062)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["terminal"] == "ADJUDICATION_INCOMPLETE__UNITS_MISSING"
    assert out["complete"] is False

def test_a_missing_unit_is_never_a_refutation(res):
    """A '>= 2 of 3' prediction with one hit and two unrun seeds must read PENDING,
    not FAILED: the missing units could still satisfy it."""
    _receipt(res, "SAME", "CONTINUED", 0, 278, 0.9062)
    _receipt(res, "SAME", "RESET", 0, 11283, 0.8958)
    _receipt(res, "SAME", "TWIN", 0, 560, 0.9062)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["predictions"]["D1a"]["verdict"] == "PENDING_MORE_UNITS"
    assert out["predictions"]["D1b"]["verdict"] == "PENDING_MORE_UNITS"
    assert out["terminal"] == "ADJUDICATION_INCOMPLETE__UNITS_MISSING"


def test_two_hits_settle_a_two_of_three_prediction_early(res):
    """The sound early decision: two hits satisfy '>= 2/3' whatever the third seed does."""
    for s in (0, 1):
        _receipt(res, "SAME", "CONTINUED", s, 278, 0.9062)
        _receipt(res, "SAME", "RESET", s, 11283, 0.8958)
        _receipt(res, "SAME", "TWIN", s, 560, 0.9062)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["predictions"]["D1b"]["verdict"] == "HELD"


def test_z2_fails_as_soon_as_one_cold_arm_reaches_the_coefficient_cell(res):
    """F-Z2: a single cold-start recovery settles Z2 FAILED with seeds still unrun,
    because Z2 predicts 0 of 3."""
    _receipt(res, "SAME", "RESET", 0, 11283, 0.8958, b_dense=9000)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    z = out["Z_registration"]["Z2"]
    assert z["verdict"] == "FAILED", z


def test_z_terminal_is_pending_while_units_are_missing(res):
    _receipt(res, "SAME", "CONTINUED", 0, 278, 0.9062, b_dense=38243)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["Z_registration"]["terminal"] == "Z_UNDETERMINED__UNITS_MISSING"


def test_duplicate_computation_is_separated_from_the_documented_shared_baseline(res, monkeypatch):
    """CROSS|TWIN and DISJ|TWIN can be the same computation in two files (the twin
    carrier-match saturates), while CROSS|RESET and DISJ|RESET are one file read twice.
    The detector must not report the documented alias as a redundancy."""
    import json as _json

    def seeded(pair, arm, seed, fps, b_morph):
        d = {
            "first_admissible": {"found": True, "B_morph": b_morph, "carrier_atrophied": "TABLE",
                                 "origin": ["seed", 1]},
            "first_dense_admissible": {"found": False},
            "final_best_capability_standard": 0.974,
            "final_best_by_carrier": {"DENSE": 0.9},
            "target_ecology": "E_sym5", "source_ecology": "E_x",
            "seeding": {"seed_fingerprints": fps},
        }
        _json.dump(d, open(os.path.join(res, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_t.json"), "w"))

    same_pop = ["aa", "bb", "cc"]
    seeded("CROSS", "TWIN", 0, same_pop, 7906)
    seeded("DISJ", "TWIN", 0, same_pop, 7906)
    seeded("CROSS", "RESET", 0, ["zz"], 596)      # DISJ|RESET aliases this same file
    out = A.adjudicate("t", seeds=(0, 1, 2))
    de = out["duplicate_experiments"]
    assert "CROSS|TWIN|S0 & DISJ|TWIN|S0" in de["duplicate_computation"], de
    assert "CROSS|RESET|S0 & DISJ|RESET|S0" in de["shared_baseline_by_design"], de
    assert de["n_undisclosed_groups"] == 1
    assert de["n_distinct_experiments"] == de["n_receipt_files"] - 1


def test_detector_is_silent_when_every_arm_is_distinct(res):
    """The no-alarm case: a checker that fires on clean data gets switched off."""
    for i, (pair, arm) in enumerate((("SAME", "CONTINUED"), ("SAME", "RESET"), ("SAME", "TWIN"))):
        _receipt(res, pair, arm, 0, 100 + i, 0.9)
    out = A.adjudicate("t", seeds=(0, 1, 2))
    assert out["duplicate_experiments"]["n_undisclosed_groups"] == 0


def _dense_receipt(tmp, pair, arm, seed, root_carrier, root_idx=2, fps=("a", "b", "c")):
    import json as _json
    carriers = ["TABLE", "PROGRAM", "KVSTORE", "DENSE"]
    carriers[root_idx] = root_carrier
    d = {"first_admissible": {"found": True, "B_morph": 100, "carrier_atrophied": "TABLE",
                              "origin": ["seed", 1]},
         "first_dense_admissible": {"found": True, "B_morph": 900, "origin": ["seed", root_idx]},
         "final_best_capability_standard": 0.9, "final_best_by_carrier": {"DENSE": 0.9},
         "target_ecology": "E_t", "source_ecology": "E_s",
         "seeding": {"seed_fingerprints": list(fps), "seed_carriers_raw": carriers}}
    _json.dump(d, open(os.path.join(tmp, f"STAGE_B6_DEV_{pair}_{arm}_S{seed}_t.json"), "w"))


def test_z5_fails_when_a_coefficient_machine_is_rooted_in_a_coefficient_seed(res):
    _dense_receipt(res, "SAME", "CONTINUED", 0, "DENSE")
    out = A.adjudicate("t", seeds=(0, 1, 2))
    z5 = out["Z_registration"]["Z5"]
    assert z5["verdict"] == "FAILED", z5
    assert z5["n_rooted_in_DENSE"] == 1


def test_z5_counts_a_duplicated_arm_once(res):
    """CROSS|TWIN and DISJ|TWIN are one experiment; Z5 must not count it twice."""
    _dense_receipt(res, "CROSS", "TWIN", 0, "TABLE")
    _dense_receipt(res, "DISJ", "TWIN", 0, "TABLE")
    out = A.adjudicate("t", seeds=(0, 1, 2))
    z5 = out["Z_registration"]["Z5"]
    assert z5["n_distinct_recoveries"] == 1, z5
