"""Exposed unit programs; new query after cold withdrawal, no prospective panel."""
import json
import os
from pathlib import Path
import subprocess
import sys

from ocm.kso.ids import content_hash
from ocm.runtime.ocm_runtime import OCMRuntime
from g1_vessel import CONFIG
import clia_reuse_vessel as V
from test_clia_reuse_vessel import fixture_state


WORKER = """
import json,sys
from pathlib import Path
from ocm.kso.ids import content_hash
from ocm.kso.warrant import Liveness
from ocm.runtime.ocm_runtime import OCMRuntime
from clia_reuse_study_common import InvocationMeter
from g1_vessel import CONFIG
from g1_field import ROOT, MODEL
import g1_vessel as G
import clia_reuse_vessel as V
root=Path(sys.argv[1]); cfg=json.loads(sys.argv[2]); phase=sys.argv[3]
r=OCMRuntime(root,config=CONFIG)
assert not r.state.operators.operators
maximum,guard=cfg["max3"],cfg["guard2"]; q=cfg["request"]
if phase=="restore": r.reinstate([cfg["registration"]])
if phase=="withdraw":
    assert "clia:application:"+content_hash(q) not in r.state.ks.ids
    try: V.bind(r,maximum)
    except ValueError as e: assert str(e)=="program is not live"
    else: raise AssertionError("dead descriptor bound")
else: V.bind(r,maximum)
V.bind(r,guard)
before=V.load(r,maximum)["support"]
events=[]
with InvocationMeter(events): out=V.apply(r,q)
aid=V.atom_id(maximum); atom=r.state.ks.atom(aid)
assert V.load(r,maximum)["support"]==before==cfg["support"]
assert atom.liveness(r.state.revoked) is (Liveness.DEAD if phase=="withdraw" else Liveness.LIVE)
qid="clia:application:"+content_hash(q)
assert r.state.ks.atom(qid).is_live(r.state.revoked)
peers=set().union(*(e.incident-{qid} for e in r.state.ks.incident_edges(qid)))
assert {ROOT,aid} <= peers
if phase=="withdraw":
    assert out["status"]=="NOT_ADMITTED",out
    assert out["answer"] is None and out["admitted_id"] is None and not events
    assert len(out["catalogue"])==4 and "apply:"+maximum in out["catalogue"]
    assert "apply:"+maximum not in out["counters"]["catalogue_visits"]
    assert out["counters"]["application_calls"]==out["counters"]["synthesis_dispatches"]==0
    stages={s["stage"]:s for s in out["trace"]["stages"]}
    assert aid in stages["GROUNDING"]["object_ids"]
    assert aid not in stages["EXTRACTION"]["payload"]["warranted_atoms"]
    assert aid in stages["EXTRACTION"]["payload"]["exploratory_only_atoms"]
    assert "apply:"+maximum not in stages["COMPOSITION"]["object_ids"]
    assert stages["COMMITMENT"]["reason"].startswith("REFUSED:")
else:
    assert out["status"]=="ADMITTED" and out["answer"]["value"]==41
    assert [e["action"] for e in events]==["application"]
retained=V.apply(r,{"kind":"clia_apply","program_id":guard,"arguments":[17,-9,0]})
assert retained["status"]=="ADMITTED" and retained["answer"]["value"]==8
# Public deterministic syntax fixture tests the unchanged dispatch/admission route, not a model score.
G.predict=lambda tokens,path,digest: {"status":"PREDICTED","model_sha256":digest,
    "words":[{"id":1,"form":"widget","head":0,"deprel":"root","upos":"NOUN"}]}
syntax=V.query(r,{"kind":"syntax","tokens":["widget"]})
assert syntax["status"]=="ADMITTED" and syntax["claim"]=="MODEL_SUPPORTED_SYNTAX_OBSERVATION"
assert len(syntax["catalogue"])==4 and syntax["reuse_counters"]["application_calls"]==0
r.persist()
print(json.dumps({"UNIT_FIXTURE":True,"phase":phase,"result":out,"events":events,
    "retained":retained,"syntax":syntax,"state_hash":r.state.kso_state_hash,
    "support":before,"revoked":sorted(r.state.revoked)}))
"""


def test_new_request_after_fresh_withdrawal_refuses_then_same_request_recovers(tmp_path):
    state = tmp_path / "state"
    runtime, records, history, _ = fixture_state(state)
    descs = {name: V.adopt(runtime, record[0], history=[history]) for name, record in records.items()}
    for desc in descs.values(): V.bind(runtime, desc["id"])
    maximum, guard = [descs[k] for k in ("jmbl_fg_max3", "jmbl_fg_mpg_guard2")]
    request = {"kind": "clia_apply", "program_id": maximum["id"], "arguments": [41, -7, 12]}
    assert "clia:application:" + content_hash(request) not in runtime.state.ks.ids
    registration = records["jmbl_fg_max3"][1]
    runtime.revoke([registration]); runtime.persist()
    config = {"max3": maximum["id"], "guard2": guard["id"], "request": request,
              "registration": registration, "support": maximum["support"]}
    prototype = Path(__file__).resolve().parent; repo = prototype.parents[1]
    child_env = {**os.environ, "PYTHONPATH": os.pathsep.join((str(repo / "src"), str(prototype)))}
    for phase in ("withdraw", "restore"):
        process = subprocess.run([sys.executable, "-c", WORKER, str(state), json.dumps(config), phase],
            text=True, capture_output=True, timeout=30, cwd=repo, env=child_env)
        (tmp_path / (phase + ".stdout")).write_text(process.stdout)
        (tmp_path / (phase + ".stderr")).write_text(process.stderr)
        assert process.returncode == 0, process.stderr
        record = json.loads(process.stdout)
        restarted = OCMRuntime(state, config=CONFIG)
        assert restarted.state.kso_state_hash == record["state_hash"]
        assert not restarted.state.operators.operators
