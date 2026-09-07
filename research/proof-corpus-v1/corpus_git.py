"""Read existing local pinned Git objects, one blob at a time; never checkout/fetch."""
import hashlib
from pathlib import PurePosixPath
import re
import subprocess
import tempfile
from corpus_contract import CorpusError, commit_identity, sha256
from corpus_tree import selected_entries


def git_environment(home):
    return {"PATH": "/usr/bin:/bin", "HOME": str(home), "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
            "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}


def object_hash(kind, body):
    return hashlib.sha1(kind.encode() + b" " + str(len(body)).encode() + b"\0" + body).hexdigest()


def parse_tree(data):
    if data and not data.endswith(b"\0"):
        raise CorpusError("SOURCE_TREE", "missing terminator")
    rows, seen = [], set()
    for raw in data.split(b"\0"):
        if not raw:
            continue
        try:
            header, path = raw.split(b"\t", 1)
            mode, kind, oid = header.decode("ascii").split()
            path = path.decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise CorpusError("SOURCE_TREE", "malformed entry") from exc
        parts = PurePosixPath(path).parts
        if not path or path.startswith("/") or any(p in (".", "..") for p in path.split("/")) or "\\" in path:
            raise CorpusError("SOURCE_PATH", path)
        if not parts or path in seen or any(ord(c) < 32 for c in path):
            raise CorpusError("SOURCE_PATH", path)
        if mode != "100644" or kind != "blob":
            raise CorpusError("SOURCE_MODE", path)
        if not re.fullmatch("[0-9a-f]{40}", oid):
            raise CorpusError("SOURCE_OBJECT", path)
        seen.add(path)
        rows.append({"path": path, "mode": mode, "oid": oid})
    return rows


def read_blob_reply(stream, expected_oid):
    header = stream.readline(256)
    match = re.fullmatch(rb"([0-9a-f]{40}) blob ([0-9]+)\n", header)
    if match is None or match[1].decode() != expected_oid:
        raise CorpusError("SOURCE_BLOB_FRAME")
    remaining = int(match[2])
    chunks = []
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            raise CorpusError("SOURCE_BLOB_TRUNCATED")
        chunks.append(chunk)
        remaining -= len(chunk)
    body = b"".join(chunks)
    if stream.read(1) != b"\n" or object_hash("blob", body) != expected_oid:
        raise CorpusError("SOURCE_BLOB_IDENTITY")
    return body


class Snapshot:
    def __init__(self, root, commit):
        commit_identity(commit)
        self.root, self.commit = str(root), commit
        self.metrics = {"blob_bytes_read": 0, "largest_blob_bytes": 0,
                        "metadata_bytes_read": 0, "git_commands": 0}
        self.entries, self.tree, self._home = [], None, None
        self._consumed = False
        self.tree_objects = {}
        self._tree_payloads = {}

    def _command(self, *args):
        return ["/usr/bin/git", "--no-replace-objects", "-c", "protocol.allow=never",
                "-C", self.root, *args]

    def _read(self, *args):
        self.metrics["git_commands"] += 1
        try:
            data = subprocess.check_output(self._command(*args), env=self.env,
                                           stderr=subprocess.PIPE, timeout=60)
        except (subprocess.SubprocessError, OSError) as exc:
            raise CorpusError("SOURCE_GIT_READ", type(exc).__name__) from exc
        self.metrics["metadata_bytes_read"] += len(data)
        return data

    def _verified_tree(self, oid):
        if oid not in self._tree_payloads:
            raw = self._read("cat-file", "tree", oid)
            if object_hash("tree", raw) != oid:
                raise CorpusError("SOURCE_TREE_IDENTITY", oid)
            self.tree_objects[oid] = {"sha256": sha256(raw), "bytes": len(raw)}
            self._tree_payloads[oid] = raw
        return self._tree_payloads[oid]

    def __enter__(self):
        self._home = tempfile.TemporaryDirectory(prefix="ocm-corpus-git-")
        self.env = git_environment(self._home.name)
        try:
            raw = self._read("cat-file", "commit", self.commit)
            if object_hash("commit", raw) != self.commit:
                raise CorpusError("SOURCE_COMMIT_IDENTITY")
            match = re.match(rb"tree ([0-9a-f]{40})\n", raw)
            if not match:
                raise CorpusError("SOURCE_COMMIT_TREE")
            self.tree = match[1].decode()
            self.entries = selected_entries(self.tree, self._verified_tree)
            self.metrics["verified_tree_objects"] = len(self.tree_objects)
            self._tree_payloads.clear()
            return self
        except BaseException:
            self._home.cleanup()
            raise

    def blobs(self):
        if self._consumed:
            raise CorpusError("SOURCE_ALREADY_CONSUMED")
        self._consumed = True
        self.metrics["git_commands"] += 1
        with tempfile.TemporaryFile() as errors:
            proc = subprocess.Popen(self._command("cat-file", "--batch"), env=self.env,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors)
            try:
                for row in self.entries:
                    proc.stdin.write((row["oid"] + "\n").encode())
                    proc.stdin.flush()
                    body = read_blob_reply(proc.stdout, row["oid"])
                    self.metrics["blob_bytes_read"] += len(body)
                    self.metrics["largest_blob_bytes"] = max(self.metrics["largest_blob_bytes"], len(body))
                    yield dict(row, body=body, sha256=sha256(body), bytes=len(body))
                proc.stdin.close()
                if proc.wait(timeout=60) != 0:
                    raise CorpusError("SOURCE_GIT_READ", "cat-file exit")
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                for stream in (proc.stdin, proc.stdout):
                    if not stream.closed:
                        stream.close()

    def __exit__(self, *exc):
        self._home.cleanup()
