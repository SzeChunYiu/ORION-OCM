"""Create-only immutable content files and exact consumed-byte validation."""
import hashlib,os,re
from pathlib import Path
from unary_contract import InputRefused
import unary_method_plain as D

def fsync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def read(root,digest,size,work):
    if type(digest) is not str or re.fullmatch("[0-9a-f]{64}",digest) is None:
        raise InputRefused("PAYLOAD_ID")
    p=root/(digest+".json")
    if p.is_symlink() or not p.is_file():raise InputRefused("PAYLOAD_MISSING")
    raw=p.read_bytes();D.bump(work,"payload_bytes_read",len(raw));D.bump(work,"payload_hashes")
    if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=digest:raise InputRefused("PAYLOAD_HASH")
    return raw

def validate(root,refs,work):
    if root.is_symlink() or not root.is_dir():raise InputRefused("PAYLOAD_ROOT")
    actual={p.name for p in root.iterdir()}
    if actual!={k+".json" for k in refs}:raise InputRefused("UNREFERENCED_OR_MISSING_PAYLOAD")
    return {k:read(root,k,n,work) for k,n in refs.items()}

def put(root,raw,work):
    digest=hashlib.sha256(raw).hexdigest();p=root/(digest+".json")
    if p.exists() or p.is_symlink():
        if read(root,digest,len(raw),work)!=raw:raise InputRefused("PAYLOAD_CHANGED")
    else:
        with p.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
        fsync_dir(root);D.bump(work,"payload_files_written");D.bump(work,"payload_bytes_written",len(raw))
    return digest

def freeze(value,work):
    D.bump(work,"decoded_nodes_frozen")
    if type(value) is dict:return ("dict",tuple((k,freeze(v,work)) for k,v in value.items()))
    if type(value) is list:return ("list",tuple(freeze(v,work) for v in value))
    return ("scalar",value)

def thaw(value,work):
    D.bump(work,"decoded_nodes_copied")
    kind,body=value
    if kind=="dict":return {k:thaw(v,work) for k,v in body}
    if kind=="list":return [thaw(v,work) for v in body]
    return body
