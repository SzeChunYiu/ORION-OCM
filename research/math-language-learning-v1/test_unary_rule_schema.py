"""Independent universal schema authority and strict transport controls."""
import copy
import pytest
from unary_contract import InputRefused
from learning_test_support import api, chain, rule, s

def test_universal_schema_all_assignments_and_real_work():
    checked=api("unary_rule_check").check_rule(rule())
    assert checked["accepted"] and checked["truth_table"]==[True]*8
    assert checked["counterexample"] is None
    assert checked["counters"]["schema_assignments"]==8
    assert checked["counters"]["expression_nodes"]>8

def test_invalid_schema_has_actual_counterexample():
    p,_=chain()
    r=api("unary_rule_contract").seal_rule(["P0","P1","P2"],p,s("every","P0","P2"))
    checked=api("unary_rule_check").check_rule(r)
    assert not checked["accepted"]
    assert checked["counterexample"] is not None and False in checked["truth_table"]

@pytest.mark.parametrize("change",["id","body","existential","extra","subclass","parameters","recipe"])
def test_tampered_or_nondata_rule_refused(change):
    r=copy.deepcopy(rule())
    class String(str):
        def __eq__(self,other):raise AssertionError("comparison hook executed")
        __hash__=str.__hash__
    if change=="id":r["rule_id"]="0"*64
    elif change=="body":r["conclusion"]["kind"]="every"
    elif change=="existential":r["premises"][0]["kind"]="some"
    elif change=="extra":r["code"]="exec"
    elif change=="subclass":r["schema"]=String(r["schema"])
    elif change=="parameters":r["parameters"]=["P1","P2","P3"]
    else:r["recipe"]="other"
    with pytest.raises(InputRefused):api("unary_rule_check").check_rule(r)

def test_existential_cannot_be_promoted_to_universal_schema():
    p,q=chain();p[0]["kind"]="some"
    with pytest.raises(InputRefused):api("unary_rule_contract").seal_rule(["P0","P1","P2"],p,q)

def test_schema_checker_does_not_call_parent_solver(monkeypatch):
    import unary_solver
    def forbidden(*a,**k):raise AssertionError("optimized solve used")
    monkeypatch.setattr(unary_solver,"solve",forbidden)
    monkeypatch.setattr(unary_solver.RegionSolver,"solve",forbidden)
    assert api("unary_rule_check").check_rule(rule())["accepted"]

@pytest.mark.parametrize("conclusion",["tautology","one_premise","padded"])
def test_primitives_and_irrelevant_padding_are_rejected(conclusion):
    m=api("unary_rule_contract")
    if conclusion=="tautology":
        ps=[s("every","P0","P1"),s("no","P1","P2")];q=s("every","P0","P0")
    elif conclusion=="one_premise":
        ps=[s("every","P0","P1"),s("no","P1","P2")];q=s("every","P0","P1")
    else:
        ps,q=chain();ps.append(s("every","P2","P2"))
    checked=api("unary_rule_check").check_rule(m.seal_rule(["P0","P1","P2"],ps,q))
    assert not checked["accepted"] and checked["reason"]=="NON_ESSENTIAL_PREMISE"
    assert all(checked["truth_table"]) and None in checked["essentiality_counterexamples"]
