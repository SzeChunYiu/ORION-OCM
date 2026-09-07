"""Actual per-call and cumulative costs must not replay historical preparation."""
from unary_solver import RegionSolver,solve
from unary_verify import verify_result
from learning_test_support import api,rule,s,task,training

def add(*rows):
    return {k:sum(row[k] for row in rows) for k in rows[0]}

def test_preparation_is_charged_once_across_two_completions():
    t=training()["task"];e=RegionSolver(t["predicates"]);p=e.prepare(t)
    preparation=dict(e.counters);binding=dict(e.binding_work)
    first=e.complete(p);mid=dict(e.binding_work);second=e.complete(p)
    assert first["counters"]["constraints_checked"]==2
    assert second["counters"]["constraints_checked"]==2
    assert e.counters==add(preparation,first["counters"],second["counters"])
    assert mid["bytes_hashed"]>binding["bytes_hashed"]
    assert e.binding_work["bytes_hashed"]>mid["bytes_hashed"]
    assert e.binding_work["decode_input_bytes"]>mid["decode_input_bytes"]
    assert e.binding_work["task_validation_calls"]>mid["task_validation_calls"]
    assert verify_result(t,first) and verify_result(t,second)
    cold=RegionSolver(t["predicates"]);cp=cold.prepare(t);cold.complete(cp)
    assert solve(t)["counters"]==cold.counters

def test_failed_match_then_fallback_has_one_prep_and_actual_binding_work():
    t=task([s("every","A","B"),s("some","B","C")],s("no","A","C"))
    e=RegionSolver(t["predicates"]);p=e.prepare(t);initial=dict(e.counters)
    before=dict(e.binding_work)
    miss=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert miss["terminal"]=="NO_MATCH" and e.counters==initial
    assert e.binding_work["bytes_hashed"]>before["bytes_hashed"]
    fallback=e.complete(p)
    assert fallback["counters"]["constraints_checked"]==2
    assert e.counters==add(initial,fallback["counters"]) and verify_result(t,fallback)

def test_proposal_assembly_does_not_recharge_parent_semantics():
    t=training()["task"];e=RegionSolver(t["predicates"]);p=e.prepare(t)
    initial=dict(e.counters)
    proposal=api("unary_rule_apply").apply_rule(rule(),t,e,p)
    assert proposal["terminal"]=="PROPOSED"
    assert e.counters==initial
    assert all(n==0 for n in proposal["result"]["counters"].values())
    assert verify_result(t,proposal["result"])
