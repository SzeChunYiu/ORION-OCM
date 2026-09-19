#!/usr/bin/env python3
import json,pathlib,sys,collections
ROOT=pathlib.Path(__file__).resolve().parent
r=json.loads((ROOT/"AI_FINDING_REGISTRY_V1.json").read_text())
allowed=set(r["allowed_verdicts"]);rows=r["rows"]
assert len(rows)==52 and len({x["id"] for x in rows})==52
assert all(x["source_id"] and x["gmi_translation"] and x["boundary"] for x in rows)
assert all(x["verdict"] in allowed for x in rows)
required=["scaling","double descent","grokking","in-context","chain-of-thought","retrieval","tool","mixture","lottery","superposition","self-supervised","JEPA","world models","planning","exploration","catastrophic","meta-learning","curriculum","distillation","quantization","low-rank","adversarial","distribution shift","calibration","hallucination","causal representation","embodiment","multi-agent","open-ended","diffusion","flow matching","energy-based","state-space","attention","convolution","recurrent","program synthesis","nearest-neighbor","kernel","decision trees","Bayesian","no-free-lunch"]
text=" ".join(x["finding"] for x in rows).lower()
missing=[q for q in required if q.lower() not in text]
assert not missing,missing
# empirical scaling rows may not be falsely marked DERIVED
for x in rows:
 if x["id"] in {"F01","F02"}:assert x["verdict"]=="EMPIRICAL_LAW_NOT_DERIVED"
counts=collections.Counter(x["verdict"] for x in rows)
res=json.loads((ROOT/"RESULT_V1.json").read_text());assert res["rows"]==52 and res["every_publication_claim"] is False
assert dict(counts)=={k:v for k,v in res["verdict_counts"].items() if v}
print(json.dumps({"status":"GREEN","rows":52,"verdict_counts":dict(sorted(counts.items())),"required_topics":len(required),"missing":[]},sort_keys=True))
