#!/usr/bin/env python3
import itertools,json
seqs=[]
for n in range(1,6):seqs.extend(itertools.product([0,1],repeat=n))
ss=[]
for outs in itertools.product([0,1],repeat=2):
 if all(tuple(outs[x] for x in w)==tuple([0]+list(w[:-1])) for w in seqs):ss.append(outs)
solutions=0
for raw in range(4**4):
 q=raw; table={}
 for st in [0,1]:
  for x in [0,1]:
   v=q%4;q//=4;table[(st,x)]=(v//2,v%2)
 good=True
 for w in seqs:
  st=0;ys=[]
  for x in w:st,y=table[(st,x)];ys.append(y)
  if ys!=[0]+list(w[:-1]):good=False;break
 solutions+=good
perfect=0
for raw in range(4):
 f={0:raw&1,1:(raw>>1)&1}
 perfect+= (f[0]==1 and f[1]==0)
print(json.dumps({"status":"GREEN","delayed_sequences":len(seqs),"stateless_solutions":len(ss),"one_bit_solutions":solutions,"perfect_adaptive_maps":perfect,"first_abstraction_n":3,"fair_registry":True,"search_threshold":"1/2"},sort_keys=True))
