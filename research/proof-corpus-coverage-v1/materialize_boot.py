"""Raw-source loader for the trusted materialization entry, never cached owned code."""
from hashlib import sha256
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
RESOURCE = ("resource_boot", "resource_contract", "resource_pidfd", "resource_cgroup",
            "resource_monitor", "resource_runner", "build_profile_policy", "build_profile",
            "resource_install", "resource_setup")
OWN = ("acquisition_contract", "materialize_objects", "materialize_git", "materialize_phase",
       "materialize_custody", "materialize_worker", "materialize_run")
NAMES = ("materialize_boot", *RESOURCE, *OWN)


def binding(path, raw):
    return dict(path=str(path), sha256=sha256(raw).hexdigest(), bytes=len(raw))


def load():
    sys.modules["materialize_boot"] = sys.modules[__name__]
    records = {}; result = {}
    for name in NAMES:
        path = HERE / (name + ".py"); raw = path.read_bytes()
        if path.resolve(strict=True) != path:
            raise ValueError("SOURCE_PATH")
        records[name] = binding(path, raw)
        if name == "materialize_boot" and globals().get("__source_record__", records[name]) != records[name]:
            raise ValueError("BOOT_LOADED_DRIFT")
        if name in RESOURCE[1:]:
            continue
        if name == "materialize_boot":
            result[name] = sys.modules[__name__]
            continue
        module = types.ModuleType(name); module.__file__ = str(path)
        module.__source_record__ = records[name]; sys.modules[name] = module
        exec(compile(raw, str(path), "exec"), module.__dict__); result[name] = module
        if name == "resource_boot":
            result.update(module.load())
    for name in RESOURCE[1:-1]:
        if result[name].__source_record__ != records[name]:
            raise ValueError("RESOURCE_LOADED_DRIFT")
    globals()["LOADED"] = records
    recheck()
    return result


def recheck():
    for name, expected in LOADED.items():
        path = HERE / (name + ".py")
        if path.resolve(strict=True) != path or binding(path, path.read_bytes()) != expected:
            raise ValueError("EXECUTED_SOURCE_DRIFT: " + name)
    return LOADED
