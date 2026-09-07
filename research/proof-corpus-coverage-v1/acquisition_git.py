"""Pinned, sequential source acquisition. No checkout, package command or retry."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

LOCK_SHA256 = "435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf"


_CUSTODY_PATH = Path(__file__).with_name("acquisition_git_custody.py")
_CUSTODY_BYTES = _CUSTODY_PATH.read_bytes()
_CUSTODY_SHA256 = "ce7c0b520cd9662a34de670bee9be4b3ef8870612b017340db2180e588bf2fb4"
if hashlib.sha256(_CUSTODY_BYTES).hexdigest() != _CUSTODY_SHA256:
    raise ValueError("CUSTODY_SOURCE_IDENTITY")
CUSTODY_SOURCE_STAMP = {"path": str(_CUSTODY_PATH), "sha256": _CUSTODY_SHA256, "bytes": len(_CUSTODY_BYTES)}
_custody = {"__file__": str(_CUSTODY_PATH), "__name__": "acquisition_frozen_custody",
            "LOADED_SOURCE_STAMP": CUSTODY_SOURCE_STAMP}
exec(compile(_CUSTODY_BYTES, str(_CUSTODY_PATH), "exec"), _custody)
_hash, _files, _tools, _verify = [_custody[n] for n in ("_hash", "_files", "_tools", "_verify")]

def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("DUPLICATE_KEY")
        value[key] = item
    return value


def _validate(raw, expected):
    if type(raw) is not bytes or len(raw) > 65536 or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("LOCK_IDENTITY")
    obj = json.loads(raw, object_pairs_hook=_pairs)
    if type(obj) is not dict or obj.get("version") != "1.2.0":
        raise ValueError("LOCK_FORMAT")
    packages = obj.get("packages")
    if type(packages) is not list or len(packages) != 9:
        raise ValueError("LOCK_DENOMINATOR")
    rows = []
    for item in packages:
        if type(item) is not dict or item.get("type") != "git" or item.get("subDir", 1) is not None:
            raise ValueError("GIT_ONLY_NO_SUBDIR")
        row = {key: item.get(key) for key in ("name", "url", "rev")}
        patterns = {"name": r"[A-Za-z][A-Za-z0-9_-]*",
                    "url": r"https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+",
                    "rev": r"[0-9a-f]{40}"}
        if any(type(row[k]) is not str or not re.fullmatch(v, row[k]) for k, v in patterns.items()):
            raise ValueError("UNPINNED_OR_UNSAFE_ROW")
        if any(row["name"] == old["name"] or row["url"] == old["url"] for old in rows):
            raise ValueError("DUPLICATE_PACKAGE")
        rows.append(row)
    return rows


def validate_lock(raw):
    """Only the registered corpus lock is production authority; inputRev is provenance."""
    return _validate(raw, LOCK_SHA256)


def _save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")


def _run(argv, env, stdout, stderr):
    return subprocess.run(argv, env=env, cwd=env["HOME"], stdin=subprocess.DEVNULL,
                          stdout=stdout, stderr=stderr, check=False).returncode


def _acquire(lock_path, output, transport, validator):
    root = Path(output).resolve()
    root.mkdir(mode=0o700)  # Existing output is never reused.
    start = time.monotonic()
    result = {"terminal": "ACQUISITION_FAILED", "output": str(root), "packages": [],
              "commands": [], "transport": "PRODUCTION_SUBPROCESS" if transport is _run
              else "INJECTED_TEST_TRANSPORT"}
    try:
        with Path(lock_path).open("rb") as stream: raw = stream.read(65537)
        rows = validator(raw)
        (root / "lock.json").write_bytes(raw)
        result["lock_sha256"] = hashlib.sha256(raw).hexdigest()
        result["packages"] = [{**r, "state": "NOT_RUN", "commands": [],
                               "bare_path": str(root / (r["name"] + ".git"))} for r in rows]
        for name in ("home", "hooks", "template", "commands"):
            (root / name).mkdir()
        env = {"PATH": "/usr/bin:/bin", "HOME": str(root / "home"),
               "XDG_CONFIG_HOME": str(root / "home"), "LC_ALL": "C", "TZ": "UTC",
               "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": "/dev/null",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
               "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
               "GIT_ALLOW_PROTOCOL": "https", "GIT_PROTOCOL_FROM_USER": "0",
               "GIT_EXEC_PATH": "/usr/lib/git-core"}
        settings = ["core.hooksPath=" + str(root / "hooks"), "init.templateDir=" + str(root / "template"),
                    "credential.helper=", "core.askPass=/bin/false", "http.proxy=",
                    "http.followRedirects=false", "http.sslVerify=true", "protocol.allow=never",
                    "protocol.https.allow=always", "fetch.fsckObjects=true",
                    "transfer.fsckObjects=true", "gc.auto=0", "core.logAllRefUpdates=false"]
        base = ["/usr/bin/git", "--no-pager", "--no-replace-objects"]
        for setting in settings:
            base += ["-c", setting]

        def command(args, package=None):
            folder = root / "commands" / ("%03d" % len(result["commands"]))
            folder.mkdir()
            child_env = {**env, "GIT_ALLOW_PROTOCOL": "https" if "fetch" in args else ""}
            deny = [] if "fetch" in args else ["-c", "protocol.https.allow=never"]
            c = {"argv": base + deny + args, "environment": child_env, "attempted": False,
                 "returncode": None, "error": None, "record": str((folder / "RESULT.json").relative_to(root))}
            _save(folder / "REQUEST.json", c)
            c["request_sha256"] = _hash(folder / "REQUEST.json")
            result["commands"].append(c)
            if package is not None:
                package["commands"].append(c["record"])
            began = time.monotonic()
            try:
                with (folder / "stdout.bin").open("xb") as out, (folder / "stderr.bin").open("xb") as err:
                    c["attempted"] = True
                    c["returncode"] = transport(c["argv"], child_env, out, err)
            except BaseException as exc:
                c["error"] = type(exc).__name__ + ": " + str(exc)
            finally:
                c["wall_s"] = time.monotonic() - began
                for key in ("stdout", "stderr"):
                    path = folder / (key + ".bin")
                    c[key] = {"path": str(path.relative_to(root)), "sha256": _hash(path),
                              "bytes": path.stat().st_size}
                _save(folder / "RESULT.json", c)
                c["receipt_sha256"] = _hash(folder / "RESULT.json")
            if c["error"] or type(c["returncode"]) is not int or c["returncode"] != 0:
                raise ValueError("COMMAND_FAILED: " + (c["error"] or str(c["returncode"])))
            return folder / "stdout.bin"

        result["custody_source"] = CUSTODY_SOURCE_STAMP.copy()
        result["tools"] = _tools()
        version = command(["--version"])
        if version.read_bytes() != b"git version 2.25.1\n":
            raise ValueError("GIT_VERSION")
        for p in result["packages"]:
            p["state"] = "FAILED"
            repo = Path(p["bare_path"])
            command(["init", "--bare", str(repo)], p)
            command(["-C", str(repo), "fetch", "--depth=1", "--no-auto-gc",
                     "--no-tags", "--no-recurse-submodules", p["url"], p["rev"]], p)
            observed = command(["-C", str(repo), "rev-parse", "--verify", "FETCH_HEAD^{commit}"], p)
            if observed.read_bytes() != (p["rev"] + "\n").encode():
                raise ValueError("COMMIT_IDENTITY")
            commit = command(["-C", str(repo), "cat-file", "commit", p["rev"]], p)
            if _hash(commit, "commit") != p["rev"]:
                raise ValueError("COMMIT_OBJECT_IDENTITY")
            with commit.open("rb") as stream:
                first = stream.readline(100)
            if not re.fullmatch(rb"tree [0-9a-f]{40}\n", first):
                raise ValueError("COMMIT_TREE_HEADER")
            tree = first[5:-1].decode()
            payload = command(["-C", str(repo), "cat-file", "tree", tree], p)
            if _hash(payload, "tree") != tree:
                raise ValueError("TREE_OBJECT_IDENTITY")
            command(["-C", str(repo), "fsck", "--full", "--strict", "--no-reflogs",
                     "--no-dangling", p["rev"]], p)
            p.update(state="ACQUIRED", commit=p["rev"], tree=tree, files=_files(repo))
        if Path(lock_path).read_bytes() != raw:
            raise ValueError("LOCK_SOURCE_DRIFT")
        _verify(result, root, validator, transport is _run)
        result["terminal"] = "ACQUIRED"
    except BaseException as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)
    result["wall_s"] = time.monotonic() - start
    result["bytes_before_result"] = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    _save(root / "RESULT.json", result)
    return result


def acquire(lock_path, output):
    """Fixed production authority. Caller supplies aggregate limits and process cleanup."""
    return _acquire(lock_path, output, _run, validate_lock)


def revalidate(result, output):
    """Custody only; caller binds the result and expected material root externally."""
    root = Path(output).resolve()
    if json.loads((root / "RESULT.json").read_bytes()) != result or result["terminal"] != "ACQUIRED":
        raise ValueError("RESULT_BINDING")
    return _verify(result, root, validate_lock, True)
