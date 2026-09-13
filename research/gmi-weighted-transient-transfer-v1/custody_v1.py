"""Complete source-bound membership and pre/post worker identity."""
import hashlib
import json
import os
import stat
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def regular_files(root):
    found={}
    def walk(directory):
        with os.scandir(directory) as entries:
            for item in entries:
                path=Path(item.path)
                mode=item.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    raise ValueError("symlink in frozen unit")
                if stat.S_ISDIR(mode):
                    walk(path)
                elif stat.S_ISREG(mode):
                    found[path.relative_to(root).as_posix()]=path
                else:
                    raise ValueError("nonregular entry in frozen unit")
    walk(root)
    return found

def verify(root):
    root=Path(root)
    found=regular_files(root)
    raw=found["MANIFEST_V1.json"].read_bytes()
    manifest=json.loads(raw)
    if set(manifest)!={"schema","payloads"} or manifest["schema"]!="WTT_MANIFEST_V1":
        raise ValueError("invalid manifest")
    rows=manifest["payloads"]
    names=[row["path"] for row in rows]
    if len(names)!=len(set(names)) or set(found)!=(set(names)|{"MANIFEST_V1.json"}):
        raise ValueError("complete membership mismatch")
    for row in rows:
        if set(row)!={"path","bytes","sha256"}:
            raise ValueError("invalid payload binding")
        data=found[row["path"]].read_bytes()
        if len(data)!=row["bytes"] or sha(data)!=row["sha256"]:
            raise ValueError("payload binding mismatch: "+row["path"])
    parents=json.loads(found["PARENT_BINDINGS_V1.json"].read_bytes())
    if len(parents)!=4 or {r["label"] for r in parents}!={"ARC","FMT","CMP","SPS"}:
        raise ValueError("parent coverage mismatch")
    for row in parents:
        data=found[row["copy"]].read_bytes()
        if row["commit"]!="df777cd79ba5ec6925fd82552e9341f8d73f3577":
            raise ValueError("parent source identity mismatch")
        if sha(data)!=row["sha256"] or len(data)!=row["bytes"]:
            raise ValueError("parent bytes mismatch")
    return raw,found["RECEIPT_V1.json"].read_bytes()
