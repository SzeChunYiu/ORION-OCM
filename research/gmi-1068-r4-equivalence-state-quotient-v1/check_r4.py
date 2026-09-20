#!/usr/bin/env python3
import json,pathlib,sys,itertools
ROOT=pathlib.Path(__file__).resolve().parent
RESEARCH=ROOT.parent
resp={"h0":(0,0,0),"h1":(0,1,0),"h2":(0,1,0)}
H=tuple(resp)

def need(cond,msg):
 if not cond: raise RuntimeError(msg)
def signature(h,tests): return tuple(resp[h][i] for i in tests)
def quotient(tests):
 d={}
 for h in H:d.setdefault(signature(h,tests),[]).append(h)
 return sorted(sorted(v) for v in d.values())
def delayed_copy_one_state_possible():
 seqs=[bits for n in range(1,6) for bits in itertools.product((0,1),repeat=n)]
 for y0,y1 in itertools.product((0,1),repeat=2):
  f={0:y0,1:y1}
  if all(tuple(f[x] for x in s)==tuple((0,)+s[:-1]) for s in seqs): return True
 return False
def delayed_copy_two_state_count():
 seqs=[bits for n in range(1,6) for bits in itertools.product((0,1),repeat=n)]
 ok=0
 choices=list(itertools.product((0,1),repeat=2))
 for cells in itertools.product(choices,repeat=4):
  table={(s,x):cells[2*s+x] for s in (0,1) for x in (0,1)}
  good=True
  for inp in seqs:
   st=0; outs=[]
   for x in inp:
    st2,y=table[(st,x)];outs.append(y);st=st2
   if tuple(outs)!=tuple((0,)+inp[:-1]):good=False;break
  if good:ok+=1
 return ok

def main():
 # Dependency refresh: this reads corrected R3 from the PR synthetic merge tree.
 p3=json.loads((RESEARCH/"gmi-1068-r3-contextual-attainability-v1/RESULT_V1.json").read_text())
 need(p3["history_scope"]=="FINITE_ADMISSIBLE_HISTORIES","R3_SCOPE_NOT_REFRESHED")
 need("FINITE_HISTORY_ATTAINABILITY_IMPLIES_OMEGA_OR_LIMIT_ATTAINABILITY" in p3["forbidden_promotions"],"R3_LIMIT_BOUNDARY_MISSING")
 need("UNIQUE_CAUSAL_BARRIER_FROM_BASELINE_ATTAINABILITY" in p3["forbidden_promotions"],"R3_BARRIER_BOUNDARY_MISSING")

 qf=quotient((0,1,2)); qr=quotient((0,))
 need(qf==[["h0"],["h1","h2"]],"FULL_QUOTIENT")
 need(qr==[["h0","h1","h2"]],"RESTRICTED_QUOTIENT")
 sep=eq=0
 for a,b in itertools.combinations(H,2):
  if resp[a]==resp[b]:eq+=1
  else:sep+=1
 need((sep,eq)==(2,1),"PAIR_COUNTS")
 need(not delayed_copy_one_state_possible(),"STATELESS_FALSE_POSITIVE")
 need(delayed_copy_two_state_count()==1,"MEALY_SOLUTION_COUNT")
 r=json.loads((ROOT/"RESULT_V1.json").read_text())
 need(r["full_quotient_classes"]==len(qf) and r["restricted_quotient_classes"]==len(qr),"RESULT_QUOTIENT")
 need(r["delayed_copy_min_states"]==2,"RESULT_MIN_STATE")
 hostiles=[
  len(qf)!=len(qr), sep>0, eq>0,
  not delayed_copy_one_state_possible(),
  delayed_copy_two_state_count()==1,
  signature("h1",(0,1,2))==signature("h2",(0,1,2))
 ]
 need(all(hostiles),"HOSTILES")
 print(json.dumps({"status":"GREEN","parent_refresh":"R3_CORRECTED","full_quotient":qf,"restricted_quotient":qr,"separated_pairs":sep,"equivalent_pairs":eq,"delayed_copy_two_state_solutions":1,"hostiles_caught":6},sort_keys=True))
if __name__=="__main__":
 try:main()
 except Exception as e:print("R4_RED:"+repr(e),file=sys.stderr);sys.exit(1)
