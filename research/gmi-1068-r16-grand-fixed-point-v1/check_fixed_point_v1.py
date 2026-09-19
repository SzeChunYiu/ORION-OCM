#!/usr/bin/env python3
import json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[0]

der=json.loads((HERE/"DERIVATION_MAP_V1.json").read_text())
concepts={c["id"]:c for c in der["concepts"]}
found={c["id"] for c in concepts.values() if c["status"]=="FOUNDATIONAL_GMI_AXIS"}
if found!={"PROCESS_CORE","CONTEXT"}:
 print("BAD_FOUNDATIONS",found,file=sys.stderr);sys.exit(1)
if der["surviving_gmi_axes"]!=["PROCESS_CORE","CONTEXT"]:
 print("BAD_AXIS_DECLARATION",file=sys.stderr);sys.exit(1)

# All ontological derived concepts must have dependency paths to a root.
outside={"EVIDENCE_WARRANT"}
memo={}
def reaches_root(cid,stack=()):
 if cid in memo:return memo[cid]
 if cid in found:memo[cid]=True;return True
 if cid in outside:memo[cid]=True;return True
 if cid in stack:raise RuntimeError("CONCEPT_CYCLE:"+cid)
 c=concepts[cid]
 deps=c.get("depends_on",[])
 if not deps:return False
 ok=all(d in concepts and reaches_root(d,stack+(cid,)) for d in deps)
 memo[cid]=ok;return ok
for cid in concepts:
 if not reaches_root(cid):
  print("NO_ROOT_PATH:"+cid,file=sys.stderr);sys.exit(1)

# theorem DAG acyclic
dag=json.loads((HERE/"THEOREM_DAG_FINAL_V1.json").read_text())
deps={n:set() for n in dag["nodes"]}
for a,b in dag["edges"]:
 if a not in deps or b not in deps:raise SystemExit("DAG_UNKNOWN")
 deps[b].add(a)
state={}
def visit(n):
 if state.get(n)==1:raise RuntimeError("DAG_CYCLE:"+n)
 if state.get(n)==2:return
 state[n]=1
 for p in deps[n]:visit(p)
 state[n]=2
for n in deps:visit(n)

# R13 empirical gaps must remain open
r13=json.loads((ROOT/"gmi-1068-r13-real-scale-evidence-adjudication-v1/RESULT_V1.json").read_text())
if r13["unearned_external_gates"]!=3:raise SystemExit("R13_EXTERNAL_GAPS_LAUNDERED")

# R14/R15 must have final receipts, not pre-CI placeholders.
r14=json.loads((ROOT/"gmi-1068-r14-formal-proof-bundle-v1/RESULT_V1.json").read_text())
if r14["status"]!="GREEN_KERNEL_CHECKED_FLAGSHIP_BUNDLE":
 raise SystemExit("R14_NOT_FINAL_GREEN:"+r14["status"])
r15=json.loads((ROOT/"gmi-1068-r15-hostile-recursive-closure-v1/RESULT_V1.json").read_text())
if r15["status"]!="GREEN_REGISTERED_HOSTILE_CLASSES_WITH_EMPIRICAL_BOUNDARIES":
 raise SystemExit("R15_NOT_FINAL_GREEN:"+r15["status"])

# Fixed-point theorem status and final receipt must be final.
ts=json.loads((HERE/"THEOREM_STATUS_FINAL_V1.json").read_text())
tf=next(x for x in ts["entries"] if x["id"]=="T-FIXED-POINT")
if tf["status"]!="PROVED_AT_REGISTERED_THEORY_SCOPE":
 raise SystemExit("FIXED_POINT_STATUS_NOT_FINAL:"+tf["status"])
res=json.loads((HERE/"RESULT_V1.json").read_text())
if res["status"]!="GRAND_GMI_FIXED_POINT_V1__THEORY_GREEN__EXTERNAL_EMPIRICAL_GATES_OPEN":
 raise SystemExit("FINAL_RECEIPT_NOT_GREEN:"+res["status"])
if res["external_empirical_gaps"]!=3:raise SystemExit("FINAL_GAPS_MISMATCH")
if "FULL_GMI_IN_ALL_CONCEIVABLE_PHYSICS" not in res["forbidden_promotions"]:
 raise SystemExit("ABSOLUTE_PROMOTION_GUARD_MISSING")

print(json.dumps({
 "status":"GREEN_FIXED_POINT_AT_REGISTERED_THEORY_SCOPE",
 "surviving_axes":sorted(found),
 "registered_concepts":len(concepts),
 "derived_or_meta":len(concepts)-len(found),
 "theorem_dag_nodes":len(dag["nodes"]),
 "external_empirical_gaps":3
},sort_keys=True))
