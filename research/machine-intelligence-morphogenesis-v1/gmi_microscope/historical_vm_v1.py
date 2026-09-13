"""Explicit historical-source selection for frozen pre-adjoint-repair receipts."""
from pathlib import Path
import hashlib
import itertools
import types
import json
import sys

AUDIT_SHA256 = "6aa6a24361c43a8086fa303ab41a692cc230a57c441b94265d03f1f52b6c715b"
MEMBERS = ("__init__.py", "core.py", "bases.py", "morph.py", "vm.py")
_IDENTITIES = itertools.count()


def historical_vm(packet=None):
    """Verify all five frozen import sources, then load a disjoint old VM package."""
    if packet is None:
        packet = (Path(__file__).resolve().parents[2] /
                  "gmi-native-adjoint-repair-v1/raw/pr551-grad-audit-20260913")
    packet = Path(packet)
    manifest_path = packet / "AUDIT_MANIFEST_V1.json"
    raw = manifest_path.read_bytes()
    if manifest_path.is_symlink() or hashlib.sha256(raw).hexdigest() != AUDIT_SHA256:
        raise ValueError("historical source manifest differs")
    rows = json.loads(raw)["files"]
    source = packet / "raw/gmi_microscope"
    buffers = {}
    for name in MEMBERS:
        path = source / name
        data = path.read_bytes()
        row = rows["raw/gmi_microscope/" + name]
        if path.is_symlink() or len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("historical import source differs: " + name)
        buffers[name] = data
    # Compile the verified bytes directly: neither .pyc nor a prior module is authority.
    while True:
        package_name = "historical_gmi_vm_ef6de91a_" + str(next(_IDENTITIES))
        if not any(n == package_name or n.startswith(package_name + ".") for n in sys.modules):
            break
    package = types.ModuleType(package_name)
    package.__package__ = package_name
    package.__path__ = []
    package.__file__ = str(source / "__init__.py")
    sys.modules[package_name] = package
    exec(compile(buffers["__init__.py"], package.__file__, "exec"), package.__dict__)
    for part in ("core", "bases", "morph", "vm"):
        name = package_name + "." + part
        module = types.ModuleType(name)
        module.__package__ = package_name
        module.__file__ = str(source / (part + ".py"))
        sys.modules[name] = module
        setattr(package, part, module)
        exec(compile(buffers[part + ".py"], module.__file__, "exec"), module.__dict__)
    return package.vm
