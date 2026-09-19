#!/usr/bin/env python3
import json, pathlib, sys, copy
ROOT=pathlib.Path(__file__).resolve().parent

class Red(Exception): pass

def preorder_model():
    objs=(0,1,2)
    arrows=[(a,b) for a in objs for b in objs if a<=b]
    def comp(f,g):
        if f[1]!=g[0]: raise Red("ILL_TYPED_COMPOSITION")
        return (f[0],g[1])
    assoc=0
    for f in arrows:
      for g in arrows:
       if f[1]!=g[0]: continue
       for h in arrows:
        if g[1]!=h[0]: continue
        if comp(comp(f,g),h)!=comp(f,comp(g,h)): raise Red("PREORDER_ASSOC")
        assoc+=1
    for f in arrows:
      if comp((f[0],f[0]),f)!=f: raise Red("PREORDER_LEFT_ID")
      if comp(f,(f[1],f[1]))!=f: raise Red("PREORDER_RIGHT_ID")
    return {"objects":3,"arrows":len(arrows),"assoc_triples":assoc}

def c2_model():
    vals=(0,1)
    op=lambda a,b:a^b
    triples=0
    for a in vals:
      for b in vals:
       for c in vals:
        if op(op(a,b),c)!=op(a,op(b,c)): raise Red("C2_ASSOC")
        triples+=1
    for a in vals:
      if op(0,a)!=a or op(a,0)!=a: raise Red("C2_ID")
    return {"objects":1,"morphisms":2,"assoc_triples":triples}

def hostiles():
    caught=[]
    try:
      f=(0,1); g=(0,1)
      if f[1]!=g[0]: raise Red("typed")
    except Red: caught.append("TYPE")
    op=lambda a,b:1-a
    if any(op(op(a,b),c)!=op(a,op(b,c)) for a in (0,1) for b in (0,1) for c in (0,1)):
      caught.append("ASSOCIATIVITY")
    op_left=lambda a,b:b
    if any(op_left(a,0)!=a for a in (0,1)): caught.append("RIGHT_IDENTITY")
    op_right=lambda a,b:a
    if any(op_right(0,a)!=a for a in (0,1)): caught.append("LEFT_IDENTITY")
    irr=json.loads((ROOT/"IRREDUCIBILITY_V1.json").read_text())
    retained={x["component"] for x in irr["retained"]}
    if "TENSOR" not in retained: caught.append("NO_TENSOR_PROMOTION")
    if "EXTERNAL_ADMISSIBILITY_PREDICATE" not in retained: caught.append("NO_ADM_PROMOTION")
    if len(caught)!=6: raise Red("HOSTILES:"+repr(caught))
    return caught

def main():
    p=preorder_model(); c=c2_model(); hs=hostiles()
    result=json.loads((ROOT/"RESULT_V1.json").read_text())
    if result["status"]!="GREEN_AT_REGISTERED_MINIMALITY_SCOPE": raise Red("STATUS")
    if result["planted_hostiles"]!=len(hs): raise Red("HOSTILE_COUNT")
    if result["finite_models"]!=2: raise Red("MODEL_COUNT")
    if result["claim_ceiling"]!="GRAND_GMI_V2_R1_TYPED_SEQUENTIAL_PROCESS_CORE_MINIMAL_RELATIVE_TO_REGISTERED_REQUIREMENTS": raise Red("CEILING")
    print(json.dumps({"status":"GREEN","preorder":p,"c2":c,"hostiles":hs},sort_keys=True))
if __name__=="__main__":
  try: main()
  except Red as e:
    print("R1_RED:"+str(e),file=sys.stderr); sys.exit(1)
