"""Small local Git objects only; no source checkout, hooks, remote or Lean."""
import os
from pathlib import Path
import subprocess


def git(root, *args, data=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Corpus fixture", GIT_COMMITTER_NAME="Corpus fixture",
               GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    return subprocess.check_output(["/usr/bin/git", "-C", str(root), *args],
                                   input=data, env=env, stderr=subprocess.PIPE)


def repository(root, files):
    root = Path(root)
    root.mkdir()
    git(root, "init", "-q", "--template=")
    for name, value in files.items():
        mode, body = value if isinstance(value, tuple) else ("100644", value)
        body = body.encode() if isinstance(body, str) else body
        oid = git(root, "hash-object", "-w", "--stdin", data=body).decode().strip()
        git(root, "update-index", "--add", "--cacheinfo", mode, oid, name)
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            path.symlink_to(body.decode())
        else:
            path.write_bytes(body)
    tree = git(root, "write-tree").decode().strip()
    commit = git(root, "commit-tree", tree, data=b"authored fixture\n").decode().strip()
    return commit
