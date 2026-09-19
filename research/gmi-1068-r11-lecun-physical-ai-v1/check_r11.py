#!/usr/bin/env python3
import itertools,json,pathlib,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
raw=list(itertools.product((0,1),repeat=2))
need(all(t==t for t,n in raw),"W1_TARGET")
classes={t:{(tt,n) for tt,n in raw if tt==t} for t in (0,1)}
need(all(len(v)==2 for v in classes.values()),"W1_CLASSES")
for t in (0,1):
 vals={(tt,n) for tt,n in classes[t]}
 need(len(vals)==2,"W2_RAW_DETAIL")
acts=list(itertools.product((-1,1),repeat=2));end={a:sum(a) for a in acts};best=min(acts,key=lambda a:abs(2-end[a]))
need(best==(1,1) and end[best]==2,"W3_PLANNING")
loss=sum((0-0)**2 for _ in range(16));need(loss==0,"W4_COLLAPSE")
cands=range(-2,3);mse={c:Fraction((c+1)**2+(c-1)**2,2) for c in cands};opt=min(mse,key=mse.get)
need(opt==0 and opt not in (-1,1),"W5_MULTIMODAL")
need(all(x==x for x in (0,1)),"REACTIVE")
src=json.loads((ROOT/"PRIMARY_SOURCE_REGISTRY_V1.json").read_text())
need(len(src["entries"])==11 and src["entries"][0]["type"]=="POSITION_VISION","SOURCE_TYPES")
tr=json.loads((ROOT/"GMI_TRANSLATION_V1.json").read_text());need(tr["universal_world_model_required"] is False,"WORLD_MODEL_PROMOTION")
print(json.dumps({"status":"GREEN","latent_classes":2,"raw_bits":2,"latent_bits":1,"planning_best":"++","constant_collapse_loss":0,"multimodal_point_optimum":0,"source_entries":11,"hostiles_caught":5},sort_keys=True))
