#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_core_v1 import CLEAN, audit, cost, ecology, evaluation, lexical, search, semantic
from fixtures_v1 import *

CLAIM_CEILING="GMI_NO_SMUGGLING_AUDIT_TOOLING_VALIDATED_AT_REGISTERED_FINITE_FIXTURE_SCOPE"
FORBIDDEN_PROMOTIONS=["ENTIRE_GMI_CORPUS_PRIOR_FREE","ALL_ARCHITECTURE_LEAKAGE_DETECTED","SEMANTIC_NEUTRALITY_PROVED","ALL_COST_MODELS_UNBIASED","ALL_SEARCH_ALGORITHMS_EQUIVALENT","ECOLOGY_REPRESENTATIVE_REAL_WORLD","P3_RECOVERY_COMPLETE","COMPLETE_GMI"]
lexical_audit=lexical; semantic_audit=semantic; cost_audit=cost; search_audit=search; evaluation_audit=evaluation; ecology_audit=ecology; audit_record=audit

def _j(x):
    if isinstance(x,Fraction): return str(x)
    if isinstance(x,tuple): return [_j(v) for v in x]
    if isinstance(x,list): return [_j(v) for v in x]
    if isinstance(x,dict): return {k:_j(v) for k,v in sorted(x.items())}
    return x

def canonical_json(x): return json.dumps(_j(x),sort_keys=True,indent=2,ensure_ascii=False)+"\n"

def build_receipt():
    vs=["transformer","self_attention","SelfAttention","Conv2D","lstm_gate","rag_retriever","RAG-Retriever"]
    lx={v:lexical(lexical_hostile(v))["terminal"] for v in vs}; cl=audit(clean_record()); sm=audit(semantic_rename_hostile()); sl=audit(local_shared_hostile()); cr=audit(cost_reversal_hostile()); z=audit(zero_cost_hostile()); so=audit(search_order_hostile()); ei=audit(evaluation_id_hostile()); em=audit(evaluation_metric_hostile()); eb=audit(ecology_bias_hostile()); uf=audit(unknown_frame_hostile()); md={b:audit(missing_disclosure_hostile(b))["subaudits"][b]["terminal"] for b in ("lexical","semantic","cost","search","evaluation","ecology")}
    checks={"clean_fixture_clean":cl["terminal"]==CLEAN,"all_lexical_variants_flag":all(v=="LEXICAL_LEAKAGE" for v in lx.values()),"semantic_rename_flags":sm["subaudits"]["semantic"]["terminal"]=="SEMANTIC_MACRO_LEAKAGE","local_shared_macro_flags":sl["subaudits"]["semantic"]["terminal"]=="SEMANTIC_MACRO_LEAKAGE","cost_reversal_flags":cr["subaudits"]["cost"]["terminal"]=="COST_PRIOR_SENSITIVE","zero_cost_privilege_flags":z["subaudits"]["cost"]["terminal"]=="COST_PRIOR_SENSITIVE","search_order_flags":so["subaudits"]["search"]["terminal"]=="SEARCH_PRIOR_SENSITIVE","evaluation_id_flags":ei["subaudits"]["evaluation"]["terminal"]=="EVALUATION_PRIOR_SENSITIVE","evaluation_metric_reversal_flags":em["subaudits"]["evaluation"]["terminal"]=="EVALUATION_PRIOR_SENSITIVE","ecology_positive_only_flags":eb["subaudits"]["ecology"]["terminal"]=="ECOLOGY_SELECTION_BIAS","unknown_frame_abstains":uf["subaudits"]["ecology"]["terminal"]=="CANNOT_AUDIT_FRAME_REPRESENTATIVENESS","missing_disclosures_fail_closed":all(v.startswith("CANNOT_AUDIT_") for v in md.values())}
    return {"schema":"GMINoSmugglingAuditResultV1","issue":855,"parent_issue":833,"claim_ceiling":CLAIM_CEILING,"forbidden_promotions":FORBIDDEN_PROMOTIONS,"lexical_hostiles":lx,"semantic_mix_terminal":sm["subaudits"]["semantic"]["terminal"],"semantic_local_terminal":sl["subaudits"]["semantic"]["terminal"],"cost_reversal":{"terminal":cr["subaudits"]["cost"]["terminal"],"winners":cr["subaudits"]["cost"]["winners"],"winner_reversal":cr["subaudits"]["cost"]["winner_reversal"]},"search_order":{"terminal":so["subaudits"]["search"]["terminal"],"winners":so["subaudits"]["search"]["winners"]},"ecology_bias":{"terminal":eb["subaudits"]["ecology"]["terminal"],"frame_prevalence":eb["subaudits"]["ecology"]["frame_prevalence"],"sample_prevalence":eb["subaudits"]["ecology"]["sample_prevalence"]},"missing_disclosures":md,"checks":checks,"verdict":"GREEN" if all(checks.values()) else "RED"}

if __name__=="__main__": print(canonical_json(build_receipt()),end="")
