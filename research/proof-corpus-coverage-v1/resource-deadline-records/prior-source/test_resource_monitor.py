import os,signal
from pathlib import Path
import pytest
import resource_monitor as monitor
import resource_runner as runner
from test_resource_contract import limits

@pytest.fixture(autouse=True)
def restore_signals():
 old={s:signal.getsignal(s) for s in (signal.SIGTERM,signal.SIGHUP)}
 try:yield
 finally:
  for sig,value in old.items():signal.signal(sig,value)

def test_walk_permission_error_is_not_empty_success(tmp_path,monkeypatch):
 def denied(root,**kwargs):
  error=PermissionError("authored denied directory")
  if kwargs.get("onerror"):kwargs["onerror"](error)
  return iter(())
 monkeypatch.setattr(monitor.os,"walk",denied)
 with pytest.raises(PermissionError):monitor.disk_snapshot([tmp_path])

def test_repeated_disk_failure_still_retains_receipt_and_restores_handlers(tmp_path,monkeypatch):
 def denied(*a,**k):raise PermissionError("authored denied scan")
 monkeypatch.setattr(runner,"disk_snapshot",denied)
 old=signal.getsignal(signal.SIGTERM)
 r=runner.run(["must-not-dispatch"],{},limits(),tmp_path/"out",[])
 assert r["terminal"]=="SETUP_REFUSED"
 assert r["cleanup"]["no_dispatch"]
 assert r["final_disk"]["available"] is False
 assert r["overshoot_bytes"] is None
 assert (tmp_path/"out/resource-receipt.json").exists()
 assert signal.getsignal(signal.SIGTERM)==old

def test_seal_write_failure_still_restores_handlers(tmp_path,monkeypatch):
 monkeypatch.setattr(runner,"disk_snapshot",lambda *a:(_ for _ in ()).throw(PermissionError("scan")))
 monkeypatch.setattr(runner,"write_json",lambda *a:(_ for _ in ()).throw(OSError("seal failure")))
 old=signal.getsignal(signal.SIGTERM)
 with pytest.raises(OSError):runner.run(["must-not-dispatch"],{},limits(),tmp_path/"out",[])
 assert signal.getsignal(signal.SIGTERM)==old
