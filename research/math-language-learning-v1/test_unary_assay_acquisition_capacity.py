"""Fixed manually authored A32/16 capacity recipe, frozen before either launch."""
import copy,json,time
import pytest
from unary_test_support import statement as s,task,pred
from unary_contract import negate
from unary_rule_identity import canonical_rule
from unary_method_selection import contract
from unary_method_process import launch
from unary_method_profile import observe
from assay_test_support import authored_only

def capacity():
    cores=[
      ([s("every","A","B"),s("every","B","C")],s("every","A","C"),
       [s("some","A","A"),s("some","B","B"),s("some","C","C"),s("not_every","B","A")]),
      ([s("every","A","B"),s("no","B","C")],s("no","A","C"),
       [s("some","A","A"),s("some","B","B"),s("some","C","C"),s("not_every","B","A")]),
      ([s("every","A","B"),s("no","A","B")],s("no","A","A"),
       [s("some","C","C"),s("not_every","C","B"),s("no","C","C"),s("every","C","B")]),
      ([s("every","A","B"),s("no","A","B")],s("every","A","C"),
       [s("some","B","B"),s("some","C","C"),s("not_every","C","B"),s("not_every","B","C")])]
    training=[];development=[];expected=[]
    for premises,query,contexts in cores:
        expected.append(canonical_rule(task(premises,query),{})["rule_id"])
        for i,context in enumerate(contexts):
            for q in (query,negate(query)):
                training.append(task([*premises,context],q))
                if i<2:development.append(task([*premises,context,s("every","C",["or",pred("C"),pred("C")])],q))
    return training,development,expected

@pytest.mark.parametrize("arm",["conventional","ocm"])
def test_authored_varied_a32_16_capacity(tmp_path,arm):
    import unary_method_plain as D
    training,development,expected=capacity()
    request={"store":str(tmp_path/"store"),"training":training,"development":development,
             "contract":contract(32,16,authored=True)}
    (tmp_path/"AUTHORED-INPUTS.json").write_bytes(D.raw({"request":request,"expected_core_ids":expected}))
    deadline=time.monotonic()+120
    p=launch(tmp_path/"A","acquire_selected",request,profile=observe(),arm=arm,deadline=deadline,timeout=120)
    assert p["reaped"] and p["group_absent"]
    assert p["terminal"]=="COMPLETED",p
    value=json.loads((tmp_path/"A/result.json").read_bytes());r=value["outcome"]
    rules=r["acquisition"]["rules"]
    assert len(r["training"])==32 and len(r["baseline"])==16 and len(r["trials"])==16*len(rules)
    assert set(expected)<=set(x["rule"]["rule_id"] for x in rules)
    assert all(len({s["semantic_key"] for s in x["supports"]})>=2 for x in rules)
    assert all(x["result"]["premises"]["kind"]=="model" for x in r["training"])
