"""Pinned source and parent archive custody. Native source is parsed, never run."""
from pathlib import Path
import io
import tarfile
from contract_v1 import require, sha, strict_json
from native_roles_v1 import native_contract

HERE = Path(__file__).resolve().parent


def bound_files(base=HERE):
    binding = strict_json((base / "SOURCE_BINDINGS_V1.json").read_bytes())
    files = {}
    for row in binding["files"]:
        path = base / row["path"]
        require(path.is_file() and not path.is_symlink(), "missing or linked source")
        data = path.read_bytes()
        require(len(data) == row["bytes"] and sha(data) == row["sha256"], "source byte drift")
        files[row["path"]] = data
    return binding, files


def current_contract(base=HERE):
    _, files = bound_files(base)
    return native_contract({n: files["raw/" + n] for n in ("native/vm.py", "native/morph.py")})


def retained_inputs(base=HERE):
    _, files = bound_files(base)
    binding = strict_json(files["raw/parent/FROZEN_INPUTS_V1.json"])
    data = files["raw/parent/PINNED_INPUTS_V1.tar.gz"]
    require(sha(data) == binding["archive_sha256"], "parent archive drift")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for item in archive.getmembers():
            require(item.isfile() and not item.issym() and not item.islnk(), "archive entry kind")
            require(item.name in binding["members"] and item.name not in result, "archive membership")
            row = binding["members"][item.name]
            payload = archive.extractfile(item).read()
            require(len(payload) == row["bytes"] and sha(payload) == row["sha256"], "archive member drift")
            result[item.name] = payload
    require(set(result) == set(binding["members"]), "missing archive entry")
    return result
