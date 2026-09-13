"""Read the immutable archive in memory; no extraction or historical code execution."""
from pathlib import Path, PurePosixPath
import io
import tarfile
from contract_v1 import require, sha, strict_json

HERE = Path(__file__).resolve().parent
BINDING_SHA = "e9f2ed135d8231b522c09bc7e3da5815fd49892bd5b1b198fad6176e6afb1b53"


def read_archive(data, binding):
    require(sha(data) == binding["archive_sha256"], "archive byte binding drift")
    expected = binding["members"]
    result = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for item in archive.getmembers():
            path = PurePosixPath(item.name)
            require(item.isfile() and not item.issym() and not item.islnk(),
                    "nonregular archive member")
            require(not path.is_absolute() and ".." not in path.parts and
                    str(path) == item.name, "noncanonical archive path")
            require(item.name in expected and item.name not in result,
                    "unregistered or duplicate archive member")
            row = expected[item.name]
            require(item.size == row["bytes"], "archive member size drift")
            value = archive.extractfile(item).read()
            require(sha(value) == row["sha256"], "archive member hash drift")
            result[item.name] = value
    require(set(result) == set(expected), "missing archive member")
    return result


def load_inputs(base=HERE):
    path = base / "FROZEN_INPUTS_V1.json"
    require(path.is_file() and not path.is_symlink(), "missing/linked input authority")
    raw = path.read_bytes()
    require(sha(raw) == BINDING_SHA, "input authority drift")
    binding = strict_json(raw)
    archive = base / binding["archive"]
    require(archive.is_file() and not archive.is_symlink(), "missing/linked archive")
    return binding, read_archive(archive.read_bytes(), binding)
