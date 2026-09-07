"""Minimal native executable/library mounts; fixture/import caches are never mounted."""
from pathlib import Path
import sys
from types import ModuleType
from hashlib import sha256
from env_inputs import bound_json, file_record, relative_name, verify_file

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / "mechanical-proof-v1" / "isolation.py"
ISOLATION = ModuleType("ocm_environment_isolation")
ISOLATION.__file__ = str(HELPER)
_helper_source = HELPER.read_bytes()
exec(compile(_helper_source, str(HELPER), "exec", dont_inherit=True), ISOLATION.__dict__)
ISOLATION.__ocm_source_sha256__ = sha256(_helper_source).hexdigest()
if Path(ISOLATION.__file__).resolve() != HELPER:
    raise ImportError("unregistered isolation helper origin")


def source_inventory():
    names = ("env_inputs.py", "env_runtime.py", "env_dispatch.py", "env_prepare.py", "env_check.py", "environment.py")
    result = {"proof-environment-v1/" + name: file_record(HERE / name) for name in names}
    result["mechanical-proof-v1/isolation.py"] = file_record(HELPER)
    return result


def verify_imports():
    for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check"):
        module = sys.modules.get(name)
        if module is not None and Path(module.__file__).resolve() != HERE / (name + ".py"):
            raise ImportError("unexpected driver module origin: " + name)
        if module is not None and getattr(module, "__ocm_source_sha256__", None) != file_record(HERE / (name + ".py"))["sha256"]:
            raise ImportError("driver source was not loaded through the qualified source-only entry: " + name)
    if ISOLATION.__ocm_source_sha256__ != file_record(HELPER)["sha256"]:
        raise ImportError("loaded isolation helper differs from source")


def verify_runtime(path, expected_sha256):
    if not sys.flags.isolated or not sys.flags.no_site:
        raise ValueError("qualified driver requires Python -I -S")
    verify_imports()
    runtime = bound_json(path, expected_sha256)
    required = {"schema", "executable", "libraries", "bwrap", "driver_sources", "build", "host_python"}
    if set(runtime) != required or runtime["schema"] != "ocm.proof-environment.runtime.v1":
        raise ValueError("runtime schema differs")
    if source_inventory() != runtime["driver_sources"]: raise ValueError("driver source drift")
    if verify_file(runtime["host_python"]) != Path(sys.executable).resolve(strict=True):
        raise ValueError("host interpreter differs from registered executable")
    verify_file(runtime["executable"]); verify_file(runtime["bwrap"])
    if runtime["bwrap"]["sha256"] != ISOLATION.BWRAP_SHA256:
        raise ValueError("unqualified isolation executable")
    libraries = runtime["libraries"]
    if type(libraries) is not list: raise ValueError("library list required")
    mounts = [(runtime["executable"]["path"], "/bridge/ocm_environment")]
    for item in libraries:
        if type(item) is not dict or set(item) != {"guest", "file"}:
            raise ValueError("library mount record required")
        guest = item["guest"]
        if type(guest) is not str or not guest.startswith(("/lib/", "/lib64/", "/bridge/lib/")):
            raise ValueError("unregistered library destination")
        if Path(guest).as_posix() != guest or any(p in ("", ".", "..") for p in guest.split("/")[1:]):
            raise ValueError("noncanonical library destination")
        verify_file(item["file"]); mounts.append((item["file"]["path"], guest))
    destinations = [Path(g) for _, g in mounts]
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(destinations) for b in destinations[i + 1:]):
        raise ValueError("overlapping runtime destinations")
    build = runtime["build"]
    if type(build) is not dict or set(build) != {"record", "sources"}:
        raise ValueError("independently qualified build binding required")
    verify_file(build["record"])
    if type(build["sources"]) is not dict or not build["sources"]:
        raise ValueError("build sources required")
    for name, record in build["sources"].items():
        relative_name(name); verify_file(record)
    return runtime, mounts


def execute(runtime, mounts, request, work, inputs, *, timeout_s, max_output_bytes):
    return ISOLATION.run_isolated(
        ["/bridge/ocm_environment", "/request/request.json", "/work/native"],
        read_only=[*mounts, (str(request), "/request/request.json"), *inputs],
        executable_sha256=runtime["executable"]["sha256"], work_dir=str(work),
        env={"HOME": "/tmp", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TMPDIR": "/tmp"},
        timeout_s=timeout_s, max_output_bytes=max_output_bytes,
        bwrap_path=runtime["bwrap"]["path"], bwrap_sha256=runtime["bwrap"]["sha256"])
