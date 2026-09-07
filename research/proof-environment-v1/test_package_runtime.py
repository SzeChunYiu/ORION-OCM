"""Authored byte fixtures test custody only; no ELF/native program is executed."""
import copy
from pathlib import Path
import sys
from hashlib import sha256
from types import ModuleType
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# Execute actual local bytes, as the production entry does; no synthetic stamps.
for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check"):
    path = HERE / (name + ".py"); raw = path.read_bytes()
    module = sys.modules.get(name, ModuleType(name)); module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    module.__ocm_source_sha256__ = sha256(raw).hexdigest()
import env_inputs as I
import env_runtime as R
import package_runtime as P


def record(path): return {"path": str(path), **I.file_record(path)}


def fixture(tmp_path):
    sources = tmp_path / "inputs"; sources.mkdir()
    def put(name, raw):
        path = sources / name; path.write_bytes(raw); return record(path)
    exe = put("checker", b"\x7fELFauthored-checker-not-executed")
    libraries = [{"guest": "/lib64/ld-linux-x86-64.so.2", "file": put("loader", b"\x7fELFloader")},
                 {"guest": "/bridge/lib/libtest.so", "file": put("library", b"\x7fELFlibrary")}]
    build = {"record": put("build.json", I.canonical({"fixture": "build evidence"})),
             "sources": {"Main.lean": put("Main.lean", b"-- authored source fixture\n")}}
    request = {"schema": "ocm.proof-environment.package-request.v1", "executable": exe,
               "libraries": libraries, "bwrap": record(Path("/usr/bin/bwrap").resolve()), "build": build}
    audit = {"schema": "ocm.proof-environment.link-import-audit.v1", "status": "AUDITED",
             "bindings": copy.deepcopy({k: request[k] for k in ("executable", "libraries", "bwrap", "build")}),
             "assertions": {"fixture_free_link_imports": True, "complete_elf_runtime_closure": True,
                            "no_unregistered_runtime_loads": True},
             "evidence": {k: put(k + ".txt", ("authored " + k + " evidence\n").encode())
                          for k in ("link", "imports", "elf")}}
    audit_path = sources / "audit.json"; audit_path.write_bytes(I.canonical(audit))
    request["audit"] = record(audit_path)
    request_path = sources / "request.json"; request_path.write_bytes(I.canonical(request))
    return request_path, request, audit


def save(request_path, request, audit):
    path = Path(request["audit"]["path"]); path.write_bytes(I.canonical(audit))
    request["audit"] = record(path); request_path.write_bytes(I.canonical(request))
    return I.file_record(request_path)["sha256"]


def run(request_path, output): return P.package(request_path, I.file_record(request_path)["sha256"], output)


def test_copies_exact_runtime_without_source_mounts_and_is_create_only(tmp_path):
    path, request, _ = fixture(tmp_path); before = I.inventory(path.parent)
    result = run(path, tmp_path / "package")
    runtime = I.bound_json(result["runtime"]["path"], result["runtime"]["sha256"])
    assert set(runtime) == {"schema", "executable", "libraries", "bwrap", "driver_sources", "build", "host_python"}
    assert runtime["schema"] == "ocm.proof-environment.runtime.v1"
    assert runtime["driver_sources"] == R.source_inventory()
    assert I.verify_file(runtime["host_python"]) == Path(sys.executable).resolve()
    for old, new in zip(request["libraries"], runtime["libraries"]):
        assert old["guest"] == new["guest"] and old["file"]["sha256"] == new["file"]["sha256"]
        assert Path(new["file"]["path"]).stat().st_mode & 0o777 == 0o555
    for item in [runtime["executable"], runtime["bwrap"], *(x["file"] for x in runtime["libraries"]),
                 runtime["build"]["record"], *runtime["build"]["sources"].values()]:
        assert I.verify_file(item).is_relative_to(tmp_path / "package")
        assert not Path(item["path"]).is_symlink()
    receipt = I.bound_json(result["receipt"]["path"], result["receipt"]["sha256"])
    assert receipt["terminal"] == "CUSTODY_PACKAGED"
    assert receipt["closure_authority"] == "EXTERNAL_AUDIT_NOT_REPERFORMED"
    assert receipt["runtime"] == result["runtime"]
    assert I.inventory(path.parent) == before
    with pytest.raises(FileExistsError): run(path, tmp_path / "package")


@pytest.mark.parametrize("change", ["missing_audit", "unreviewed", "false_assertion", "missing_evidence", "wrong_binding"])
def test_unaudited_or_mismatched_link_import_evidence_refuses(tmp_path, change):
    path, request, audit = fixture(tmp_path)
    if change == "missing_audit":
        del request["audit"]; path.write_bytes(I.canonical(request))
    else:
        if change == "unreviewed": audit["status"] = "UNREVIEWED"
        if change == "false_assertion": audit["assertions"]["fixture_free_link_imports"] = False
        if change == "missing_evidence": del audit["evidence"]["imports"]
        if change == "wrong_binding": audit["bindings"]["executable"]["sha256"] = "0" * 64
        save(path, request, audit)
    with pytest.raises(ValueError): run(path, tmp_path / "package")
    assert not (tmp_path / "package/runtime.json").exists()


@pytest.mark.parametrize("guest", ["/lib", "/usr/lib/x.so", "/lib/../x", "/lib//x", "/lib/./x", "/lib64/ld-linux-x86-64.so.2"])
def test_bad_or_duplicate_mount_destination_refuses(tmp_path, guest):
    path, request, audit = fixture(tmp_path); request["libraries"][1]["guest"] = guest
    audit["bindings"]["libraries"] = copy.deepcopy(request["libraries"]); save(path, request, audit)
    with pytest.raises(ValueError): run(path, tmp_path / "package")


@pytest.mark.parametrize("change", ["source_bytes", "audit_bytes", "non_elf", "symlink", "bad_bwrap", "source_name", "malformed_bwrap"])
def test_input_custody_and_mount_type_fail_closed(tmp_path, change):
    path, request, audit = fixture(tmp_path)
    if change == "source_bytes": Path(request["build"]["sources"]["Main.lean"]["path"]).write_text("drift")
    elif change == "audit_bytes": Path(request["audit"]["path"]).write_text("{}")
    else:
        if change == "non_elf":
            p = Path(request["libraries"][1]["file"]["path"]); p.write_bytes(b"source or olean cache")
            request["libraries"][1]["file"] = record(p)
        if change == "symlink":
            p = path.parent / "linked"; p.symlink_to(request["executable"]["path"])
            request["executable"]["path"] = str(p)
        if change == "bad_bwrap": request["bwrap"] = request["executable"]
        if change == "malformed_bwrap": request["bwrap"] = {}
        if change == "source_name": request["build"]["sources"]["../escape"] = request["build"]["sources"].pop("Main.lean")
        audit["bindings"] = copy.deepcopy({k: request[k] for k in ("executable", "libraries", "bwrap", "build")})
        save(path, request, audit)
    with pytest.raises(ValueError): run(path, tmp_path / "package")
    assert not (tmp_path / "package/runtime.json").exists()


def test_independently_bound_request_digest_required(tmp_path):
    path, _, _ = fixture(tmp_path)
    with pytest.raises(ValueError): P.package(path, "0" * 64, tmp_path / "package")
    assert not (tmp_path / "package").exists()


def test_postcopy_source_drift_prevents_runtime_publication(tmp_path, monkeypatch):
    path, request, _ = fixture(tmp_path); original = I.snapshot
    target = Path(request["build"]["sources"]["Main.lean"]["path"])
    def drift_after_verified_copy(binding, destination):
        copied = original(binding, destination)
        if binding["path"] == str(target): target.write_bytes(b"changed after copy")
        return copied
    monkeypatch.setattr(P, "snapshot", drift_after_verified_copy)
    with pytest.raises(ValueError, match="binding differs"): run(path, tmp_path / "package")
    assert not (tmp_path / "package/runtime.json").exists()


def test_actual_isolated_cli_and_exact_runtime_verifier_accept_package(tmp_path):
    import subprocess
    path, _, _ = fixture(tmp_path)
    command = [sys.executable, "-I", "-S", str(HERE / "package_runtime.py"), str(path),
               I.file_record(path)["sha256"], str(tmp_path / "cli-package")]
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    assert process.returncode == 0, process.stderr
    result = I.parse_json(process.stdout)
    script = """from pathlib import Path
from hashlib import sha256
from types import ModuleType
import sys
here = Path(sys.argv[1])
for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check"):
    path = here / (name + ".py"); raw = path.read_bytes()
    module = ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    module.__ocm_source_sha256__ = sha256(raw).hexdigest()
value, mounts = sys.modules["env_runtime"].verify_runtime(sys.argv[2], sys.argv[3])
assert len(mounts) == 3 and all(Path(source).is_file() for source, _ in mounts)
print("EXACT_RUNTIME_SCHEMA_ACCEPTED_NO_NATIVE_EXECUTION")
"""
    verified = subprocess.run([sys.executable, "-I", "-S", "-c", script, str(HERE),
                               result["runtime"]["path"], result["runtime"]["sha256"]],
                              capture_output=True, text=True, check=False)
    assert verified.returncode == 0, verified.stderr
    assert verified.stdout.strip() == "EXACT_RUNTIME_SCHEMA_ACCEPTED_NO_NATIVE_EXECUTION"


def test_postcopy_destination_drift_prevents_runtime_publication(tmp_path, monkeypatch):
    path, request, _ = fixture(tmp_path); original = P.snapshot
    def changed_copy(binding, destination):
        value = original(binding, destination)
        if binding == request["executable"]: Path(destination).write_bytes(b"\x7fELFchanged copy")
        return value
    monkeypatch.setattr(P, "snapshot", changed_copy)
    with pytest.raises(ValueError, match="binding differs"): run(path, tmp_path / "package")
    assert not (tmp_path / "package/runtime.json").exists()


def test_nonqualified_driver_import_refuses_before_output(tmp_path, monkeypatch):
    path, _, _ = fixture(tmp_path)
    monkeypatch.delattr(I, "__ocm_source_sha256__")
    with pytest.raises(ImportError, match="source-only"): run(path, tmp_path / "package")
    assert not (tmp_path / "package").exists()
