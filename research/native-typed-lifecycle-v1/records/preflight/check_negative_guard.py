"""Focused data-only exact-refusal guard controls; no native operation."""
from pathlib import Path
import ast,copy,hashlib,json,os,time,types
HERE=Path(__file__).resolve().parent.parent
source=HERE/"run_b.py";body=source.read_bytes()
tree=ast.parse(body);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="require_native_negative")
def require(ok,why):
    if not ok:raise ValueError(why)
scope={"C":types.SimpleNamespace(require=require)}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),"exec"),scope)
guard=scope["require_native_negative"]
prefix=["ordinary-proof-0","ordinary-proof-1"];claim={"label":"issued-negative"}
accepted={"terminal":"NATIVE_REJECTED","native_calls":1,"error":{"stage":"native_check","pending":claim["label"]},"verified_labels":prefix}
records=[];started=time.perf_counter()
guard(copy.deepcopy(accepted),claim,prefix,"clean")
records.append({"check":"exact_claim_after_complete_prefix","pass":True})
for name,field,value in [("prefix_refusal","pending","ordinary-proof-1"),("other_claim","pending","other-issued"),
                         ("preflight_refusal","stage","issued_claim_binding")]:
    changed=copy.deepcopy(accepted);changed["error"][field]=value
    try:guard(changed,claim,prefix,name)
    except ValueError as exc:require("NATIVE_NEGATIVE_DID_NOT_REFUSE_EXACT_ISSUED_CLAIM" in str(exc),"wrong guard")
    else:raise AssertionError("false acceptance")
    records.append({"check":name,"pass":True})
changed=copy.deepcopy(accepted);changed["verified_labels"]=prefix[:-1]
try:guard(changed,claim,prefix,"incomplete_prefix")
except ValueError as exc:require("NATIVE_NEGATIVE_DID_NOT_REFUSE_EXACT_ISSUED_CLAIM" in str(exc),"wrong guard")
else:raise AssertionError("incomplete prefix accepted")
records.append({"check":"incomplete_prefix","pass":True})
require(source.read_bytes()==body,"source changed")
result={"terminal":"NEGATIVE_GUARD_DATA_ONLY_PASS","checks":records,"pid":os.getpid(),"parent_pid":os.getppid(),
 "source":{"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest()},"source_unchanged":True,
 "native_calls":0,"bridge_calls":0,"learner_calls":0,"wall_s":time.perf_counter()-started,
 "scope":"Extracted pure guard against declared small receipt records; no actual native result or population claim"}
with (HERE/"preflight/NEGATIVE-GUARD.json").open("x") as out:json.dump(result,out,sort_keys=True,indent=2);out.write("\n")
print(json.dumps({"terminal":result["terminal"],"checks":len(records),"native_calls":0}))
