"""Training-only discovery, semantic support independence, and finite-world boundary."""
import copy
import json
import pytest
from unary_contract import InputRefused
from unary_solver import solve
from learning_test_support import api, training, pred, s, task

def test_two_semantically_distinct_supports_mechanically_mine_proper_rule():
    result=api("unary_rule_acquire").acquire([training("B"),training("C")])
    assert result["terminal"]=="RULES_ACQUIRED" and result["rules"]
    for item in result["rules"]:
        assert len({x["semantic_key"] for x in item["supports"]})==2
        assert len(item["rule"]["premises"])==2 and item["schema_certificate"]["accepted"]
    for key in ("subset_candidates","canonicalization_nodes","key_nodes"):
        assert result["counters"][key]>0
    assert result["counters"]["semantic_worlds"]>=255*6*2

def test_renamings_and_equivalent_context_are_one_support():
    a=training("B")
    raw=json.dumps(a["task"])
    for old,new in zip("ABC","XYZ"):raw=raw.replace('"'+old+'"','"'+new+'"')
    renamed=json.loads(raw)
    equivalent=copy.deepcopy(a["task"]);equivalent["premises"].append(s("every","A","A"))
    episodes=[a,{"task":renamed,"result":solve(renamed)},
              {"task":equivalent,"result":solve(equivalent)}]
    result=api("unary_rule_acquire").acquire(episodes)
    assert result["terminal"]=="NO_REPEATED_RULE" and not result["rules"]

def test_all_true_region_is_included_in_training_semantics():
    lhs=["and",pred("A"),pred("B")]
    possible=task([],s("some",lhs,pred("C")))
    impossible=task([],s("some",lhs,["and",pred("C"),["not",pred("C")]]))
    m=api("unary_rule_identity")
    assert m.semantic_key(possible,{})!=m.semantic_key(impossible,{})

def test_unchecked_training_result_is_refused():
    a=training();a["result"]["status"]="UNKNOWN"
    with pytest.raises(InputRefused):api("unary_rule_acquire").acquire([a])

def test_full_context_is_not_a_proper_subcover():
    t=task([s("every","A","B"),s("no","B","C")],s("no","A","C"))
    result=api("unary_rule_acquire").acquire([{"task":t,"result":solve(t)}])
    assert result["counters"].get("subset_candidates",0)==0 and not result["rules"]

def test_redundant_primitive_candidates_are_counted_and_rejected():
    t=task([s("every","A","B"),s("no","B","C"),s("every","C","C"),
            s("some","B","B")],s("every","A","B"))
    r=api("unary_rule_acquire").acquire([{"task":t,"result":solve(t)}])
    assert not r["rules"] and r["counters"]["nonessential_rejections"]>0
    assert any(x["reason"]=="NON_ESSENTIAL_PREMISE" for x in r["attempts"])
