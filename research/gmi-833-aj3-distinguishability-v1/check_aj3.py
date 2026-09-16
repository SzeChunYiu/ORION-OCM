from __future__ import annotations
from fractions import Fraction
import itertools, json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
HYP=("p","q")
TESTS=("cheap","expensive")
COST={"cheap":1,"expensive":2}
VALUES=(Fraction(0),Fraction(1,2),Fraction(1))

def tv_binary(a,b):
    return abs(a-b)

def accessible_tests(budget):
    return tuple(e for e in TESTS if COST[e] <= budget)

def distinguishability(table, tests):
    return max((tv_binary(table[("p",e)],table[("q",e)]) for e in tests), default=Fraction(0))

def discrimination_success(delta):
    return (Fraction(1)+delta)/2

def decision_gain(delta, requirement):
    if requirement=="CLASSIFY_HYPOTHESIS":
        return discrimination_success(delta)-Fraction(1,2)
    if requirement=="CONSTANT_UTILITY":
        return Fraction(0)
    raise ValueError("unknown requirement")

def main():
    worlds=0; monotonicity_failures=0; physical_bound_failures=0
    exact_equivalent_worlds=0; perfectly_distinguishable_worlds=0
    accessible_hidden_worlds=0; decision_irrelevance_worlds=0
    budget_profile_hist=Counter()

    for row in itertools.product(VALUES, repeat=4):
        table={}; i=0
        for h in HYP:
            for e in TESTS:
                table[(h,e)]=row[i]; i+=1
        worlds += 1
        dphys=distinguishability(table,TESTS)
        d0=distinguishability(table,accessible_tests(0))
        d1=distinguishability(table,accessible_tests(1))
        d2=distinguishability(table,accessible_tests(2))
        monotonicity_failures += int(not (d0 <= d1 <= d2))
        physical_bound_failures += int(any(d > dphys for d in (d0,d1,d2)))
        physical_bound_failures += int(d2 != dphys)
        exact_equivalent_worlds += int(dphys==0)
        perfectly_distinguishable_worlds += int(dphys==1)
        accessible_hidden_worlds += int(d1==0 and dphys>0)
        decision_irrelevance_worlds += int(dphys>0 and decision_gain(dphys,"CONSTANT_UTILITY")==0)
        budget_profile_hist[(str(d0),str(d1),str(d2))] += 1
        assert discrimination_success(dphys) == (Fraction(1)+dphys)/2
        assert decision_gain(dphys,"CLASSIFY_HYPOTHESIS") == dphys/2

    hostile={("p","cheap"):Fraction(0),("q","cheap"):Fraction(0),
             ("p","expensive"):Fraction(0),("q","expensive"):Fraction(1)}
    assert distinguishability(hostile,accessible_tests(1))==0
    assert distinguishability(hostile,accessible_tests(2))==1

    eps=Fraction(1,2)
    x,y,z=Fraction(0),Fraction(1,2),Fraction(1)
    assert abs(x-y)<=eps and abs(y-z)<=eps and not abs(x-z)<=eps

    derived_information_controls={"perfect_binary_equal_prior_bits":1,"identical_laws_bits":0}

    assert worlds==81
    assert monotonicity_failures==0
    assert physical_bound_failures==0

    result={
      "status":"GREEN",
      "registered_worlds":worlds,
      "exact_equivalent_worlds":exact_equivalent_worlds,
      "perfectly_distinguishable_worlds":perfectly_distinguishable_worlds,
      "resource_accessibility_monotonicity_failures":monotonicity_failures,
      "accessible_exceeds_physical_failures":physical_bound_failures,
      "worlds_distinguishable_physically_but_hidden_at_budget_1":accessible_hidden_worlds,
      "worlds_physically_distinguishable_but_irrelevant_to_constant_utility":decision_irrelevance_worlds,
      "budget_profile_count":len(budget_profile_hist),
      "resource_hostile":"PHYSICAL_DELTA_1__ACCESSIBLE_DELTA_0_AT_BUDGET_1",
      "epsilon_transitivity_hostile":"0~0.5 AND 0.5~1 BUT 0!~1 AT EPSILON_0.5",
      "equal_prior_discrimination_law":"P_success=(1+TV)/2",
      "derived_information_controls":derived_information_controls,
      "forbidden_promotions":[
        "EPSILON_INDISTINGUISHABILITY_IS_EQUIVALENCE_WITHOUT_EXTRA_CONSTRUCTION",
        "PHYSICAL_DISTINGUISHABILITY_EQUALS_ACCESSIBLE_DISTINGUISHABILITY",
        "PHYSICAL_DISTINGUISHABILITY_EQUALS_DECISION_RELEVANCE",
        "SHANNON_BIT_IS_ONTOLOGICAL_PRIMITIVE",
        "OPERATIONAL_QUOTIENT_REPRESENTED_INSIDE_MACHINE"
      ],
      "claim_ceiling":"AJ3_DISTINGUISHABILITY_RESOURCE_ACCESS_AND_DECISION_RELEVANCE_AT_FINITE_REGISTERED_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
