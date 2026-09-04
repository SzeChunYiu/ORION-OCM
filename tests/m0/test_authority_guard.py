import pytest
from ocm.epistemics.authority import ANCHORS, AuthorityViolation, guard_text

def test_parent_sufficient_upgrade_mutation_is_rejected():
 a=next(x for x in ANCHORS if "M2_SOLVE" in x.path); original="registered terminal PARENT_SUFFICIENT"; guard_text(a,original)
 with pytest.raises(AuthorityViolation): guard_text(a,original.replace("PARENT_SUFFICIENT","KSO_SUPERIOR"))

def test_language_alpha_is_not_laundered_from_l0():
 a=next(x for x in ANCHORS if x.path.endswith("kso_language_v0.py")); text='LANGUAGE_KSO_L0_CONTROLLED_GREEN\n"open_domain_language": False\n'; guard_text(a,text)
 with pytest.raises(AuthorityViolation): guard_text(a,text+"LANGUAGE_KSO_ALPHA\n")
