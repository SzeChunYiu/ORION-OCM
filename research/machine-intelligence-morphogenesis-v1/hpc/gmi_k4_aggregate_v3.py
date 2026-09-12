#!/usr/bin/env python3
"""Fail-closed aggregate for protected grammar-native K4 V3 only."""
from __future__ import annotations
import argparse,collections,glob,hashlib,json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); FREEZE=os.path.join(ROOT,"GMI_K4_LOFO_FREEZE_V1.json"); GEN=os.path.join(ROOT,"GMI_K4_GENERATOR_FREEZE_V1.json"); SUCC=os.path.join(ROOT,"GMI_K4_GRAMMAR_NATIVE_SUCCESSOR_FREEZE_V3.json"); BEACON=os.path.join(ROOT,"GMI_K4_PUBLIC_BEACON_V3.json"); RES=os.path.join(ROOT,"microscopes","results","k4_v3")
def jh(p): raw=open(p).read(); return json.loads(raw),hashlib.sha256(raw.encode()).hexdigest()
def plan(fr): return [{"family":f,"grammar":g,"cell":c} for f in sorted(fr["families"]) for g in sorted(fr["grammars"]) for c in ("w1","w2","w4","w8")]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pattern",default=os.path.join(RES,"K4V3_*.json")); ap.add_argument("--reveal-names",action="store_true"); ap.add_argument("--out-json",default=os.path.join(RES,"K4_V3_AGGREGATE.json")); ap.add_argument("--out-md",default=os.path.join(RES,"K4_V3_AGGREGATE.md")); a=ap.parse_args()
    full,fsha=jh(FREEZE); fr=dict(full); fr.pop("name_key",None); gen,gsha=jh(GEN); succ,ssha=jh(SUCC); beacon,bsha=jh(BEACON)
    if succ.get("status")!="FROZEN_BEFORE_V3_PUBLIC_BEACON_AND_ANY_V3_PROTECTED_RESULT": raise SystemExit("bad V3 successor")
    if beacon.get("status")!="ACQUIRED_NO_REROLL" or not beacon.get("sha256_signature_consistency_verified"): raise SystemExit("bad V3 beacon")
    p=plan(fr); files=sorted(glob.glob(a.pattern)); by=collections.defaultdict(list); parse=[]
    for path in files:
        try:
            r=json.load(open(path)); r["_path"]=path
            if r.get("schema")!="GMIK4TaskReceiptV4": parse.append({"path":path,"error":f"wrong schema {r.get('schema')}"}); continue
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
        for k,v in (("freeze_artifact_sha256",fsha),("generator_freeze_sha256",gsha),("successor_freeze_sha256",ssha),("public_beacon_sha256",bsha)):
            if r.get(k)!=v: er.append(k+"_mismatch")
        th=hashlib.sha256(json.dumps({**spec,"prediction_freeze":fsha,"generator_freeze":gsha,"successor_freeze":ssha},sort_keys=True).encode()).hexdigest(); seed=int(hashlib.sha256(("GMI-K4-V3"+th+beacon["randomness"]).encode()).hexdigest()[:16],16)%(2**32)
        if r.get("task_hash")!=th: er.append("task_hash_mismatch")
        if r.get("seed")!=seed: er.append("seed_mismatch")
        if r.get("public_beacon_round")!=beacon.get("target_round"): er.append("beacon_round_mismatch")
        if r.get("status")!="OK" or r.get("exit_code")!=0: er.append("task_failed")
        raw=r.get("raw_result")
        if not isinstance(raw,dict) or raw.get("schema")!="GMIK4GrammarNativeCellV3": er.append("wrong_raw_result_schema")
        if isinstance(raw,dict) and raw.get("grammar")!=spec["grammar"]: er.append("raw_grammar_mismatch")
        if er: errors.append({"task_index":i,"path":r.get("_path"),"errors":er})
        rows.append(r)
    cnt=collections.Counter(r.get("verdict","MISSING") for r in rows); fc={f:collections.Counter() for f in sorted(fr["families"])}; gc={g:collections.Counter() for g in sorted(fr["grammars"])}; cc={c:collections.Counter() for c in ("w1","w2","w4","w8")}
    inv_sizes={}; prefixes={}
    for r in rows:
        fc[r["family"]][r["verdict"]]+=1; gc[r["grammar"]][r["verdict"]]+=1; cc[r["cell"]][r["verdict"]]+=1; raw=r.get("raw_result",{}); inv_sizes[r["grammar"]]=raw.get("grammar_inventory_size"); prefixes[r["grammar"]]=raw.get("grammar_token_prefix")
    complete=not errors and len(rows)==len(p); allgreen=complete and cnt.get("K4_RECOVERY_GREEN",0)==len(p)
    terminal=("K4_V3_EXECUTION_INVALID" if errors else "K4_V3_ALL_REGISTERED_CELLS_GREEN__IG4_IG5_PENDING" if allgreen else "K4_V3_CONTAINS_THEORY_RED" if cnt.get("THEORY_RED",0) else "K4_V3_CONTAINS_INCONCLUSIVE" if any(cnt.get(x,0) for x in ("INCONCLUSIVE_GRAMMAR","INCONCLUSIVE_SEARCH","TASK_FAILED")) else "K4_V3_MIXED")
    names=full.get("name_key",{}) if a.reveal_names else {}; fam={f:{**dict(fc[f]),**({"revealed_name":names.get(f)} if a.reveal_names else {})} for f in sorted(fc)}
    rep={"schema":"GMIK4GrammarNativeAggregateV3","terminal":terminal,"prediction_freeze_sha256":fsha,"generator_freeze_sha256":gsha,"successor_freeze_sha256":ssha,"public_beacon_sha256":bsha,"public_beacon_round":beacon.get("target_round"),"expected_tasks":len(p),"receipts_found":len(files),"validated_rows":len(rows),"structural_errors":errors,"verdict_counts":dict(cnt),"family_summary":fam,"grammar_summary":{k:dict(v) for k,v in gc.items()},"cell_summary":{k:dict(v) for k,v in cc.items()},"grammar_inventory_sizes":inv_sizes,"grammar_token_prefixes":prefixes,"all_complete":complete,"all_green_same_author_grammar_native_scope":allgreen,"independence":{"generator":"FROZEN","seed":"FUTURE_PUBLIC_BEACON","implementation_disjointness":"REQUIRED_BY_V3_ENGINE","IG-4":"PENDING_INDEPENDENT_BUCKETING","IG-5":"PENDING_INDEPENDENT_PRIMITIVES"},"known_form_zero_prior_global_terminal":False,"no_gap_global_terminal":False,"claim_ceiling":"Grammar-native protected K4 at same-author finite scope only; IG-4/IG-5, K5, real-transfer and hardware gates remain separate."}
    os.makedirs(os.path.dirname(a.out_json),exist_ok=True); json.dump(rep,open(a.out_json,"w"),indent=1,sort_keys=True)
    lines=["# Protected grammar-native K4 V3 aggregate","",f"Terminal: `{terminal}`","",f"Validated: **{len(rows)}/{len(p)}**; structural error groups: **{len(errors)}**.","","## Verdicts",""]+[f"- `{k}`: {cnt[k]}" for k in sorted(cnt)]+["","## Grammars",""]+[f"- `{g}`: inventory={inv_sizes.get(g)}, prefix={prefixes.get(g)}, verdicts={dict(gc[g])}" for g in sorted(gc)]+["","## Families",""]
    for f in sorted(fam):
        nm=f" — {fam[f].get('revealed_name')}" if a.reveal_names else ""; vals=", ".join(f"{k}={v}" for k,v in fam[f].items() if k!="revealed_name") or "none"; lines.append(f"- `{f}`{nm}: {vals}")
    lines += ["","IG-4 and IG-5 remain external independence gates. This aggregate cannot flip K5 or global closure terminals.",""]; open(a.out_md,"w").write("\n".join(lines)); print(json.dumps({"terminal":terminal,"counts":dict(cnt),"validated":len(rows),"errors":len(errors)},sort_keys=True)); return 0 if not errors else 2
if __name__=="__main__": raise SystemExit(main())
