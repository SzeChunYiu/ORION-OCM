#!/usr/bin/env python3
import importlib.util,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("causal",ROOT/"causal_derivation_v1.py")
causal=importlib.util.module_from_spec(spec);spec.loader.exec_module(causal)
deny=["neuron","neural","relu","layer","network","backprop","attention","convolution","transformer","target-architecture"]
src=(ROOT/"causal_derivation_v1.py").read_text().lower()
hits=[t for t in deny if t in src]
if hits: raise SystemExit("CAUSAL_DENYLIST_HITS:"+repr(hits))
counts,winners=causal.run()
assert counts=={"worlds":375,"k0":15,"k1":120,"k2":240,"routeA_checks":24375,"routeB_checks":24375,"remint_checks":24375},counts
def flat(d):
 out={}
 for k,v in d.items():
  assert len(k)==1
  out[k[0]]=v
 return out
wa=flat(winners["S_ARITH"]);wb=flat(winners["S_BRANCH"])
assert wa=={"AFFINE":15,"HINGE":360},wa
assert wb=={"AFFINE":15,"BRANCH":360},wb
r=json.loads((ROOT/"RESULT_V1.json").read_text())
assert r["winners_S_ARITH"]=={"AFFINE":15,"HINGE":360,"BRANCH":0,"TABLE":0}
assert r["winners_S_BRANCH"]=={"AFFINE":15,"HINGE":0,"BRANCH":360,"TABLE":0}
assert r["posthoc_neural_like_matches"]==360 and r["literal_historical_ignorance_claim"] is False
cl=json.loads((ROOT/"POSTHOC_CLASSIFIER_V1.json").read_text())
assert cl["causal_access"] is False
print(json.dumps({"status":"GREEN","counts":counts,"winners_S_ARITH":wa,"winners_S_BRANCH":wb,"denylist_hits":hits,"substrate_inversions":360,"posthoc_neural_like":360},sort_keys=True))
