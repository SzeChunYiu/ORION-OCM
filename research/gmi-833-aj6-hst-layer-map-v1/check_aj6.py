from __future__ import annotations
import itertools, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FUNCS=((0,0),(0,1),(1,0),(1,1))
TARGET=(0,1)

def error(f,target=TARGET):
    return sum(int(a!=b) for a,b in zip(f,target))/len(target)

def developmental_worlds():
    worlds=[]
    for cur in range(4):
        others=[i for i in range(4) if i!=cur]
        for mask in range(1<<len(others)):
            reach={cur}
            for k,i in enumerate(others):
                if mask & (1<<k): reach.add(i)
            worlds.append({"current":cur,"reach":frozenset(reach),"current_error":error(FUNCS[cur]),"future_best_error":min(error(FUNCS[i]) for i in reach)})
    return worlds

def governed_update(state, patch, allow_substrate_change=False):
    protected={"substrate_laws","operational_process_frame"}
    if not allow_substrate_change and protected.intersection(patch):
        raise ValueError("LOWER_LAYER_PREMISE_CHANGE_REQUIRES_EXPLICIT_SCOPE_CHANGE")
    out=dict(state); out.update(patch); return out

def main():
    mapping={
      "L":"presentation / legal organization language over AJ4 machine organizations",
      "Q":"proposal/search kernel over organization or presentation changes",
      "H":"inherited archive, library, methods and persistent organization state",
      "E":"task/environment ecology feeding registered requirements",
      "R":"resource-allocation policy over AJ4/AJ5 raw resource coordinates",
      "V":"verifier/evaluator implemented through AJ2/AJ3 operational tests and registered decision criteria",
      "C":"external constitutional/governance boundary for legal adoption and protected evaluation"
    }
    assert set(mapping)==set("LQHERVC")

    worlds=developmental_worlds(); assert len(worlds)==32
    same_current_different_future=0
    for i,a in enumerate(worlds):
        for b in worlds[i+1:]:
            if a["current"]==b["current"] and a["current_error"]==b["current_error"] and a["future_best_error"]!=b["future_best_error"]:
                same_current_different_future+=1
    assert same_current_different_future==51

    seed={"current_org":0,"L":frozenset(range(4)),"Q":"FROZEN","H":(),"E":"IDENTITY","R":{"edits":0},"V":"EXACT_BOOL","C":"PROTECTED","substrate_laws":"BOOL_STATIC","operational_process_frame":"AJ1"}
    frozen=governed_update(seed,{"Q":"FROZEN","R":{"edits":0}})
    edit=governed_update(seed,{"Q":"ONE_HAMMING_EDIT","R":{"edits":1}})
    frozen_reach={0}; edit_reach={i for i,f in enumerate(FUNCS) if sum(a!=b for a,b in zip(FUNCS[0],f))<=1}
    assert min(error(FUNCS[i]) for i in frozen_reach)==0.5
    assert min(error(FUNCS[i]) for i in edit_reach)==0.0
    assert frozen["current_org"]==edit["current_org"]==0

    lower_layer_hostile="NOT_RUN"
    try:
        governed_update(seed,{"substrate_laws":"MAGIC_ORACLE"})
    except ValueError:
        lower_layer_hostile="REJECTED"
    assert lower_layer_hostile=="REJECTED"

    theorem_map={
      "HST_T01":"reach-set dominance under optional inheritance -> developmental reach layer",
      "HST_T02":"operator/primitive reach expansion -> AJ4/AJ5 organization/presentation layer",
      "HST_T03":"representation insufficiency -> AJ2/AJ3 operational distinction layer",
      "HST_T04_T05":"coded-search/macro amortization -> presentation/search-resource layer",
      "HST_T08":"Blackwell information dominance -> AJ3 decision-relevance layer",
      "HST_T09_T10":"transfer/evolvability -> developmental capability-response layer",
      "HST_LIMITS":"meta-NFL/Rice/halting/Godel/Blum boundaries remain limits; lowering does not remove them"
    }

    result={
      "status":"GREEN",
      "hst_state_mapping":mapping,
      "finite_developmental_worlds":len(worlds),
      "same_current_capability_different_future_pairs":same_current_different_future,
      "frozen_future_best_identity_error":0.5,
      "one_edit_future_best_identity_error":0.0,
      "current_organization_same":True,
      "lower_layer_mutation_without_scope_change":lower_layer_hostile,
      "theorem_family_map":theorem_map,
      "development_changes_allowed":["organization","presentation/language","proposal kernel","archive/library","task ecology","resource policy","verifier subject to C"],
      "development_does_not_silently_change":["substrate laws","AJ1 operational frame assumptions"],
      "forbidden_promotions":["HST_IS_SUBSTRATE_ONTOLOGY","CURRENT_CAPABILITY_DETERMINES_DEVELOPMENTAL_POTENTIAL","DEVELOPMENT_ALWAYS_IMPROVES","LOWERING_REMOVES_META_NFL_OR_UNDECIDABILITY","UNREGISTERED_SUBSTRATE_CHANGE_COUNTS_AS_DEVELOPMENT"],
      "claim_ceiling":"AJ6_HST_AS_DEVELOPMENT_OVER_PROCESS_ORGANIZATIONS_AT_REGISTERED_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
