from __future__ import annotations
import itertools, json
from pathlib import Path
from collections import Counter

HERE=Path(__file__).resolve().parent
ACTIONS=(0,1)
REWARDS=tuple(itertools.product(range(3), repeat=2))
SOURCES=("DISTAL_VIABILITY","INTERNAL_DRIVE","EXTERNAL_SPECIFICATION","SOCIAL_INSTITUTIONAL")

def optimal_actions(reward):
    best=max(reward)
    return tuple(a for a in ACTIONS if reward[a]==best)

def main():
    # Frozen world dynamics: one state, both actions deterministically self-loop.
    transition={(0,a):0 for a in ACTIONS}
    assert transition[(0,0)]==transition[(0,1)]==0

    opt_hist=Counter(optimal_actions(r) for r in REWARDS)
    assert opt_hist==Counter({(0,):3,(1,):3,(0,1):3})

    incompatible=0
    for i,r in enumerate(REWARDS):
        for q in REWARDS[i+1:]:
            if set(optimal_actions(r)).isdisjoint(optimal_actions(q)):
                incompatible+=1
    assert incompatible==9

    # Same observed deterministic behaviour is compatible with multiple reward functions.
    action0_optimal=[r for r in REWARDS if 0 in optimal_actions(r)]
    action1_optimal=[r for r in REWARDS if 1 in optimal_actions(r)]
    assert len(action0_optimal)==len(action1_optimal)==6

    # Objective-source provenance is distinct from effective requirements: the same Q can
    # arise from multiple source types, so Q alone does not identify its provenance.
    provenance=[(src,a) for src in SOURCES for a in ACTIONS]
    by_q=Counter(a for _,a in provenance)
    assert by_q==Counter({0:4,1:4})

    # A world/process provenance record cannot fill an absent value source.
    process_provenance={"substrate":"AJ1","organization":"AJ4","development":"AJ6"}
    assert "objective_source" not in process_provenance

    result={
      "status":"GREEN",
      "world_dynamics":"one state; actions 0/1 both self-loop",
      "reward_functions_checked":len(REWARDS),
      "optimal_action_set_histogram":{"{0}":3,"{1}":3,"{0,1}":3},
      "incompatible_objective_pairs_same_dynamics":incompatible,
      "rewards_compatible_with_observed_action0":len(action0_optimal),
      "rewards_compatible_with_observed_action1":len(action1_optimal),
      "objective_source_types":list(SOURCES),
      "provenance_records":len(provenance),
      "sources_per_effective_binary_requirement":4,
      "theorems":{
        "AJ7_NO_GO":"world transition dynamics alone do not determine a unique requirement/reward/optimal action relation",
        "AJ7_IDENTIFIABILITY":"observed optimal behaviour does not generally identify a unique reward",
        "AJ7_PROVENANCE":"effective requirement Q does not by itself identify whether its source was viability, internal drive, external specification or social/institutional constraint"
      },
      "forbidden_promotions":["OBJECTIVE_DERIVED_FROM_DYNAMICS_ALONE","OBSERVED_POLICY_IDENTIFIES_UNIQUE_REWARD","EFFECTIVE_Q_IDENTIFIES_ITS_SOURCE","PHYSICS_SUPPLIES_UNIQUE_NORMATIVE_ORDER"],
      "claim_ceiling":"AJ7_OBJECTIVE_UNDERDETERMINATION_AND_SOURCE_PROVENANCE_AT_REGISTERED_FINITE_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
