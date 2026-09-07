"""Matched direct parent, actual persistence and warm shared proposal computation."""
import importlib,importlib.util
import pytest
from learning_test_support import training
from test_unary_method_runtime import fresh
from unary_solver import RegionSolver
from unary_contract import InputRefused
from unary_verify import verify_result
def api(name):
    assert importlib.util.find_spec(name),"missing adaptive parent "+name
    return importlib.import_module(name)
def populated(tmp_path):
    store=api("unary_parent_store").ParentStore(tmp_path/"parent",create=True)
    c=api("unary_method_selection").contract(2,1,authored=True)
    result=store.acquire_selected([training("B")["task"],training("C")["task"]],[fresh()],c)
    assert store.method_ids and result["terminal"]=="SELECTED"
    return store
def test_parent_actual_use_without_hidden_solve_and_cold_recovery(tmp_path,monkeypatch):
    store=populated(tmp_path);b=api("unary_parent_runtime").ParentRuntime(store)
    monkeypatch.setattr(RegionSolver,"complete",lambda *a:pytest.fail("hidden query completion"))
    r=b.solve(fresh());assert r["terminal"]=="CHECKED"
    assert r["packet"]["use"]["recipes_applied"]==1 and verify_result(fresh(),r["packet"]["result"])
    cold=api("unary_parent_store").ParentStore(store.root)
    assert len(cold.uses)==1 and cold.method_ids==store.method_ids
def test_parent_warm_mask_and_posting_cache(tmp_path):
    store=populated(tmp_path);b=api("unary_parent_runtime").ParentRuntime(store)
    one=b.solve(fresh());two=b.solve(fresh())
    assert two["packet"]["execution"]["engine_cache_reused"]
    assert two["packet"]["execution"]["index"]["posting_cache_hits"]==1
    assert two["packet"]["execution"]["parent_semantic_total"]["cache_misses"]<one["packet"]["execution"]["parent_semantic_total"]["cache_misses"]
    assert two["packet"]["execution"]["parent_semantic_total"]["cache_key_nodes"]>0
@pytest.mark.parametrize("role,recipes",[("discovery",1),("utility",0),("schema_environment",0)])
def test_parent_role_revision_is_not_proof_erasure(tmp_path,role,recipes):
    store=populated(tmp_path);b=api("unary_parent_runtime").ParentRuntime(store);mid=store.method_ids[0]
    store.revise(role,"REVOKED",mid=mid)
    r=b.solve(fresh());assert r["terminal"]=="CHECKED" and r["packet"]["use"]["recipes_applied"]==recipes
    store.revise(role,"LIVE",mid=mid);assert b.solve(fresh())["packet"]["use"]["recipes_applied"]==1
@pytest.mark.parametrize("fault",["payload","extra","journal"])
def test_parent_public_operation_rechecks_persistent_data(tmp_path,fault):
    store=populated(tmp_path)
    if fault=="payload":
        p=next((store.root/"payloads").iterdir());p.write_bytes(b"{}")
    elif fault=="extra":(store.root/"payloads"/("0"*64+".json")).write_bytes(b"{}")
    else:store.journal.append("FORGED",{},expected_head=store.head)
    with pytest.raises(InputRefused):api("unary_parent_runtime").ParentRuntime(store).solve(fresh())
def test_pending_use_never_restores_as_zero_uses(tmp_path,monkeypatch):
    store=populated(tmp_path);append=store._append
    def fail(kind,body):
        if kind=="USE":raise OSError("authored durable use failure")
        return append(kind,body)
    monkeypatch.setattr(store,"_append",fail)
    with pytest.raises(OSError):api("unary_parent_runtime").ParentRuntime(store).solve(fresh())
    with pytest.raises(InputRefused,match="INCOMPLETE_USE"):api("unary_parent_store").ParentStore(store.root)
