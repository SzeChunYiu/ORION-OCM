from __future__ import annotations
from fractions import Fraction
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FUNCS={"CONST0":(0,0),"IDENTITY":(0,1),"NOT":(1,0),"CONST1":(1,1)}

def score(table,target):
    return Fraction(sum(int(a==b) for a,b in zip(table,target)),2)

def mean(xs):
    return sum(xs,Fraction(0))/len(xs)

def main():
    ident=FUNCS["IDENTITY"]; neg=FUNCS["NOT"]; c0=FUNCS["CONST0"]
    collapsed_best=max(score(FUNCS[k],ident) for k in ("CONST0","CONST1"))
    assert collapsed_best==Fraction(1,2)

    systems={
      "FIXED_LOOKUP_ID":{"output":ident,"preserves":True,"develops":False,"source":"built-in table"},
      "FIXED_CALCULATOR_NOT":{"output":neg,"preserves":True,"develops":False,"source":"built-in rule"},
      "PASSIVE_MEMORY":{"output":c0,"preserves":True,"develops":False,"source":"stores input but output ignores memory"},
      "RANDOM_DYNAMICS":{"output":None,"preserves":False,"develops":False,"source":"fair independent random bit"},
      "UNIVERSAL_INTERPRETER_DEFAULT":{"output":c0,"preserves":False,"develops":False,"source":"interpreter with no task program supplied"},
      "TABLE_LEARNER_BEFORE":{"output":c0,"preserves":False,"develops":True,"source":"mutable table before labelled truth table"},
      "TABLE_LEARNER_AFTER":{"output":ident,"preserves":True,"develops":True,"source":"table updated from labelled truth table"}
    }

    id_scores={k:(Fraction(1,2) if v["output"] is None else score(v["output"],ident)) for k,v in systems.items()}
    assert id_scores["FIXED_LOOKUP_ID"]==1
    assert id_scores["PASSIVE_MEMORY"]==collapsed_best
    assert id_scores["RANDOM_DYNAMICS"]==Fraction(1,2)
    assert id_scores["TABLE_LEARNER_BEFORE"]==Fraction(1,2) and id_scores["TABLE_LEARNER_AFTER"]==1

    # Preservation alone is insufficient for exploitation: passive memory keeps x internally but does not improve identity-task value.
    assert systems["PASSIVE_MEMORY"]["preserves"] and id_scores["PASSIVE_MEMORY"]==collapsed_best

    # Fixed control can be perfect at scope without development.
    assert id_scores["FIXED_LOOKUP_ID"]==1 and not systems["FIXED_LOOKUP_ID"]["develops"]

    # High current capability need not imply adaptation to a changed requirement.
    frozen_id_current=score(ident,ident); frozen_id_shifted=score(ident,neg)
    assert frozen_id_current==1 and frozen_id_shifted==0

    # Low current capability can have high developmental response once task information is supplied.
    learner_before=score(c0,ident); learner_after=score(ident,ident)
    assert learner_before==Fraction(1,2) and learner_after==1

    # Universal finite interpreter: with the correct external program each of four tasks is solved exactly;
    # without task/program information a fixed default has mean 1/2 across the four tasks.
    oracle_selected=[score(FUNCS[name],FUNCS[name]) for name in FUNCS]
    default_scores=[score(c0,target) for target in FUNCS.values()]
    assert mean(oracle_selected)==1 and mean(default_scores)==Fraction(1,2)

    # Computational unfolding without new external information: target table is already stored.
    dormant_before=score(c0,ident); dormant_after=score(ident,ident)
    external_information_acquired=0
    assert dormant_before==Fraction(1,2) and dormant_after==1 and external_information_acquired==0

    # Random novelty/entropy is not target information. Exact fair independent joint P(Y,T)=1/4.
    joint={(y,t):Fraction(1,4) for y in (0,1) for t in (0,1)}
    py={y:sum(joint[(y,t)] for t in (0,1)) for y in (0,1)}
    pt={t:sum(joint[(y,t)] for y in (0,1)) for t in (0,1)}
    independent=all(joint[(y,t)]==py[y]*pt[t] for y in (0,1) for t in (0,1))
    random_expected_accuracy=joint[(0,0)]+joint[(1,1)]
    assert independent and random_expected_accuracy==Fraction(1,2)

    result={
      "status":"GREEN",
      "negative_controls":["FIXED_LOOKUP_ID","FIXED_CALCULATOR_NOT","PASSIVE_MEMORY","RANDOM_DYNAMICS","UNIVERSAL_INTERPRETER_DEFAULT"],
      "identity_scores":{k:f"{v.numerator}/{v.denominator}" for k,v in id_scores.items()},
      "collapsed_constant_baseline":"1/2",
      "passive_memory_preserves_but_does_not_exploit":True,
      "random_fair_bit_entropy_bits":1,
      "random_target_mutual_information_bits":0,
      "random_expected_accuracy":"1/2",
      "fixed_lookup_perfect_without_development":True,
      "high_current_frozen_identity_score":"1",
      "high_current_after_NOT_shift_score":"0",
      "low_current_learner_before":"1/2",
      "learner_after_task_information":"1",
      "finite_interpreter_with_correct_external_program_mean":"1",
      "finite_interpreter_fixed_default_mean":"1/2",
      "dormant_capability_before_compute":"1/2",
      "dormant_capability_after_compute":"1",
      "dormant_external_information_acquired_bits":0,
      "classification_boundary":{
        "SCOPED_CONTROL_CAPABILITY":"may be exhibited by a fixed organization; development is not necessary",
        "DEVELOPMENTAL_CAPABILITY":"history/information changes future organization/search/capability response",
        "UNIVERSAL_DEFINITION":"NOT_FROZEN"
      },
      "forbidden_promotions":["PRESERVING_INFORMATION_IS_SUFFICIENT_FOR_INTELLIGENCE","HIGH_ENTROPY_IS_INTELLIGENCE","TURING_OR_FINITE_UNIVERSALITY_IS_SUFFICIENT_FOR_INTELLIGENCE","CURRENT_CAPABILITY_IDENTIFIES_DEVELOPMENTAL_CAPABILITY","DEVELOPMENT_IS_NECESSARY_FOR_ALL_SCOPED_MACHINE_CAPABILITY","UNIVERSAL_INTELLIGENCE_DEFINITION_PROVED"],
      "claim_ceiling":"AJ8_NEGATIVE_CONTROLS_AND_FIXED_VS_DEVELOPMENTAL_CAPABILITY_BOUNDARY_AT_REGISTERED_FINITE_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
