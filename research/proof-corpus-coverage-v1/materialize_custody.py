"""Read-only materialization receipt and byte custody; never invokes Git or sources."""
from pathlib import Path
import hashlib
import os
import stat
import acquisition_contract as c
import materialize_objects as objects
import materialize_phase as phase


def same(left, right):
    return c.canonical(left) == c.canonical(right)


def workspace(result, root, deadline):
    ws = root / "workspace"
    if result["workspace"] != str(ws) or ws.resolve(strict=True) != ws:
        raise ValueError("WORKSPACE_PATH")
    observed = set()
    def fail(error): raise error
    for base, dirs, files in os.walk(ws, followlinks=False, onerror=fail):
        if Path(base) == ws:
            if ".git" not in dirs: raise ValueError("WORKSPACE_GIT")
            dirs.remove(".git")
        observed.update(str((Path(base) / n).relative_to(ws)) for n in dirs + files)
    if observed != set(result["entries"]): raise ValueError("WORKSPACE_MEMBERSHIP")
    for name, entry in result["entries"].items():
        objects.remaining(deadline); path = ws / name; mode = entry["mode"]
        if mode == "120000":
            if not path.is_symlink(): raise ValueError("WORKSPACE_LINK")
            raw = os.fsencode(os.readlink(path))
            if (os.readlink(path) != entry["target"] or len(raw) != entry["bytes"]
                or hashlib.sha256(raw).hexdigest() != entry["sha256"]):
                raise ValueError("WORKSPACE_LINK_DRIFT")
            if not path.resolve(strict=False).is_relative_to(ws) or (ws / ".git") in path.resolve(strict=False).parents:
                raise ValueError("WORKSPACE_LINK_ESCAPE")
        elif mode in ("40000", "040000"):
            if path.is_symlink() or not path.is_dir(): raise ValueError("WORKSPACE_DIRECTORY")
        elif mode in ("100644", "100755"):
            if (path.is_symlink() or not path.is_file()
                or objects.stamp(path) != {k: entry[k] for k in ("sha256", "bytes")}
                or stat.S_IMODE(path.stat().st_mode) != (0o755 if mode == "100755" else 0o644)):
                raise ValueError("WORKSPACE_BLOB")
        else: raise ValueError("WORKSPACE_MODE")
    if objects.file_map(ws / ".git", deadline) != result["git_metadata"]:
        raise ValueError("GIT_METADATA_DRIFT")
    for path in (ws / ".git").rglob("*"):
        if stat.S_IMODE(path.stat().st_mode) != (0o555 if path.is_dir() else 0o444):
            raise ValueError("GIT_METADATA_MODE")


def material(result, expected, root, request):
    deadline = request["start"]["whole_deadline_monotonic"]
    if (result.get("terminal") != "MATERIALIZED" or result.get("source_custody") != "UNCHANGED"
        or result.get("source") != expected["bare_path"]
        or result.get("commit") != expected["commit"] or result.get("tree") != expected["tree"]
        or not same(result.get("deadline_monotonic"), deadline)
        or not same(result.get("acquisition_reference"), request["reference"])):
        raise ValueError("MATERIAL_IDENTITY")
    wanted = {n + ".py": {k: request["sources"][n][k] for k in ("sha256", "bytes")}
              for n in ("materialize_git", "materialize_objects")}
    if not same(result["source_files"], wanted): raise ValueError("MATERIAL_SOURCE")
    if objects.file_map(expected["bare_path"], deadline) != expected["files"]:
        raise ValueError("BARE_POST_DRIFT")
    plumbing = objects.Git(root / "workspace/.git", root / "records", deadline, [])
    operations = [["--version"], ["fsck", "--full", "--strict", "--no-reflogs", "--no-dangling", expected["commit"]],
                  ["cat-file", "--batch"], ["read-tree", expected["commit"]],
                  ["write-tree"], ["rev-parse", "--verify", "HEAD"]]
    if len(result["commands"]) != len(operations): raise ValueError("MATERIAL_COMMAND_COUNT")
    for index, command in enumerate(result["commands"]):
        folder = root / "records" / ("%03d" % index)
        if (command["record"] != str(folder) or command.get("attempted") is not True
            or type(command.get("pid")) is not int or command["pid"] <= 0
            or type(command.get("returncode")) is not int or command["returncode"] != 0
            or command.get("reaped") is not True or command.get("group_absent") is not True
            or command.get("stdout_complete") is not True or command.get("error") or command.get("cleanup_error")):
            raise ValueError("MATERIAL_COMMAND")
        raw, _ = phase.read(folder / "RESULT.json")
        if not same(raw, command): raise ValueError("MATERIAL_COMMAND_RECEIPT")
        request, _ = phase.read(folder / "REQUEST.json")
        wanted = dict(argv=plumbing.base + operations[index], environment=plumbing.env,
                      attempted=False, pid=None, returncode=None)
        if (not same(request, wanted) or command["argv"] != wanted["argv"]
            or command["environment"] != wanted["environment"]):
            raise ValueError("MATERIAL_COMMAND_REQUEST")
        if set(command["streams"]) != {"stdin", "stdout", "stderr"}:
            raise ValueError("MATERIAL_COMMAND_STREAMS")
        for name, binding in command["streams"].items():
            if name not in ("stdin", "stdout", "stderr") or objects.stamp(folder / (name + ".bin")) != binding:
                raise ValueError("MATERIAL_COMMAND_RAW")
    if not result["commands"]: raise ValueError("MATERIAL_COMMAND_MISSING")
    workspace(result, root, deadline)


def verify(result, request, root):
    root = Path(root)
    if (result.get("terminal") != "ALL_MATERIALIZED" or result.get("output") != str(root)
        or result.get("semantic_checks_reached") != 0
        or not same(result.get("reference"), request["reference"])
        or len(result.get("materials", [])) != 10):
        raise ValueError("WORKER_RESULT")
    names = [r["name"] for r in request["materials"]]
    if len(names) != 10 or len(set(names)) != 10 or [r["name"] for r in result["materials"]] != names:
        raise ValueError("MATERIAL_DENOMINATOR")
    for row, expected in zip(result["materials"], request["materials"]):
        location = root / expected["name"]
        value, binding = phase.read(location / "RESULT.json")
        if row["receipt"] != binding or not same(row["result"], value):
            raise ValueError("MATERIAL_RECEIPT")
        material(value, expected, location, request)
    phase.clock(request["start"])
    return dict(terminal="TEN_MATERIALS_REVALIDATED", materials=10, semantic_checks_reached=0)
