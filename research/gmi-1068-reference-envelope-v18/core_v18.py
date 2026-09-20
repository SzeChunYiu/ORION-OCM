"""Reuse the actual immutable partial-context and encoded-value implementations."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
Q = ROOT / "research/gmi-1068-context-specializations-v17"


def inherited(name):
    path = Q / (name + ".py")
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    module = sys.modules[name]
    if Path(module.__file__).resolve() != path.resolve():
        raise ValueError("inherited context module binding mismatch")
    return module


core = inherited("core_v17")
specializations = inherited("specializations_v17")
Context = core.Context
flags = core.flags
observe = core.observe
compare = core.compare
Encoded = specializations.Encoded
encode = specializations.encode
decoded = specializations.decoded
acceptance = specializations.acceptance
