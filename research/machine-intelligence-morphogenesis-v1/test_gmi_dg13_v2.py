"""RV-377-150 -- DG-13 V2 instruments: E_parity_v2 is parity, E_parity is untouched, V2 scoring is leak-free."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gmi_microscope import ecology, smooth  # noqa: E402


def test_e_parity_v1_is_still_the_historical_identity_table():
    assert ecology.REGISTRY["E_parity"]["table"] == list(range(16))
    assert "deprecated_reason" in ecology.REGISTRY["E_parity"]


def test_e_parity_v2_is_true_parity():
    assert ecology.REGISTRY["E_parity_v2"]["criterion"] == "all"   # the unseen split is parity-degenerate
    assert all(bin(x).count("1") % 2 == 0 for x in smooth.TRAIN) and all(bin(x).count("1") % 2 == 1 for x in smooth.UNSEEN)
    t = ecology.target_of(ecology.REGISTRY["E_parity_v2"])
    for x in smooth.ALL_X:
        assert t[x] == (smooth.FX_ONE if bin(x).count("1") % 2 else 0)


def test_v2_intervention_scores_only_never_revealed_inputs():
    J = ecology.INTERVENTIONS["extra_unseen_feedback_v2"]
    assert J["extra"] is True and J["score"] == "unrevealed"
    fed = set(smooth.UNSEEN[:4]); scored = set(smooth.UNSEEN[4:])
    assert fed.isdisjoint(scored) and fed | scored == set(smooth.UNSEEN)
    assert ecology.INTERVENTIONS["extra_unseen_feedback"] == {"extra": True}   # V1 byte-identical
    assert len(ecology.INTERVENTION_FAMILY_V2) == 6 and "extra_unseen_feedback" not in ecology.INTERVENTION_FAMILY_V2
