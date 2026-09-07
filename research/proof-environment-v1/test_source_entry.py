"""Actual source-only CLI launch against harmless, matching-header cached bytecode."""
import importlib.util
import marshal
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import pytest

HERE = Path(__file__).resolve().parent


@pytest.mark.parametrize("cached", ["env_inputs", "isolation"])
def test_qualified_entry_ignores_unbound_cached_driver_code(tmp_path, cached):
    package = tmp_path / "research/proof-environment-v1"; package.mkdir(parents=True)
    mechanical = package.parent / "mechanical-proof-v1"; mechanical.mkdir()
    for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check", "environment"):
        shutil.copyfile(HERE / (name + ".py"), package / (name + ".py"))
    shutil.copyfile(HERE.parent / "mechanical-proof-v1/isolation.py", mechanical / "isolation.py")
    source = (mechanical if cached == "isolation" else package) / (cached + ".py")
    cache = Path(importlib.util.cache_from_source(str(source))); cache.parent.mkdir(exist_ok=True)
    code = compile("raise RuntimeError('UNREGISTERED_CACHE_EXECUTED')", str(source), "exec")
    header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(source.stat().st_mtime), source.stat().st_size)
    cache.write_bytes(header + marshal.dumps(code))
    control_code = "import sys; sys.path.insert(0, sys.argv[1]); __import__(sys.argv[2])"
    control = subprocess.run([sys.executable, "-I", "-S", "-c", control_code, str(source.parent), cached],
                             capture_output=True, timeout=15, check=False)
    assert control.returncode != 0 and b"UNREGISTERED_CACHE_EXECUTED" in control.stderr
    result = subprocess.run([sys.executable, "-I", "-S", str(package / "environment.py"), "prepare", "--help"],
                            capture_output=True, timeout=15, check=False)
    assert result.returncode == 0, result.stderr.decode()
    assert b"--freeze-sha256" in result.stdout
    assert b"UNREGISTERED_CACHE_EXECUTED" not in result.stdout + result.stderr
