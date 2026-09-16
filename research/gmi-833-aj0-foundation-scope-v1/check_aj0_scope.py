from __future__ import annotations
import itertools, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
VALID={"MATHEMATICAL_FOUNDATION","PHYSICAL_SUBSTRATE_ASSUMPTIONS","PROCESS_THEORY","PRESENTATION_GRAMMAR","REALIZATION","DEVELOPMENT","DECISION_CAPABILITY","SELECTION","EVIDENCE_GOVERNANCE"}
REQUIRED_IDS={"#837/gmi-833-foundation-v1","#846/gmi-833-parent-equivalence-v1","#848/gmi-833-morphcap-v1","#851/gmi-833-global-uncertainty-v1","#854/gmi-833-axiom-core-v1","#855/gmi-833-no-smuggling-audit-v1","#863/gmi-833-robustness-controls-v1","#868/gmi-833-g0-register-core-v1","#875/gmi-833-g0-grammar-bias-v1"}
FORBIDDEN_G0={"ULTIMATE_MI_SUBSTRATE","UNIQUE_MINIMAL_MI_SUBSTRATE","UNBIASED_UNIVERSAL_GRAMMAR"}
FORBIDDEN_AXIOM={"ULTIMATE_ONTOLOGICAL_BASIS","ABSOLUTE_CONSISTENCY"}
def require(cond,msg):
    if not cond: raise RuntimeError(msg)
def validate(reg):
    errs=[]; rows=reg.get("flagship_results",[]); ids={r.get("id") for r in rows}
    if ids!=REQUIRED_IDS: errs.append("FLAGSHIP_COVERAGE_MISMATCH")
    for r in rows:
        if r.get("primary_layer") not in VALID: errs.append("INVALID_PRIMARY_LAYER:"+str(r.get("id")))
        if not set(r.get("dependencies",[]))<=VALID: errs.append("INVALID_DEPENDENCY_LAYER:"+str(r.get("id")))
    by={r["id"]:r for r in rows if "id" in r}
    if "#868/gmi-833-g0-register-core-v1" not in by or not FORBIDDEN_G0<=set(by["#868/gmi-833-g0-register-core-v1"].get("forbidden_promotions",[])): errs.append("G0_DEMOTION_MISSING")
    if "#854/gmi-833-axiom-core-v1" not in by or not FORBIDDEN_AXIOM<=set(by["#854/gmi-833-axiom-core-v1"].get("forbidden_promotions",[])): errs.append("AXIOM_DEMOTION_MISSING")
    d=reg.get("demotions",{})
    if "primitiv" not in d.get("state_carrier","").lower(): errs.append("STATE_PRIMITIVITY_SCOPE_MISSING")
    if set(reg.get("primitive_policy",{}).get("promotion_requires",[]))!={"DERIVATION_THEOREM","INVARIANCE_THEOREM"}: errs.append("ANTI_PROMOTION_RULE_MISSING")
    return errs
def promotion_allowed(operational,ontological,derivation,invariance): return (not (operational and ontological)) or (derivation and invariance)
def main():
    reg=json.loads((HERE/"FOUNDATION_LAYER_REGISTRY.json").read_text()); require(validate(reg)==[],f"positive registry invalid: {validate(reg)}")
    hostiles=[]
    for name,mut in [("missing_flagship",lambda x:x["flagship_results"].pop()),("invalid_layer",lambda x:x["flagship_results"][0].__setitem__("primary_layer","MAGIC")),("g0_promotion_gap",lambda x:x["flagship_results"][7].__setitem__("forbidden_promotions",[])),("axiom_promotion_gap",lambda x:x["flagship_results"][4].__setitem__("forbidden_promotions",[])),("state_primitivity_gap",lambda x:x["demotions"].__setitem__("state_carrier","state is fundamental")),("anti_promotion_gap",lambda x:x["primitive_policy"].__setitem__("promotion_requires",[]))]:
        x=json.loads(json.dumps(reg)); mut(x); caught=bool(validate(x)); hostiles.append((name,caught)); require(caught,f"hostile escaped: {name}")
    rows=[]
    for operational,ontological,derivation,invariance in itertools.product([False,True],repeat=4):
        allowed=promotion_allowed(operational,ontological,derivation,invariance); expected=(not (operational and ontological)) or (derivation and invariance); require(allowed==expected,"promotion truth-table mismatch"); rows.append((operational,ontological,derivation,invariance,allowed))
    illegal=[r for r in rows if r[0] and r[1] and not (r[2] and r[3]) and r[4]]; require(illegal==[],f"illegal promotions accepted: {illegal}")
    result={"status":"GREEN","optimized_mode_safe":True,"registry_rows":len(reg["flagship_results"]),"named_hostiles":{n:"REJECTED" for n,_ in hostiles},"exhaustive_promotion_cases":len(rows),"illegal_promotions_accepted":0,"claim_ceiling":"AJ0_FOUNDATION_SCOPE_AND_ANTI_PROMOTION_CONTRACT_AT_REGISTERED_FLAGSHIP_SCOPE"}; (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
