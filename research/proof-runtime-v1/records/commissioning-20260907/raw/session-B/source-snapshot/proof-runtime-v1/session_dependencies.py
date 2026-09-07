"""Explicit host imports of the unchanged commissioned mechanism; never learner mounts."""
import importlib
from pathlib import Path
import sys

MECHANICAL = Path(__file__).resolve().parent.parent / "mechanical-proof-v1"
sys.path.insert(0, str(MECHANICAL))
NAMES = ("runtime_bundle", "isolation", "lean_transport", "proof_check", "kernel_check",
         "episode", "f0_fixture", "f0_terms", "f0_search")
MODULES = {name: importlib.import_module(name) for name in NAMES}
for name, module in MODULES.items():
    if Path(module.__file__).resolve() != MECHANICAL / (name + ".py"):
        raise ImportError("unregistered host module origin: " + name)
run_isolated = MODULES["isolation"].run_isolated
check_staged = MODULES["kernel_check"].check_staged
stage_candidate = MODULES["proof_check"].stage_candidate
validate_worker = MODULES["episode"].validate_worker
verify_runtime = MODULES["episode"]._runtime_check
f0_fixture = MODULES["f0_fixture"].f0_fixture
file_hash = MODULES["runtime_bundle"].file_hash
WORKER_FILES = MODULES["episode"].WORKER_FILES
TARGET_SHA256 = MODULES["proof_check"].TARGET_SHA256
FOUNDATION_SHA256 = MODULES["proof_check"].FOUNDATION_SHA256
