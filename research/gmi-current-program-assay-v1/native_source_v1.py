"""Execute verified source buffers in a fresh private package; no pyc/import-cache reuse."""
from pathlib import Path
import hashlib
import json
import sys
import types
import uuid

HERE = Path(__file__).resolve().parent
ORDER = ("core", "bases", "morph", "vm", "smooth", "zoo", "ecology")


def source_bytes():
    binding = json.loads((HERE / "SOURCE_BINDINGS_V1.json").read_text())
    buffers = {}
    for row in binding["files"]:
        data = (HERE / row["path"]).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("frozen source mismatch: " + row["path"])
        buffers[Path(row["path"]).name] = data
    return buffers


def load():
    buffers = source_bytes()
    name = "_program_assay_" + uuid.uuid4().hex
    package = types.ModuleType(name)
    package.__path__ = []
    sys.modules[name] = package
    try:
        for short in ORDER:
            full = name + "." + short
            mod = types.ModuleType(full)
            mod.__file__ = str(HERE / "raw/native-df777cd7" / (short + ".py"))
            mod.__package__ = name
            sys.modules[full] = mod
            setattr(package, short, mod)
            exec(compile(buffers[short + ".py"], mod.__file__, "exec"), mod.__dict__)
    except BaseException:
        for key in list(sys.modules):
            if key == name or key.startswith(name + "."):
                del sys.modules[key]
        raise
    return package
