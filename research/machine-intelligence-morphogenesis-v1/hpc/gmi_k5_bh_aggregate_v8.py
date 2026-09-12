#!/usr/bin/env python3
"""K5 B-H revival V8 aggregator (RV-377-170 / RV-377-171).

Scores lane cells with the frozen V1 stochastic rule + V2 admissibility addendum against the V8 plan's per-cell
predictions (never the core's own predicted_winner); scores probe cells against their numbered predictions only.
"""
from __future__ import annotations
import argparse,collections,glob,hashlib,json,os,statistics as st,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:sys.path.insert(0,ROOT)
from hpc.gmi_k5_bh_task_v8 import PLAN,contracts,plan,task_seed
def vk(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tier",choices=["development","protected"],default="development");ap.add_argument("--pattern");ap.add_argument("--out-json");a=ap.parse_args()
    res=os.path.join(ROOT,"microscopes","results","k5_bh_v8" if a.tier=="protected" else "k5_bh_v8_dev");pat=a.pattern or os.path.join(res,"K5BHV8*_*.json");outp=a.out_json or os.path.join(res,f"K5_BH_REVIVAL_AGGREGATE_V8_{a.tier.upper()}.json")
    pl,ph,hs,verified=contracts(a.tier);p=plan(pl,ph);by=collections.defaultdict(list);errs=[]
    for path in glob.glob(pat):
        try:
            r=json.load(open(path));r["_path"]=path
            if r.get("schema")!="GMIK5BHTaskReceiptV8":errs.append({"path":path,"error":"schema"});continue
            if r.get("tier")!=a.tier.upper():errs.append({"path":path,"error":"tier"});continue
            by[r.get("task_index")].append(r)
        except Exception as e:errs.append({"path":path,"error":repr(e)})
    rows=[]
    for i,s in enumerate(p):
        if len(by.get(i,[]))!=1:errs.append({"task_index":i,"error":"missing_or_duplicate"});continue
        r=by[i][0];e=[]
        if any(r.get(k)!=v for k,v in s.items()):e.append("task_spec")
        for k,v in hs.items():
            if r.get("freeze_hashes",{}).get(k)!=v:e.append(k+"_hash")
        th=hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if r.get("task_hash")!=th:e.append("task_hash")
        if r.get("seed")!=task_seed(a.tier,th,hs,verified):e.append("seed")
        if verified and r.get("public_beacon_round")!=verified["target_round"]:e.append("round")
        raw=r.get("raw_result")
        if r.get("status")!="OK" or r.get("exit_code")!=0:e.append("task_failed")
        if not isinstance(raw,dict) or not isinstance(raw.get("admissible"),list):e.append("raw")
        elif raw.get("observed_winner")!="NONE" and raw.get("observed_winner") not in raw["admissible"]:e.append("observed_outside_admissible")
        if e:errs.append({"task_index":i,"errors":e})
        rows.append(r)
    grouped=collections.defaultdict(list)
    for r in rows:grouped[(r["lane"],r["kind"],vk(r["value"]))].append(r)
    cells={};lanes=collections.defaultdict(list);probes={};rep=int(pl["replicates_per_value"])
    for lane in sorted(pl["lanes"]):
        L=pl["lanes"][lane]
        for c in L["cells"]:
            rs=grouped.get((lane,"cell",vk(c["value"])),[]);bad=sum(not r.get("v8_predicted_admissible",False) for r in rs);agree=sum(r.get("task_verdict")=="AGREE" for r in rs);m=[float(r.get("v8_prediction_margin",0)) for r in rs];mean=sum(m)/len(m) if m else 0.0
            if len(rs)!=rep:cv="INVALID"
            elif bad>=6:cv="THEORY_RED"
            elif bad>0:cv="INCONCLUSIVE"
            elif agree>=6 and mean>0:cv="GREEN"
            elif len(rs)-agree>=6 and mean<0:cv="THEORY_RED"
            else:cv="INCONCLUSIVE"
            extra={}
            if lane=="C_FEATURE_LEARNING" and rs:
                ob=[r["raw_result"]["observables"] for r in rs];gain=[(o["fixed_test_error"]-o["trainable_test_error"])*100 for o in ob];mf=st.mean(o["fixed_test_error"] for o in ob)
                extra={"mean_fixed_test_error":mf,"mean_trainable_test_error":st.mean(o["trainable_test_error"] for o in ob),"mean_gain_pp":st.mean(gain),"n_gain_exceeds_surplus":sum(g>(o["trainable_objective"]-o["fixed_objective"]+g) for g,o in zip(gain,ob)),"gain_band":c.get("predicted_gain_pp_band"),"gain_in_band":(c["predicted_gain_pp_band"][0]<=st.mean(gain)<=c["predicted_gain_pp_band"][1]) if c.get("predicted_gain_pp_band") else None,"world_check_P_C4":(L["world_check_band"][0]<=mf-c["linear_bayes_floor"]<=L["world_check_band"][1])}
            if lane=="E_CONTROL" and rs:
                ob=[r["raw_result"]["observables"] for r in rs];extra={"mean_direct_return":st.mean(o["direct_normalized_return"] for o in ob),"n_direct_admissible":sum("DIRECT" in r["raw_result"]["admissible"] for r in rs),"n_model_admissible":sum("MODEL" in r["raw_result"]["admissible"] for r in rs)}
            cells[f"{lane}:{vk(c['value'])}"]={"verdict":cv,"n":len(rs),"agree":agree,"predicted_inadmissible":bad,"mean_margin":mean,"predicted_winner":c["predicted_winner"],**extra};lanes[lane].append(cv)
        pr=L.get("probe")
        if pr:
            rs=grouped.get((lane,"probe",vk(pr["value"])),[]);ck=pr["checks"];res_p={"n":len(rs),"predicted_winner":pr["predicted_winner"],"agree_with_predicted_winner":sum(r.get("task_verdict")=="AGREE" for r in rs)}
            if rs and lane=="C_FEATURE_LEARNING":
                ob=[r["raw_result"]["observables"] for r in rs];fi=sum(o["fixed_test_error"]>0.18 for o in ob);ta=sum(o["trainable_test_error"]<=0.18 for o in ob);g=st.mean((o["fixed_test_error"]-o["trainable_test_error"])*100 for o in ob)
                res_p.update({"fixed_inadmissible":fi,"trainable_admissible":ta,"mean_gain_pp":g,"P-C5":fi>=ck["fixed_inadmissible_min"],"P-C6":ta<=ck["trainable_admissible_max"],"P-C7":ck["gain_pp_band"][0]<=g<=ck["gain_pp_band"][1],"n_observed_NONE":sum(r["raw_result"]["observed_winner"]=="NONE" for r in rs)})
            if rs and lane=="E_CONTROL":
                ob=[r["raw_result"]["observables"] for r in rs];di=sum("DIRECT" not in r["raw_result"]["admissible"] for r in rs);md=st.mean(o["direct_normalized_return"] for o in ob);ma=sum("MODEL" in r["raw_result"]["admissible"] for r in rs)
                res_p.update({"direct_inadmissible":di,"mean_direct_return":md,"model_admissible":ma,"P-E4":ck["direct_inadmissible_range"][0]<=di<=ck["direct_inadmissible_range"][1],"P-E5":ck["mean_dret_band"][0]<=md<=ck["mean_dret_band"][1],"P-E6":ma>=ck["model_admissible_min"]})
            probes[f"{lane}:probe:{vk(pr['value'])}"]=res_p
    lanev={l:("INVALID" if "INVALID" in cs else "THEORY_RED" if "THEORY_RED" in cs else "GREEN" if len(cs)==4 and all(x=="GREEN" for x in cs) else "INCONCLUSIVE") for l,cs in lanes.items()}
    e_inadm=sum(v["predicted_inadmissible"] for k,v in cells.items() if k.startswith("E_CONTROL:"));kill={"P-E7_lane_inadmissible_total":e_inadm,"P-E7_killed":e_inadm>int(pl["lanes"]["E_CONTROL"]["kill_max_lane_inadmissible"])}
    complete=not errs and all(v!="INVALID" for v in lanev.values());tier=a.tier.upper()
    terminal=f"K5_BH_V8_{tier}_EXECUTION_INVALID" if not complete else f"K5_BH_V8_{tier}_GREEN" if all(v=="GREEN" for v in lanev.values()) else f"K5_BH_V8_{tier}_CONTAINS_RED" if "THEORY_RED" in lanev.values() else f"K5_BH_V8_{tier}_INCONCLUSIVE"
    out={"schema":"GMIK5BHRevivalAggregateV8","tier":tier,"protected":a.tier=="protected","terminal":terminal,"freeze_hashes":hs,"verified_beacon_contract":verified,"structural_errors":errs,"cell_results":cells,"lane_results":lanev,"probe_results":probes,"kill_conditions":kill,"protected_v7_outcomes_remain_authoritative":True,"known_form_zero_prior_global_terminal":False,"no_gap_global_terminal":False}
    os.makedirs(os.path.dirname(outp),exist_ok=True);json.dump(out,open(outp,"w"),indent=1,sort_keys=True);print(json.dumps({"terminal":terminal,"lane_results":lanev,"errors":len(errs),"probes":probes,"kill":kill},sort_keys=True));return 0 if complete else 2
if __name__=="__main__":raise SystemExit(main())
