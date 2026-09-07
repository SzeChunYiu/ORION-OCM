"""Isolate global module replacement by the new materialization loader controls."""
from pathlib import Path
import sys
import pytest


@pytest.fixture(autouse=True)
def restore_materializer_module_registry(request):
    if not request.path.name.startswith("test_materialize_"):
        yield
        return
    # The production loader deliberately replaces owned modules. Keep that
    # behavior inside each authored test so older controls see their own imports.
    names = {path.stem for path in Path(__file__).parent.glob("*.py")}
    before = {name: sys.modules[name] for name in names if name in sys.modules}
    try:
        yield
    finally:
        for name in names:
            if name in before:
                sys.modules[name] = before[name]
            else:
                sys.modules.pop(name, None)
