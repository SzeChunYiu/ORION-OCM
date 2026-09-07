"""Real KSO and issuer persistence; no proof-channel labels stand in for checks."""
import importlib,importlib.util
from dataclasses import replace
import pytest
from unary_contract import InputRefused
from ocm.runtime.ocm_runtime import OCMRuntime
from learning_test_support import training

def module(name):
    assert importlib.util.find_spec(name) is not None,"missing runtime seam: "+name
    return importlib.import_module(name)

def populated(tmp_path):
    rt=OCMRuntime(tmp_path/"ocm")
    store=module("unary_method_store").MethodStore(rt,create=True)
    receipt=store.acquire([training("B"),training("C")])
    assert receipt["method_ids"]
    return rt,store,receipt

def test_real_admission_and_cold_restore(tmp_path):
    rt,store,receipt=populated(tmp_path);mid=receipt["method_ids"][0]
    item=store.read(mid)
    assert item["correctness"]=="LIVE" and item["eligible"]
    assert item["envelope"]["rule"]["rule_id"]==item["rule_id"]
    assert rt.state.certificates[mid]=="EXACT_CHECKER"
    rt.persist()
    cold=module("unary_method_store").MethodStore(OCMRuntime(rt.root))
    assert cold.read(mid)["envelope"]==item["envelope"]
    assert cold.work["schema_checks"]>0 and cold.work["journal_rows_read"]>0

@pytest.mark.parametrize("role,live,eligible",[("discovery",True,True),("utility",True,False),
                                               ("schema_environment",False,False)])
def test_support_roles_are_separate(tmp_path,role,live,eligible):
    rt,store,receipt=populated(tmp_path);mid=receipt["method_ids"][0]
    item=store.read(mid);eid=item["envelope"][role]
    rt.revoke([eid]);revised=store.read(mid)
    assert (revised["correctness"]=="LIVE")==live and revised["eligible"]==eligible
    rt.reinstate([eid]);assert store.read(mid)["eligible"]

@pytest.mark.parametrize("change",["raw","hash","source","unknown_method"])
def test_restored_rule_cannot_be_forged(tmp_path,change,monkeypatch):
    rt,store,receipt=populated(tmp_path);mid=receipt["method_ids"][0]
    if change=="unknown_method":
        with pytest.raises(InputRefused):store.read("unary:method:forged")
        return
    atom=rt.state.ks.atom_view[mid]
    if change=="raw":
        bad=replace(atom,meta=(("data",'{"code":"exec"}'),))
    elif change=="hash":bad=replace(atom,content_ref="0"*64)
    else:
        d=module("unary_method_data")
        monkeypatch.setattr(d,"sources",lambda work=None:{"changed":"0"*64})
        with pytest.raises(InputRefused):store.read(mid)
        return
    rt.state.ks=replace(rt.state.ks,atoms=tuple(bad if x.atom_id==mid else x for x in rt.state.ks.atoms))
    with pytest.raises(InputRefused):store.read(mid)

def test_interrupted_two_ledger_issuance_is_not_empty_success(tmp_path,monkeypatch):
    rt=OCMRuntime(tmp_path/"ocm");M=module("unary_method_store");store=M.MethodStore(rt,create=True)
    original=rt.admit_batch
    def interrupted(items):
        original(items)
        raise RuntimeError("interrupted after actual KSO batch")
    monkeypatch.setattr(rt,"admit_batch",interrupted)
    with pytest.raises(RuntimeError):store.acquire([training("B"),training("C")])
    assert any(a.atom_type=="procedure" for a in rt.state.ks.atoms)
    with pytest.raises(InputRefused,match="INCOMPLETE_ISSUANCE"):M.MethodStore(OCMRuntime(rt.root))

def test_index_refuses_stale_field_and_revocation(tmp_path):
    rt,store,receipt=populated(tmp_path);I=module("unary_method_index")
    index=I.MethodIndex(store);ids=index.select("no")
    assert ids and index.work["index_probes"]==1
    rt.revoke([store.read(ids[0])["envelope"]["utility"]])
    with pytest.raises(InputRefused,match="STALE_INDEX"):index.select("no")
    fresh=I.MethodIndex(store)
    assert fresh.select("no")==[] and fresh.refusals

def test_bad_training_never_admits_method(tmp_path):
    rt=OCMRuntime(tmp_path/"ocm");store=module("unary_method_store").MethodStore(rt,create=True)
    example=training();example["result"]["status"]="UNKNOWN"
    with pytest.raises(InputRefused):store.acquire([example])
    assert not store.method_ids and not rt.state.ks.atoms
