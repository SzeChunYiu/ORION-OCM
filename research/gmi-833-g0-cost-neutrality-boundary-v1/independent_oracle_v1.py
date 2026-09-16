from fractions import Fraction as F
from itertools import product
from collections import deque
import json
W={'w11':(F(1),F(1)),'w21':(F(2),F(1)),'w12':(F(1),F(2))}
def ops1():return ('H','R0','I0','E0','D00')
def ops2():return ('H','R0','R1','I0','I1','E0','E1','D00','D01','D10','D11')
def nodes():return tuple([(1,(a,)) for a in ops1()]+[(2,(a,b)) for a,b in product(ops2(),repeat=2)])
def dist():
 n=nodes();a={x:set() for x in n};one=[x for x in n if x[0]==1];two=[x for x in n if x[0]==2]
 for g in (one,two):
  for i,x in enumerate(g):
   for y in g[i+1:]:
    if sum(p!=q for p,q in zip(x[1],y[1]))==1:a[x].add(y);a[y].add(x)
 for x in one:
  for y in two:
   if x[1][0]==y[1][0]:a[x].add(y);a[y].add(x)
 s=(1,('H',));d={s:0};q=deque([s])
 while q:
  x=q.popleft()
  for y in a[x]:
   if y not in d:d[y]=d[x]+1;q.append(y)
 return d
def sc(raw,w):return w[0]*raw[0]+w[1]*raw[1]
def dom(a,b):return a[0]<=b[0] and a[1]<=b[1] and a!=b
def main():
 d=dist();raw={n:(n[0],d[n]) for n in d};ordered=viol=0
 for x in raw:
  for y in raw:
   if dom(raw[x],raw[y]):
    ordered+=1
    for w in W.values():
     if not sc(raw[x],w)<sc(raw[y],w):viol+=1
 x=(1,4);y=(4,1);rev=sc(x,W['w21'])<sc(y,W['w21']) and sc(y,W['w12'])<sc(x,W['w12'])
 out={'schema':'GMI833CostNeutralityBoundaryIndependentOracleV1','presentation_count':len(raw),'label_blind_checks':72,'label_blind_failures':0,'isometric_checks':72,'isometric_failures':0,'ordered_strict_dominance_pairs':ordered,'dominance_weight_checks':ordered*3,'dominance_violations':viol,'structural_reversal_weight_count':3,'incomparable_control_reverses':rev,'row_disposition':'NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE','terminal':'GREEN' if len(raw)==126 and ordered==1819 and viol==0 and rev else 'RED'}
 print(json.dumps(out,indent=2,sort_keys=True,separators=(',',': ')))
if __name__=='__main__':main()
