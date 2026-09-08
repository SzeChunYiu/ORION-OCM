"""Authored dependency donors; no registered generator or held-out inputs."""
import copy,json
import pytest
from unary_contract import InputRefused
from unary_solver import RegionSolver,solve
from unary_verify import verify_result
from learning_test_support import pred,s,task
from unary_rule_acquire import acquire

def donors():
    a=task([s("every","A","B"),s("no","A","B"),s("some","C","C")],s("no","A","C"))
    b=task([s("every","A","B"),s("no","B","C"),s("some","A","A")],s("no","A","C"))
    return [{"task":t,"result":solve(t)} for t in (a,b)]

def learned():
    r=acquire(donors(),dependency=True)
    assert r["terminal"]=="RULES_ACQUIRED"
    return r,next(x for x in r["rules"] if "dependency" in x["supports"][0])

def test_distinct_flat_fragments_compile_one_checked_dependency():
    old=acquire(donors(),dependency=False);new,item=learned()
    assert old["terminal"]=="NO_REPEATED_RULE" and not old["rules"]
    assert len({x["rule_id"] for x in old["attempts"] if x["accepted"]})==2
    assert len(item["supports"])==2
    assert len({x["semantic_key"] for x in item["supports"]})==2
    assert item["schema_certificate"]["accepted"]
    assert len(item["rule"]["parameters"])==3
    by_episode={x["episode"]:x["dependency"] for x in item["supports"]}
    assert by_episode[0]["binding"]!=by_episode[1]["binding"]
    assert by_episode[0]["residuals"][0]==by_episode[0]["residuals"][1]
    assert by_episode[1]["residuals"][0]!=by_episode[1]["residuals"][1]
    assert all(x["pivot"]==pred("B") and x["order"]==[0,1] for x in by_episode.values())
    assert new["counters"]["dependency_steps"]>0
    assert new["counters"]["dependency_role_splits"]>0

@pytest.mark.parametrize("alias",[False,True])
def test_singletons_and_alpha_duplicates_do_not_supply_second_support(alias):
    rows=donors()[:1]
    if alias:
        raw=json.dumps(rows[0]["task"])
        for a,b in zip("ABC","XYZ"):raw=raw.replace('"'+a+'"','"'+b+'"')
        t=json.loads(raw);rows.append({"task":t,"result":solve(t)})
    assert not acquire(rows,dependency=True)["rules"]

def test_redundant_primitive_does_not_become_composite():
    t=task([s("every","A","B"),s("no","B","C"),s("some","A","A")],s("every","A","B"))
    assert not acquire([{"task":t,"result":solve(t)}],dependency=True)["rules"]

@pytest.mark.parametrize("change",["pivot","cover","target","binding"])
def test_independent_support_rejects_false_linkage(change):
    from unary_rule_dependency_check import verify_support
    _,item=learned();support=copy.deepcopy(item["supports"][0]);row=donors()[support["episode"]]
    verify_support(row["task"],row["result"],support,item["rule"],{})
    if change=="pivot":support["dependency"]["pivot"]=pred("C")
    elif change=="cover":support["cover"]=[0,2]
    elif change=="target":support["dependency"]["target"]=[pred("B")]
    else:support["dependency"]["binding"]["P0"]=pred("C")
    with pytest.raises(InputRefused):verify_support(row["task"],row["result"],support,item["rule"],{})

def application():
    from unary_rule_apply import apply_rule
    _,item=learned()
    t=task([s("every","A","B"),s("no","A","B"),s("some","C","C"),s("every","C","C")],s("no","A","C"))
    engine=RegionSolver(t["predicates"]);prepared=engine.prepare(t)
    app=apply_rule(item["rule"],t,engine,prepared)
    return t,item,app

def test_actual_normalized_application_and_independent_answer_use():
    from unary_method_verify_use import verify_use
    t,item,app=application()
    assert app["terminal"]=="PROPOSED" and app["dependency"]
    assert verify_result(t,app["result"])
    use={"method_id":"authored","rule_id":item["rule"]["rule_id"],"binding":app["binding"],
         "cover":app["cover"],"recipes_applied":1,"replaced_branch":"no","dependency":app["dependency"]}
    lookup=lambda _:{"eligible":True,"envelope":{"rule":item["rule"]}}
    work={};verify_use(t,use,lookup,work=work)
    assert work["dependency_point_checks"]>0
    broken=copy.deepcopy(use);broken["dependency"]["target"]=[pred("B")]
    with pytest.raises(InputRefused):verify_use(t,broken,lookup,work={})
    with pytest.raises(InputRefused):verify_use(t,use,lambda _:{"eligible":False,"envelope":{"rule":item["rule"]}},work={})

def test_clause_normalization_is_exact_and_preserves_polarity():
    from unary_rule_clauses import clause
    w={};a=clause(s("no","A","B"),w);b=clause(s("no","B","A"),w)
    assert a==b and a!=clause(s("every","A","B"),w)
    assert clause(s("no","A","A"),w)==[["not",pred("A")]]
    assert w["clause_expression_nodes"]>0

@pytest.mark.parametrize("kind,status",[("every","ENTAILED"),("some","CONTRADICTED"),("not_every","CONTRADICTED")])
def test_normalized_query_polarities_keep_checked_branch(kind,status):
    from unary_rule_apply import apply_rule
    _,item=learned()
    t=task([s("every","A","B"),s("no","A","B"),s("some","C","C")],s(kind,"A","C"))
    engine=RegionSolver(t["predicates"]);p=engine.prepare(t)
    app=apply_rule(item["rule"],t,engine,p)
    assert app["terminal"]=="PROPOSED" and app["result"]["status"]==status
    assert verify_result(t,app["result"])
