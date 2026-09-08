"""Authored coordinator integration; no registered candidate stream."""
import copy,time
import pytest
from unary_test_support import statement as s,task
from unary_method_profile import observe
from assay_test_support import authored_only

def fixture():
    p=[s("every","P0","P1"),s("no","P1","P2")];q=s("no","P0","P2")
    training=[task([*p,s("some",x,x)],q) for x in ("P0","P2")]
    final=[task([*p,s("some",x,x),s("every","P2","P2")],q) for x in ("P0","P1")]
    return {"training":training,"development":[final[0]],"final":final}

def test_actual_small_complete_phase_lifetimes_and_roles(tmp_path):
    from unary_assay_coordinator import run_authored
    out=run_authored(tmp_path/"run",[fixture()],deadline=time.monotonic()+100,profile=observe())
    assert out["abort"] is None,out
    assert all(s["state"] in ("COMPLETED","NOT_APPLICABLE") for s in out["slots"].values()),out
    assert len(out["calls"])==52
    from unary_assay_ledger import read
    records=[read(tmp_path/"run/reports",r) for r in out["calls"]]
    ps=[r["facts"]["process"] for r in records]
    assert len({p["pid"] for p in ps})==52
    assert all(a["ended_monotonic"]<=b["started_monotonic"] for a,b in zip(ps,ps[1:]))
    assert [r["arm"] for r in records[:2]]==["ADAPTIVE_PARENT","OCM_ENABLED"]
    assert [r["arm"] for r in records[2:6]]==["EXACT_PARENT","ADAPTIVE_PARENT","OCM_ENABLED","OCM_KNOCKOUT"]
    assert all(r["request"]["deadline_monotonic"]==out["deadline_monotonic"] for r in records if r["mode"]=="presented_batch")
    assert all(p["deadline_monotonic"]==out["deadline_monotonic"] for p in ps)
    assert out["episodes"][0]["role_reference"]["row_id"]=="e0/final/0"
    from unary_assay_analysis import analyze
    from unary_assay_ledger import write
    work={};analysis=analyze(tmp_path/"run",expected_sources=out["sources"],work=work)
    write(tmp_path/"run","ANALYSIS.json",analysis)
    assert analysis["apparatus"]["episodes"][0]["terminal"]=="CHECKED_CAUSAL_REUSE_APPARATUS"
    assert analysis["apparatus"]["episodes"][0]["comparison"]=="PARENT_SUFFICIENT"
    assert analysis["apparatus"]["terminal"]=="CANNOT_CHECK"  # one authored episode, not four scientific episodes
    assert len(work["call_audits"])==52
    assert all(x["terminal"]=="ECONOMICS_CANNOT_CHECK" for x in analysis["economics"])
    ref=out["calls"][0];path=tmp_path/"run/reports"/ref["path"]
    before=path.read_bytes();(tmp_path/"TAMPER-BEFORE.json").write_bytes(before)
    path.write_bytes(b"{}");(tmp_path/"TAMPER-AFTER.json").write_bytes(path.read_bytes())
    from unary_assay_auth import CustodyFailure
    from unary_contract import InputRefused
    try:
        with pytest.raises(InputRefused,match="RECORD_HASH"):
            analyze(tmp_path/"run",expected_sources=out["sources"],work={})
    finally:path.write_bytes(before)
    assert path.read_bytes()==(tmp_path/"TAMPER-BEFORE.json").read_bytes()

def test_expired_original_deadline_never_starts_session(tmp_path):
    from unary_assay_coordinator import run_authored
    from unary_contract import InputRefused
    with pytest.raises(InputRefused,match="DEADLINE"):
        run_authored(tmp_path/"late",[fixture()],deadline=time.monotonic()-1,profile=observe())
    assert not (tmp_path/"late").exists()

def test_fixed_entry_cannot_draw_master_in_engineering(tmp_path):
    from unary_assay_coordinator import run
    out=run(tmp_path/"blocked",deadline=time.monotonic()+20,profile=observe())
    assert not out["calls"]
    assert all(e["generation_terminal"]!="GENERATED" for e in out["episodes"])
    assert len(out["episodes"])==4
