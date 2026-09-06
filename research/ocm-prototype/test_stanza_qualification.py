"""Pre-inference custody and execution-status controls; no learned-model calls."""
import json
from pathlib import Path
import pytest
import stanza_qualification_capture as C
import stanza_qualification_grade as G

def sealed(**updates):
    return {"status":"ACTOR_SEALED","exit_code":0,"outer_timeout":False,**updates}

@pytest.mark.parametrize("record,n,valid,terminal", [
    (sealed(),100,100,"DONOR_QUALITY_PROGRESSION_ONLY"),
    (sealed(),99,99,"CANNOT_CHECK_EXECUTION_OR_BINDING"),
    (sealed(exit_code=1),100,100,"CANNOT_CHECK_EXECUTION_OR_BINDING"),
    (sealed(status="CANNOT_CHECK_EXECUTION_OR_BINDING"),100,100,"CANNOT_CHECK_EXECUTION_OR_BINDING"),
    (sealed(),100,99,"INPUT_CONTRACT_MISMATCH"),
    (sealed(outer_timeout=True),20,20,"EXECUTION_DEADLINE_EXCEEDED")])
def test_execution_failure_never_becomes_contract_failure(record,n,valid,terminal):
    assert G.decision(record,n,valid,True,True)==terminal

def test_prediction_clean_and_explicit_refusal(tmp_path):
    p=tmp_path/"rows"
    rows=[dict(id="a",completed=True,status="PREDICTED",words=[]),
          dict(id="b",completed=True,status="INPUT_CONTRACT_MISMATCH",words=None,reason="mismatch")]
    p.write_text("\n".join(json.dumps(x) for x in rows))
    assert list(G.checked_predictions(p,["a","b"]))==["a","b"]
    assert G.checked_predictions(tmp_path/"missing",["a"])=={}

@pytest.mark.parametrize("change",[{"completed":False},{"status":"UNKNOWN"},{"words":None},
                                  {"id":"unassigned"}])
def test_prediction_binding_refusal(tmp_path,change):
    p=tmp_path/"rows"
    p.write_text(json.dumps({**dict(id="a",completed=True,status="PREDICTED",words=[]),**change}))
    with pytest.raises(ValueError):G.checked_predictions(p,["a"])

@pytest.mark.parametrize("changed",["runtime-plan-v1.json","runtime-v1/launch-plan.json"])
def test_qualified_launch_metadata_drift_refused_before_run(tmp_path,monkeypatch,changed):
    q=tmp_path/"qualification";q.mkdir();(q/"runtime-v1").mkdir()
    names=("runtime-plan-v1.json","runtime-v1/launch-plan.json")
    for name in names:(q/name).write_text("{}")
    manifest=q/"qualification-manifest-v1.json"
    manifest.write_text(json.dumps({"records":{name:C.sha(q/name) for name in names}}))
    monkeypatch.setattr(C,"QUAL_SHA",C.sha(manifest))
    (q/changed).write_text("changed")
    with pytest.raises(ValueError,match="binding"):C.execute(q,tmp_path/"never-started")
    assert not (tmp_path/"never-started").exists()


def test_explicit_donor_inability_remains_cannot_check(tmp_path):
    p=tmp_path/"rows"
    p.write_text(json.dumps(dict(id="a",completed=True,status="CANNOT_CHECK",words=None,reason="donor unavailable")))
    rows=G.checked_predictions(p,["a"])
    assert rows["a"]["status"]=="CANNOT_CHECK"
    assert G.decision(sealed(),99,99,True,True)=="CANNOT_CHECK_EXECUTION_OR_BINDING"


def test_cpu_accounting_does_not_infer_descendants_from_wait4(tmp_path):
    from types import SimpleNamespace
    from stanza_qualification_capture import cpu_accounting
    # Values from the actual retained native prediction: wrapper != actor.
    (tmp_path/"actor-receipt.json").write_text('{"process_cpu_s": 7.032604}')
    result = cpu_accounting(SimpleNamespace(ru_utime=0, ru_stime=0),
        SimpleNamespace(ru_utime=0.001, ru_stime=0.000535), tmp_path)
    assert result["outer_direct_child_cpu_s"] == pytest.approx(0.001535)
    assert result["actor_self_reported_cpu_s"] == 7.032604
    assert result["total_process_tree_cpu_s"] is None
    assert result["complete_cpu_custody"] is False
    (tmp_path/"actor-receipt.json").write_text('{"process_cpu_s": true}')
    assert cpu_accounting(SimpleNamespace(ru_utime=0, ru_stime=0),
        SimpleNamespace(ru_utime=0, ru_stime=0), tmp_path)["actor_self_reported_cpu_s"] is None
