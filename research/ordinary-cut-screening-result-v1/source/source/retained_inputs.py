"""Custody and ordered occurrence selection; no extraction or native interpretation."""
import hashlib,json
from pathlib import Path
def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def identity(path):
 raw=Path(path).read_bytes();return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def read_bound(pin):
 path=Path(pin["path"]);raw=path.read_bytes()
 if {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}!={k:pin[k] for k in ("bytes","sha256")}:
  raise ValueError("input identity")
 return json.loads(raw)
def occurrences(previous):
 result=[]
 for ri,root in enumerate(previous["roots"]):
  for ci,cut in enumerate(root.get("cuts",[])):
   if cut["status"]!="CUT_PROPOSAL":continue
   result.append({"occurrence_index":len(result),"root_index":ri,"root_ordinal":root["ordinal"],
                  "root_label":root["label"],"cut_index":ci,"canonical_id":cut["canonical_id"],
                  "body_sha256":digest(cut["body"]),"body":cut["body"]})
 return result
def validate(previous,contracts,p1_pin,expected_count,expected_occurrences):
 if previous["terminal"]!="TRAINING_ONLY_OPPORTUNITY_RECORDED" or not all(
   previous[k] for k in ("inputs_unchanged","sources_unchanged","request_unchanged")):
  raise ValueError("predecessor custody")
 if previous["P1_contracts"]!={k:p1_pin[k] for k in ("bytes","sha256")}:
  raise ValueError("exact predecessor P1")
 if type(contracts) is not list or len(contracts)!=expected_count:
  raise ValueError("full P1 inventory count")
 if len({r["label"] for r in contracts})!=len(contracts):raise ValueError("duplicate P1 labels")
 rows=occurrences(previous)
 if len(rows)!=expected_occurrences:raise ValueError("all retained occurrence count")
 return rows
def write(path,value):
 with Path(path).open("x") as f:
  json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write("\n")
