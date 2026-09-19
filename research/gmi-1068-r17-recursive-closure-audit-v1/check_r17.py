#!/usr/bin/env python3
import json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
RESEARCH=HERE.parent
r16=RESEARCH/"gmi-1068-r16-grand-fixed-point-v1"
dag=json.loads((r16/"THEOREM_DAG_FINAL_V1.json").read_text())
children={n:set() for n in dag["nodes"]}
for a,b in dag["edges"]:children[a].add(b)
def reopen(seed):
 seen={seed};stack=[seed]
 while stack:
  x=stack.pop()
  for y in children[x]:
   if y not in seen:seen.add(y);stack.append(y)
 return seen
# planted upstream/mid/formal defects must propagate through the reverse-dependency cone.
for seed,must in [
 ("R1_PROCESS",{"R1_PROCESS","R3_ATTAIN","R14_FORMAL","R15_HOSTILE","R16_FIXED_POINT"}),
 ("R3_ATTAIN",{"R3_ATTAIN","R4_QUOTIENT","R5_GEOMETRY","R6_GENESIS","R15_HOSTILE","R16_FIXED_POINT"}),
 ("R14_FORMAL",{"R14_FORMAL","R15_HOSTILE","R16_FIXED_POINT"})]:
 got=reopen(seed)
 missing=must-got
 if missing:
  print("BAD_REOPEN",seed,sorted(missing),file=sys.stderr);sys.exit(1)

r13=json.loads((RESEARCH/"gmi-1068-r13-real-scale-evidence-adjudication-v1/RESULT_V1.json").read_text())
if r13["unearned_external_gates"]!=3:raise SystemExit("R13_BOUNDARY_COUNT")
r14=json.loads((RESEARCH/"gmi-1068-r14-formal-proof-bundle-v1/RESULT_V1.json").read_text())
if r14["status"]!="GREEN_KERNEL_CHECKED_FLAGSHIP_BUNDLE":raise SystemExit("R14_NOT_GREEN")
r15=json.loads((RESEARCH/"gmi-1068-r15-hostile-recursive-closure-v1/RESULT_V1.json").read_text())
if r15["status"]!="GREEN_REGISTERED_HOSTILE_CLASSES_WITH_EMPIRICAL_BOUNDARIES":raise SystemExit("R15_NOT_GREEN")
r16res=json.loads((r16/"RESULT_V1.json").read_text())
if r16res["status"]!="GRAND_GMI_FIXED_POINT_V1__THEORY_GREEN__EXTERNAL_EMPIRICAL_GATES_OPEN":raise SystemExit("R16_NOT_GREEN")
r0=json.loads((RESEARCH/"gmi-1068-grand-unified-v2-r0/MERGE_GATE_V1.json").read_text())
if not {"UNKNOWN","CANNOT_CHECK"}.issubset(set(r0["valid_nonpositive_terminals"])):raise SystemExit("NEGATIVE_TERMINALS_LOST")
res=json.loads((HERE/"RESULT_V1.json").read_text())
if res["status"]!="GREEN_RECURSIVE_CLOSURE_AT_REGISTERED_AUDITED_SCOPE":raise SystemExit("R17_RECEIPT_NOT_FINAL")
if "NO_UNKNOWN_UNKNOWNS" not in res["forbidden_promotions"]:raise SystemExit("UNKNOWN_UNKNOWN_GUARD_MISSING")
print(json.dumps({"status":"GREEN_RECURSIVE_CLOSURE_AT_REGISTERED_AUDITED_SCOPE","planted_defects":3,"R1_reopen_count":len(reopen("R1_PROCESS")),"R3_reopen_count":len(reopen("R3_ATTAIN")),"R14_reopen_count":len(reopen("R14_FORMAL")),"external_empirical_gaps":3},sort_keys=True))
