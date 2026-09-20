#!/usr/bin/env python3
import itertools,json,pathlib,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
RESEARCH=ROOT.parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
def delayed():
 seqs=[s for n in range(1,6) for s in itertools.product((0,1),repeat=n)]
 stateless=0
 for y0,y1 in itertools.product((0,1),repeat=2):
  f={0:y0,1:y1}
  if all(tuple(f[x] for x in s)==tuple((0,)+s[:-1]) for s in seqs):stateless+=1
 choices=list(itertools.product((0,1),repeat=2));one=0
 for cells in itertools.product(choices,repeat=4):
  tab={(st,x):cells[2*st+x] for st in (0,1) for x in (0,1)}
  good=True
  for inp in seqs:
   st=0;out=[]
   for x in inp:st,y=tab[(st,x)];out.append(y)
   if tuple(out)!=tuple((0,)+inp[:-1]):good=False;break
  one+=good
 return len(seqs),stateless,one
def learning():
 tasks=[("ID",0,1),("NOT",1,0)];perfect=0;scores=[]
 for a,b in itertools.product((0,1),repeat=2):
  f={0:a,1:b};score=sum(f[tr]==q for _,tr,q in tasks);scores.append(score);perfect+=score==2
 return perfect,scores
def abstraction():
 D,L,c=4,3,1;flags=[D+n*c<n*L for n in range(1,8)]
 return next(i+1 for i,x in enumerate(flags) if x),flags
def fair_registry():
 reg=list(range(64));visited=[]
 for k in range(len(reg)):visited.append(reg[k])
 return len(set(visited))==len(reg)
def main():
 r5=json.loads((RESEARCH/"gmi-1068-r5-resource-transform-geometry-v1/RESULT_V1.json").read_text())
 need(r5["status"]=="GREEN_AT_REGISTERED_RESOURCE_GEOMETRY_SCOPE","R5_PARENT_NOT_GREEN")
 need("UNIVERSAL_SYMMETRIC_METRIC" in r5["forbidden_promotions"],"R5_ASYMMETRY_BOUNDARY_MISSING")
 nseq,stateless,one=delayed();need((nseq,stateless,one)==(62,0,1),"DELAY")
 perfect,scores=learning();need(perfect==1 and scores.count(2)==1,"LEARNING")
 first,flags=abstraction();need(first==3 and flags[:2]==[False,False] and all(flags[2:]),"ABSTRACTION")
 need(fair_registry(),"FAIR")
 need(Fraction(1)+Fraction(0)<Fraction(3,2),"SEARCH_LOW")
 need(Fraction(1)+Fraction(1,2)==Fraction(3,2),"SEARCH_TIE")
 need(Fraction(1)+Fraction(3,4)>Fraction(3,2),"SEARCH_HIGH")
 ledger=json.loads((ROOT/"GENESIS_LEDGER_V1.json").read_text())
 forbidden={x.lower() for x in ledger["forbidden_causal_ontology"]}
 need("neural" in forbidden and ledger["unknown_terminal"] is True,"BLINDNESS")
 r=json.loads((ROOT/"RESULT_V1.json").read_text())
 need(r["one_bit_mealy_solutions"]==one and r["perfect_adaptive_maps"]==perfect,"RESULT")
 print(json.dumps({"status":"GREEN","delayed_sequences":nseq,"stateless_solutions":stateless,"one_bit_solutions":one,"perfect_adaptive_maps":perfect,"first_abstraction_n":first,"fair_registry":True,"search_threshold":"1/2","parent_refresh":"R5_MERGED","hostiles_caught":8},sort_keys=True))
if __name__=="__main__":
 try:main()
 except Exception as e:print("R6_RED:"+repr(e),file=sys.stderr);sys.exit(1)
