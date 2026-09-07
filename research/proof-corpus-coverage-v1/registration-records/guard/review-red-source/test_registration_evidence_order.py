import copy
import pytest
from registration_evidence_fixture import COMMIT, TREE, fixture
from registration_evidence_order import verify_order


def test_complete_order_and_four_assignments_no_alarm():
    assert verify_order(*fixture(), 5, COMMIT, TREE) == {"population": 5, "assignments": 4, "continuation_cursor": 4}


@pytest.mark.parametrize("mutate", [
    lambda p,a,r: p["rows"].reverse(),
    lambda p,a,r: p["rows"].pop(),
    lambda p,a,r: p["rows"].__setitem__(1, copy.deepcopy(p["rows"][0])),
    lambda p,a,r: p["rows"][0].update(assignment_digest="f"*64),
    lambda p,a,r: p.update(commit="9"*40),
    lambda p,a,r: p.update(tree="9"*40),
    lambda p,a,r: a.update(continuation_cursor=True),
    lambda p,a,r: a["rows"][0].update(assignment_rank=False),
    lambda p,a,r: a["rows"][0]["stages"][0].update(state="PASSED"),
    lambda p,a,r: a["rows"][0]["wrapper"].update(oid="a"*40),
    lambda p,a,r: a["population"].update(sha256="f"*64),
    lambda p,a,r: r.update(semantic_checks_reached=False),
    lambda p,a,r: r.update(wrapper_source_parsed=True),
])
def test_registered_order_tamper_refuses(mutate):
    pop, ass, reg = fixture(); mutate(pop, ass, reg)
    with pytest.raises(ValueError): verify_order(pop, ass, reg, 5, COMMIT, TREE)
