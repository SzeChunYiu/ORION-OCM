import importlib.util,json
from pathlib import Path
import pytest

def subject():
 assert importlib.util.find_spec("lake_build_fixture") is not None,"authored Lake fixture missing"
 import lake_build_fixture as m
 return m

def test_fixture_git_pin_source_and_lock(tmp_path):
 m=subject();data=m.create_fixture(tmp_path/"case")
 source=Path(data["workspace"]);lock=json.loads((source/"lake-manifest.json").read_bytes())
 assert lock["packages"][0]["rev"]==data["dependency_revision"]
 assert (source/".lake/packages/authored/.git/HEAD").read_text().strip()==data["dependency_revision"]
 assert data["source_inventory"]==m.inventory(source)
 assert "import Authored" in (source/"Fixture.lean").read_text()

def test_create_only(tmp_path):
 m=subject();root=tmp_path/"case";root.mkdir();(root/"sentinel").write_text("keep")
 with pytest.raises(FileExistsError):m.create_fixture(root)
 assert (root/"sentinel").read_text()=="keep"

def test_profile_exact_mounts_and_command(tmp_path):
 m=subject();data=m.create_fixture(tmp_path/"case");p=m.make_profile(data,[],[],{}, {})
 assert p["argv"]==["/lean/bin/lake","--dir","/workspace","--no-cache","--keep-toolchain","--rehash","--verbose","build","+Fixture:olean"]
 guests={x["guest"] for x in p["writable"]}
 assert "/workspace/.lake/config" in guests and "/workspace/.lake/packages/authored/.lake/build" in guests
 assert "/workspace/.lake" not in guests
 assert p["environment"]["HOME"]=="/work/home"
 assert len(p["materials"])==1

def outputs(m,data):
 root=Path(data["root"])
 for relative in m.REQUIRED:
  p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b"fixture output")

def test_artifact_presence_is_not_completion(tmp_path):
 m=subject();data=m.create_fixture(tmp_path/"case");outputs(m,data)
 assert m.assess(data,{"terminal":"COMMAND_FAILED"})["terminal"]=="LAKE_BUILD_REFUSED"

def test_missing_or_empty_output_refuses(tmp_path):
 m=subject();data=m.create_fixture(tmp_path/"case");outputs(m,data)
 receipt={"terminal":"COMPLETED","post_input_custody":"UNCHANGED","dispatch":{"returncode":0,"evidence_complete":True,"cleanup":{"members_empty":True,"reaped":True,"controllers_removed":True}}}
 for rel in m.REQUIRED:
  p=Path(data["root"])/rel;old=p.read_bytes();p.write_bytes(b"")
  assert m.assess(data,receipt)["terminal"]=="LAKE_BUILD_REFUSED"
  p.write_bytes(old)
 assert m.assess(data,receipt)["terminal"]=="AUTHORED_LAKE_BUILD_PASS"

@pytest.mark.parametrize("path",["Fixture.lean","lake-manifest.json",".lake/packages/authored/.git/HEAD"])
def test_source_lock_and_git_drift_refuse(tmp_path,path):
 m=subject();data=m.create_fixture(tmp_path/"case");outputs(m,data)
 (Path(data["workspace"])/path).write_text("changed")
 receipt={"terminal":"COMPLETED","post_input_custody":"UNCHANGED","dispatch":{"returncode":0,"evidence_complete":True,"cleanup":{"members_empty":True,"reaped":True,"controllers_removed":True}}}
 assert m.assess(data,receipt)["terminal"]=="LAKE_BUILD_REFUSED"

@pytest.mark.parametrize("field,value",[("returncode",False),("returncode",7),("evidence_complete",False)])
def test_process_refusal_causes_cannot_pass(tmp_path,field,value):
 m=subject();data=m.create_fixture(tmp_path/"case");outputs(m,data)
 receipt={"terminal":"COMPLETED","post_input_custody":"UNCHANGED","dispatch":{"returncode":0,
          "evidence_complete":True,"cleanup":{"members_empty":True,"reaped":True,"controllers_removed":True}}}
 receipt["dispatch"][field]=value
 assert m.assess(data,receipt)["terminal"]=="LAKE_BUILD_REFUSED"

@pytest.mark.parametrize("field",["members_empty","reaped","controllers_removed"])
def test_incomplete_cleanup_refuses(tmp_path,field):
 m=subject();data=m.create_fixture(tmp_path/"case");outputs(m,data)
 receipt={"terminal":"COMPLETED","post_input_custody":"UNCHANGED","dispatch":{"returncode":0,
          "evidence_complete":True,"cleanup":{"members_empty":True,"reaped":True,"controllers_removed":True}}}
 receipt["dispatch"]["cleanup"][field]=False
 assert m.assess(data,receipt)["terminal"]=="LAKE_BUILD_REFUSED"
