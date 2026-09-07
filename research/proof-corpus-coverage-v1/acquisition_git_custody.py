"""Byte custody checks for acquisition; no subprocess or network operation."""
import hashlib
import json
import os
from pathlib import Path
import stat

def _hash(path, kind=None):
    size = path.stat().st_size
    h = hashlib.sha1() if kind else hashlib.sha256()
    if kind:
        h.update((kind + " " + str(size) + "\0").encode())
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _files(root):
    result = {}
    def fail(error): raise error
    if not stat.S_ISDIR(root.lstat().st_mode): raise ValueError("MATERIAL_KIND")
    for parent, dirs, files in os.walk(root, onerror=fail):
        for name in dirs + files:
            p = Path(parent) / name
            mode = p.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)): raise ValueError("MATERIAL_KIND")
            if stat.S_ISREG(mode):
                result[str(p.relative_to(root))] = {"sha256": _hash(p), "bytes": p.stat().st_size}
    return result


def _tools():
    return {s: {"resolved": str(Path(s).resolve(strict=True)), "sha256": _hash(Path(s)),
                "bytes": Path(s).stat().st_size}
            for s in ("/usr/bin/git", "/usr/lib/git-core/git", "/usr/lib/git-core/git-remote-https",
                      "/etc/ssl/certs/ca-certificates.crt")}


def _verify(result, output, validator, production):
    root = Path(output).resolve()
    if result["output"] != str(root) or (production and result["transport"] != "PRODUCTION_SUBPROCESS"):
        raise ValueError("OUTPUT_OR_TRANSPORT_BINDING")
    if result["custody_source"] != LOADED_SOURCE_STAMP or _hash(Path(__file__)) != LOADED_SOURCE_STAMP["sha256"]:
        raise ValueError("CUSTODY_SOURCE_DRIFT")
    rows = validator((root / "lock.json").read_bytes())
    commands = result["commands"]
    if len(result["packages"]) != 9 or len(commands) != 55 or result["tools"] != _tools():
        raise ValueError("ACQUISITION_BINDING")
    for i, c in enumerate(commands):
        folder = root / "commands" / ("%03d" % i)
        if c["record"] != str((folder / "RESULT.json").relative_to(root)):
            raise ValueError("COMMAND_PATH")
        receipt = json.loads((folder / "RESULT.json").read_bytes())
        expected = {k: v for k, v in c.items() if k != "receipt_sha256"}
        if receipt != expected or _hash(folder / "RESULT.json") != c["receipt_sha256"]:
            raise ValueError("COMMAND_RECEIPT")
        request = json.loads((folder / "REQUEST.json").read_bytes())
        if _hash(folder / "REQUEST.json") != c["request_sha256"] or any(
                request[k] != c[k] for k in ("argv", "environment", "record")):
            raise ValueError("COMMAND_REQUEST")
        if c["attempted"] is not True or type(c["returncode"]) is not int or c["returncode"] != 0 or c["error"]:
            raise ValueError("COMMAND_NOT_SUCCESS")
        for key in ("stdout", "stderr"):
            path = folder / (key + ".bin")
            if c[key] != {"path": str(path.relative_to(root)), "sha256": _hash(path), "bytes": path.stat().st_size}:
                raise ValueError("COMMAND_RAW")
    for i, (expected, package) in enumerate(zip(rows, result["packages"])):
        repo = root / (expected["name"] + ".git")
        if any(package[k] != v for k, v in expected.items()) or package["state"] != "ACQUIRED" or package["bare_path"] != str(repo):
            raise ValueError("PACKAGE_BINDING")
        subset = commands[1 + 6*i:7 + 6*i]
        if package["commands"] != [c["record"] for c in subset]: raise ValueError("PACKAGE_COMMANDS")
        observed, commit, tree = [root / c["stdout"]["path"] for c in subset[2:5]]
        with commit.open("rb") as stream: first = stream.readline(100)
        if (observed.read_bytes() != (expected["rev"] + "\n").encode() or package["commit"] != expected["rev"]
                or _hash(commit, "commit") != expected["rev"] or first != ("tree " + package["tree"] + "\n").encode()
                or _hash(tree, "tree") != package["tree"]): raise ValueError("OBJECT_BINDING")
        if _files(repo) != package["files"]: raise ValueError("MATERIAL_DRIFT")
    return {"terminal": "MATERIAL_BYTES_REVALIDATED", "packages": len(rows)}


