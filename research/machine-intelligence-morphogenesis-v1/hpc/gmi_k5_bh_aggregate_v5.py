#!/usr/bin/env python3
"""Aggregate protected K5 B-H V5 with preregistered quality/admissibility enforcement."""
from __future__ import annotations
import argparse,collections,glob,hashlib,json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE=os.path.join(ROOT,"GMI_K5_BH_PHASE_FREEZE_V1.json"); SCORE=os.path.join(ROOT,"GMI_K5_BH_SCORING_FREEZE_V1.json")
C2=os.path.join(ROOT,"GMI_K5_BH_DESIGN_CORRIGENDUM_V2.json"); C3=os.path.join(ROOT,"GMI_K5_BH_CONTINUAL_CORRIGENDUM_V3.json")
ADM=os.path.join(ROOT,"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json"); EX=os.path.join(ROOT,"GMI_K5_BH_EXECUTION_FREEZE_V5.json")
BEACON=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V5.json"); RES=os.path.join(ROOT,"microscopes","results","k5_bh_v5")
def jh(p): raw=open(p).read(); return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def plan(ex): return [{"lane":lane,"parameter":sp["parameter"],"value":v,"replicate":r} for lane in sorted(ex["final_task_plan"]) for v in ex["final_task_plan"][lane]["values"] for r in range(int(ex["replicates_per_value"]))]
def vkey(v): return json.dumps(v,sort_keys=True,separators=(",",":"))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pattern",default=os.path.join(RES,"K5BHV5_*.json")); ap.add_argument("--out-json",default=os.path.join(RES,"K5_BH_AGGREGATE_V5.json")); ap.add_argument("--out-md",default=os.path.join(RES,"K5_BH_AGGREGATE_V5.md")); a=ap.parse_args()
    phase,ph=jh(PHASE); score,sc=jh(SCORE); c2,c2h=jh(C2); c3,c3h=jh(C3); adm,ah=jh(ADM); ex,exh=jh(EX); b,bh=jh(BEACON)
    if adm.get("status")!="FROZEN_BEFORE_K5_PUBLIC_BEACON_AND_ANY_PROTECTED_K5_RESULT": raise SystemExit("bad admissibility addendum")
    if ex.get("status")!="FROZEN_BEFORE_K5_V5_BEACON_AND_PROTECTED_EXECUTION": raise SystemExit("bad V5 execution freeze")
    if b.get("schema")!="GMIK5BHPublicBeaconV5" or b.get("status")!="ACQUIRED_NO_REROLL" or not b.get("sha256_signature_consistency_verified"): raise SystemExit("bad V5 public beacon")
    hs={"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":exh,"beacon":bh}; p=plan(ex); files=sorted(glob.glob(a.pattern)); by=collections.defaultdict(list); parse=[]
    for path in files:
        try:
            r=json.load(open(path)); r["_path"]=path
            if r.get("schema")!="GMIK5BHTaskReceiptV5": parse.append({"path":path,"error":f"wrong schema {r.get('schema')}"}); continue
            by[r.get("task_index")].append(r)
        except Exception as e: parse.append({"path":path,"error":repr(e)})
    errors=[]
    if parse: errors.append({"parse_or_schema_failures":parse})
    miss=[i for i in range(len(p)) if not by.get(i)]; dup={str(i):[x.get("_path") for x in xs] for i,xs in by.items() if len(xs)!=1}; extra=sorted(i for i in by if not isinstance(i,int) or not 0<=i<len(p))
    if miss: errors.append({"missing_task_indices":miss})
    if dup: errors.append({"duplicate_task_indices":dup})
    if extra: errors.append({"extra_task_indices":extra})
    rows=[]
    for i,spec in enumerate(p):
        if len(by.get(i,[]))!=1: continue
        r=by[i][0]; er=[]
        if any(r.get(k)!=v for k,v in spec.items()): er.append("task_spec_mismatch")
        rh=r.get("freeze_hashes",{})
        for k,v in hs.items():
            if rh.get(k)!=v: er.append(k+"_hash_mismatch")
        key={**spec,"phase":ph,"score":sc,"corr2":c2h,"corr3":c3h,"admissibility":ah,"execution":exh}
        th=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(",",":")).encode()).hexdigest(); seed=int(hashlib.sha256(("GMI-K5-BH-V5"+th+b["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
        if r.get("task_hash")!=th: er.append("task_hash_mismatch")
        if r.get("seed")!=seed: er.append("seed_mismatch")
        if r.get("public_beacon_round")!=b.get("target_round"): er.append("beacon_round_mismatch")
        if r.get("status")!="OK" or r.get("exit_code")!=0: er.append("task_failed")
        raw=r.get("raw_result")
        if not isinstance(raw,dict) or not all(k in raw for k in ("predicted_winner","observed_winner","prediction_margin","observables","admissible")): er.append("incomplete_raw_result")
        elif not isinstance(raw.get("admissible"),list): er.append("admissible_not_list")
        else:
            obs=raw.get("observed_winner")
            if obs!="NONE" and obs not in raw["admissible"]: er.append("observed_winner_outside_admissible")
        if er: errors.append({"task_index":i,"path":r.get("_path"),"errors":er})
        rows.append(r)

    grouped=collections.defaultdict(list)
    for r in rows: grouped[(r["lane"],vkey(r["value"]))].append(r)
    exact=set(score["exact_lanes"]); stoch=set(score["stochastic_lanes"]); cell_results={}; lane_cells=collections.defaultdict(list)
    for lane in sorted(ex["final_task_plan"]):
        for val in ex["final_task_plan"][lane]["values"]:
            rs=grouped.get((lane,vkey(val)),[]); key=f"{lane}:{vkey(val)}"; d={"lane":lane,"value":val,"n":len(rs)}
            if len(rs)!=int(ex["replicates_per_value"]): cv="INVALID_MISSING_REPLICATES"; d["reason"]="replicate_count"
            else:
                badpred=sum(r["raw_result"]["predicted_winner"] not in r["raw_result"]["admissible"] for r in rs)
                agree=sum(r["raw_result"]["predicted_winner"]==r["raw_result"]["observed_winner"] and r["raw_result"]["predicted_winner"] in r["raw_result"]["admissible"] for r in rs)
                margins=[float(r["raw_result"]["prediction_margin"]) for r in rs]; mean=sum(margins)/len(margins)
                d.update({"agree_admissible":agree,"disagree_or_inadmissible":len(rs)-agree,"predicted_inadmissible":badpred,"mean_prediction_margin":mean,"min_margin":min(margins),"max_margin":max(margins),
                          "predicted_winners":dict(collections.Counter(r["raw_result"]["predicted_winner"] for r in rs)),"observed_winners":dict(collections.Counter(r["raw_result"]["observed_winner"] for r in rs))})
                if lane in exact:
                    cv="THEORY_RED" if badpred else ("GREEN" if agree==len(rs) else "THEORY_RED")
                elif lane in stoch:
                    if badpred>=6: cv="THEORY_RED"
                    elif badpred>0: cv="INCONCLUSIVE"
                    elif agree>=6 and mean>0: cv="GREEN"
                    elif (len(rs)-agree)>=6 and mean<0: cv="THEORY_RED"
                    else: cv="INCONCLUSIVE"
                else: cv="INVALID_UNKNOWN_SCORING_CLASS"
            d["cell_verdict"]=cv; cell_results[key]=d; lane_cells[lane].append(cv)
    lane_results={}
    for lane,cells in lane_cells.items():
        if any(x.startswith("INVALID") for x in cells): lv="INVALID"
        elif "THEORY_RED" in cells: lv="THEORY_RED"
        elif all(x=="GREEN" for x in cells) and len(cells)==4: lv="GREEN"
        else: lv="INCONCLUSIVE"
        lane_results[lane]={"verdict":lv,"cells":cells}
    complete=not errors and len(rows)==len(p) and all(not d["cell_verdict"].startswith("INVALID") for d in cell_results.values()); allgreen=complete and all(x["verdict"]=="GREEN" for x in lane_results.values()); anyred=any(x["verdict"]=="THEORY_RED" for x in lane_results.values())
    terminal=("K5_BH_V5_EXECUTION_INVALID" if not complete else "K5_BH_V5_SYNTHETIC_PHASE_TOURNAMENT_GREEN" if allgreen else "K5_BH_V5_SYNTHETIC_PHASE_TOURNAMENT_CONTAINS_RED" if anyred else "K5_BH_V5_SYNTHETIC_PHASE_TOURNAMENT_INCONCLUSIVE")
    rep={"schema":"GMIK5BHAggregateV5","terminal":terminal,"freeze_hashes":hs,"public_beacon_round":b.get("target_round"),"expected_tasks":len(p),"receipts_found":len(files),"validated_rows":len(rows),"structural_errors":errors,"cell_results":cell_results,"lane_results":lane_results,"all_complete":complete,"all_lanes_green":allgreen,
         "admissibility_rule":"GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json","known_form_zero_prior_global_terminal":False,"no_gap_global_terminal":False,
         "claim_ceiling":"Synthetic held-regime K5 evidence with quality constitution enforced. Independent authorship, real transfer, large-model scaling and physical frontiers remain external gates."}
    os.makedirs(os.path.dirname(a.out_json),exist_ok=True); json.dump(rep,open(a.out_json,"w"),indent=1,sort_keys=True)
    lines=["# K5 B-H V5 admissibility-aware protected tournament","",f"Terminal: `{terminal}`","",f"Validated tasks: **{len(rows)}/{len(p)}**; structural error groups: **{len(errors)}**.","","## Lane verdicts",""]+[f"- `{l}`: **{lane_results[l]['verdict']}** — {lane_results[l]['cells']}" for l in sorted(lane_results)]+["","## Cell details",""]
    for k in sorted(cell_results):
        d=cell_results[k]; lines.append(f"- `{k}`: {d['cell_verdict']} (n={d['n']}, admissible_agree={d.get('agree_admissible')}, predicted_inadmissible={d.get('predicted_inadmissible')}, mean_margin={d.get('mean_prediction_margin')})")
    lines += ["","No GREEN may be produced by a winner that fails the frozen quality constitution.",""]; open(a.out_md,"w").write("\n".join(lines)); print(json.dumps({"terminal":terminal,"lane_results":{k:v["verdict"] for k,v in lane_results.items()},"validated":len(rows),"errors":len(errors)},sort_keys=True)); return 0 if complete else 2
if __name__=="__main__": raise SystemExit(main())
