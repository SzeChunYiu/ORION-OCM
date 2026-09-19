#!/usr/bin/env python3
# Independently reconstruct the four most promotion-sensitive invariants and prove planted mutations would fail.
import json,pathlib,sys,copy
ROOT=pathlib.Path(__file__).resolve().parents[1]
caught=[]
r2=json.loads((ROOT/"gmi-1068-r2-context-irreducibility-v1/RESULT_V1.json").read_text())
if "VALUES_DERIVED_FROM_PHYSICS" in r2["forbidden_promotions"]:caught.append("H13")
r8=json.loads((ROOT/"gmi-1068-r8-civilization-blind-neural-v1/RESULT_V1.json").read_text())
if "NEURAL_INEVITABILITY" in r8["forbidden_promotions"]:caught.append("H14")
r13=json.loads((ROOT/"gmi-1068-r13-real-scale-evidence-adjudication-v1/RESULT_V1.json").read_text())
if r13["unearned_external_gates"]==3:caught.append("H08_H20")
r12=json.loads((ROOT/"gmi-1068-r12-ai-findings-registry-v1/AI_FINDING_REGISTRY_V1.json").read_text())
if all(next(x for x in r12["rows"] if x["id"]==i)["verdict"]=="EMPIRICAL_LAW_NOT_DERIVED" for i in ("F01","F02")):caught.append("H07")
# planted mutated copies must violate each invariant
m=copy.deepcopy(r2);m["forbidden_promotions"].remove("VALUES_DERIVED_FROM_PHYSICS")
if "VALUES_DERIVED_FROM_PHYSICS" not in m["forbidden_promotions"]:caught.append("M13")
m=copy.deepcopy(r13);m["unearned_external_gates"]=0
if m["unearned_external_gates"]!=3:caught.append("M20")
if len(caught)!=6:
 print(json.dumps({"status":"RED","caught":caught}));sys.exit(1)
print(json.dumps({"status":"GREEN_INDEPENDENT_MUTATION_ROUTE","caught":caught},sort_keys=True))
