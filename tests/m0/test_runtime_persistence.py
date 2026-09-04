from __future__ import annotations
import json
from pathlib import Path
import pytest
from ocm.runtime import OCMRuntime

def test_restart_revoke_reinstate_lifecycle(tmp_path:Path):
 log=tmp_path/"state.jsonl"; first=OCMRuntime(log); first.learn_procedure("AND",(0,0,0,1),11); first.admit_object("object:demo",b"payload",(11,)); first.link_dependency("object:demo","procedure:AND"); snap=first.snapshot(); assert first.run("AND",(1,1))==("PASS",1)
 second=OCMRuntime(log); assert second.snapshot()==snap and second.run("AND",(1,1))==("PASS",1); second.revoke(11)
 third=OCMRuntime(log); assert third.run("AND",(1,1))==("GAP_REVOKED_PROCEDURE",None) and third.snapshot()["revoked_set"]==["11"]; third.reinstate(11)
 fourth=OCMRuntime(log); assert fourth.run("AND",(1,1))==("PASS",1); assert fourth.snapshot()["revoked_set"]==[]; assert fourth.snapshot()["dependency_links"]=={"object:demo":["procedure:AND"]}; assert fourth.snapshot()["content_hashes"]["object:demo"]

def test_event_hash_chain_rejects_tamper(tmp_path:Path):
 log=tmp_path/"state.jsonl"; r=OCMRuntime(log); r.learn_procedure("AND",(0,0,0,1),99); row=json.loads(log.read_text()); row["payload"]["table"]=[1,1,1,1]; log.write_text(json.dumps(row)+"\n")
 with pytest.raises(ValueError,match="event content hash mismatch"): OCMRuntime(log)

def test_outside_registered_domain_is_cannot_check(tmp_path:Path):
 r=OCMRuntime(tmp_path/"state.jsonl"); r.learn_procedure("AND",(0,0,0,1),3); assert r.run("AND",(2,0))==("CANNOT_CHECK_INPUT_OUTSIDE_REGISTERED_DOMAIN",None)
