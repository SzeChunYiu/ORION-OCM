#!/usr/bin/env python3
import json,pathlib,sys,collections
ROOT=pathlib.Path(__file__).resolve().parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
r11=json.loads((ROOT.parent/"gmi-1068-r11-lecun-physical-ai-v1/RESULT_V1.json").read_text())
need(r11["status"]=="GREEN_SOURCE_TYPED_GMI_TRANSLATION_AT_REGISTERED_SCOPE","R11_PARENT_NOT_GREEN")
r=json.loads((ROOT/"AI_FINDING_REGISTRY_V1.json").read_text());allowed=set(r["allowed_verdicts"]);rows=r["rows"]
need(len(rows)==52 and len({x["id"] for x in rows})==52,"ROW_COUNT_OR_IDS")
need(all(x["source_id"] and x["gmi_translation"] and x["boundary"] for x in rows),"MISSING_FIELDS")
need(all(x["verdict"] in allowed for x in rows),"BAD_VERDICT")
required=["scaling","double descent","grokking","in-context","chain-of-thought","retrieval","tool","mixture","lottery","superposition","self-supervised","JEPA","world models","planning","exploration","catastrophic","meta-learning","curriculum","distillation","quantization","low-rank","adversarial","distribution shift","calibration","hallucination","causal representation","embodiment","multi-agent","open-ended","diffusion","flow matching","energy-based","state-space","attention","convolution","recurrent","program synthesis","nearest-neighbor","kernel","decision trees","Bayesian","no-free-lunch"]
text=" ".join(x["finding"] for x in rows).lower();missing=[q for q in required if q.lower() not in text];need(not missing,"MISSING_TOPICS:"+repr(missing))
for x in rows:
 if x["id"] in {"F01","F02"}:need(x["verdict"]=="EMPIRICAL_LAW_NOT_DERIVED","SCALING_PROMOTION")
counts=collections.Counter(x["verdict"] for x in rows)
res=json.loads((ROOT/"RESULT_V1.json").read_text());need(res["rows"]==52 and res["every_publication_claim"] is False,"RESULT_SCOPE")
need(dict(counts)=={k:v for k,v in res["verdict_counts"].items() if v},"COUNT_DRIFT")
print(json.dumps({"status":"GREEN","rows":52,"verdict_counts":dict(sorted(counts.items())),"required_topics":len(required),"missing":[]},sort_keys=True))
