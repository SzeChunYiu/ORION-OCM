#!/usr/bin/env python3
"""Fail-closed aggregate for protected null-aware K4 V6, binding execution code into provenance."""
from __future__ import annotations
import argparse,collections,glob,hashlib,json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));PRED=os.path.join(ROOT,"GMI_K4_LOFO_FREEZE_V1.json");SCI=os.path.join(ROOT,"GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json");EXEC=os.path.join(ROOT,"GMI_K4_EXECUTION_FREEZE_V6.json");BEACON=os.path.join(ROOT,"GMI_K4_PUBLIC_BEACON_V6.json");RES=os.path.join(ROOT,"microscopes","results","k4_v6")
def jh(p):raw=open(p).read();return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def plan(fr):return [{"family":f,"grammar":g,"cell":c} for f in sorted(fr["families"]) for g in sorted(fr["grammars"]) for c in ("w1","w2","w4","w8")]
def red(v):return isinstance(v,str) and v.startswith("THEORY_RED")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pattern",default=os.path.join(RES,"K4V6_*.json"));ap.add_argument("--reveal-names",action="store_true");ap.add_argument("--out-json",default=os.path.join(RES,"K4_V6_AGGREGATE.json"));ap.add_argument("--out-md",default=os.path.join(RES,"K4_V6_AGGREGATE.md"));a=ap.parse_args()
    full,ph=jh(PRED);fr=dict(full);fr.pop("name_key",None);sci,sh=jh(SCI);ex,eh=jh(EXEC);b,bh=jh(BEACON)
    if sci.get("status")!="FROZEN_BEFORE_V5_PUBLIC_BEACON_AND_ANY_V5_SEARCH_RESULT":raise SystemExit("bad science freeze")
    if ex.get("status")!="FROZEN_BEFORE_K4_V6_BEACON_AND_PROTECTED_EXECUTION":raise SystemExit("bad execution freeze")
    if b.get("schema")!="GMIK4PublicBeaconV6" or b.get("status")!="ACQUIRED_NO_REROLL" or not b.get("sha256_signature_consistency_verified"):raise SystemExit("bad beacon")
    hs={"prediction":ph,"science":sh,"execution":eh,"beacon":bh};p=plan(fr);files=sorted(glob.glob(a.pattern));by=collections.defaultdict(list);parse=[]
    for path in files:
        try:
            r=json.load(open(path));r["_path"]=path
            if r.get("schema")!="GMIK4TaskReceiptV7":parse.append({"path":path,"error":f"wrong schema {r.get('schema')}"});continue
            by[r.get("task_index")].append(r)
        except Exception as e:parse.append({"path":path,"error":repr(e)})
    errors=[]
    if parse:errors.append({"parse_or_schema_failures":parse})
    miss=[i for i in range(len(p)) if not by.get(i)];dup={str(i):[x.get("_path") for x in xs] for i,xs in by.items() if len(xs)!=1};extra=sorted(i for i in by if not isinstance(i,int) or not 0<=i<len(p))
    if miss:errors.append({"missing_task_indices":miss})
    if dup:errors.append({"duplicate_task_indices":dup})
    if extra:errors.append({"extra_task_indices":extra})
    rows=[]
    for i,spec in enumerate(p):
        if len(by.get(i,[]))!=1:continue
        r=by[i][0];er=[]
        if any(r.get(k)!=v for k,v in spec.items()):er.append("task_spec_mismatch")
        for k,v in hs.items():
            if r.get("freeze_hashes",{}).get(k)!=v:er.append(k+"_hash_mismatch")
        key={**spec,"prediction":ph,"science":sh,"execution":eh};th=hashlib.sha256(json.dumps(key,sort_keys=True,separators=(",",":")).encode()).hexdigest();seed=int(hashlib.sha256(("GMI-K4-V6"+th+b["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
        if r.get("task_hash")!=th:er.append("task_hash_mismatch")
        if r.get("seed")!=seed:er.append("seed_mismatch")
        if r.get("public_beacon_round")!=b.get("target_round"):er.append("beacon_round_mismatch")
        if r.get("status")!="OK" or r.get("exit_code")!=0:er.append("task_failed")
        raw=r.get("raw_result")
        if not isinstance(raw,dict) or raw.get("schema")!="GMIK4NullAwareMeasuredResourceCellV5":er.append("wrong_raw_result_schema")
        elif raw.get("family")!=spec["family"] or raw.get("grammar")!=spec["grammar"] or raw.get("cell")!=spec["cell"]:er.append("raw_task_spec_mismatch")
        if isinstance(raw,dict):
            cov=raw.get("coverage",{});budget=int(r.get("resource_request",{}).get("budget_scored_candidates",0) or 0)
            if raw.get("verdict")=="K4_RECOVERY_GREEN" and (budget<1_000_000 or not cov.get("budget_requirement_met")):er.append("green_below_registered_search_cap")
            if raw.get("null_frontier") is None:er.append("null_frontier_missing")
        if er:errors.append({"task_index":i,"path":r.get("_path"),"errors":er})
        rows.append(r)
    cnt=collections.Counter(r.get("verdict","MISSING") for r in rows);fc={f:collections.Counter() for f in sorted(fr["families"])};nulls=collections.Counter()
    for r in rows:
        fc[r["family"]][r["verdict"]]+=1;n=(r.get("raw_result") or {}).get("null_dominating_id")
        if n:nulls[n]+=1
    complete=not errors and len(rows)==len(p);allgreen=complete and cnt.get("K4_RECOVERY_GREEN",0)==len(p);anyred=any(red(k) and v for k,v in cnt.items())
    terminal=("K4_V6_EXECUTION_INVALID" if errors else "K4_V6_ALL_REGISTERED_CELLS_GREEN__IG4_IG5_PENDING" if allgreen else "K4_V6_CONTAINS_THEORY_RED" if anyred else "K4_V6_CONTAINS_INCONCLUSIVE" if any(cnt.get(x,0) for x in ("INCONCLUSIVE_GRAMMAR","INCONCLUSIVE_SEARCH","TASK_FAILED")) else "K4_V6_MIXED")
    names=full.get("name_key",{}) if a.reveal_names else {};fam={f:{**dict(fc[f]),**({"revealed_name":names.get(f)} if a.reveal_names else {})} for f in sorted(fc)}
    rep={"schema":"GMIK4NullAwareAggregateV6","terminal":terminal,"freeze_hashes":hs,"public_beacon_round":b.get("target_round"),"expected_tasks":len(p),"receipts_found":len(files),"validated_rows":len(rows),"structural_errors":errors,"verdict_counts":dict(cnt),"family_summary":fam,"null_dominance_counts":dict(nulls),"all_complete":complete,"all_green_same_author_v6_scope":allgreen,"known_form_zero_prior_global_terminal":False,"no_gap_global_terminal":False,"claim_ceiling":"Execution-frozen, null-aware, DG-10-corrected same-author K4 only; IG-4/IG-5 and external transfer/hardware gates remain."}
    os.makedirs(os.path.dirname(a.out_json),exist_ok=True);json.dump(rep,open(a.out_json,"w"),indent=1,sort_keys=True)
    lines=["# Protected K4 V6 aggregate","",f"Terminal: `{terminal}`","",f"Validated: **{len(rows)}/{len(p)}**; structural error groups: **{len(errors)}**.","","## Verdicts",""]+[f"- `{k}`: {cnt[k]}" for k in sorted(cnt)]+["","## Null dominance",""]+[f"- `{k}`: {nulls[k]}" for k in sorted(nulls)]+["","## Families",""]
    for f in sorted(fam):
        nm=f" — {fam[f].get('revealed_name')}" if a.reveal_names else "";vals=", ".join(f"{k}={v}" for k,v in fam[f].items() if k!="revealed_name") or "none";lines.append(f"- `{f}`{nm}: {vals}")
    open(a.out_md,"w").write("\n".join(lines)+"\n");print(json.dumps({"terminal":terminal,"counts":dict(cnt),"nulls":dict(nulls),"validated":len(rows),"errors":len(errors)},sort_keys=True));return 0 if not errors else 2
if __name__=="__main__":raise SystemExit(main())
