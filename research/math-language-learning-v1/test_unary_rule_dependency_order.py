"""Premise order preserves observed donor roles; no registered inputs."""
from itertools import permutations
import copy
import pytest
from unary_solver import solve
from unary_rule_acquire import acquire
from unary_rule_dependency_check import verify_support
from test_unary_rule_dependency import donors

@pytest.mark.parametrize("order",list(permutations(range(3))))
def test_observed_dependency_survives_each_premise_order(order):
    clean=donors();baseline=acquire(clean,dependency=True)
    expected=next(x for x in baseline["rules"] if "dependency" in x["supports"][0])
    rows=[]
    for row in clean:
        task=copy.deepcopy(row["task"])
        task["premises"]=[task["premises"][i] for i in order]
        rows.append({"task":task,"result":solve(task)})
    result=acquire(rows,dependency=True)
    item=next(x for x in result["rules"] if "dependency" in x["supports"][0])
    assert item["rule"]==expected["rule"]
    assert {s["semantic_key"] for s in item["supports"]}=={s["semantic_key"] for s in expected["supports"]}
    for support in item["supports"]:
        row=rows[support["episode"]]
        assert support["dependency"]["order"]==[order.index(0),order.index(1)]
        assert verify_support(row["task"],row["result"],support,item["rule"],{})["accepted"]
    assert result["counters"]["dependency_steps"]==baseline["counters"]["dependency_steps"]
    assert result["counters"]["dependency_binding_candidates"]==(
        result["counters"]["dependency_steps"]+result["counters"].get("dependency_role_binding_rejections",0))
    if order.index(1)<order.index(0):
        assert result["counters"]["dependency_role_binding_rejections"]>0
        assert result["counters"]["clause_binding_combinations"]>baseline["counters"]["clause_binding_combinations"]

def test_nonrole_checker_refusal_is_not_swallowed(monkeypatch):
    import unary_rule_dependency as D
    from unary_contract import InputRefused
    def refuse(*args):raise InputRefused("DEPENDENCY_WEAKENING")
    monkeypatch.setattr(D,"verify_support",refuse)
    with pytest.raises(InputRefused,match="^DEPENDENCY_WEAKENING$"):
        acquire(donors(),dependency=True)
