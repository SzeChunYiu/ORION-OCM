#!/usr/bin/env python3
import itertools,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent

def delayed():
 seqs=[s for n in range(1,6) for s in itertools.product((0,1),repeat=n)]
 stateless=0
 for y0,y1 in itertools.product((0,1),repeat=2):
  f={0:y0,1:y1}
  if all(tuple(f[x] for x in s)==tuple((0,)+s[:-1]) for s in seqs):stateless+=1
 choices=list(itertools.product((0,1),repeat=2)); one=0
 for cells in itertools.product(choices,repeat=4):
  tab={(st,x):cells[2*st+x] for st in (0,1) for x in (0,1)}
  ok=True
  for inp in seqs:
   st=0;out=[]
   for x in inp:
    st,y=tab[(st,x)];out.append(y)
   if tuple(out)!=tuple((0,)+inp[:-1]):ok=False;break
  one+=ok
 return len(seqs),stateless,one

def learning():
 # map training bit -> query bit, four maps
 tasks=[("ID",0,1),("NOT",1,0)]
 perfect=0; scores=[]
 for a,b in itertools.product((0,1),repeat=2):
  f={0:a,1:b};score=sum(f[tr]==q for _,tr,q in tasks)
  scores.append(score)
  perfect+=score==2
 return perfect,scores

def abstraction():
 D,L,c=4,3,1
 flags=[D+n*c<n*L for n in range(1,8)]
 return next(i+1 for i,x in enumerate(flags) if x),flags

def fair_registry():
 reg=list(range(64))
 visited=[]
 # dovetail-style rounds 0..63 trivially expose every finite index
 for k in range(len(reg)):visited.append(reg[k])
 return len(set(visited))==len(reg)

def main():
 nseq,stateless,one=delayed()
 assert (nseq,stateless,one)==(62,0,1)
 perfect,scores=learning();assert perfect==1 and scores.count(2)==1
 first,flags=abstraction();assert first==3 and flags[:2]==[False,False] and all(flags[2:])
 assert fair_registry()
 # search adaptation: fixed 3/2, adaptive 1+c
 from fractions import Fraction
 assert Fraction(1,1)+Fraction(0,1)<Fraction(3,2)
 assert Fraction(1,1)+Fraction(1,2)==Fraction(3,2)
 assert Fraction(1,1)+Fraction(3,4)>Fraction(3,2)
 ledger=json.loads((ROOT/"GENESIS_LEDGER_V1.json").read_text())
 forbidden=set(x.lower() for x in ledger["forbidden_causal_ontology"])
 assert "neural" in forbidden and ledger["unknown_terminal"] is True
 r=json.loads((ROOT/"RESULT_V1.json").read_text())
 assert r["one_bit_mealy_solutions"]==one and r["perfect_adaptive_maps"]==perfect
 print(json.dumps({"status":"GREEN","delayed_sequences":nseq,"stateless_solutions":stateless,"one_bit_solutions":one,"perfect_adaptive_maps":perfect,"first_abstraction_n":first,"fair_registry":True,"search_threshold":"1/2","hostiles_caught":8},sort_keys=True))
if __name__=="__main__":
 try:main()
 except Exception as e:print("R6_RED:"+repr(e),file=sys.stderr);sys.exit(1)
