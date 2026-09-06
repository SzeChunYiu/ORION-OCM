"""Pinned Lean acquisition and copied Python/individual ELF dependency recipe."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

from runtime_bundle import copy_python, file_hash, tree_manifest

ARCHIVE_SHA256 = "890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235"
ARCHIVE_BYTES = 570405234
ENVIRONMENT = {"PATH": "/usr/bin:/bin", "LANG": "C"}


def _elf(path):
    with Path(path).open("rb") as stream: header = stream.read(18)
    return (len(header) == 18 and header[:4] == b"\x7fELF" and header[5] in (1, 2)
            and int.from_bytes(header[16:18], "little" if header[5] == 1 else "big") in (2, 3))


def elf_files(roots):
    """Trusted executable/shared ELF files, including dynamically imported extensions."""
    return sorted({path for root in roots for path in Path(root).rglob("*")
                   if path.is_file() and not path.is_symlink() and _elf(path)})


def runtime_elfs(lean, python):
    """Approved Lean entry plus Python ELF extensions; not dormant Lean build tools."""
    return sorted({Path(lean) / "bin/lean", *elf_files([python])})


def shared_libraries(executables, roots, destination, *, private_library_dirs=()):
    """Inspect reviewed ELF files only; ldd must never receive candidate data.

    Resolve every external dependency to a regular file and copy it individually.
    Missing/unknown/conflicting dependency evidence refuses before destination writes.
    """
    started = time.monotonic()
    destination = Path(destination)
    if destination.exists() or destination.is_symlink(): raise FileExistsError(destination)
    roots = [Path(root).resolve(strict=True) for root in roots]
    private = [Path(root).resolve(strict=True) for root in private_library_dirs]
    if any(not root.is_dir() or str(root) in ("/", "/usr", "/lib", "/home") for root in private):
        raise ValueError("specific trusted private library directory required")
    environment = dict(ENVIRONMENT)
    if private: environment["LD_LIBRARY_PATH"] = ":".join(map(str, private))
    guests, inspections = {}, []
    ldd_hash = file_hash("/usr/bin/ldd")
    for executable in sorted({Path(p).resolve(strict=True) for p in executables}):
        if not executable.is_file() or not _elf(executable): raise ValueError("reviewed ELF file required")
        before = file_hash(executable)
        phase_start = time.monotonic()
        result = subprocess.run(["/usr/bin/ldd", str(executable)], capture_output=True, text=True,
                                timeout=30, env=environment)
        if before != file_hash(executable): raise ValueError("inspected ELF identity changed")
        inspections.append({"executable": str(executable), "sha256": before,
                            "argv": ["/usr/bin/ldd", str(executable)], "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr,
                            "wall_s": time.monotonic() - phase_start})
        if "not found" in result.stdout + result.stderr:
            error = OSError("required shared library unavailable: " + str(executable))
            error.inspection = inspections
            raise error
        static = (result.stdout + result.stderr).strip() in ("statically linked", "not a dynamic executable")
        if result.returncode != 0 and not static: raise OSError("ldd inspection failed")
        if static: continue
        if result.stderr.strip(): raise OSError("unexpected ldd diagnostics")
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not lines: raise ValueError("missing dependency inspection output")
        for line in lines:
            if re.fullmatch(r"linux-(?:vdso|gate)\.so\.\d+ \(0x[0-9a-fA-F]+\)", line): continue
            match = re.fullmatch(r"(?:(?P<soname>\S+)\s+=>\s+)?(?P<path>/\S+)\s+\(0x[0-9a-fA-F]+\)", line)
            if match is None: raise ValueError("unrecognized dependency output")
            guest = Path(match["path"])
            source = guest.resolve(strict=True)
            if not source.is_file() or not _elf(source): raise ValueError("nonregular ELF dependency")
            if any(source.is_relative_to(root) for root in roots): continue
            if any(source.is_relative_to(root) for root in private):
                name = match["soname"]
                if not name or not re.fullmatch(r"[A-Za-z0-9_+.-]+\.so(?:\.[A-Za-z0-9_+.-]+)*", name):
                    raise ValueError("private dependency requires a canonical SONAME")
                guest = Path("/lib/x86_64-linux-gnu") / name
            elif str(guest) != match["path"] or ".." in guest.parts:
                raise ValueError("ambiguous loader path")
            digest = file_hash(source)
            previous = guests.get(str(guest))
            if previous and previous["sha256"] != digest: raise ValueError("conflicting loader dependency")
            guests[str(guest)] = {"original_source": str(source), "sha256": digest, "bytes": source.stat().st_size}
    if file_hash("/usr/bin/ldd") != ldd_hash: raise ValueError("ldd identity changed")
    destination.mkdir(exist_ok=False)
    for data in guests.values():
        source = Path(data["original_source"])
        copy = destination / (data["sha256"] + "-" + source.name)
        if not copy.exists(): shutil.copy2(source, copy)
        if file_hash(source) != data["sha256"] or file_hash(copy) != data["sha256"]:
            raise ValueError("copied dependency identity changed")
        data["source"] = str(copy.resolve())
    return {"mounts": [(data["source"], guest) for guest, data in sorted(guests.items())],
            "files": guests, "inspection": inspections, "ldd_sha256": ldd_hash,
            "environment": environment, "private_library_dirs": list(map(str, private)),
            "wall_s": time.monotonic() - started,
            "copied_bytes": sum(p.stat().st_size for p in destination.iterdir())}


def prepare_runtime(archive, python_prefix, destination):
    """Prepare fresh copied artifacts. No download, proof or search is performed."""
    started = time.monotonic(); phases = {}
    archive, destination = Path(archive), Path(destination)
    if archive.is_symlink() or not archive.is_file() or archive.resolve(strict=True) != archive:
        raise ValueError("regular canonical pinned release archive required")
    if archive.stat().st_size != ARCHIVE_BYTES or file_hash(archive) != ARCHIVE_SHA256:
        raise ValueError("unregistered Lean release archive")
    phases["archive_validation_wall_s"] = time.monotonic() - started
    destination.mkdir(exist_ok=False)
    copied_archive = destination / "registered-release.tar.zst"
    phase_start = time.monotonic()
    shutil.copyfile(archive, copied_archive)
    if file_hash(copied_archive) != ARCHIVE_SHA256: raise ValueError("copied release archive changed")
    phases["archive_copy_wall_s"] = time.monotonic() - phase_start
    tar_hash, zstd_hash = file_hash("/usr/bin/tar"), file_hash("/usr/bin/zstd")
    argv = ["/usr/bin/tar", "--zstd", "-xf", str(copied_archive), "-C", str(destination)]
    phase_start = time.monotonic()
    extraction = subprocess.run(argv, check=True, capture_output=True, text=True, timeout=180,
                                env=ENVIRONMENT)
    phases["extraction_wall_s"] = time.monotonic() - phase_start
    if file_hash("/usr/bin/tar") != tar_hash or file_hash("/usr/bin/zstd") != zstd_hash:
        raise ValueError("extraction tool identity changed")
    lean = destination / "lean-4.33.1-linux"
    phase_start = time.monotonic()
    python = copy_python(python_prefix, destination / "python")
    phases["python_copy_inventory_wall_s"] = time.monotonic() - phase_start
    roots = [lean, Path(python["directory"])]
    phase_start = time.monotonic()
    lean_files = tree_manifest(lean)
    phases["lean_inventory_wall_s"] = time.monotonic() - phase_start
    phase_start = time.monotonic()
    try:
        libraries = shared_libraries(runtime_elfs(*roots), roots, destination / "shared-libraries",
                                     private_library_dirs=[Path(python_prefix) / "lib"])
    except OSError as error:
        if hasattr(error, "inspection"):
            (destination / "dependency-failure.json").write_text(json.dumps(error.inspection, indent=2) + "\n")
        raise
    phases["elf_inventory_dependencies_wall_s"] = time.monotonic() - phase_start
    record = {"lean_root": str(lean.resolve()), "lean_files": lean_files,
              "archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
              "archive_source": str(archive), "copied_archive": str(copied_archive.resolve()),
              "extraction": {"argv": argv, "tar_sha256": tar_hash, "zstd_sha256": zstd_hash,
                             "returncode": extraction.returncode, "stdout": extraction.stdout,
                             "stderr": extraction.stderr, "environment": dict(ENVIRONMENT)},
              "python": python, "shared_libraries": libraries, "phases": phases,
              "dependency_scope": "Approved Lean entry and its ldd closure plus copied Python executable/extensions; dormant Lean build/sysroot executables are inventoried but not runtime-qualified.",
              "acquisition": {"downloaded_this_call": False, "archive_bytes": ARCHIVE_BYTES,
                              "download_wall_s": None, "scope": "Existing pinned archive; prior download cost unavailable here."},
              "preparation_wall_s": time.monotonic() - started, "cpu_s": None, "peak_rss_bytes": None,
              "scope": "Copied artifact identities; no proof/search result or complete no-neural qualification."}
    (destination / "runtime-manifest.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record
