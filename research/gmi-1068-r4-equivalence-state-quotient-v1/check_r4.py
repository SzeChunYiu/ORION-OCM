#!/usr/bin/env python3
import json,pathlib,sys,itertools
ROOT=pathlib.Path(__file__).resolve().parent
resp={"h0":(0,0,0),"h1":(0,1,0),"h2":(0,1,0)}
H=tuple(resp)

def signature(h,tests): return tuple(resp[h][i] for i in tests)
def quotient(tests):
 d={}
 for h in H:d.setdefault(signature(h,tests),[]).append(h)
 return sorted(sorted(v) for v in d.values())
def delayed_copy_one_state_possible():
 # all stateless maps input->output
 seqs=[bits for n in range(1,6) for bits in itertools.product((0,1),repeat=n)]
 for y0,y1 in itertools.product((0,1),repeat=2):
  f={0:y0,1:y1}
  if all(tuple(f[x] for x in s)==tuple((0,)+s[:-1]) for s in seqs): return True
 return False
def delayed_copy_two_state_count():
 seqs=[bits for n in range(1,6) for bits in itertools.product((0,1),repeat=n)]
 ok=0
 # Mealy table per state,input -> (next_state,output), 4 cells, each 4 choices =>256
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
 qf=quotient((0,1,2)); qr=quotient((0,))
 assert qf==[["h0"],["h1","h2"]],qf
 assert qr==[["h0","h1","h2"]],qr
 sep=eq=0
 for a,b in itertools.combinations(H,2):
  if resp[a]==resp[b]:eq+=1
  else:sep+=1
 assert (sep,eq)==(2,1)
 assert not delayed_copy_one_state_possible()
 assert delayed_copy_two_state_count()==1
 r=json.loads((ROOT/"RESULT_V1.json").read_text())
 assert r["full_quotient_classes"]==len(qf) and r["restricted_quotient_classes"]==len(qr)
 assert r["delayed_copy_min_states"]==2
 hostiles=[
  len(qf)!=len(qr),
  sep>0,
  eq>0,
  not delayed_copy_one_state_possible(),
  delayed_copy_two_state_count()==1,
  signature("h1",(0,1,2))==signature("h2",(0,1,2))
 ]
 assert all(hostiles)
 print(json.dumps({"status":"GREEN","full_quotient":qf,"restricted_quotient":qr,"separated_pairs":sep,"equivalent_pairs":eq,"delayed_copy_two_state_solutions":1,"hostiles_caught":6},sort_keys=True))
if __name__=="__main__":
 try:main()
 except Exception as e:print("R4_RED:"+repr(e),file=sys.stderr);sys.exit(1)
