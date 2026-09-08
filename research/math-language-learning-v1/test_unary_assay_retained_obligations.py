"""Retained schedule/lineage falsifiers with explicit synthetic authenticated facts."""
import copy,time
from pathlib import Path
import pytest
from assay_test_support import authored_only
from unary_assay_phase import ARMS,ROLES,Session
from unary_assay_schedule import key,expected
from unary_assay_ledger import inventory,copy_store,write
from unary_assay_auth import CustodyFailure
from unary_method_profile import observe

def mode_for(phase,mutation):return "acquire_selected" if phase=="A" else ("revise" if mutation else "presented_batch")

def retained(tmp_path,monkeypatch,*,fault=None,episodes=1,abort=None):
    import unary_assay_analysis as a
    sources={"authored":"synthetic authority for isolated analysis controls"}
    monkeypatch.setattr(a,"inspect",lambda path,**kw: facts[str(path)])
    monkeypatch.setattr(a.R,"episode",lambda *args,**kw: copy.deepcopy(known))
    root=tmp_path/"retained";root.mkdir()
    for part in ("calls","reports","stores"): (root/part).mkdir()
    from unary_assay_ledger import Ledger
    ledger=Ledger(root/"ledger",deadline=time.monotonic()+60)
    slots={};refs=[];copies=[];facts={};post={};previous={};counts={}
    rows=[{"row_id":r,"presentation":"ast","terminal":"CHECKED",
           "use":{"recipes_applied":1,"rule_id":"rule"}} for r in ("r0","r1")]
    known={"selection":"SELECTED","selected":["rule"],"semantic_keys":{"r0":"s0","r1":"s1"},
           "B":{"OCM_ENABLED":{"rows":rows},"ADAPTIVE_PARENT":{"rows":rows},
                "OCM_KNOCKOUT":{"rows":[]}},"C_complete":True,"role_reference":"r0"}
    for e in range(episodes):
        skipped=abort is not None and e>abort.get("episode",e)
        ledger.append("GENERATION",{"episode":e,"result":{"terminal":"UNAVAILABLE" if skipped else "GENERATED"}})
        for slot in a.schedule_ids(e):
            _,phase,arm=slot.split("--")
            detail={"episode":e,"phase":phase,"arm":arm}
            ledger.append("EXPECTED",{"slot":slot,**detail})
            mutation=any(phase==r+"-"+v for r in ROLES for v in ("withdraw","reinstate"))
            na=(arm=="EXACT_PARENT" and mutation) or skipped
            state="UNAVAILABLE" if skipped else ("NOT_APPLICABLE" if na else "COMPLETED")
            if fault in ("missing_C","missing_role") and slot==key(e,"C" if fault=="missing_C" else "utility-restored","OCM_ENABLED"):
                na=True;state="NOT_APPLICABLE" if fault=="missing_C" else "COMPLETED"
            ref=None
            if not na:
                request={};before=None;prior=0
                if arm!="EXACT_PARENT":
                    target=root/"stores"/slot
                    if phase=="A":target.mkdir()
                    else:
                        origin=key(e,"A","ADAPTIVE_PARENT" if arm=="ADAPTIVE_PARENT" else "OCM_ENABLED")
                        if phase not in ("B","C"):origin=previous.get((e,phase.rsplit("-",1)[0],arm),origin)
                        if fault=="C_from_B" and phase=="C" and arm=="OCM_ENABLED":origin=key(e,"B",arm)
                        if fault=="role_from_B" and phase=="utility-withdraw" and arm=="OCM_ENABLED":origin=key(e,"B",arm)
                        if fault=="role_reset_A" and phase=="utility-restored" and arm=="OCM_ENABLED":origin=key(e,"A",arm)
                        cp=copy_store(root/"stores"/origin,target,deadline=time.monotonic()+60)
                        cr=write(root/"reports",slot+"-copy.json",cp);copies.append(cr);ledger.append("COPY",cr)
                        before=inventory(target);prior=counts[origin]
                    (target/"state").write_text(slot)
                    post[slot]=inventory(target);request["store"]=str(target)
                    if phase not in ("A","B","C"):previous[(e,phase.rsplit("-",1)[0],arm)]=slot
                counts[slot]=prior+(1 if mode_for(phase,mutation)=="presented_batch" else 0)
                f={"terminal":"CHECKED","rows":[],"prior_uses":prior,"use_count":counts[slot]}
                path=root/"calls"/slot;facts[str(path)]=f
                mode="acquire_selected" if phase=="A" else ("revise" if mutation else "presented_batch")
                record={"slot":slot,"path":str(path),"arm":arm,"mode":mode,"request":request,
                        "facts":f,"source_before":sources,"source_after":sources,"error":None,
                        "store_before_dispatch":before,"store_after_audit":post.get(slot)}
                if fault=="precopy_drift" and phase=="C" and arm=="OCM_ENABLED":
                    record["store_before_dispatch"]={"authored":"different"}
                ref=write(root/"reports",slot+".json",record);refs.append(ref)
            value={"state":state,"detail":detail}
            if ref is not None:value["record"]=ref
            if state=="COMPLETED":ledger.append("SLOT",{"slot":slot,"state":"ATTEMPTED","detail":detail})
            ledger.append("SLOT",{"slot":slot,**value});slots[slot]=value
    manifest={"root":str(root),"sources":sources,"profile":{},"deadline_monotonic":0.,
              "calls":refs,"copies":copies,"slots":slots,"physical":{},
              "episodes":[{"episode":e} for e in range(episodes)],"abort":abort}
    ref=write(root,"COORDINATOR.json",manifest);ledger.append("FINAL",ref)
    return a.analyze(root,expected_sources=sources,work={})

def test_clean_declared_lifetimes_and_copy_lineage(tmp_path,monkeypatch):
    result=retained(tmp_path,monkeypatch)
    assert result["apparatus"]["episodes"][0]["terminal"]=="CHECKED_CAUSAL_REUSE_APPARATUS"

@pytest.mark.parametrize("fault",["missing_C","missing_role"])
def test_missing_required_call_cannot_be_hidden_by_na_or_completed(tmp_path,monkeypatch,fault):
    result=retained(tmp_path,monkeypatch,fault=fault)
    assert result["apparatus"]["episodes"][0]["terminal"]=="CANNOT_CHECK"

@pytest.mark.parametrize("fault",["C_from_B","role_from_B","role_reset_A","precopy_drift"])
def test_copy_lineage_must_bind_original_A_and_immediate_role_state(tmp_path,monkeypatch,fault):
    with pytest.raises(CustodyFailure,match="COPY_|RESTART_"):retained(tmp_path,monkeypatch,fault=fault)

def test_semantic_failure_affects_only_its_origin_episode(tmp_path,monkeypatch):
    cause={"kind":"SEMANTIC_CONTROL_FAILED","reason":"authored failure","episode":1,"slot":"e1--B--OCM_ENABLED"}
    result=retained(tmp_path,monkeypatch,episodes=3,abort={**cause,"causes":[cause]})
    assert [r["terminal"] for r in result["apparatus"]["episodes"]]==[
        "CHECKED_CAUSAL_REUSE_APPARATUS","SEMANTIC_CONTROL_FAILED","CANNOT_CHECK"]
    assert result["apparatus"]["terminal"]=="SEMANTIC_CONTROL_FAILED"

def test_session_failure_retains_actual_episode_and_slot(tmp_path,monkeypatch):
    import unary_assay_phase as p
    monkeypatch.setattr(p,"launch",lambda *a,**kw:{"terminal":"COMPLETED","returncode":0})
    def bad(*a,**kw):raise p.A.ControlFailure("authored invalid answer")
    monkeypatch.setattr(p.A,"inspect",bad)
    s=Session(tmp_path/"session",deadline=time.monotonic()+10,profile=observe())
    slot=key(2,"B","EXACT_PARENT");s.expect(slot,{"episode":2,"phase":"B","arm":"EXACT_PARENT"})
    s.call(slot,"EXACT_PARENT","presented_batch",{"rows":[]})
    assert s.abort["episode"]==2 and s.abort["slot"]==slot

def test_no_use_na_requires_authenticated_complete_C():
    from unary_assay_obligations import completion
    from unary_assay_analysis import schedule_ids
    states={slot:{"state":"NOT_APPLICABLE"} for slot in schedule_ids(0)}
    calls=[]
    for phase,arms in (("A",("ADAPTIVE_PARENT","OCM_ENABLED")),("B",ARMS),("C",ARMS)):
        for arm in arms:
            slot=key(0,phase,arm);states[slot]={"state":"COMPLETED"}
            calls.append({"slot":slot,"error":None,"facts":{"terminal":"CHECKED"}})
    assert completion(0,states,calls,{"C_complete":True,"role_reference":None})==[]
    assert len(completion(0,states,calls,{"role_reference":None}))==48
