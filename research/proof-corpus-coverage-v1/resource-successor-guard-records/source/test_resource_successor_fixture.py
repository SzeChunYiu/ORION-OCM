"""Authored archive data only; no resource controller imports or execution."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

def raw(value): return (json.dumps(value,sort_keys=True,separators=(",", ":"))+"\n").encode()
def binding(data): return {"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
def archive(members):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode="w",format=tarfile.USTAR_FORMAT) as tar:
        for name,data in members:
            item=tarfile.TarInfo(name);item.size=len(data);tar.addfile(item,io.BytesIO(data))
    return gzip.compress(stream.getvalue(),mtime=0)
def seal(root,schema):
    data=raw({"schema":schema,"terminal":"COMPLETE","files":{
        x.relative_to(root).as_posix():binding(x.read_bytes()) for x in root.rglob("*")
        if x.is_file() and x.relative_to(root).as_posix()!="SEAL.json"}})
    (root/"SEAL.json").write_bytes(data);return binding(data)["sha256"]
def freeze(data):
    return raw({"schema":"ocm.f1.resource-freeze.v1","count":1,"files":{
        "a.py":{**binding(data),"origin":"/unopened/host/a.py","snapshot":"/unopened/snapshot/a.py"}}})
def put_archive(root,values):
    packed=archive(list(values.items()));members=raw({n:binding(b) for n,b in values.items()})
    (root/"final-qualification.tar.gz").write_bytes(packed)
    (root/"final-qualification.members.json").write_bytes(members)
    return {"archive":"final-qualification.tar.gz",**binding(packed),"members":len(values),
            "raw_bytes":sum(map(len,values.values())),"member_map":{
                "file":"final-qualification.members.json",**binding(members)}}
def make_fixture(base):
    old=base/"resource-records";old.mkdir();new=base/"resource-successor-records";new.mkdir()
    current=base/"current";current.mkdir();history=new/"historical-source";history.mkdir()
    before=b"raise SystemExit('historical resource must never execute')\n"
    after=b"raise SystemExit('current resource must never execute')\n"
    (current/"a.py").write_bytes(after);(history/"a.py").write_bytes(before)
    oldfreeze=freeze(before);newfreeze=freeze(after);result=raw({"terminal":"AUTHORED_CONTROL_DATA"})
    for root,fr,code in [(old,oldfreeze,before),(new,newfreeze,after)]:
        (root/"SOURCE_FREEZE.json").write_bytes(fr);(root/"RESULT.json").write_bytes(result)
        prefix="qualification/" if root==old else ""
        row=put_archive(root,{prefix+"SOURCE_FREEZE.json":fr,prefix+"source/a.py":code})
        index={"schema":"ocm.f1.resource-evidence-archive.v1","source_freeze":binding(fr),
               "result":binding(result),"archives":[row]}
        (root/"INDEX.json").write_bytes(raw(index))
    oldpin=seal(old,"ocm.f1.resource-evidence-seal.v1")
    index=json.loads((new/"INDEX.json").read_bytes());index["schema"]="ocm.f1.resource-successor-index.v1"
    index["historical"]={"seal_sha256":oldpin,"source_dir":"historical-source","source_count":1}
    host=raw({"inputs":[{"path":"/unopened/host/library",**binding(b"not read")}],"scope":"metadata only"})
    (new/"HOST-INPUTS.json").write_bytes(host)
    index["omissions"]={"file":"HOST-INPUTS.json",**binding(host),"scope":"not revalidated"}
    (new/"INDEX.json").write_bytes(raw(index))
    return new,old,current,oldpin
