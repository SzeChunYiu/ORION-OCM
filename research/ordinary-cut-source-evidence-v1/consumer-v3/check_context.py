"""Authored transport boundary controls; no native verifier, exporter, miner or census."""
import copy,hashlib,importlib.util,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"donor")]
import teaching_packet as T
import structural_fixture as F
def p(label,kind="$p"):
    return {"label":label,"kind":kind,"statement":["|-","ph"],"floating":[],"essential":[],"dv":[]}
def descriptor(label):return {"path":"SYNTHETIC/"+label,"bytes":1,"sha256":hashlib.sha256(label.encode()).hexdigest()}
def raw(label):return {k:v for k,v in descriptor(label).items() if k!="path"}
trace,used,_=F.fixture()
trace["label"]=trace["source"]["label"]="train-4096"
trace["source"].update(active_variables=["ch","ph","ps"],raw=raw("source4096"),proof_raw=raw("proof4096"))
axioms=[p("axiom"+str(i),"$a") for i in range(93)]+[T.contract(used[x]) for x in ("compose","pair","wrap")]
base=[p("base"+str(i)) for i in range(4095)]+axioms
new=[T.contract(trace["source"])]+[p("train-"+str(i)) for i in range(4097,4224)]
extra=[p("new-axiom"+str(i),"$a") for i in range(4)]
all_contracts=base+extra+new
request={"corpus":descriptor("corpus"),"registry_scope":descriptor("registry"),
         "release_receipt":descriptor("release"),"qualified_native_trace_authority":descriptor("authority"),
         "P1_inventory":descriptor("P1"),"P0_contracts":descriptor("P0")}
release={"schema":"ordinary.training-release.v2","corpus":request["corpus"],"registry_scope":request["registry_scope"],
         "closed_source":raw("prefix"),"ordinals":list(range(4096,4224)),
         "roots":[{"ordinal":i,"label":r["label"],"source_disposition":"RELEASED","statement":r["statement"],
                   "source_raw":raw("source"+str(i)),"proof_raw":raw("proof"+str(i))}
                  for i,r in zip(range(4096,4224),new)],
         "axiom_identities":[{"label":r["label"],"raw":raw(r["label"])} for r in axioms+extra]}
inventory={"schema":"ordinary.native-P1-inventory.v2","release":request["release_receipt"],
           "native_trace_authority":request["qualified_native_trace_authority"],"inventory_policy":T.POLICY,
           "base_labels":[r["label"] for r in base+extra],"released_labels":[r["label"] for r in new],
           "contracts":all_contracts}
rows=[dict(ordinal=i,label=r["label"],source_disposition="RELEASED",whole_contract=T.contract_identity(r),
           trace_disposition="TRACE_UNUSABLE",trace=None,contracts={}) for i,r in zip(range(4096,4224),new)]
rows[0].update(trace_disposition="TRACE_READY",trace=trace,contracts=used)
packet={"schema":"ordinary.training-trace-packet.v2","release":request["release_receipt"],
        "ordinals":list(range(4096,4224)),"roots":rows,
        "native_trace_authority":request["qualified_native_trace_authority"],"P1_inventory":request["P1_inventory"]}
authority={"schema":"ordinary.native-prefix-authority.v2","terminal":"FRESH_PREFIX_NATIVE_VERIFIED",
           "proof_ordinal_count":4223,"verified_labels":[r["label"] for r in base+new if r["kind"]=="$p"],
           "release":request["release_receipt"],"registry_scope":request["registry_scope"],
           "corpus":request["corpus"],"P0_contracts":request["P0_contracts"],"prefix":descriptor("prefix"),
           "axioms":[{"contract":r,"raw":raw(r["label"])} for r in axioms+extra],
           "additional_axiom_labels":[r["label"] for r in extra],
           "selected_scope_bindings":{r["label"]:{"contract":T.contract_identity(r),"source_raw":raw("source"+str(i)),
              "proof_raw":raw("proof"+str(i)),"active_variables":["ch","ph","ps"],"active_dv":[]}
              for i,r in zip(range(4096,4224),new)},
           "trace_bindings":{"train-4096":{"trace":T.contract_identity(trace),"contracts":T.contract_identity(used)}},
           "trace_dispositions":{r["label"]:{"status":rows[j]["trace_disposition"],
              "reason":None if j==0 else "AUTHORED_UNUSABLE"} for j,r in enumerate(new)}}
original=(base,packet,inventory,release,request,authority);checks=[];start=time.perf_counter()
def check(name,test):test();checks.append(name)
assert T.validate(*original)==all_contracts
checks.append("span-bearing floating/essential and ordinary contracts accepted")
assert len([r for r in all_contracts if r["kind"]=="$a"])==100 and len(all_contracts)==4323
checks.append("all P0/released theorems and four new axioms remain")
spec=importlib.util.spec_from_file_location("predecessor",ROOT/"history/teaching_packet-v2.py")
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
try:old.validate(*original)
except KeyError as exc:assert str(exc)=="'dv'"
else:raise AssertionError("old hypothesis projection defect not reproduced")
checks.append("predecessor hypothesis projection defect reproduced")
def bind(args):
    row=args[1]["roots"][0]
    args[5]["trace_bindings"][row["label"]]={"trace":T.contract_identity(row["trace"]),"contracts":T.contract_identity(row["contracts"])}
def reject(name,change,rehash=False):
    args=copy.deepcopy(original);change(args)
    if rehash:bind(args)
    try:T.validate(*args)
    except (ValueError,KeyError,TypeError,IndexError):checks.append(name)
    else:raise AssertionError(name)
reject("wrong floating statement refused",lambda a:a[1]["roots"][0]["contracts"]["wph"].update(statement=["wff","ps"]),True)
reject("wrong essential statement refused",lambda a:a[1]["roots"][0]["contracts"]["h0"].update(statement=["|-","ph"]),True)
reject("changed prior span refuses old native binding",lambda a:a[1]["roots"][0]["contracts"]["h0"].update(span=[2,3]))
reject("out-of-order span refused even with rebound double",lambda a:a[1]["roots"][0]["contracts"]["h0"].update(span=[100,101]),True)
reject("missing hypothesis span refused",lambda a:a[1]["roots"][0]["contracts"]["h0"].pop("span"),True)
reject("missing used hypothesis refused",lambda a:a[1]["roots"][0]["contracts"].pop("h0"),True)
reject("foreign ordinary contract refused",lambda a:a[1]["roots"][0]["contracts"]["compose"].update(statement=["|-","ph"]),True)
reject("referenced proof body extra field refused",lambda a:a[1]["roots"][0]["contracts"]["compose"].update(proof=["hidden"]),True)
reject("wrong source active context refused",lambda a:a[5]["selected_scope_bindings"]["train-4096"].update(active_variables=[]))
reject("extra native trace binding refused",lambda a:a[5]["trace_bindings"].update(foreign={}))
reject("changed raw native axiom identity refused",lambda a:a[5]["axioms"][0].update(raw=raw("wrong")))
reject("missing selected whole scope refused",lambda a:a[5]["selected_scope_bindings"].pop("train-4097"))
reject("source DV outside ready transport refused",lambda a:a[1]["roots"][0]["trace"]["source"].update(dv=[["ph","ps"]]),True)
args=copy.deepcopy(original);row=args[1]["roots"][0]
row.update(trace_disposition="TRACE_UNUSABLE",trace=None,contracts={})
args[5]["trace_bindings"].pop("train-4096")
args[5]["trace_dispositions"]["train-4096"]={"status":"TRACE_UNUSABLE","reason":"OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE"}
assert T.validate(*args)==all_contracts
checks.append("native-qualified whole theorem retained when transport is unusable")
reject("ready row paired with unusable native disposition refused",
       lambda a:a[5]["trace_dispositions"]["train-4096"].update(status="TRACE_UNUSABLE"))
print(json.dumps({"terminal":"PURE_CONTEXT_CONTROLS_PASS","checks":checks,
                  "fixture_scope":"Entire 4223-label authority and trace are authored doubles; no native validity asserted.",
                  "native_calls":0,"exporter_calls":0,"extractor_calls":0,"alias_calls":0,
                  "corpus_reads":0,"wall_s":time.perf_counter()-start},sort_keys=True))
