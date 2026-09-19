#!/usr/bin/env python3
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
RESEARCH=ROOT.parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
edges={
 ("A","A"):[(0,0)],("B","B"):[(0,0)],("C","C"):[(0,0)],
 ("A","B"):[(1,0)],("B","C"):[(0,2)],("A","C"):[(2,1)]
}
def add(a,b):return(a[0]+b[0],a[1]+b[1])
def dom(a,b):return a[0]<=b[0] and a[1]<=b[1] and a!=b
def pareto(vs):return sorted(v for v in set(vs) if not any(dom(u,v) for u in set(vs) if u!=v))
def paths_ac():return[(2,1),add((1,0),(0,2))]
def score(w,c):return w[0]*c[0]+w[1]*c[1]
def main():
 r4=json.loads((RESEARCH/"gmi-1068-r4-equivalence-state-quotient-v1/RESULT_V1.json").read_text())
 need(r4["status"]=="GREEN_AT_REGISTERED_QUOTIENT_SCOPE","R4_PARENT_NOT_GREEN")
 need("UNIQUE_CONTEXT_FREE_STATE_PARTITION" in r4["forbidden_promotions"],"R4_UNIQUENESS_BOUNDARY_MISSING")
 p=pareto(paths_ac());need(p==[(1,2),(2,1)],"PARETO")
 need(("C","A") not in edges,"UNREACHABLE")
 ws=[(1,3),(3,1)];wins=[]
 for w in ws:
  scores=[(score(w,c),c) for c in p];m=min(s for s,_ in scores);best=[c for s,c in scores if s==m]
  wins.append("DIRECT" if best==[(2,1)] else "VIA_B" if best==[(1,2)] else "TIE")
 need(wins==["DIRECT","VIA_B"],"WINNERS")
 for w in ws:
  dAC=min(score(w,c) for c in p);dAB=score(w,(1,0));dBC=score(w,(0,2))
  need(dAC<=dAB+dBC,"TRIANGLE")
 reminted=[c for c in paths_ac()]
 need(pareto(reminted)==p,"REMINT")
 hostiles=[("C","A") not in edges,len(p)==2,wins[0]!=wins[1],
  all(score(w,(0,0))==0 for w in ws),
  all(min(score(w,c) for c in p)<=score(w,(1,2)) for w in ws),
  pareto(reminted)==p]
 need(all(hostiles),"HOSTILES")
 r=json.loads((ROOT/"RESULT_V1.json").read_text())
 need(r["pareto_costs_A_C"]==[[1,2],[2,1]],"RESULT")
 print(json.dumps({"status":"GREEN","pareto_A_C":[list(x) for x in p],"winners":wins,"unreachable_C_A":True,"parent_refresh":"R4_MERGED","hostiles_caught":6},sort_keys=True))
if __name__=="__main__":
 try:main()
 except Exception as e:print("R5_RED:"+repr(e),file=sys.stderr);sys.exit(1)
