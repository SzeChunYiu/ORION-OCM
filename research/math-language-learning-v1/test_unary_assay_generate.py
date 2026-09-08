"""Injected authored sequences exercise retention; production draw never executes."""
from assay_test_support import authored_only
import copy,json
import pytest
from assay_test_support import api,chain,other,grouped,draw,Sink

def run(tmp_path,source,targets=(("train",1),),limit=5,clock=lambda:0,deadline=10,sink=None):
    m=api("unary_assay_generate");sink=sink or Sink(tmp_path/"records.jsonl");o={};work={}
    result=m._episode(0,source,targets,limit,sink=sink,deadline=deadline,clock=clock,work=work,observation=o)
    return result,sink,o,work

def test_cross_split_semantic_duplicate_and_rejections_not_inserted(tmp_path):
    a=chain();duplicate=copy.deepcopy(a)
    duplicate["premises"][0]["left"]=["and",["pred","P0"],["pred","P0"]]
    duplicate["premises"]*=2
    def source(split,d,slot):
        return draw(a if split=="train" else duplicate if d==0 else grouped(),split,d,slot)
    r,sink,o,work=run(tmp_path,source,(("train",1),("development",1)))
    assert r["terminal"]=="GENERATED" and not r["missing"]
    assert [x["reason"] for x in sink.rows if x["kind"]=="DRAW"]==["ACCEPTED","SEMANTIC_DUPLICATE","ACCEPTED"]
    assert len(r["accepted_syntax"])==len(r["accepted_semantic"])==2
    assert work["semantic_worlds"]==3*6*255
    assert [x["row_id"] for x in r["partitions"]["development"]]==["e0/development/0"]

def test_rejected_gate_has_unreached_identities_and_complete_fields(tmp_path):
    a=chain();bad=copy.deepcopy(a);bad["premises"]=[];bad["query"]={"kind":"every","left":["pred","P0"],"right":["pred","P0"]}
    r,sink,o,work=run(tmp_path,lambda s,d,k:draw(bad if d==0 else a,s,d,k))
    row=next(x for x in sink.rows if x["kind"]=="DRAW")
    assert row["reason"]=="MISSING_PREDICATE"
    assert row["syntax_key"] is None and row["semantic_key"] is None
    assert row["candidate"]["fields"]==[{"authored_fixture":True}]
    assert json.loads(row["candidate"]["task_bytes"])==bad
    assert len(r["accepted_syntax"])==1

def test_exhaustion_keeps_original_missing_slots_and_skips_dependents(tmp_path):
    r,sink,o,work=run(tmp_path,lambda s,d,k:draw(chain(),s,d,k),(("train",2),("development",1)),limit=1)
    assert r["terminal"]=="GENERATION_CANNOT_CHECK"
    assert [(x["row_id"],x["reason"]) for x in r["missing"]]==[("e0/train/1","DRAW_LIMIT"),("e0/development/0","DEPENDENCY_UNAVAILABLE")]
    assert sum(x["kind"]=="DRAW" for x in sink.rows)==1

def test_episode_sets_start_empty_without_replaying_a_seed(tmp_path):
    m=api("unary_assay_generate");sink=Sink(tmp_path/"records.jsonl")
    for episode in (0,1):
        r=m._episode(episode,lambda s,d,k:draw(chain(),s,d,k),(("train",1),),1,
                     sink=sink,deadline=10,clock=lambda:0,work={},observation={})
        assert r["terminal"]=="GENERATED" and len(r["accepted_semantic"])==1

def test_expired_deadline_never_dispatches_candidate(tmp_path):
    def forbidden(*a):pytest.fail("candidate dispatched after deadline")
    r,sink,o,work=run(tmp_path,forbidden,clock=lambda:10)
    assert r["missing"][0]["reason"]=="DEADLINE"
    assert not any(x["kind"]=="DRAW" for x in sink.rows)

def test_deadline_crossing_semantics_retains_attempt_without_accepting(tmp_path,monkeypatch):
    m=api("unary_assay_generate");original=m.I.semantic_key;now=[0]
    def slow(t,w):
        out=original(t,w);now[0]=11;return out
    monkeypatch.setattr(m.I,"semantic_key",slow)
    r,sink,o,work=run(tmp_path,lambda s,d,k:draw(chain(),s,d,k),clock=lambda:now[0])
    assert not r["partitions"]["train"] and not r["accepted_semantic"]
    row=next(x for x in sink.rows if x["kind"]=="DRAW")
    assert row["reason"]=="DEADLINE" and row["semantic_key"] is not None
    assert work["semantic_worlds"]==6*255

def test_sink_failure_preserves_attempt_and_does_not_admit(tmp_path):
    m=api("unary_assay_generate");o={};work={}
    def failed(row):raise OSError("authored durable sink failure")
    with pytest.raises(OSError,match="authored durable"):
        m._episode(0,lambda s,d,k:draw(chain(),s,d,k),(("train",1),),2,
                   sink=failed,deadline=10,clock=lambda:0,work=work,observation=o)
    assert o["stage"]=="RECORDING_CANNOT_CHECK"
    assert o["active_record"]["reason"]=="ACCEPTED" and not o["partitions"]["train"]
    assert work["sink_attempts"]==1 and work.get("sink_successes",0)==0

def test_candidate_exception_keeps_unavailable_slots_without_retry(tmp_path):
    calls=[]
    def failed(*args):calls.append(args);raise RuntimeError("authored draw failure")
    r,sink,o,work=run(tmp_path,failed)
    assert len(calls)==1 and r["missing"][0]["reason"]=="DRAW_EXCEPTION"
    assert "authored draw failure" in o["error"]

def test_syntax_duplicate_stops_before_semantic_work(tmp_path):
    a=chain()
    r,sink,o,work=run(tmp_path,lambda s,d,k:draw(a if d<2 else other(),s,d,k),(("train",2),))
    assert [x["reason"] for x in sink.rows if x["kind"]=="DRAW"]==["ACCEPTED","SYNTAX_DUPLICATE","ACCEPTED"]
    duplicate=[x for x in sink.rows if x["kind"]=="DRAW"][1]
    assert duplicate["semantic_key"] is None and work["semantic_worlds"]==2*6*255

def test_deadline_crossing_durable_draw_append_keeps_slot_unadmitted(tmp_path):
    now=[0];sink=Sink(tmp_path/"records.jsonl")
    def slow(row):
        sink(row)
        if row["kind"]=="DRAW":now[0]=11
    r,_,o,work=run(tmp_path,lambda s,d,k:draw(chain(),s,d,k),clock=lambda:now[0],sink=slow)
    assert not r["partitions"]["train"] and not r["accepted_syntax"]
    assert r["missing"][0]["reason"]=="DEADLINE_AFTER_APPEND"
    assert sink.rows[0]["reason"]=="ACCEPTED"
    assert sink.rows[0]["authority"]=="PROVISIONAL_UNTIL_EPISODE_RESULT"

def test_final_result_append_overrun_is_an_explicit_terminal_override(tmp_path):
    now=[0];sink=Sink(tmp_path/"records.jsonl")
    def slow(row):
        sink(row)
        if row["kind"]=="EPISODE_RESULT":now[0]=11
    r,_,o,work=run(tmp_path,lambda s,d,k:draw(chain(),s,d,k),clock=lambda:now[0],sink=slow)
    assert r["terminal"]=="GENERATION_CANNOT_CHECK" and r["reason"]=="DEADLINE_AFTER_RESULT_APPEND"
    assert sink.rows[-1]["kind"]=="EPISODE_OVERRUN"
    assert len(r["partitions"]["train"])==1 and not r["missing"]

def test_final_sink_failure_keeps_already_admitted_rows(tmp_path):
    m=api("unary_assay_generate");sink=Sink(tmp_path/"records.jsonl");o={}
    def failed(row):
        if row["kind"]=="EPISODE_RESULT":raise OSError("authored final sink failure")
        sink(row)
    with pytest.raises(OSError,match="authored final"):
        m._episode(0,lambda s,d,k:draw(chain(),s,d,k),(("train",1),),2,
                   sink=failed,deadline=10,clock=lambda:0,work={},observation=o)
    assert o["stage"]=="RECORDING_CANNOT_CHECK" and len(o["partitions"]["train"])==1
    assert o["active_record"]["kind"]=="EPISODE_RESULT"
