import importlib.util,json,subprocess,sys
from pathlib import Path
import pytest

def test_source_entry_ignores_matching_header_cached_code(tmp_path):
 assert importlib.util.find_spec("resource_boot") is not None,"source-only controller entry missing"
 import resource_boot
 from importlib._bootstrap_external import _code_to_timestamp_pyc
 source=Path(__file__).parent
 for name in [*resource_boot.MODULES,"resource_boot"]:
  (tmp_path/(name+".py")).write_bytes((source/(name+".py")).read_bytes())
 target=tmp_path/"resource_contract.py";stat=target.stat()
 cache=Path(importlib.util.cache_from_source(str(target)));cache.parent.mkdir()
 cache.write_bytes(_code_to_timestamp_pyc(compile("raise RuntimeError('stale-cache-consumed')",str(target),"exec"),int(stat.st_mtime),stat.st_size))
 red=subprocess.run([sys.executable,"-c","import resource_contract"],cwd=tmp_path,capture_output=True)
 assert red.returncode!=0 and b"stale-cache-consumed" in red.stderr
 green=subprocess.run([sys.executable,"-I","-S",str(tmp_path/"resource_boot.py"),"check-sources"],cwd=tmp_path,capture_output=True)
 assert green.returncode==0,green.stderr.decode()
 result=json.loads(green.stdout)
 assert result["loaded_from"]=="RAW_SOURCE_BYTES"
 assert result["sources"]["resource_contract"]["sha256"]

def test_preloaded_unstamped_module_is_replaced():
 assert importlib.util.find_spec("resource_boot") is not None,"source-only controller entry missing"
 import resource_boot,types
 fake=types.ModuleType("resource_contract");fake.sentinel="wrong"
 old=sys.modules.get("resource_contract");sys.modules["resource_contract"]=fake
 try:
  modules=resource_boot.load()
  assert modules["resource_contract"] is not fake
  assert not hasattr(modules["resource_contract"],"sentinel")
 finally:
  if old is not None:sys.modules["resource_contract"]=old

def test_privileged_helper_contract_uses_source_bytes(tmp_path):
 from importlib._bootstrap_external import _code_to_timestamp_pyc
 source=Path(__file__).parent
 for name in ("resource_setup.py","resource_contract.py"):
  (tmp_path/name).write_bytes((source/name).read_bytes())
 target=tmp_path/"resource_contract.py";stat=target.stat()
 cache=Path(importlib.util.cache_from_source(str(target)));cache.parent.mkdir()
 cache.write_bytes(_code_to_timestamp_pyc(compile("raise RuntimeError('stale-helper-cache')",str(target),"exec"),int(stat.st_mtime),stat.st_size))
 red=subprocess.run([sys.executable,"-c","import resource_contract"],cwd=tmp_path,capture_output=True)
 assert red.returncode!=0 and b"stale-helper-cache" in red.stderr
 green=subprocess.run([sys.executable,"-c","import resource_setup;print(resource_setup.validate_limits.__name__)"],cwd=tmp_path,capture_output=True)
 assert green.returncode==0 and green.stdout==b"validate_limits\n",green.stderr.decode()
