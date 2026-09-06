"""Metadata-only prospective binding. Never import or execute G1 or the sparse donor."""
from pathlib import Path
from fractions import Fraction
import importlib.metadata as metadata
import json
import os
import platform
import subprocess
import sys
from trial_common import ROOT, read, sha, write, record_files

CTX=Path("/home/billy/orion-director-work/20260906/g1-current-context-v2-20260906")
REPO=Path("/home/billy/orion-director-work/20260906/ocm-exact-sparse")
COMMIT="bac7f9375f1dac98f20a3a2d6154e6c7903231e4"
SCOPE="DIRECT_SV_SOLVE_WITH_COMMITMENT_DECISION; no durable query/result append; binder persistence included"

def main():
    if subprocess.check_output(["/usr/bin/git","-C",str(REPO),"rev-parse","HEAD"],text=True).strip()!=COMMIT:
        raise ValueError("DONOR_COMMIT_DRIFT")
    inventory=sha(CTX/"SHA256SUMS")
    if inventory!="1e96b33b63c6b60256c7738fe1a2d2a1e0ed762543a4517c8883e94b66519293":raise ValueError("CONTEXT_CHANGED")
    for line in (CTX/"SHA256SUMS").read_text().splitlines():
        expected,rel=line.split("  ",1)
        if sha(CTX/rel)!=expected:raise ValueError("CONTEXT_FILE_CHANGED:"+rel)
    context=read(CTX/"CONTEXT_MANIFEST.json"); receipt=read(CTX/"RESTORE_RECEIPT.json")
    old=read(CTX/"input/F0.json")
    packet=REPO/"research/ocm-prototype/results/representation-donor-g1-applicability-20260906"
    if sha(packet/"SHA256SUMS")!=context["original_packet_inventory_sha256"]:raise ValueError("STRUCTURAL_PACKET_CHANGED")
    seals=dict((rel,h) for h,rel in (line.split("  ",1) for line in (packet/"SHA256SUMS").read_text().splitlines()))
    if sha(packet/"kernels.json")!=seals["kernels.json"]:raise ValueError("KERNEL_INPUT_CHANGED")
    kernel=read(packet/"kernels.json"); ids=kernel["WARRANTED"]["ids"]
    if ids!=kernel["EXPLORATORY"]["ids"] or len(ids)!=78 or set(ids)!=set(receipt["seed"]):raise ValueError("FIELD_ORDER_CHANGED")
    def rational(v):
        x=Fraction(v);return f"{x.numerator}/{x.denominator}"
    state={k:receipt[k] for k in ("kso_state_hash","registry_revision","evidence_epoch","revoked","N")}
    state.update(edges=receipt["hyperedges"],ks_digest="473a4b5dfd381bcba8129eedf18bc355f4f34dc8cf67fbde62c3f401eb76ef70")
    manifests=receipt["operator_manifests"]
    binding=[{"program_id":p["descriptor_id"],"registry_key":next(k for k,v in manifests.items() if v["operator_id"]=="apply:"+p["descriptor_id"])}
             for p in receipt["programs"].values()]
    expected={"state":state,"task":receipt["task"],"config":receipt["config"],"request":receipt["request"],
              "program_sha256":receipt["programs"]["max3"]["program_sha256"],"ids":ids,"alpha":"1/3",
              "query_seed":[rational(receipt["seed"][i]) for i in ids],"uniform_seed":["1/78"]*78,
              "catalogue":["syntax:udpipe1","procedure:cvc5"]+sorted(v["operator_id"] for v in manifests.values()),
              "binding_receipts":binding}
    files={};packages={};runtime_modules={}
    for name,module in (("sympy","sympy"),("z3-solver","z3"),("sexpdata","sexpdata"),("mpmath","mpmath"),("ufal.udpipe",None),("cvc5",None)):
        dist=metadata.distribution(name); records={}
        for file in dist.files:
            rel=str(file)
            if rel.endswith(".dist-info/RECORD") or rel.endswith((".so",".dylib",".dll")):
                p=Path(dist.locate_file(file)).resolve(); records[str(p)]=sha(p);files[str(p)]=sha(p)
        record=next(Path(dist.locate_file(f)).resolve() for f in dist.files if str(f).endswith(".dist-info/RECORD"))
        verified=record_files(Path(dist.locate_file("")).resolve(),record)
        records.update(verified);files.update(verified)
        packages[name]={"version":dist.version,"record_verified_files":records,"installed_files":len(records)}
        if module:
            p=Path(dist.locate_file(module+"/__init__.py")).resolve()
            if not p.is_file():p=Path(dist.locate_file(module+".py")).resolve()
            runtime_modules[module]={"path":str(p),"sha256":sha(p)};files[str(p)]=sha(p)
    files[str(Path(sys.executable).resolve())]=sha(sys.executable)
    expected_origins={}
    for rel,record in context["source_files"].items():
        if rel.startswith("src/") and rel.endswith(".py"):
            name=rel[4:-3].replace("/",".")
            if name.endswith(".__init__"):name=name[:-9]
        elif rel.startswith("research/ocm-prototype/") and rel.endswith(".py"):name=rel[len("research/ocm-prototype/"):-3].replace("/",".")
        else:continue
        expected_origins[name]={"path":str(CTX/"source"/rel),"sha256":record["sha256"]}
    for name in ("bound_context","restore_context"):
        p=CTX/(name+".py");expected_origins[name]={"path":str(p),"sha256":sha(p)}
    donor=read(ROOT/"DONOR_SOURCE.json")
    for name in donor["files"]:
        filename=Path(name).name;p=ROOT/"source"/filename
        expected_origins[p.stem]={"path":str(p),"sha256":sha(p)}
        source=subprocess.check_output(["/usr/bin/git","-C",str(REPO),"show",COMMIT+":research/ocm-prototype/"+filename])
        if __import__("hashlib").sha256(source).hexdigest()!=sha(p):raise ValueError("DONOR_COPY_DRIFT")
    assignments=[]
    for pair in range(7):
        for arm in (("reference","sympy") if pair%2==0 else ("sympy","reference")):
            assignments.append({"index":len(assignments),"pair":pair,"arm":arm})
    env={k:os.environ.get(k) for k in ("SYMPY_GROUND_TYPES","SYMPY_USE_CACHE","OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")}
    trial_files={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.glob("*.py"))}
    trial_files.update({str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/"source").glob("*.py"))})
    trial_files["DONOR_SOURCE.json"]=sha(ROOT/"DONOR_SOURCE.json")
    manifest={"schema":"OCM.ExactSparseTrial.v1","registration":"https://github.com/SzeChunYiu/ORION-OCM/issues/72#issuecomment-5558797826",
              "study_status":"PROSPECTIVE_NO_G1_CALL_EXECUTED","consumer_scope":SCOPE,
              "python":sys.executable,"python_version":platform.python_version(),"python_sha256":sha(sys.executable),
              "cpu":0,"address_bytes":4294967296,"seconds_per_process":120,
              "original_envelope_source":"context/input/F0.json; same 4 GiB and CPU 0, new registered 120 seconds/process",
              "assignments":assignments,"expected":expected,"context_root":str(CTX),"context_inventory_sha256":inventory,
              "core_source_commit":context["current_source_commit"],"donor_repository_commit":COMMIT,
              "numerical_source_commit":"6678900ef3e3dc563a6d65fdcde24e1b4160ac82",
              "later_main_audit":"Frozen f4 execution closure retained. Later main bab65cf changes firing.py and dialogue/workspace.py; not incorporated. JSONL retained. This is not current-main execution.",
              "trial_files":trial_files,"runtime_files":files,"runtime_packages":packages,"runtime_modules":runtime_modules,
              "runtime_environment":env,"expected_module_origins":expected_origins,
              "input_order_source":{"kernels_sha256":sha(packet/"kernels.json"),"packet_inventory_sha256":sha(packet/"SHA256SUMS")},
              "gates":{"all_processes":14,"all_calls":28,"all_four_vectors_exact":True,"warm_median_B_over_A_at_most":"4/5","total_process_median_B_over_A_less_than":"1"},
              "cache_policy":"no output/factor cache; same host-compiled programs reused for two calls; candidate-only independent residual charged",
              "metadata_rules":{"selected_answer":["consumer.answer.application_wall_s"],
                 "application_checks":"Only solve-phase selected apply receipt check_wall_s; every other field retained",
                 "binding_receipts":"Only binding_receipts[*].bind_wall_s; identities compared",
                 "invocations":"Exact application schema only. Index must equal assigned call index. started_monotonic/finished_monotonic validated and retained as telemetry. action/payload/result matched; result.application_wall_s binds raw selected duration and shares its one exclusion. No PID field exists; unexpected keys fail.",
                 "preparation_events":"Must be empty; no exclusion",
                 "process":"PID/call position/hash/paths bind custody; wall/CPU/RSS retained as telemetry, not algorithmic outputs"},
              "cost_scope":"direct SV and commitment decision, real bind persistence and pointwise application/check; query journal/post-solve admission excluded; complete process-tree CPU not verified"}
    write(ROOT/"MANIFEST.json",manifest)
    print(json.dumps({"manifest_sha256":sha(ROOT/"MANIFEST.json"),"trial_files":len(trial_files),"runtime_files":len(files),"scope":SCOPE}))

if __name__=="__main__":main()
