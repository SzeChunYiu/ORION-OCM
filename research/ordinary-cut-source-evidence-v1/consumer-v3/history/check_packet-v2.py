"""Synthetic complete-P1 and trace-unusable controls. No native or corpus interpretation."""
import copy,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import teaching_packet as T
import run_opportunity as O
def c(label,kind="$p"):
    return {"label":label,"kind":kind,"statement":["|-","ph"],"floating":[],"essential":[],"dv":[]}
def desc(p):return dict(path=str(p),**O.identity(p))
def save(p,value):O.write(p,value);return desc(p)
start=time.perf_counter();out=Path(sys.argv[1]);out.mkdir()
base=[c("base-"+str(i)) for i in range(4095)]+[c("axiom-"+str(i),"$a") for i in range(96)]
new=[c("train-"+str(i)) for i in range(4096,4224)]
all_contracts=base+[c("new-axiom","$a")]+new
scope=desc(ROOT/"REGISTRY-SCOPE.json")
corpus={"path":"/home/billy/orion-director-work/20260908/metamath-curriculum-feasibility-v1/set.mm",
        "bytes":51126635,"sha256":"7b70cd8cca88aeb72a8dd97029d0b506015fb0325afec581cdc9add8ca0c8547"}
prefix={"bytes":1,"sha256":"0"*64}
release={"schema":"ordinary.training-release.v2","corpus":corpus,"registry_scope":scope,
         "closed_source":prefix,"ordinals":list(range(4096,4224)),
         "roots":[{"ordinal":i,"label":r["label"],"source_disposition":"RELEASED","statement":r["statement"]}
                  for i,r in zip(range(4096,4224),new)],
         "axiom_identities":[{"label":r["label"]} for r in all_contracts if r["kind"]=="$a"]}
release_pin=save(out/"synthetic-release.json",release)
authority={"schema":"ordinary.native-prefix-authority.v2","terminal":"FRESH_PREFIX_NATIVE_VERIFIED",
           "release":release_pin,"registry_scope":scope,"prefix":dict(path="SYNTHETIC_ONLY",**prefix),
           "proof_ordinal_count":4223,"verified_labels":[r["label"] for r in base+new if r["kind"]=="$p"]}
authority_pin=save(out/"synthetic-authority-NOT-NATIVE.json",authority)
inventory={"schema":"ordinary.native-P1-inventory.v2","release":release_pin,"native_trace_authority":authority_pin,
           "inventory_policy":T.POLICY,"base_labels":[r["label"] for r in all_contracts if r not in new],
           "released_labels":[r["label"] for r in new],"contracts":all_contracts}
inventory_pin=save(out/"synthetic-P1.json",inventory)
packet={"schema":"ordinary.training-trace-packet.v2","release":release_pin,"ordinals":list(range(4096,4224)),
        "native_trace_authority":authority_pin,"P1_inventory":inventory_pin,
        "roots":[dict(ordinal=i,label=r["label"],source_disposition="RELEASED",whole_contract=T.contract_identity(r),
                      trace_disposition="TRACE_UNUSABLE",trace=None,contracts={}) for i,r in zip(range(4096,4224),new)]}
request={"schema":"ordinary.training-opportunity-request.v2","corpus":corpus,"registry_scope":scope,
         "release_receipt":release_pin,"qualified_native_trace_authority":authority_pin,"P1_inventory":inventory_pin}
checks=[]
assert T.validate(base,packet,inventory,release,request,authority)==all_contracts
checks.append("all 128 trace-unusable native-contract stubs retain complete P1")
# Independent codec oracle: terminal byte is a newline, not two literal slash-n bytes.
canonical=json.dumps(new[0],sort_keys=True,separators=(",",":"),allow_nan=False).encode()+bytes([10])
import hashlib
assert T.contract_identity(new[0])=={"bytes":len(canonical),"sha256":hashlib.sha256(canonical).hexdigest()}
checks.append("whole-contract digest uses one actual final newline")
def reject(name,where,change):
    args=[copy.deepcopy(x) for x in (base,packet,inventory,release,request,authority)]
    change(args[where])
    try:T.validate(*args)
    except (ValueError,KeyError,TypeError):checks.append(name)
    else:raise AssertionError(name)
reject("dropped unusable whole theorem refused",2,lambda x:x["contracts"].pop())
reject("changed P0 contract refused",2,lambda x:x["contracts"][0].update(statement=["|-","ps"]))
reject("extra theorem shortcut refused",2,lambda x:x["contracts"].append(c("future")))
reject("omitted new axiom refused",2,lambda x:x["contracts"].pop(4191))
reject("wrong whole theorem digest refused",1,lambda x:x["roots"][0]["whole_contract"].update(sha256="1"*64))
reject("trace-ready flag with no trace refused",1,lambda x:x["roots"][0].update(trace_disposition="TRACE_READY"))
reject("wrong authority population refused",5,lambda x:x.update(proof_ordinal_count=4222))
reject("wrong registry scope authority refused",5,lambda x:x.update(registry_scope={}))
request.update(P0_contracts=save(out/"synthetic-P0.json",base),training_packet=save(out/"synthetic-packet.json",packet),
               gate_path=str(out/"synthetic-gate.json"),max_token_states=2000000,max_wall_s=60,
               sources={str(p.relative_to(ROOT)):O.identity(p) for p in list(ROOT.glob("*.py"))+list((ROOT/"donor").rglob("*.py")) if "__pycache__" not in p.parts})
request_path=out/"synthetic-request.json";save(request_path,request)
save(out/"synthetic-gate.json",{"authorization":"ROOT_TRAINING_OPPORTUNITY_GATE","request":O.identity(request_path),
                              "scope":"Authored pure driver double only; no native qualification or actual corpus permission."})
assert O.main(request_path,out/"driver") == 0
actual=json.loads((out/"driver/RESULT.json").read_bytes())
assert actual["terminal"]=="TRAINING_ONLY_OPPORTUNITY_RECORDED" and actual["native_calls"]==0
assert len(actual["roots"])==128 and all(x["status"]=="TRACE_UNUSABLE" and x["P1_retained"] for x in actual["roots"])
assert json.loads((out/"driver/P1-CONTRACTS.json").read_bytes())==all_contracts
checks.append("actual driver records unusable traces without aborting or weakening P1")
print(json.dumps({"terminal":"PURE_PACKET_CONTROLS_PASS","checks":checks,"native_calls":0,"corpus_reads":0,
                  "authority":"Entire packet and authority are synthetic doubles; no native acceptance asserted.",
                  "wall_s":time.perf_counter()-start},sort_keys=True))
