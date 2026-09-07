from pathlib import Path
import pytest
import resource_setup as setup

def test_profile_removal_refuses_populated_owned_controller(tmp_path,monkeypatch):
 group=tmp_path/"owned";group.mkdir();(group/"cgroup.procs").write_text("123\n")
 monkeypatch.setattr(setup,"paths",lambda name:{"memory":group})
 def forbidden(*a,**k):raise AssertionError("parser must not run")
 monkeypatch.setattr(setup.subprocess,"run",forbidden)
 with pytest.raises(ValueError,match="still protects populated"):
  setup.apparmor("test-012345",tmp_path/"not-read",remove=True)

def test_exact_file_binding_rejects_boolean_byte_count(tmp_path):
 from resource_contract import record,verify
 p=tmp_path/"one";p.write_bytes(b"x");binding=record(p);binding["bytes"]=True
 with pytest.raises(ValueError):verify(binding)
