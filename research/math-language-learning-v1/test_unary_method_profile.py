"""Explicit interpreter observations are launcher inputs, not learned method data."""
import importlib,importlib.util,json,sys
from pathlib import Path
import pytest
from unary_contract import InputRefused
import unary_method_process as P

def profile_api():
    assert importlib.util.find_spec("unary_method_profile"),"missing explicit interpreter binding"
    return importlib.import_module("unary_method_profile")

def test_observed_current_interpreter_has_exact_version_and_file():
    B=profile_api();profile=B.observe()
    assert profile["executable"]==str(Path(sys.executable).resolve())
    assert profile["version"]=="3.11.14" and B.validate(profile)==profile
    assert B.verify(profile)["sha256"]==profile["sha256"]

@pytest.mark.parametrize("change",["version","relative","extra","hash_type"])
def test_malformed_profile_is_refused(change):
    B=profile_api();profile=B.observe()
    if change=="version":profile["version"]="3.11"
    elif change=="relative":profile["executable"]="python"
    elif change=="extra":profile["entrypoint"]="anything.py"
    else:profile["sha256"]=True
    with pytest.raises(InputRefused):B.validate(profile)

def test_parent_wrong_hash_refuses_before_dispatch_with_record(tmp_path,monkeypatch):
    B=profile_api();profile=B.observe();profile["sha256"]="0"*64
    monkeypatch.setattr(P.subprocess,"Popen",lambda *a,**k:pytest.fail("mismatched interpreter dispatched"))
    result=P.launch(tmp_path/"parent","solve",{},profile=profile)
    assert result["terminal"]=="PROCESS_REFUSED" and result["pid"] is None
    assert "PYTHON_HASH" in result["error"] and result["profile"]==profile
    assert json.loads((tmp_path/"parent/PROCESS.json").read_bytes())==result

def test_actual_child_checks_profile_independently(tmp_path,monkeypatch):
    B=profile_api();profile=B.observe();actual=P.subprocess.Popen
    def altered(argv,**kwargs):
        env=dict(kwargs["env"]);wrong=dict(profile,sha256="0"*64)
        env["OCM_UNARY_PYTHON_PROFILE"]=P.D.raw(wrong).decode()
        return actual(argv,**dict(kwargs,env=env))
    monkeypatch.setattr(P.subprocess,"Popen",altered)
    result=P.launch(tmp_path/"child","solve",{},profile=profile)
    assert result["terminal"]=="PROCESS_REFUSED" and result["returncode"]==2
    child=json.loads((tmp_path/"child/result.json").read_bytes())
    assert "PYTHON_HASH" in child["reason"] and child["profile"]["sha256"]=="0"*64
    assert result["reaped"] and result["group_absent"]
