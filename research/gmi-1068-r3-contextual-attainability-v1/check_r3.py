#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent
vals={"h0":(0,0),"h1":(1,2),"h2":(2,5),"h3":(2,3)}
full=set(vals)
budget={"h0","h1"}

def dominates(a,b):
  # higher performance, lower cost; at least one strict
  pa,ca=vals[a]; pb,cb=vals[b]
  return pa>=pb and ca<=cb and (pa>pb or ca<cb)

def frontier(H):
  return sorted(h for h in H if not any(dominates(g,h) for g in H if g!=h))

def cap(H,t): return any(vals[h][0]>=t for h in H)
def scalar_winner(H,lam):
  scores={h:lam*vals[h][0]-vals[h][1] for h in H}
  m=max(scores.values())
  return sorted(h for h,s in scores.items() if s==m)

def main():
  assert budget<=full
  assert {vals[h] for h in budget} <= {vals[h] for h in full}
  ff=frontier(full); fb=frontier(budget)
  assert ff==["h0","h1","h3"],ff
  assert fb==["h0","h1"],fb
  assert not cap(budget,2) and cap(full,2)
  assert not cap(full,3)
  assert scalar_winner(full,1)==["h0"]
  assert scalar_winner(full,3)==["h3"]
  hostiles=[
   int(not budget.issuperset(full)),
   int(set(ff)!=set(full)),
   int(not cap(budget,2)),
   int(cap(full,2)),
   int(not cap(full,3)),
   int(scalar_winner(full,1)!=scalar_winner(full,3))
  ]
  assert sum(bool(x) for x in hostiles)==6
  r=json.loads((ROOT/"RESULT_V1.json").read_text())
  assert r["full_frontier_count"]==len(ff)
  assert r["budget_frontier_count"]==len(fb)
  print(json.dumps({"status":"GREEN","full_frontier":ff,"budget_frontier":fb,"phase_low":scalar_winner(full,1),"phase_high":scalar_winner(full,3),"hostiles_caught":6},sort_keys=True))
if __name__=="__main__":
  try: main()
  except Exception as e:
    print("R3_RED:"+repr(e),file=sys.stderr);sys.exit(1)
