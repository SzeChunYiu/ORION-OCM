"""Full immutable unit membership and expected payload authority."""
import json
import os
import stat
from pathlib import Path
from sources_v1 import sha,verify_sources

def regular_files(root):
    root=Path(root)
    if root.is_symlink():
        raise ValueError("unit root is a link")
    found={}
    def walk(directory):
        with os.scandir(directory) as entries:
            for item in entries:
                path=Path(item.path)
                mode=item.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    raise ValueError("symlink in unit")
                if stat.S_ISDIR(mode):
                    walk(path)
                elif stat.S_ISREG(mode):
                    found[path.relative_to(root).as_posix()]=path
                else:
                    raise ValueError("nonregular entry")
    walk(root)
    return found

def verify(root):
    root=Path(root)
    found=regular_files(root)
    raw=found["MANIFEST_V1.json"].read_bytes()
    manifest=json.loads(raw)
    if set(manifest)!={"schema","payloads"} or manifest["schema"]!="MTR_MANIFEST_V1":
        raise ValueError("invalid manifest")
    rows=manifest["payloads"]
    names=[row["path"] for row in rows]
    if len(names)!=len(set(names)) or set(found)!=(set(names)|{"MANIFEST_V1.json"}):
        raise ValueError("complete membership mismatch")
    for row in rows:
        if set(row)!={"path","bytes","sha256"}:
            raise ValueError("invalid binding")
        data=found[row["path"]].read_bytes()
        if len(data)!=row["bytes"] or sha(data)!=row["sha256"]:
            raise ValueError("payload mismatch: "+row["path"])
    verify_sources(root)
    return raw,found["RECEIPT_V1.json"].read_bytes()
