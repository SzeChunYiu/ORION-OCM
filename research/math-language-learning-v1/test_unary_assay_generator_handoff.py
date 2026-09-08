"""Real producer/consumer seam with an explicit engineering-only SHA stream."""
import copy,time
import pytest
from assay_test_support import authored_only
from unary_contract import InputRefused
from unary_method_profile import observe
from unary_assay_ledger import replay,write
from unary_assay_auth import ControlFailure
from unary_assay_recheck import episode as recheck
import unary_assay_coordinator as C
import unary_assay_stream as S

ENGINEERING_MASTER="engineering-only/generator-handoff-repair/20260908/v1"

@pytest.fixture(scope="module")
def generated_run(tmp_path_factory):
    """Fixed dimensions/producer/coordinator; only field seed and dispatch are authored."""
    root=tmp_path_factory.mktemp("synthetic-generator-handoff")/"run"
    original_choice=S.choice;choice_masters=set()
    def guarded_choice(master,*args,**kwargs):
        if master==S.MASTER:raise InputRefused("REGISTERED_STREAM_FORBIDDEN_IN_ENGINEERING")
        if master!=ENGINEERING_MASTER:raise InputRefused("UNREGISTERED_ENGINEERING_TAG")
        choice_masters.add(master)
        return original_choice(master,*args,**kwargs)
    def draw(e,split,attempt,slot,*,work):
        return S.build_candidate(e,split,attempt,slot,
            lambda tag,pool:S.choice(ENGINEERING_MASTER,e,split,attempt,tag,pool,work=work),work=work)
    class RefusedDispatch(C.Session):
        def call(self,slot,arm,mode,request):
            assert mode=="acquire_selected", "this seam control must never execute scientific service"
            self.mark(slot,"ATTEMPTED",None)
            record={"slot":slot,"arm":arm,"mode":mode,"request":request,
                    "error":"AUTHORED_DISPATCH_REFUSAL","facts":None}
            ref=write(self.root/"reports",slot+".json",record);self.calls.append(ref)
            self.mark(slot,"UNAVAILABLE","AUTHORED_DISPATCH_REFUSAL",record=ref)
            return record
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(S,"choice",guarded_choice);patch.setattr(S,"draw",draw)
        patch.setattr(C,"Session",RefusedDispatch)
        with pytest.raises(InputRefused,match="REGISTERED_STREAM_FORBIDDEN"):
            S.choice(S.MASTER,0,"train",0,"guard",[0],work={})
        result=C.run(root,deadline=time.monotonic()+90,profile=observe())
    rows=replay(root/"ledger")
    generated=[r["body"]["result"] for r in rows if r["kind"]=="GENERATION"]
    assert choice_masters=={ENGINEERING_MASTER}
    assert len(generated)==4 and all(g["terminal"]=="GENERATED" for g in generated)
    assert all(tuple(g["partitions"])==("development","final","train") for g in generated)
    draws=[r["body"] for r in rows if r["kind"]=="GENERATOR" and r["body"]["kind"]=="DRAW"]
    assert draws and all(f["choice"]["input"][0]==ENGINEERING_MASTER for d in draws for f in d["candidate"]["fields"])
    return root,result,generated

def test_real_generator_reaches_all_eight_acquisition_boundaries(generated_run):
    root,result,generated=generated_run
    assert len(result["calls"])==8, result["episodes"]
    assert result["abort"] is None
    for e,g in enumerate(generated):
        assert "failed_stage" not in result["episodes"][e]
        assert result["episodes"][e]["reason"]=="A_INCOMPLETE"
        assert [len(g["partitions"][s]) for s in S.SPLITS]==list(S.SIZES)
        for split in S.SPLITS:
            assert [r["row_id"] for r in g["partitions"][split]]==[
                f"e{e}/{split}/{i}" for i in range(S.SIZES[S.SPLITS.index(split)])]
        for arm in ("ADAPTIVE_PARENT","OCM_ENABLED"):
            slot=f"e{e}--A--{arm}"
            from unary_assay_ledger import read
            call=read(root/"reports",result["slots"][slot]["record"])
            assert call["request"]["training"]==[r["task"] for r in g["partitions"]["train"]]
            assert call["request"]["development"]==[r["task"] for r in g["partitions"]["development"]]
            assert result["slots"][slot]["reason"]=="AUTHORED_DISPATCH_REFUSAL"
    assert sum(v.get("reason")=="UNREACHED" for v in result["slots"].values())==224

def test_retained_recheck_consumes_the_same_real_generated_partitions(generated_run):
    _,_,generated=generated_run
    g=generated[0]
    call={"slot":"e0--A--ADAPTIVE_PARENT","error":"AUTHORED_DISPATCH_REFUSAL","facts":None,
          "request":{"training":[r["task"] for r in g["partitions"]["train"]],
                     "development":[r["task"] for r in g["partitions"]["development"]]}}
    assert recheck(0,g,[call],work={})=={}
    changed=copy.deepcopy(call);changed["request"]["training"].pop()
    with pytest.raises(ControlFailure,match="ACQUISITION_INPUT_SUBSTITUTION"):
        recheck(0,g,[changed],work={})

def test_authored_convenience_input_normalizes_to_producer_contract():
    from test_unary_assay_coordinator import fixture
    inputs=fixture();before=copy.deepcopy(inputs)
    g=C.authored_partitions(inputs,0,{})
    assert set(g["partitions"])==set(S.SPLITS)
    assert [r["task"] for r in g["partitions"]["train"]]==inputs["training"]
    assert [r["row_id"] for r in g["partitions"]["train"]]==["e0/train/0","e0/train/1"]
    assert inputs==before
