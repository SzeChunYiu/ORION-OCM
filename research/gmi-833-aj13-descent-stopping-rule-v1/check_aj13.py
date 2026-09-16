from __future__ import annotations

import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(path): return json.loads((ROOT/path).read_text())


def main():
    aj1=load(Path('research/gmi-833-aj1-operational-process-base-v1/RESULT_V1.json'))
    aj5=load(Path('research/gmi-833-aj5-g0-compilation-v1/RESULT_V1.json'))
    aj12=load(Path('research/gmi-833-aj12-foundation-substrate-relativity-v1/RESULT_V1.json'))

    checks={}
    required_tags={'MATHEMATICAL_FOUNDATION','LOGIC/METATHEORY','PHYSICAL_SUBSTRATE_LAW','RESOURCE_MODEL','VALUE/REQUIREMENT_INPUT'}
    checks['1_remaining_assumptions_explicitly_tagged']=set(aj12['assumption_tags'].values())==required_tags

    base_text=(ROOT/'research/gmi-833-aj1-operational-process-base-v1/THEORY.md').read_text().lower()
    forbidden_mechanisms=['neural network','transformer','attention head','bayesian network','planner','retrieval architecture','genetic algorithm','program synthesizer']
    leaked=[x for x in forbidden_mechanisms if x in base_text]
    checks['2_no_mi_family_specific_mechanism_in_operational_base']=not leaked

    irr=aj1['relative_irredundancy_removals']
    checks['3_each_registered_operational_component_has_loss_boundary']=set(irr)=={'Obj','compose','tensor','identity','Adm_S','Obs_S'} and len(set(irr.values()))==6

    checks['4_semantic_theorems_survive_materially_different_presentation']=(
        aj5['alternate_relational_presentation_rows']==99 and aj5['alternate_presentation_failures']==0
        and {'protected I/O trace','terminal outcome','final registered values at bounded execution scope'}<=set(aj5['invariants'])
        and len(aj12['formalization_styles'])==2 and aj12['composition_transfer_checks']==16
    )

    parent_files=[
      ROOT/'research/gmi-833-aj1-operational-process-base-v1/PARENT_LEDGER.md',
      ROOT/'research/gmi-833-aj5-g0-compilation-v1/PARENT_LEDGER.md',
      ROOT/'research/gmi-833-aj12-foundation-substrate-relativity-v1/PARENT_LEDGER.md'
    ]
    checks['5_strongest_parent_ownership_explicit']=all(p.exists() and len(p.read_text().strip())>100 for p in parent_files)

    checks['6_further_descent_is_foundation_physics_value_not_hidden_mi_mechanism']=(
        aj12['physical_hypercomputation'].startswith('EMPIRICAL_OPEN')
        and {'GODEL_INCOMPLETENESS_SCOPE_PRESERVED','TARSKI_OBJECT_LANGUAGE_METALANGUAGE_BOUNDARY_PRESERVED'}<=set(aj12['metatheory_boundaries'])
        and not leaked
    )

    all_pass=all(checks.values())
    terminal='FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE' if all_pass else 'DESCENT_CONTINUES__MATERIAL_HIDDEN_ASSUMPTION_OR_INVARIANCE_GAP'
    assert all_pass
    result={
      'status':'GREEN',
      'stop_conditions':checks,
      'operational_base_family_leaks':leaked,
      'terminal':terminal,
      'interpretation':'GMI-specific descent may stop at the registered operational layer; remaining foundation/metatheory/physics/resource/value assumptions remain explicit and relative',
      'forbidden_terminal':'ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN',
      'forbidden_promotions':['UNIQUE_METAPHYSICAL_BOTTOM','ALL_PHYSICAL_LAWS_DERIVED','ALL_MATHEMATICS_SELF_JUSTIFIED','COMPLETE_GMI'],
      'claim_ceiling':'AJ13_FOUNDATION_RELATIVE_OPERATIONAL_DESCENT_STOPPING_RULE_SATISFIED_AT_REGISTERED_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
