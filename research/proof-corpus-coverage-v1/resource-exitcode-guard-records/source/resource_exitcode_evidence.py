"""Additive exit-code correction custody, keeping both earlier qualifications historical."""
import argparse
import hashlib
import json
from pathlib import Path
import types

HELPER_SHA256 = "2d15a21e2c20bfc9063721e94848ab441f12cf8227c45c4ea5d4732eccfc8fec"
PRIOR_SHA256 = "3d900f8700445844c1b3c926a1ff150f702c43f841e94a208608ff171645d8c7"
HISTORICAL_SHA256 = "2457516e82e1b07062360655dc0dfbce772f3b72aa16379bcfadb23eb6ae00e0"
SEAL_SHA256 = "9c36d2396ab1ed8f94e54c810d2486488b869174e413d21635ca32d64143b39e"

def helper():
    path=Path(__file__).resolve().parent/"resource_successor_evidence.py"
    if path.is_symlink() or not path.is_file() or path.stat().st_size>65536:
        raise ValueError("EXITCODE_HELPER_FILE")
    source=path.read_bytes()
    if hashlib.sha256(source).hexdigest()!=HELPER_SHA256:raise ValueError("EXITCODE_HELPER_IDENTITY")
    module=types.ModuleType("resource_prior_custody");module.__file__=str(path)
    exec(compile(source,str(path),"exec"),module.__dict__)
    return module

def audit_exitcode(root,expected_seal=SEAL_SHA256,source_root=None,prior_root=None,historical_root=None,
                   expected_prior=PRIOR_SHA256,expected_historical=HISTORICAL_SHA256):
    base=helper();_,audit=base.helpers();root=Path(root)
    current=Path(source_root) if source_root is not None else Path(__file__).resolve().parent
    prior=Path(prior_root) if prior_root is not None else root.parent/"resource-successor-records"
    historical=Path(historical_root) if historical_root is not None else root.parent/"resource-records"
    values=base.package(audit,root,expected_seal);index=audit.parse(values["INDEX.json"])
    if index["schema"]!="ocm.f1.resource-exitcode-index.v1":raise ValueError("EXITCODE_INDEX_SCHEMA")
    history=index["historical"]
    if history["seal_sha256"]!=expected_prior:raise ValueError("EXITCODE_PRIOR_AUTHORITY")
    dirname=audit.safe_name(history["source_dir"])
    if type(history["source_count"]) is not int or history["source_count"]<1:
        raise ValueError("EXITCODE_PRIOR_SOURCE_COUNT")
    def check_prior():
        return base.audit_successor(prior,expected_prior,root/dirname,historical,expected_historical)
    prior_result=check_prior()
    previous=base.package(audit,prior,expected_prior)
    previous_freeze=base.source_freeze(audit,previous["SOURCE_FREEZE.json"])
    expected_names={dirname+"/"+name for name in previous_freeze["files"]}
    if expected_names!={name for name in values if name.startswith(dirname+"/")}:
        raise ValueError("EXITCODE_PRIOR_SOURCE_SET")
    if history["source_count"]!=previous_freeze["count"]:raise ValueError("EXITCODE_PRIOR_SOURCE_COUNT")
    for key,name in [("source_freeze","SOURCE_FREEZE.json"),("result","RESULT.json")]:
        audit.checked(values[name],index[key],"EXITCODE_"+key.upper()+"_HASH")
    omission=index["omissions"];name=audit.safe_name(omission["file"])
    audit.checked(values[name],base.binding(omission),"EXITCODE_OMISSION_BINDING")
    if not isinstance(omission["scope"],str) or not omission["scope"]:raise ValueError("EXITCODE_OMISSION_SCOPE")
    maps,count,total=base.archives(audit,root,values,index["archives"])
    freeze=base.source_freeze(audit,values["SOURCE_FREEZE.json"])
    base.snapshot(audit,maps["final-qualification.tar.gz"],freeze,values["SOURCE_FREEZE.json"],"")
    base.check_current(audit,current,freeze)
    base.package(audit,root,expected_seal);check_prior();base.check_current(audit,current,freeze)
    return {"terminal":"RESOURCE_EXITCODE_CUSTODY_PASS",
            "historical_archive_members":prior_result["historical_archive_members"],
            "historical_sources":prior_result["historical_sources"],
            "prior_successor_archive_members":prior_result["successor_archive_members"],
            "prior_successor_sources":prior_result["current_sources"],
            "correction_archive_members":count,"correction_raw_bytes":total,"current_sources":freeze["count"],
            "omitted_host_inputs_revalidated":False,
            "scope":"Three separately bound source generations; only correction sources are current. Archive custody, not resource/native/corpus execution or omitted host-input revalidation."}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parent/"resource-exitcode-records")
    parser.add_argument("--seal-sha256",default=SEAL_SHA256);args=parser.parse_args()
    try:result=audit_exitcode(args.root,args.seal_sha256);code=0
    except Exception as exc:result={"terminal":"CANNOT_CHECK_RESOURCE_EXITCODE_CUSTODY","reason":str(exc)};code=2
    print(json.dumps(result,sort_keys=True,separators=(",",":")));return code

if __name__=="__main__":raise SystemExit(main())
