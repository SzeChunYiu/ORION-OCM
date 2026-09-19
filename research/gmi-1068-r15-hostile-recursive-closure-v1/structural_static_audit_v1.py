#!/usr/bin/env python3
import json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
PKGS={
"R1":"gmi-1068-r1-minimal-process-core-v1",
"R2":"gmi-1068-r2-context-irreducibility-v1",
"R3":"gmi-1068-r3-contextual-attainability-v1",
"R4":"gmi-1068-r4-equivalence-state-quotient-v1",
"R5":"gmi-1068-r5-resource-transform-geometry-v1",
"R6":"gmi-1068-r6-blank-computer-genesis-v1",
"R7":"gmi-1068-r7-blind-family-atlas-v1",
"R8":"gmi-1068-r8-civilization-blind-neural-v1",
"R9":"gmi-1068-r9-update-law-unification-v1",
"R10":"gmi-1068-r10-information-control-unification-v1",
"R11":"gmi-1068-r11-lecun-physical-ai-v1",
"R12":"gmi-1068-r12-ai-findings-registry-v1",
"R13":"gmi-1068-r13-real-scale-evidence-adjudication-v1",
"R14":"gmi-1068-r14-formal-proof-bundle-v1",
}
issues=[]
for r,p in PKGS.items():
 path=ROOT/p/"RESULT_V1.json"
 if not path.exists():issues.append((r,"MISSING_RESULT"));continue
 o=json.loads(path.read_text())
 if not o.get("claim_ceiling"):issues.append((r,"MISSING_CEILING"))
 if r!="R14" and not o.get("forbidden_promotions"):issues.append((r,"MISSING_FORBIDDEN"))
 if "FULL_GMI" in str(o.get("claim_ceiling","")):issues.append((r,"FULL_GMI_IN_CEILING"))

# H05 architecture-family token in causal R8
causal=(ROOT/PKGS["R8"]/"causal_derivation_v1.py").read_text().lower()
for tok in ["neuron","neural","relu","layer","network","backprop","attention","convolution","transformer","target-architecture"]:
 if tok in causal:issues.append(("R8","CAUSAL_LEAK:"+tok))
# H06
cl=json.loads((ROOT/PKGS["R8"]/"POSTHOC_CLASSIFIER_V1.json").read_text())
if cl.get("causal_access") is not False:issues.append(("R8","CLASSIFIER_CAUSAL_ACCESS"))
# H07
reg=json.loads((ROOT/PKGS["R12"]/"AI_FINDING_REGISTRY_V1.json").read_text())
for row in reg["rows"]:
 if row["id"] in {"F01","F02"} and row["verdict"]!="EMPIRICAL_LAW_NOT_DERIVED":issues.append(("R12","SCALING_PROMOTION"))
# H08
adj=json.loads((ROOT/PKGS["R13"]/"GATE_ADJUDICATION_V1.json").read_text())
for gid in {"G10","G11","G12"}:
 g=next(x for x in adj["gates"] if x["id"]==gid)
 if not g["status"].startswith("UNEARNED"):issues.append(("R13","EXTERNAL_GATE_PROMOTION:"+gid))
# H09
src=json.loads((ROOT/PKGS["R11"]/"PRIMARY_SOURCE_REGISTRY_V1.json").read_text())
if src["entries"][0]["type"]!="POSITION_VISION":issues.append(("R11","POSITION_PROMOTED"))
# H10 fixed point not yet final in R0 registry
r0=json.loads((ROOT/"gmi-1068-grand-unified-v2-r0"/"THEOREM_STATUS_V1.json").read_text())
cand=next(x for x in r0["entries"] if x["id"]=="T-CAND-FIXED-POINT")
if cand["status"] not in {"CONJECTURE","PROVED"}:issues.append(("R0","FIXED_POINT_STATUS_INVALID"))
# H11
if "UNIQUE_CONTEXT_FREE_STATE_PARTITION" not in json.loads((ROOT/PKGS["R4"]/"RESULT_V1.json").read_text())["forbidden_promotions"]:issues.append(("R4","STATE_UNIQUENESS_UNGUARDED"))
# H12
if "UNIVERSAL_SYMMETRIC_METRIC" not in json.loads((ROOT/PKGS["R5"]/"RESULT_V1.json").read_text())["forbidden_promotions"]:issues.append(("R5","SYMMETRY_UNGUARDED"))
# H13
if "VALUES_DERIVED_FROM_PHYSICS" not in json.loads((ROOT/PKGS["R2"]/"RESULT_V1.json").read_text())["forbidden_promotions"]:issues.append(("R2","VALUE_PROMOTION_UNGUARDED"))
# H14
r8=json.loads((ROOT/PKGS["R8"]/"RESULT_V1.json").read_text())
if not {"NEURAL_UNIQUENESS","NEURAL_INEVITABILITY"}.issubset(set(r8["forbidden_promotions"])):issues.append(("R8","NEURAL_PROMOTION_UNGUARDED"))
# H16 old symbols retired, transport not automatic
r3=json.loads((ROOT/PKGS["R3"]/"RESULT_V1.json").read_text())
if not any("GAMMA" in x for x in r3["forbidden_promotions"]):issues.append(("R3","LEGACY_TRANSPORT_UNGUARDED"))
# H17
r6=json.loads((ROOT/PKGS["R6"]/"RESULT_V1.json").read_text())
if "LITERAL_PRIOR_FREE_SEARCH" not in r6["forbidden_promotions"]:issues.append(("R6","PRIOR_FREE_PROMOTION"))
# H18
g0=json.loads((ROOT/"gmi-1068-grand-unified-v2-r0"/"MERGE_GATE_V1.json").read_text())
if not {"UNKNOWN","CANNOT_CHECK"}.issubset(set(g0["valid_nonpositive_terminals"])):issues.append(("R0","NEGATIVE_TERMINALS_REMOVED"))
# H19
cov=json.loads((ROOT/PKGS["R14"]/"FORMAL_COVERAGE_V1.json").read_text())
if not cov.get("empirical_claims_not_proved_by_kernel"):issues.append(("R14","EMPIRICAL_KERNEL_BOUNDARY_MISSING"))
# H20
b=json.loads((pathlib.Path(__file__).resolve().parent/"BOUNDARIES_V1.json").read_text())
if len(b["preserved_external_boundaries"])<3:issues.append(("R15","EMPIRICAL_BOUNDARIES_DROPPED"))
# H21: every round checker whose workflow invokes -O must be fail-closed without bare Python asserts.
for rr in ("R4","R5","R6","R7","R8","R9","R10","R11","R12","R13"):
 checker=RESEARCH/PKGS[rr]/("check_"+rr.lower()+".py")
 if checker.exists():
  for lineno,line in enumerate(checker.read_text().splitlines(),1):
   stripped=line.strip()
   if stripped.startswith("assert ") or ";assert " in line:
    issues.append((rr,f"OPTIMIZED_ASSERT_FAIL_OPEN:{lineno}"))
if issues:
 print(json.dumps({"status":"RED","issues":issues},sort_keys=True));sys.exit(1)
print(json.dumps({"status":"GREEN_REGISTERED_HOSTILE_CLASSES","packages":len(PKGS),"registered_checks":21,"issues":[],"external_boundaries":len(b["preserved_external_boundaries"])},sort_keys=True))
