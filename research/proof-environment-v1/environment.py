"""Qualified CLI entry: python -I -S environment.py prepare|check [options]."""
from pathlib import Path
from hashlib import sha256
import sys
from types import ModuleType

if not sys.flags.isolated or not sys.flags.no_site:
    raise SystemExit("Use the independently registered Python with -I -S.")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# Compile the exact source bytes. Timestamp/size-valid .pyc files are not authority.
for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check"):
    path = HERE / (name + ".py")
    if path.resolve(strict=True) != path or not path.is_file():
        raise SystemExit("Unregistered source path: " + str(path))
    source = path.read_bytes(); module = ModuleType(name); module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    module.__ocm_source_sha256__ = sha256(source).hexdigest()
env_prepare, env_check = sys.modules["env_prepare"], sys.modules["env_check"]
from env_runtime import verify_imports

verify_imports()
if len(sys.argv) < 2 or sys.argv[1] not in {"prepare", "check"}:
    raise SystemExit("Expected prepare or check; inspection uses an inspect preparation freeze.")
operation = sys.argv.pop(1)
raise SystemExit({"prepare": env_prepare.main, "check": env_check.main}[operation]())
