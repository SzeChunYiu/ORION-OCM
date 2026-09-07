"""One-time deterministic archival of assigned existing records; no source execution."""
from pathlib import Path
from hashlib import sha256
import gzip
import json
import os
import stat
import tarfile
import time

BASE = Path("/home/billy/orion-director-work/20260907")
OUT = Path(__file__).resolve().parent
ROOTS = {
    "materializer-repair": "materialize-review-repair-v1",
    "entry-qualification": "materialize-entry-qualification-v1",
    "portability-repair": "materialize-portability-review-v1",
    "config-review": "coverage-build-config-review-v1",
    "scheduling-hold": "coverage-materialization-envelope-v1",
    "scheduling-audit": "materialization-scheduling-review-v1",
}


def identity(path):
    digest = sha256(); size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block); size += len(block)
    return dict(sha256=digest.hexdigest(), bytes=size)


def save(name, value):
    with (OUT / name).open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2); stream.write("\n")


def inventory(root):
    files = {}; directories = {}; links = {}
    def fail(error): raise error
    for base, dirs, names in os.walk(root, followlinks=False, onerror=fail):
        for name in sorted(dirs + names):
            path = Path(base) / name; relative = str(path.relative_to(root)); mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                links[relative] = dict(target=os.readlink(path), mode=stat.S_IMODE(mode))
            elif stat.S_ISDIR(mode):
                directories[relative] = dict(mode=stat.S_IMODE(mode))
            elif stat.S_ISREG(mode):
                files[relative] = {**identity(path), "mode": stat.S_IMODE(mode)}
            else: raise ValueError("unsupported original type: " + relative)
    return dict(files=files, directories=directories, symlinks=links)


def archive(label, directory):
    root = BASE / directory; before = inventory(root)
    members = {n: {k: v[k] for k in ("sha256", "bytes")} for n, v in before["files"].items()}
    archive_path = OUT / (label + ".tar.gz")
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name in sorted(members):
                    info = tarfile.TarInfo(name); info.size = members[name]["bytes"]
                    info.mode = 0o644; info.uid = info.gid = info.mtime = 0
                    with (root / name).open("rb") as stream: tar.addfile(info, stream)
    seen = set()
    with tarfile.open(archive_path, mode="r:gz", ignore_zeros=True) as tar:
        for item in tar:
            if not item.isfile() or item.name not in members or item.name in seen:
                raise ValueError("archive membership")
            seen.add(item.name); digest = sha256(); size = 0
            with tar.extractfile(item) as stream, (root / item.name).open("rb") as original:
                while True:
                    block = stream.read(1048576)
                    if original.read(len(block) or 1) != block: raise ValueError("archive/original bytes")
                    if not block: break
                    digest.update(block); size += len(block)
            if dict(sha256=digest.hexdigest(), bytes=size) != members[item.name]:
                raise ValueError("archive hash")
    if seen != set(members) or inventory(root) != before: raise ValueError("original post-custody")
    save(label + ".members.json", members)
    save(label + ".tree.json", before)
    return dict(original_root=str(root), archive={"file": archive_path.name, **identity(archive_path)},
                member_map={"file": label + ".members.json", **identity(OUT / (label + ".members.json"))},
                tree_metadata={"file": label + ".tree.json", **identity(OUT / (label + ".tree.json"))},
                regular_members=len(members), raw_bytes=sum(v["bytes"] for v in members.values()),
                symlinks_metadata_only=len(before["symlinks"]), directories_metadata_only=len(before["directories"]),
                readback="Every archived regular byte compared directly with original; complete original tree rechecked afterward.")


def main():
    began = time.monotonic()
    rows = {label: archive(label, directory) for label, directory in ROOTS.items()}
    source = OUT / "source"; source.mkdir()
    scripts = {}
    for name in ("launch_materialization_v1.py", "read_pinned_build_config.py"):
        path = BASE / name; raw = path.read_bytes()
        with (source / name).open("xb") as stream: stream.write(raw)
        if raw != path.read_bytes(): raise ValueError("script drift")
        scripts[name] = dict(original=str(path), retained="source/" + name, **identity(path))
    pre = json.loads((BASE / ROOTS["scheduling-hold"] / "PRELAUNCH.json").read_bytes())
    config = json.loads((BASE / ROOTS["config-review"] / "RESULT.json").read_bytes())
    if scripts["launch_materialization_v1.py"]["sha256"] != pre["launcher"]["sha256"]:
        raise ValueError("launcher binding")
    if scripts["read_pinned_build_config.py"]["sha256"] != config["reader_sha256"]:
        raise ValueError("reader binding")
    qualified = json.loads((BASE / ROOTS["entry-qualification"] / "01-focused/SOURCE-AFTER.json").read_bytes())
    production = {n: v for n, v in qualified.items() if not n.startswith("test_") and n != "materialize_test_support"}
    if len(production) != 18: raise ValueError("current source set")
    for value in production.values():
        if identity(Path(value["path"])) != {k: value[k] for k in ("sha256", "bytes")}:
            raise ValueError("current source drift")
    current_tests = json.loads((BASE / ROOTS["portability-repair"] / "green-v2/PROCESS.json").read_bytes())["sources_after"]
    for value in current_tests.values():
        if identity(Path(value["path"])) != {k: value[k] for k in ("sha256", "bytes")}:
            raise ValueError("current test drift")
    save("SOURCE_FREEZE.json", dict(current_production_helpers=production, current_portability_tests=current_tests,
         scope="Current18 production/helper identities are separate from historical26/47 test closures; current4 portability test/helper files have the separate narrow9-control record."))
    save("INDEX.json", dict(schema="ocm.f1.materialization-records.v1", archives=rows, scripts=scripts,
         regular_members=sum(x["regular_members"] for x in rows.values()),
         raw_bytes=sum(x["raw_bytes"] for x in rows.values()),
         compressed_bytes=sum(x["archive"]["bytes"] for x in rows.values()),
         symlinks_metadata_only=sum(x["symlinks_metadata_only"] for x in rows.values()),
         packaging_wall_before_index_s=time.monotonic()-began,
         scope="Archival and byte readback only. No tests, native fixtures, controller, corpus materialization or build dispatched."))
    print(json.dumps(dict(archives=len(rows), members=sum(x["regular_members"] for x in rows.values()),
          raw_bytes=sum(x["raw_bytes"] for x in rows.values()), compressed_bytes=sum(x["archive"]["bytes"] for x in rows.values()))))


if __name__ == "__main__": main()
