"""Use a mined method on a larger Boolean context without re-solving its query."""
import pytest
from unary_contract import InputRefused
from unary_solver import RegionSolver
from unary_verify import verify_result
from learning_test_support import api, training, pred, s, task, rule

def test_mined_schema_substitution_constructs_verified_certificate(monkeypatch):
    rules=api("unary_rule_acquire").acquire([training("B"),training("C")])["rules"]
    left=["or",pred("X"),pred("W")]
    t=task([s("every",left,"Y"),s("no","Y","Z"),s("some","Y","Y")],s("some",left,"Z"))
    engine=RegionSolver(t["predicates"]);p=engine.prepare(t)
    def forbidden(*a,**k):raise AssertionError("query was solved")
    monkeypatch.setattr(engine,"solve",forbidden);monkeypatch.setattr(engine,"complete",forbidden)
    proposals=[api("unary_rule_apply").apply_rule(x["rule"],t,engine,p) for x in rules]
    hits=[x for x in proposals if x["terminal"]=="PROPOSED"]
    assert hits
    for hit in hits:
        assert hit["cover"]==[0,1] and verify_result(t,hit["result"])
        assert hit["result"]["status"]=="CONTRADICTED"
        assert hit["counters"]["recipes_applied"]==1
        assert hit["counters"]["matching_nodes"]>0 and hit["counters"]["key_nodes"]>0

def test_missing_used_support_does_not_apply_rule():
    t=task([s("every","A","B"),s("some","B","C")],s("no","A","C"))
    e=RegionSolver(t["predicates"]);p=e.prepare(t)
    r=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert r["terminal"]=="NO_MATCH" and r["counters"]["recipes_applied"]==0

def test_inconsistent_base_is_not_explosive_method_use():
    t=task([s("some","A","B"),s("no","A","B")],s("no","A","C"))
    e=RegionSolver(t["predicates"]);p=e.prepare(t)
    r=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert r["terminal"]=="INCONSISTENT_BASE" and r["counters"]["recipes_applied"]==0

def test_changed_task_cannot_reuse_prepared_binding():
    t=training()["task"];e=RegionSolver(t["predicates"]);p=e.prepare(t)
    t["premises"].pop()
    with pytest.raises(InputRefused):api("unary_rule_apply").apply_rule(rule(),t,e,p)

def test_old_binding_removed_but_legitimate_alternate_match_remains():
    t=task([s("every","A","B"),s("no","B","C"),s("every","A","D"),
            s("no","D","C"),s("some","B","B")],s("no","A","C"))
    e=RegionSolver(t["predicates"]);old=e.prepare(t)
    first=api("unary_rule_apply").apply_rule(rule(),t,e,old)
    assert first["cover"]==[0,1] and verify_result(t,first["result"])
    t["premises"].pop(0)
    with pytest.raises(InputRefused):api("unary_rule_apply").apply_rule(rule(),t,e,old)
    fresh=e.prepare(t);second=api("unary_rule_apply").apply_rule(rule(),t,e,fresh)
    assert second["cover"]==[1,2] and verify_result(t,second["result"])

@pytest.mark.parametrize("change",["repeated_parameter","polarity"])
def test_structural_binding_never_confuses_names_or_polarity(change):
    t=task([s("every","A","B"),s("no","D","C"),s("some","B","B")],s("no","A","C"))
    if change=="polarity":
        t["premises"][1]=s("every","B","C");t["predicates"].remove("D")
    e=RegionSolver(t["predicates"]);p=e.prepare(t)
    hit=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert hit["terminal"]=="NO_MATCH" and hit["counters"]["recipes_applied"]==0

def test_assembled_certificate_tampering_is_not_accepted():
    t=training()["task"];e=RegionSolver(t["predicates"]);p=e.prepare(t)
    r=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert verify_result(t,r["result"])
    r["result"]["query_false"]["cover"]=[0]
    assert not verify_result(t,r["result"])
