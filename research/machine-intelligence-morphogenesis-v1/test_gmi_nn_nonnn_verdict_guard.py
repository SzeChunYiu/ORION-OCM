"""RV-377-210 audit guard: absence of evidence is unresolved, not proved infeasibility
(CERTIFICATE_INPUT_CORRECTION_20260913.md, upstream PR #513)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gmi_microscope.nn_nonnn_packet import verdict  # noqa: E402


def test_empty_support_with_complete_evidence_is_infeasible():
    assert verdict(set(), True) == "INFEASIBLE_AT_REGISTERED_SCOPE"


def test_empty_support_with_incomplete_evidence_abstains():
    assert verdict(set(), False) == "UNRESOLVED__INCOMPLETE_EVIDENCE"


def test_canonical_verdicts_unchanged():
    assert verdict({"NEURAL"}) == "DERIVED_NEURAL"
    assert verdict({"NON_NEURAL"}) == "DERIVED_NON_NEURAL"
    assert verdict({"HYBRID"}) == "DERIVED_HYBRID"
    assert verdict({"NEURAL", "NON_NEURAL"}) == "FAMILY_COEXISTENCE"
