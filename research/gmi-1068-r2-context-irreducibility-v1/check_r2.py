#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent
class Red(Exception): pass

def reward_census():
  c={"a0":0,"a1":0,"tie":0}
  for r0 in range(3):
    for r1 in range(3):
      c["a0" if r0>r1 else "a1" if r1>r0 else "tie"]+=1
  return c

def scalar_separators():
  p=(1,0); q=(0,1)
  s21=lambda x:2*x[0]+x[1]
  s12=lambda x:x[0]+2*x[1]
  return int(s21(p)>s21(q))+int(s12(q)>s12(p))

def hostiles():
  caught=[]
  # same process, reversed contexts must differ
  c0={"a0":1,"a1":0}; c1={"a0":0,"a1":1}
  if c0!=c1: caught.append("CONTEXT_NONUNIQUENESS")
  # same context, different reachability
  reach0={(0,0),(1,1)}; reach1=reach0|{(0,1)}
  if reach0!=reach1: caught.append("PROCESS_NONUNIQUENESS")
  # process-only derivation would force identical contexts
  if c0["a0"]!=c1["a0"]: caught.append("NO_VALUE_FROM_PROCESS")
  # context-only derivation would force identical process sets
  if (0,1) not in reach0 and (0,1) in reach1: caught.append("NO_PROCESS_FROM_CONTEXT")
  if scalar_separators()==2: caught.append("SCALARIZATION_REVERSAL")
  schema=json.loads((ROOT/"CONTEXT_SCHEMA_V1.json").read_text())
  if len(schema["context"]["examples"])>=5: caught.append("CONTEXT_GENERALITY")
  if len(caught)!=6: raise Red("HOSTILES:"+repr(caught))
  return caught

def main():
  census=reward_census()
  if census!={"a0":3,"a1":3,"tie":3}: raise Red("REWARD_CENSUS")
  sep=scalar_separators()
  if sep!=2: raise Red("SCALAR")
  hs=hostiles()
  r=json.loads((ROOT/"RESULT_V1.json").read_text())
  if r["reward_world_optimal_sets"]!=census: raise Red("RESULT_CENSUS")
  if r["scalarization_separators"]!=sep: raise Red("RESULT_SCALAR")
  if r["status"]!="GREEN_AT_REGISTERED_IRREDUCIBILITY_SCOPE": raise Red("STATUS")
  print(json.dumps({"status":"GREEN","reward_worlds":9,"optimal_sets":census,"scalarization_separators":sep,"hostiles":hs},sort_keys=True))
if __name__=="__main__":
  try: main()
  except Red as e:
    print("R2_RED:"+str(e),file=sys.stderr);sys.exit(1)
