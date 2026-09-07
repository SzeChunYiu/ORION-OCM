"""Create-only native runtime custody; this program never executes an input file.

Usage: python -I -S package_runtime.py REQUEST EXPECTED_SHA256 NEW_OUTPUT_DIRECTORY
REQUEST uses package-request.v1 and exact file records for executable, libraries,
bwrap, build {record,sources}, and audit. Each library is {guest,file}.
The independently registered request digest authorizes a link-import-audit.v1
receipt with exact bindings for executable/libraries/bwrap/build, status AUDITED,
three true assertions, and link/imports/elf evidence file records. The external
reviewer must inspect actual imports/link objects (including embedded fixtures),
recursive ELF resolution, and runtime loads/data access. Here these assertions
are bound and retained, NOT independently established by supplied filenames,
ELF magic, or matching hashes. No native closure qualification is produced.

Only binary and individually specified ELF files become guest mounts. Build,
driver and audit sources are retained as custody evidence, never guest mounts.
Runtime uses the canonical current host interpreter and pinned bubblewrap.
Failures retain create-only partial output; runtime.json is published last.
"""
from pathlib import Path
import sys
from hashlib import sha256
from types import ModuleType

# CLI compiles registered local source; no input-specified code/library is loaded.
if __name__ == "__main__":
    if not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit("Use the registered Python with -I -S.")
    here = Path(__file__).resolve().parent
    for name in ("env_inputs", "env_runtime", "env_dispatch", "env_prepare", "env_check"):
        path = here / (name + ".py")
        if path.resolve(strict=True) != path: raise ImportError("noncanonical driver source")
        raw = path.read_bytes(); module = ModuleType(name); module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
        module.__ocm_source_sha256__ = sha256(raw).hexdigest()
from env_inputs import (bound_json, canonical, create_root, digest, file_record,
                        relative_name, snapshot, verify_file, write_bytes, write_json)
import env_runtime as R

ASSERTIONS = {"fixture_free_link_imports", "complete_elf_runtime_closure", "no_unregistered_runtime_loads"}
BINDINGS = ("executable", "libraries", "bwrap", "build")


def exact(value, keys, message):
    if type(value) is not dict or set(value) != set(keys): raise ValueError(message)


def record(path): return {"path": str(Path(path)), **file_record(path)}


def elf(binding):
    path = verify_file(binding)
    with path.open("rb") as stream:
        if stream.read(4) != b"\x7fELF": raise ValueError("ELF mount required; source/cache files are not mounts")


def destinations(libraries):
    if type(libraries) is not list: raise ValueError("explicit library list required")
    paths = [Path("/bridge/ocm_environment")]
    for item in libraries:
        exact(item, ("guest", "file"), "exact library mount required")
        guest = item["guest"]
        if type(guest) is not str or not guest.startswith(("/lib/", "/lib64/", "/bridge/lib/")):
            raise ValueError("unregistered library destination")
        path = Path(guest)
        if path.as_posix() != guest or any(p in ("", ".", "..") for p in guest.split("/")[1:]):
            raise ValueError("noncanonical library destination")
        if any(path == p or path.is_relative_to(p) or p.is_relative_to(path) for p in paths):
            raise ValueError("overlapping runtime destinations")
        paths.append(path)


def audit_request(request):
    exact(request, ("schema", *BINDINGS, "audit"), "exact packaging request required")
    if request["schema"] != "ocm.proof-environment.package-request.v1": raise ValueError("request schema differs")
    build = request["build"]; exact(build, ("record", "sources"), "exact build binding required")
    if type(build["sources"]) is not dict or not build["sources"]: raise ValueError("build sources required")
    names = []
    for name in build["sources"]:
        p = Path(relative_name(name))
        if any(p.is_relative_to(q) or q.is_relative_to(p) for q in names): raise ValueError("overlapping source names")
        names.append(p)
    destinations(request["libraries"])
    audit_path = verify_file(request["audit"])
    audit = bound_json(audit_path, request["audit"]["sha256"])
    exact(audit, ("schema", "status", "bindings", "assertions", "evidence"), "exact audited receipt required")
    if audit["schema"] != "ocm.proof-environment.link-import-audit.v1" or audit["status"] != "AUDITED":
        raise ValueError("audited link/import/ELF receipt required")
    if audit["bindings"] != {k: request[k] for k in BINDINGS}: raise ValueError("audit bindings differ")
    exact(audit["assertions"], ASSERTIONS, "explicit audit assertions required")
    if any(value is not True for value in audit["assertions"].values()): raise ValueError("audit is incomplete")
    exact(audit["evidence"], ("link", "imports", "elf"), "link/import/ELF evidence required")
    verify_file(request["bwrap"])
    if request["bwrap"]["sha256"] != R.ISOLATION.BWRAP_SHA256: raise ValueError("unqualified isolation executable")
    return audit


def package(request_path, expected_sha256, output):
    """Return runtime/receipt file records; requires independently authorized inputs."""
    R.verify_imports()
    request = bound_json(request_path, expected_sha256)
    request_binding = record(request_path)
    if request_binding["sha256"] != expected_sha256: raise ValueError("request changed after binding")
    audit = audit_request(request)
    driver_sources = R.source_inventory()
    driver_files = {name: record(R.HERE.parent / name) for name in driver_sources}
    packager = record(Path(__file__).resolve(strict=True))
    python = record(Path(sys.executable).resolve(strict=True))
    binaries = [request["executable"], request["bwrap"], *(x["file"] for x in request["libraries"])]
    sources = [request_binding, request["audit"], request["build"]["record"], python, packager,
               *binaries, *request["build"]["sources"].values(), *audit["evidence"].values(), *driver_files.values()]
    for binding in sources: verify_file(binding)
    for binding in binaries: elf(binding)
    root = create_root(output); copied = []
    def copy(binding, name, executable=False):
        destination = root / name; destination.parent.mkdir(parents=True, exist_ok=True)
        value = snapshot(binding, destination); destination.chmod(0o555 if executable else 0o444)
        copied.append(value); return value
    native = copy(request["executable"], "bin/ocm_environment", True)
    libraries = [{"guest": item["guest"], "file": copy(item["file"], "libraries/" + str(i), True)}
                 for i, item in enumerate(request["libraries"])]
    bwrap = copy(request["bwrap"], "host/bwrap", True)
    build = {"record": copy(request["build"]["record"], "custody/build-record.json"),
             "sources": {name: copy(binding, "custody/build-sources/" + name)
                         for name, binding in request["build"]["sources"].items()}}
    custody = {"request": copy(request_binding, "custody/request.json"),
               "audit": copy(request["audit"], "custody/audit.json"),
               "evidence": {name: copy(binding, "custody/evidence/" + name)
                            for name, binding in audit["evidence"].items()},
               "driver_sources": {name: copy(binding, "custody/driver/" + name)
                                  for name, binding in driver_files.items()},
               "packager": copy(packager, "custody/package_runtime.py")}
    runtime = {"schema": "ocm.proof-environment.runtime.v1", "executable": native, "libraries": libraries,
               "bwrap": bwrap, "host_python": python, "build": build, "driver_sources": driver_sources}
    for binding in sources + copied: verify_file(binding)
    if R.source_inventory() != driver_sources: raise ValueError("driver source drift during packaging")
    R.verify_imports()
    raw = canonical(runtime)
    runtime_binding = {"path": str(root / "runtime.json"), "sha256": digest(raw), "bytes": len(raw)}
    receipt = {"schema": "ocm.proof-environment.package-receipt.v1", "terminal": "CUSTODY_PACKAGED",
               "closure_authority": "EXTERNAL_AUDIT_NOT_REPERFORMED", "runtime": runtime_binding,
               "custody": custody, "postcopy_sources_verified": sources}
    write_json(root / "package-receipt.json", receipt)
    write_bytes(root / "runtime.json", raw)
    return {"runtime": runtime_binding, "receipt": record(root / "package-receipt.json")}


if __name__ == "__main__":
    if len(sys.argv) != 4: raise SystemExit("usage: package_runtime.py REQUEST EXPECTED_SHA256 NEW_OUTPUT_DIRECTORY")
    sys.stdout.buffer.write(canonical(package(sys.argv[1], sys.argv[2], sys.argv[3])))
