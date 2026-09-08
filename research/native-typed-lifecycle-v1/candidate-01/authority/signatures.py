"""Canonicalize retained finite tables; no theorem labels or proof/runtime calls."""
import hashlib,itertools,json
def raw(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
def project_world(world,injection):
 answer=0
 for region in range(8):
  if world&(1<<region):
   projected=sum(1<<i for i,target in enumerate(injection) if region&(1<<target))
   answer|=1<<projected
 return answer
def canonical(table,predicates):
 n=len(predicates)
 if not 1<=n<=3 or len(table)!=(1<<(1<<n))-1:raise ValueError("TABLE_DIMENSIONS")
 values=[r["truth"] for r in table]
 if [r["world_mask"] for r in table]!=list(range(1,len(table)+1)):raise ValueError("WORLD_POPULATION")
 width=len(values[0])
 if width<2 or any(len(v)!=width or any(type(b)is not bool for b in v) for v in values):
  raise ValueError("TRUTH_SHAPE")
 roles=[];joints=[]
 for injection in itertools.permutations(range(3),n):
  expanded=[values[project_world(world,injection)-1] for world in range(1,256)]
  joint=[[all(v[:-1]),v[-1]] for v in expanded]
  mapping={p:"Q"+str(i) for p,i in zip(predicates,injection)}
  roles.append((raw(expanded),mapping,expanded))
  joints.append((raw(joint),mapping,joint))
 def best(choices):
  body,mapping,table=min(choices,key=lambda v:v[0])
  return {"sha256":hashlib.sha256(body).hexdigest(),"positive_mapping":mapping,"table":table}
 return {"role_ordered":best(roles),"joint_premise_query":best(joints)}
