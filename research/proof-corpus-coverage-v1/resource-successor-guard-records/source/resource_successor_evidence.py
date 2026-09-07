"""Authenticate historical and successor resource archives; never execute their sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import types

HISTORICAL_SHA256 = "2457516e82e1b07062360655dc0dfbce772f3b72aa16379bcfadb23eb6ae00e0"
GUARD_SHA256 = "b6d0909df6c6d3ee8818a548b09a8b53f20ded184617340a44aaa3723a762703"
SEAL_SHA256 = "3d900f8700445844c1b3c926a1ff150f702c43f841e94a208608ff171645d8c7"

def helpers():
    path=Path(__file__).resolve().parent/"resource_evidence.py"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>65536:
        raise ValueError("HISTORICAL_GUARD_FILE")
    source=path.read_bytes()
    if hashlib.sha256(source).hexdigest()!=GUARD_SHA256:raise ValueError("HISTORICAL_GUARD_IDENTITY")
    module=types.ModuleType("historical_resource_guard");module.__file__=str(path)
    exec(compile(source,str(path),"exec"),module.__dict__)
    return module,module.shared()

def binding(record):return {key:record[key] for key in ("bytes","sha256")}
def fail_walk(error):raise error

def file_set(root):
    if root.is_symlink() or not root.is_dir():raise ValueError("SUCCESSOR_PACKAGE_PATH")
    files=set()
    for directory,dirs,names in os.walk(root,followlinks=False,onerror=fail_walk):
        for name in dirs+names:
            path=Path(directory)/name
            if path.is_symlink():raise ValueError("SUCCESSOR_PACKAGE_PATH")
            if name in names:
                if not path.is_file():raise ValueError("SUCCESSOR_PACKAGE_PATH")
                files.add(path.relative_to(root).as_posix())
    return files

def package(audit,root,expected):
    if not isinstance(expected,str) or not re.fullmatch("[0-9a-f]{64}",expected):
        raise ValueError("SUCCESSOR_SEAL_FORMAT")
    actual=file_set(root)
    seal_raw=audit.read_file(root/"SEAL.json",audit.MAX_ARCHIVE_BYTES)
    if hashlib.sha256(seal_raw).hexdigest()!=expected:raise ValueError("SUCCESSOR_SEAL_HASH")
    seal=audit.parse(seal_raw)
    if (set(seal)!={"schema","terminal","files"} or seal["terminal"]!="COMPLETE"
            or seal["schema"]!="ocm.f1.resource-successor-seal.v1"):
        raise ValueError("SUCCESSOR_SEAL_SCHEMA")
    if actual!=set(seal["files"])|{"SEAL.json"}:raise ValueError("SUCCESSOR_PACKAGE_SET")
    values={}
    for name,record in seal["files"].items():
        audit.safe_name(name)
        values[name]=audit.checked(audit.read_file(root/name,audit.MAX_ARCHIVE_BYTES),record,"SUCCESSOR_FILE_HASH")
    return values

def archives(audit,root,values,rows):
    seen=set();maps={};members=total=0
    for row in rows:
        name=audit.safe_name(row["archive"]);inventory=audit.safe_name(row["member_map"]["file"])
        if name in seen:raise ValueError("DUPLICATE_SUCCESSOR_ARCHIVE")
        seen.add(name)
        if name not in values or inventory not in values:raise ValueError("SUCCESSOR_UNSEALED_ARCHIVE")
        if any(type(row[k]) is not int or row[k]<0 for k in ("members","raw_bytes")):
            raise ValueError("SUCCESSOR_COUNT_TYPE")
        audit.checked(values[name],binding(row),"SUCCESSOR_ARCHIVE_HASH")
        audit.checked(values[inventory],binding(row["member_map"]),"SUCCESSOR_MEMBER_MAP_HASH")
        maps[name]=audit.parse(values[inventory])
        result=audit.audit_archive(root/name,maps[name])
        if result!={"members":row["members"],"bytes":row["raw_bytes"]}:raise ValueError("SUCCESSOR_COUNTS")
        members+=result["members"];total+=result["bytes"]
    if seen!={n for n in values if n.endswith(".tar.gz")}:raise ValueError("SUCCESSOR_ARCHIVE_SET")
    return maps,members,total

def source_freeze(audit,raw):
    freeze=audit.parse(raw)
    if type(freeze["count"]) is not int or freeze["count"]<1 or freeze["count"]!=len(freeze["files"]):
        raise ValueError("SUCCESSOR_SOURCE_COUNT")
    for name in freeze["files"]:
        audit.safe_name(name)
        if "/" in name:raise ValueError("SUCCESSOR_SOURCE_PATH")
    return freeze

def snapshot(audit,members,freeze,raw,prefix):
    expected={prefix+"SOURCE_FREEZE.json":{"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}}
    expected.update({prefix+"source/"+n:binding(r) for n,r in freeze["files"].items()})
    for name,record in expected.items():
        if members.get(name)!=record:raise ValueError("SUCCESSOR_SNAPSHOT_BINDING")

def check_current(audit,current,freeze):
    if current.is_symlink() or not current.is_dir():raise ValueError("SUCCESSOR_SOURCE_PATH")
    for name,record in freeze["files"].items():
        path=current/name
        try:path.resolve().relative_to(current.resolve())
        except ValueError as exc:raise ValueError("SUCCESSOR_SOURCE_PATH") from exc
        audit.checked(audit.read_file(path,audit.MAX_MEMBER_BYTES),binding(record),"CURRENT_SUCCESSOR_SOURCE")

def audit_successor(root,expected_seal=SEAL_SHA256,source_root=None,historical_root=None,
                    expected_historical=HISTORICAL_SHA256):
    old,audit=helpers();root=Path(root)
    current=Path(source_root) if source_root is not None else Path(__file__).resolve().parent
    history=Path(historical_root) if historical_root is not None else root.parent/"resource-records"
    values=package(audit,root,expected_seal);index=audit.parse(values["INDEX.json"])
    if index["schema"]!="ocm.f1.resource-successor-index.v1":raise ValueError("SUCCESSOR_INDEX_SCHEMA")
    prior=index["historical"]
    if prior["seal_sha256"]!=expected_historical:raise ValueError("HISTORICAL_AUTHORITY")
    dirname=audit.safe_name(prior["source_dir"])
    if type(prior["source_count"]) is not int or prior["source_count"]<1:raise ValueError("HISTORICAL_SOURCE_COUNT")
    file_set(history)
    old_result=old.audit_resource(history,expected_historical,root/dirname)
    old_seal_raw=audit.read_file(history/"SEAL.json",audit.MAX_ARCHIVE_BYTES)
    if hashlib.sha256(old_seal_raw).hexdigest()!=expected_historical:raise ValueError("HISTORICAL_AUTHORITY")
    old_seal=audit.parse(old_seal_raw)
    def retained(name):
        return audit.checked(audit.read_file(history/name,audit.MAX_ARCHIVE_BYTES),old_seal["files"][name],"HISTORICAL_FILE_HASH")
    old_raw=retained("SOURCE_FREEZE.json");old_freeze=source_freeze(audit,old_raw)
    old_map=audit.parse(retained("final-qualification.members.json"))
    snapshot(audit,old_map,old_freeze,old_raw,"qualification/")
    names={dirname+"/"+n for n in old_freeze["files"]}
    if names!={n for n in values if n.startswith(dirname+"/")}:raise ValueError("HISTORICAL_SOURCE_SET")
    if prior["source_count"]!=old_freeze["count"]:raise ValueError("HISTORICAL_SOURCE_COUNT")
    for key,name in [("source_freeze","SOURCE_FREEZE.json"),("result","RESULT.json")]:
        audit.checked(values[name],index[key],"SUCCESSOR_"+key.upper()+"_HASH")
    omission=index["omissions"];omitted_name=audit.safe_name(omission["file"])
    audit.checked(values[omitted_name],binding(omission),"SUCCESSOR_OMISSION_BINDING")
    if not isinstance(omission["scope"],str) or not omission["scope"]:raise ValueError("SUCCESSOR_OMISSION_SCOPE")
    maps,count,total=archives(audit,root,values,index["archives"])
    freeze=source_freeze(audit,values["SOURCE_FREEZE.json"])
    snapshot(audit,maps["final-qualification.tar.gz"],freeze,values["SOURCE_FREEZE.json"],"")
    check_current(audit,current,freeze)
    package(audit,root,expected_seal)
    if file_set(history)!=set(old_seal["files"])|{"SEAL.json"}:
        raise ValueError("HISTORICAL_PACKAGE_SET")
    for name in old_seal["files"]:retained(name)
    if audit.read_file(history/"SEAL.json",audit.MAX_ARCHIVE_BYTES)!=old_seal_raw:
        raise ValueError("HISTORICAL_AUTHORITY")
    check_current(audit,current,freeze)
    return {"terminal":"RESOURCE_SUCCESSOR_CUSTODY_PASS","historical_archive_members":old_result["archive_members"],
            "historical_sources":old_freeze["count"],"successor_archive_members":count,"successor_raw_bytes":total,
            "current_sources":freeze["count"],"omitted_host_inputs_revalidated":False,
            "scope":"Historical archived snapshots and separately current successor sources; no archived source, resource, native or corpus execution"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parent/"resource-successor-records")
    parser.add_argument("--seal-sha256",default=SEAL_SHA256)
    args=parser.parse_args()
    try:result=audit_successor(args.root,args.seal_sha256);code=0
    except Exception as exc:result={"terminal":"CANNOT_CHECK_RESOURCE_SUCCESSOR_CUSTODY","reason":str(exc)};code=2
    print(json.dumps(result,sort_keys=True,separators=(",",":")));return code

if __name__=="__main__":raise SystemExit(main())
