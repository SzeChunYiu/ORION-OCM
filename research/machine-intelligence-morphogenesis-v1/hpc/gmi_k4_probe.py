#!/usr/bin/env python3
"""Development-only LUNARC sizing/import probe for protected grammar-native K4 V3."""
from __future__ import annotations
import hashlib, json, os, platform, resource, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "GMI_K4_LOFO_FREEZE_V1.json"); GEN_FREEZE = os.path.join(ROOT, "GMI_K4_GENERATOR_FREEZE_V1.json")
SUCCESSOR = os.path.join(ROOT, "GMI_K4_GRAMMAR_NATIVE_SUCCESSOR_FREEZE_V3.json"); OUT = os.path.join(ROOT, "LUNARC_ENV_PROBE_V1.json")


def sh(cmd):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=30); return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e: return {"returncode": -1, "stdout": "", "stderr": repr(e)}

def jh(p): raw=open(p).read(); return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()


def main():
    full, fsha = jh(FREEZE); fr=dict(full); fr.pop("name_key", None); gen,gsha=jh(GEN_FREEZE); succ,ssha=jh(SUCCESSOR)
    if gen.get("status") != "FROZEN_BEFORE_ANY_K4_SEARCH_RESULT": raise SystemExit("bad generator freeze")
    if succ.get("status") != "FROZEN_BEFORE_V3_PUBLIC_BEACON_AND_ANY_V3_PROTECTED_RESULT": raise SystemExit("bad V3 successor freeze")
    partitions=sh(["sinfo","-h","-o","%P|%a|%l|%c|%m|%G"]); assoc=sh(["sacctmgr","-n","-P","show","assoc",f"user={os.environ.get('USER','')}","format=Account,Partition,QOS"]); slurm=sh(["sinfo","--version"])
    fam=sorted(fr["families"])[0]; gram=sorted(fr["grammars"])[0]; seed=0x4B345033
    from gmi_k4_search_v3 import run_cell
    t=time.perf_counter(); r=run_cell(fam,gram,"w1",freeze=fr,seed=seed,budget=1_000_000); wall=time.perf_counter()-t; ru=resource.getrusage(resource.RUSAGE_SELF)
    rec={"schema":"LUNARCEnvProbeV4","status":"DEVELOPMENT_ONLY_MEASURED_NOT_SUBMITTED","scientific_use":"SIZING_AND_IMPORT_SMOKE_ONLY__EXCLUDED_FROM_PROTECTED_K4_V3",
         "host":platform.node(),"platform":platform.platform(),"python":sys.version,"cwd":os.getcwd(),"freeze_sha256":fsha,"generator_freeze_sha256":gsha,"successor_freeze_sha256":ssha,
         "slurm_version":slurm,"partitions":partitions,"associations":assoc,
         "pilot":{"family":fam,"grammar":gram,"cell":"w1","development_seed":seed,"development_verdict_not_evidence":r.get("verdict"),"wall_seconds":wall,"peak_rss_kb":ru.ru_maxrss,"candidate_space_size":r.get("coverage",{}).get("candidate_space_size"),"grammar_inventory_size":r.get("grammar_inventory_size")},
         "sizing_rule_frozen_here":{"time_safety_factor":50.0,"minimum_wall_seconds":300,"memory_safety_factor":4.0,"minimum_memory_mib":512,"note":"Renderer uses measured pilot only; scientific verdict is excluded."}}
    json.dump(rec,open(OUT,"w"),indent=1,sort_keys=True); print(json.dumps({"wrote":OUT,"status":rec["status"],"pilot_wall_seconds":wall,"candidate_space_size":rec["pilot"]["candidate_space_size"],"partition_probe_rc":partitions["returncode"],"assoc_probe_rc":assoc["returncode"]}))

if __name__=="__main__": main()
