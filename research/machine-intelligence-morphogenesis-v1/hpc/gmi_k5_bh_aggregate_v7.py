#!/usr/bin/env python3
from __future__ import annotations
import argparse,collections,glob,hashlib,json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));PHASE=os.path.join(ROOT,"GMI_K5_BH_PHASE_FREEZE_V1.json");SCORE=os.path.join(ROOT,"GMI_K5_BH_SCORING_FREEZE_V1.json");C2=os.path.join(ROOT,"GMI_K5_BH_DESIGN_CORRIGENDUM_V2.json");C3=os.path.join(ROOT,"GMI_K5_BH_CONTINUAL_CORRIGENDUM_V3.json");ADM=os.path.join(ROOT,"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json");EXEC=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V7.json");BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V7.json");RES=os.path.join(ROOT,"microscopes","results","k5_bh_v7")
def jh(p):raw=open(p).read();return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def vk(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def plan(ex):return [{"lane":l,"parameter":s["parameter"],"value":v,"replicate":r} for l,s in sorted(ex["final_task_plan"].items()) for v in s["values"] for r in range(int(ex["replicates_per_value"]))]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--pattern",default=os.path.join(RES,"K5BHV7_*.json"));ap.add_argument("--out-json",default=os.path.join(RES,"K5_BH_AGGREGATE_V7.json"));a=ap.parse_args();phase,ph=jh(PHASE);score,sc=jh(SCORE);c2,c2h=jh(C2);c3,c3h=jh(C3);adm,ah=jh(ADM);ex,eh=jh(EXEC);b,bh=jh(BEACON)
 from hpc.gmi_beacon_verify import verify_beacon
 ver=verify_beacon(repo_root=ROOT,freeze_path=EXEC,beacon=b,expected_schema="GMIK5BHPublicBeaconV7");hs={"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":eh,"beacon":bh};p=plan(ex);by=collections.defaultdict(list);errs=[];files=glob.glob(a.pattern)
 for path in files:
  try:
   r=json.load(open(path));r["_path"]=path
   if r.get("schema")!="GMIK5BHTaskReceiptV7":errs.append({"path":path,"error":"schema"});continue
   by[r.get("task_index")].append(r)
  except Exception as e:errs.append({"path":path,"error":repr(e)})
 rows=[]
 for i,s in enumerate(p):
  if len(by.get(i,[]))!=1:errs.append({"task_index":i,"error":"missing_or_duplicate"});continue
  r=by[i][0];e=[]
  if any(r.get(k)!=v for k,v in s.items()):e.append("task_spec")
  for k,v in hs.items():
   if r.get("freeze_hashes",{}).get(k)!=v:e.append(k+"_hash")
  key={**s,"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":eh};th=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(",",":")).encode()).hexdigest();seed=int(hashlib.sha256(("GMI-K5-BH-V7"+th+ver["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
  if r.get("task_hash")!=th:e.append("task_hash")
  if r.get("seed")!=seed:e.append("seed")
  if r.get("public_beacon_round")!=ver["target_round"]:e.append("round")
  raw=r.get("raw_result")
  if r.get("status")!="OK" or r.get("exit_code")!=0:e.append("task_failed")
  if not isinstance(raw,dict) or not isinstance(raw.get("admissible"),list):e.append("raw")
  elif raw.get("observed_winner")!="NONE" and raw.get("observed_winner") not in raw["admissible"]:e.append("observed_outside_admissible")
  if e:errs.append({"task_index":i,"errors":e})
  rows.append(r)
 grouped=collections.defaultdict(list)
 for r in rows:grouped[(r.get("lane"),vk(r.get("value")))].append(r)
 exact=set(score["exact_lanes"]);stoch=set(score["stochastic_lanes"]);cells={};lanes=collections.defaultdict(list)
 for lane in sorted(ex["final_task_plan"]):
  for value in ex["final_task_plan"][lane]["values"]:
   rs=grouped.get((lane,vk(value)),[]);bad=sum((r.get("raw_result") or {}).get("predicted_winner") not in (r.get("raw_result") or {}).get("admissible",[]) for r in rs);agree=sum((r.get("raw_result") or {}).get("predicted_winner")== (r.get("raw_result") or {}).get("observed_winner") and (r.get("raw_result") or {}).get("predicted_winner") in (r.get("raw_result") or {}).get("admissible",[]) for r in rs);m=[float((r.get("raw_result") or {}).get("prediction_margin",0)) for r in rs];mean=sum(m)/len(m) if m else 0
   if len(rs)!=ex["replicates_per_value"]:cv="INVALID"
   elif lane in exact:cv="THEORY_RED" if bad or agree!=len(rs) else "GREEN"
   elif bad>=6:cv="THEORY_RED"
   elif bad>0:cv="INCONCLUSIVE"
   elif agree>=6 and mean>0:cv="GREEN"
   elif len(rs)-agree>=6 and mean<0:cv="THEORY_RED"
   else:cv="INCONCLUSIVE"
   cells[f"{lane}:{vk(value)}"]={"verdict":cv,"n":len(rs),"agree":agree,"predicted_inadmissible":bad,"mean_margin":mean};lanes[lane].append(cv)
 lanev={l:("INVALID" if "INVALID" in cs else "THEORY_RED" if "THEORY_RED" in cs else "GREEN" if len(cs)==4 and all(x=="GREEN" for x in cs) else "INCONCLUSIVE") for l,cs in lanes.items()};complete=not errs and all(v!="INVALID" for v in lanev.values());terminal="K5_BH_V7_EXECUTION_INVALID" if not complete else "K5_BH_V7_GREEN" if all(v=="GREEN" for v in lanev.values()) else "K5_BH_V7_CONTAINS_RED" if "THEORY_RED" in lanev.values() else "K5_BH_V7_INCONCLUSIVE";rep={"schema":"GMIK5BHAggregateV7","terminal":terminal,"freeze_hashes":hs,"verified_beacon_contract":ver,"structural_errors":errs,"cell_results":cells,"lane_results":lanev,"known_form_zero_prior_global_terminal":False,"no_gap_global_terminal":False};os.makedirs(os.path.dirname(a.out_json),exist_ok=True);json.dump(rep,open(a.out_json,"w"),indent=1,sort_keys=True);print(json.dumps({"terminal":terminal,"lane_results":lanev,"errors":len(errs)},sort_keys=True));return 0 if complete else 2
if __name__=="__main__":raise SystemExit(main())
