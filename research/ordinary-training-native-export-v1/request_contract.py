import hashlib,json,re
REQUEST_SCHEMA="ordinary.training-trace-export-request.v2"
RELEASE_SCHEMA="ordinary.training-release.v2"
ORDINALS=tuple(range(4096,4224))
SOURCE_NAMES=("trace_export.py","bound_io.py","request_contract.py","population.py",
              "native_export.py","packet_export.py","trace_transport.py","donor/trace_source.py","donor/trace_adapter.py")
CORPUS={"path":"/home/billy/orion-director-work/20260908/metamath-curriculum-feasibility-v1/set.mm",
        "bytes":51126635,"sha256":"7b70cd8cca88aeb72a8dd97029d0b506015fb0325afec581cdc9add8ca0c8547"}
PYTHON={"path":"/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11",
        "bytes":21334200,"sha256":"edca1fc80dbd58182c849c13707fb6bfb522b0d7049adc408225f7c69b124d3b"}
VERIFIER={"path":"/home/billy/orion-director-work/20260908/metamath-curriculum-feasibility-v1/mmverify.py",
          "bytes":28925,"sha256":"a1586636b9f3b8378932e129a1a8299dab8ad39098eca22480583947d1f644b8"}
DONORS={"donor/trace_source.py":{"bytes":4115,"sha256":"d00d25305c202cedd412c4f620f3e84801d4b24544f7550c7f5fea296775e525"},
        "donor/trace_adapter.py":{"bytes":7036,"sha256":"b8f54435e5d2e5208bf07f55a3cd02d771f8d0371a9f25bdf7cceab59057f91a"}}
DISPOSITIONS={"RELEASED","EXCLUDED_PRIOR_PROTECTED","EXCLUDED_DEPENDS_PRIOR_PROTECTED"}

def canonical(value):return (json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
def identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}

def pin(value,path=True):
    keys={"path","bytes","sha256"} if path else {"bytes","sha256"}
    if not isinstance(value,dict) or set(value)!=keys:raise ValueError("missing or malformed binding")
    if type(value["bytes"]) is not int or value["bytes"]<0:raise ValueError("binding length")
    if not isinstance(value["sha256"],str) or re.fullmatch("[0-9a-f]{64}",value["sha256"]) is None:raise ValueError("digest")
    if path and (not isinstance(value["path"],str) or not value["path"].startswith("/")):raise ValueError("absolute bound path")

def validate_request(req):
    keys={"schema","ordinals","corpus","python","verifier","prefix","release","registry_scope",
          "authority_contract","observer_contract","P0_contracts","gate_path","sources"}
    if not isinstance(req,dict) or set(req)!=keys or req["schema"]!=REQUEST_SCHEMA:raise ValueError("request schema")
    if not isinstance(req["ordinals"],list) or any(type(x) is not int for x in req["ordinals"]) or req["ordinals"]!=list(ORDINALS):raise ValueError("fixed ordinal population")
    for key in ("corpus","python","verifier","prefix","release","registry_scope","authority_contract","observer_contract","P0_contracts"):pin(req[key])
    if req["corpus"]!=CORPUS or req["python"]!=PYTHON or req["verifier"]!=VERIFIER:raise ValueError("new source/runtime authority required")
    if not isinstance(req["gate_path"],str) or not req["gate_path"].startswith("/"):raise ValueError("missing native gate")
    if not isinstance(req["sources"],dict) or set(req["sources"])!=set(SOURCE_NAMES):raise ValueError("source population")
    for value in req["sources"].values():pin(value,False)
    if any(req["sources"][n]!=v for n,v in DONORS.items()):raise ValueError("unchanged donor identity required")

def validate_release(release,req):
    if release.get("schema")!=RELEASE_SCHEMA or release.get("ordinals")!=list(ORDINALS):raise ValueError("released population")
    if release.get("corpus")!=req["corpus"] or release.get("registry_scope")!=req["registry_scope"]:raise ValueError("source/registry identity")
    if release.get("closed_source")!={k:req["prefix"][k] for k in ("bytes","sha256")}:raise ValueError("prefix identity")
    roots=release.get("roots")
    if not isinstance(roots,list) or len(roots)!=128:raise ValueError("retain all 128 positions")
    if any(type(x.get("ordinal")) is not int for x in roots) or [x.get("ordinal") for x in roots]!=list(ORDINALS):raise ValueError("ordinal order")
    labels=[x.get("label") for x in roots]
    if any(not isinstance(x,str) or not x for x in labels) or len(set(labels))!=128:raise ValueError("root labels")
    if any(x.get("source_disposition") not in DISPOSITIONS for x in roots):raise ValueError("source disposition")

def validate_authority(plan,req,release):
    keys={"schema","authority_id","status","release","prefix","registry_scope","corpus",
          "python","verifier","axiom_identities","proof_ordinal_count","base_policy"}
    if not isinstance(plan,dict) or set(plan)!=keys:raise ValueError("new explicit authority contract required")
    if plan["schema"]!="ordinary.native-export-authority-contract.v2":raise ValueError("authority schema")
    if plan["status"]!="PROSPECTIVE_NEW_AUTHORITY_CONTRACT":raise ValueError("old receipt is not new authority")
    if not isinstance(plan["authority_id"],str) or not plan["authority_id"]:raise ValueError("new authority ID required")
    for key in ("release","prefix","registry_scope","corpus","python","verifier"):
        if plan[key]!=req[key]:raise ValueError("authority contract differs: "+key)
    if plan["proof_ordinal_count"]!=4223 or plan["base_policy"]!="ALL_PREFIX_AXIOMS":raise ValueError("authority population")
    if plan["axiom_identities"]!=release["axiom_identities"]:raise ValueError("new axiom authority contract required")
