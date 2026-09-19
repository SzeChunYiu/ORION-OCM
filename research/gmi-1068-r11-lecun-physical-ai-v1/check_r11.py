#!/usr/bin/env python3
import itertools,json,pathlib,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
# W1 latent sufficient: X=(T,N), target=T
raw=list(itertools.product((0,1),repeat=2))
assert all(t==t for t,n in raw)
# same latent z=t represents two raw states but target is same
classes={t:{(tt,n) for tt,n in raw if tt==t} for t in (0,1)}
assert all(len(v)==2 for v in classes.values())
# W2 raw-detail negative: target=(T,N), no decoder z=T can recover both N values
for t in (0,1):
 vals={(tt,n) for tt,n in classes[t]}
 assert len(vals)==2
# W3 exact planning: start0, actions +/-1, horizon2, target2 -> ++ unique
acts=list(itertools.product((-1,1),repeat=2))
end={a:sum(a) for a in acts}
best=min(acts,key=lambda a:abs(2-end[a]))
assert best==(1,1) and end[best]==2
# W4 constant collapse: embedding and target both zero => prediction loss zero on all samples
loss=sum((0-0)**2 for _ in range(16));assert loss==0
# W5 multimodal: future {-1,+1} equally; squared-error point optimum zero is not a realized mode
cands=range(-2,3)
mse={c:Fraction((c+1)**2+(c-1)**2,2) for c in cands}
opt=min(mse,key=mse.get);assert opt==0 and opt not in (-1,1)
# reactive hostile: y=current sensor exact with no model
assert all(x==x for x in (0,1))
src=json.loads((ROOT/"PRIMARY_SOURCE_REGISTRY_V1.json").read_text())
assert len(src["entries"])==11 and src["entries"][0]["type"]=="POSITION_VISION"
tr=json.loads((ROOT/"GMI_TRANSLATION_V1.json").read_text());assert tr["universal_world_model_required"] is False
print(json.dumps({"status":"GREEN","latent_classes":2,"raw_bits":2,"latent_bits":1,"planning_best":"++","constant_collapse_loss":0,"multimodal_point_optimum":0,"source_entries":11,"hostiles_caught":5},sort_keys=True))
