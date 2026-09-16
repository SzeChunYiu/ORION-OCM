from fractions import Fraction
import itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
PRIOR=(1,1); LIKE={'e0':(3,1),'e1':(1,3)}

def norm(ws):
 s=sum(ws); return tuple(Fraction(w,s) for w in ws)

def route1(e):
 # generic multiply then normalize; no family registry or architecture label
 raw=tuple(PRIOR[i]*LIKE[e][i] for i in range(2)); return norm(raw),raw

def route2(e):
 # independent finite integer-weight search for the minimum positive pair matching required odds
 target=Fraction(LIKE[e][0],LIKE[e][1]); hits=[]
 for a,b in itertools.product(range(1,7),repeat=2):
  if Fraction(a,b)==target: hits.append((a+b,a,b))
 _,a,b=min(hits); return norm((a,b)),(a,b),len(hits)

def main():
 out={'schema':'AJ9G_BLIND_EVIDENCE_OUTCOME_V1','registry_data_used':False,'status':'SEARCH_COMPLETE','evidence':{}}
 for e in LIKE:
  p1,r1=route1(e); p2,r2,n=route2(e)
  assert p1==p2
  out['evidence'][e]={'route1_raw':r1,'route2_min_raw':r2,'route2_ratio_hits':n,'normalized':[str(x) for x in p1]}
 assert out['evidence']['e0']['normalized']==['3/4','1/4']
 assert out['evidence']['e1']['normalized']==['1/4','3/4']
 (HERE/'BLIND_OUTCOME_V1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
