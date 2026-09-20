"""Use the immutable V15 Context implementation, with one cached Python type."""
import importlib.util
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "gmi-1068-partial-context-v15/context_v15.py"
NAME = "_gmi_immutable_context_v15"
if NAME not in sys.modules:
    spec = importlib.util.spec_from_file_location(NAME, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
core = sys.modules[NAME]
if Path(core.__file__).resolve() != SOURCE.resolve():
    raise ValueError("context module binding mismatch")
Context = core.Context
observe = core.observe
compare = core.compare
domain = core.domain
quotient = core.quotient


def checked(context):
    if type(context) is not Context:
        raise ValueError("validated V15 Context required")
    return context


def flags(values):
    if type(values) is not tuple or any(type(v) is not bool for v in values):
        raise ValueError("canonical strict Boolean tuple required")
    return values


def order(relation):
    if type(relation) is not tuple:
        raise ValueError("canonical order tuple required")
    return Context(0, len(relation), (), (), (), relation).order
