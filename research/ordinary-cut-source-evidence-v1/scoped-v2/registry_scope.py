"""Validate a bounded allocation declaration; this is never an execution gate."""
import hashlib,json
from pathlib import Path
COMMIT="7ddd528c948ae375618ad1ca476b28b9a0eec7d6"
CORPUS="7b70cd8cca88aeb72a8dd97029d0b506015fb0325afec581cdc9add8ca0c8547"
COVERAGE="DECLARED_REGISTRY_UNIVERSE_ONLY"
UNIVERSE={"source_metadata":{"bytes":8320,"sha256":"b5c7804f728fe9e31df6389e64835f9b14e3c724d9f548e5a83ec5c103164076"},
          "lineage":{"bytes":4794,"sha256":"132cf745930dcf0d3ea1164e9a71e56104b5265c08de2d83ff59234eb22ceed4"}}
FIELDS={"schema","decision","corpus_commit","corpus_sha256","coverage","universe",
        "protected_labels","base_p_ordinals","training_p_ordinals","replacement",
        "universal_clearance","heldout_independence","novelty_claim",
        "future_disclosure_policy","authorization_boundary"}
def identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def validate(scope,corpus):
    if set(scope)!=FIELDS:raise ValueError("registry scope schema")
    expected={"schema":"ordinary.registry-scope.v2","decision":"ROOT_SCOPED_PROSPECTIVE_ALLOCATION",
              "corpus_commit":COMMIT,"corpus_sha256":CORPUS,"coverage":COVERAGE,
              "base_p_ordinals":[1,4095],"training_p_ordinals":[4096,4223]}
    if any(scope[k]!=v for k,v in expected.items()) or corpus["sha256"]!=CORPUS:
        raise ValueError("registry scope identity or population")
    if any(scope[k] is not False for k in ("replacement","universal_clearance","heldout_independence","novelty_claim")):
        raise ValueError("unqualified registry claim")
    labels=scope["protected_labels"]
    if not isinstance(labels,list) or any(type(x) is not str or not x for x in labels) or len(set(labels))!=len(labels):
        raise ValueError("protected label schema")
    if set(scope["universe"])!={"source_metadata","lineage","source_record_count"} or type(scope["universe"]["source_record_count"]) is not int or scope["universe"]["source_record_count"]!=27:
        raise ValueError("registry universe schema")
    for key in ("source_metadata","lineage"):
        row=scope["universe"][key]
        if set(row)!={"path","bytes","sha256"} or type(row["bytes"]) is not int or row["bytes"]<1 or len(row["sha256"])!=64:
            raise ValueError("registry universe binding")
        if {k:row[k] for k in ("bytes","sha256")}!=UNIVERSE[key]:raise ValueError("different registry universe")
    if any(type(scope[k]) is not str or not scope[k] for k in ("future_disclosure_policy","authorization_boundary")):
        raise ValueError("registry qualification wording")
    return scope
def read_declared(scope,corpus):
    validate(scope,corpus);values={}
    for key in ("source_metadata","lineage"):
        row=scope["universe"][key];raw=Path(row["path"]).read_bytes()
        if identity(raw)!={k:row[k] for k in ("bytes","sha256")}:raise ValueError("registry universe identity")
        values[key]=json.loads(raw)
    if len(values["source_metadata"]["records"])!=scope["universe"]["source_record_count"]:
        raise ValueError("registry record population")
    source=values["lineage"]["corpus"]
    if source["upstream_commit"]!=COMMIT or source["file"]!=corpus:
        raise ValueError("registry corpus lineage")
    return values
