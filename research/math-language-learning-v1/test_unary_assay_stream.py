"""Hash/order/rotation controls using only authored choices and non-study tags."""
from assay_test_support import authored_only
import copy
import pytest
from unary_contract import InputRefused
from assay_test_support import api

def test_nonstudy_known_sha_choice_and_actual_work():
    m=api("unary_assay_stream");work={}
    r=m.choice("authored-sha-control-v1",1,"train",2,"query/left",[0,1,2],work=work)
    assert r["canonical_input"]=='["authored-sha-control-v1",1,"train",2,"query/left"]'
    assert r["sha256"]=="4a03253b05c4f12347d5ce1d4e1ae57b05a5b6f0c771c60f2229fa6452f7ad0f"
    assert r["index"]==0 and work["bytes_hashed"]==52
    assert m.MASTER=="ocm-unary-causal-v1" and m.SIZES==(32,16,32)
    assert m.MAX_ATTEMPTS==65536 and m.EPISODES==4

def test_expression_order_and_detached_choices():
    m=api("unary_assay_stream");a=m.expressions("train");b=m.expressions("development")
    assert len(a)==3 and len(b)==24 and b[:3]==a
    assert b[3]==["not",["pred","P0"]]
    assert b[6]==["and",["pred","P0"],["pred","P0"]]
    assert b[14]==["and",["pred","P2"],["pred","P2"]]
    assert b[15]==["or",["pred","P0"],["pred","P0"]]
    b[0][1]="changed";assert m.expressions("final")[0]==["pred","P0"]

@pytest.mark.parametrize("slot,kind",[(0,"every"),(1,"no"),(2,"some"),(3,"not_every")])
def test_authored_field_choices_preserve_slot_rotation_and_duplicates(slot,kind):
    m=api("unary_assay_stream");seen=[]
    def choose(tag,pool):seen.append(tag);return {"index":0,"authored":True}
    r=m.build_candidate(0,"train",7,slot,choose,work={})
    assert len(r["task"]["premises"])==2 and r["task"]["premises"][0]==r["task"]["premises"][1]
    assert r["task"]["query"]["kind"]==kind
    assert seen==["premise_count",*[f"premise/{i}/{f}" for i in range(2) for f in ("kind","left","right")],"query/left","query/right"]
    assert r["attempt"]==7 and r["slot"]==slot and len(r["fields"])==9
    assert all("value" in x and "field" in x for x in r["fields"])

@pytest.mark.parametrize("index",[True,-1,999])
def test_invalid_authored_choice_is_refused(index):
    with pytest.raises(InputRefused,match="CHOICE_INDEX"):
        api("unary_assay_stream").build_candidate(0,"train",0,0,lambda *a:{"index":index},work={})

def test_engineering_guard_refuses_before_any_registered_hash():
    m=api("unary_assay_stream");work={}
    with pytest.raises(InputRefused,match="REGISTERED_STREAM_FORBIDDEN"):
        m.draw(0,"train",0,0,work=work)
    with pytest.raises(InputRefused,match="REGISTERED_STREAM_FORBIDDEN"):
        m.choice(m.MASTER,0,"train",0,"query/left",[0,1,2],work=work)
    assert work=={}
