"""Pure ranking arithmetic fixtures; these synthetic records are never admitted rules."""
import pytest
from unary_method_selection_check import decisions
from unary_contract import InputRefused

def row(q):
    return {"task":{},"observation":{"query_constraints":q,
        "parent_semantic_total":{"constraints_checked":q+3},"preparation":{"constraints_checked":3}}}

def data(benefits,matches=None):
    n=len(benefits);rules=[{"rule_id":str(i).zfill(2)} for i in range(n)]
    trials=[]
    for i,benefit in enumerate(benefits):
        t=row(20-benefit);t.update(rule_id=rules[i]["rule_id"],row=0,
            application={"counters":{"matching_nodes":0 if matches is None else matches[i]}})
        trials.append(t)
    return {"acquisition":{"rules":[{"rule":r} for r in rules]},"baseline":[row(20)],"trials":trials}

def test_positive_only_max_eight_and_rule_id_routing():
    d=data([0,-1,1,2,3,4,5,6,7,8,9,10]);r=decisions(d)
    assert [x["rule_id"] for x in r["selected"]]==["04","05","06","07","08","09","10","11"]
    assert [x["benefit"] for x in r["ranking"]]==list(range(10,-2,-1))

def test_matching_cost_then_inner_size_then_identity_ties():
    d=data([3,3,3,3],[2,1,1,1])
    d["acquisition"]["rules"][1]["rule"]["padding"]="extra authored bytes"
    r=decisions(d)
    assert [x["rule_id"] for x in r["ranking"]]==["02","03","01","00"]

@pytest.mark.parametrize("change",["missing","order","counter"])
def test_trial_integrity_errors_do_not_delete_candidates(change):
    d=data([3,2])
    if change=="missing":d["trials"].pop()
    elif change=="order":d["trials"].reverse()
    else:d["trials"][0]["application"]["counters"]["matching_nodes"]=None
    with pytest.raises(InputRefused):decisions(d)
