from __future__ import annotations
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def project(r):
    assert r['status']=='GREEN'
    c=r['ai2_compile']; d=r['ai3_recovery']; a=r['ai4_development']; s=r['ai5_selection']; u=r['ai6_subfamilies']; disc=r['ai8_discovery']; gates=r['ai7_success_gate']
    out={
      'status':'GREEN',
      'freeze_commit':r['freeze_commit'],
      'causal_forbidden_token_hits':sum(len(v) for v in r['no_smuggling_source_audit']['forbidden_token_hits'].values()),
      'd1':{
        'supplied_family_members':c['lower']['supplied_family_networks'],
        'input_evaluations':c['lower']['supplied_family_input_evaluations'],
        'tree_lowering_mismatches':c['lower']['lower_arithmetic_mismatches'],
        'stack_lowering_mismatches':c['lower']['stack_presentation_mismatches'],
        'g0_mismatches':c['g0']['semantic_mismatches'],
        'g0_max_program_instructions':c['g0']['max_program_instructions'],
        'g0_max_runtime_steps':c['g0']['max_runtime_steps'],
        'g0_registers':c['g0']['registers']
      },
      'd2':{
        'tree_min_size':d['tree']['size'],'tree_semantics_seen':d['tree']['unique_semantics'],
        'stack_min_length':d['stack']['length'],'stack_states_seen':d['stack']['states_seen'],
        'identity_control_sizes':d['identity_control_sizes'],'affine_exact_matches':d['affine_no_go']['exact_matches'],
        'semantic_remint_preserved':d['remint']['semantic_preservation']
      },
      'dev':{'reverse_cases':len(a['reverse_cases']),'fixed_outputs_with_or_without_gradient':a['fixed_outputs_with_or_without_gradient']},
      'd3':{'heldout_horizons':len(s['heldout']),'pareto_front':s['pareto_front'],'price_hostile_composition_wins':s['price_hostile_composition_wins']},
      'subfamily_microscopes':sorted(k for k in u if k!='all_are_structural_pressure_results_not_named_architecture_primitives'),
      'discovery':{
        'generated':disc['generated_count'],'verified':disc['verified_count'],
        'pareto_mechanism_classes':disc['pareto_mechanism_classes'],'preferred_mechanism_classes':disc['preferred_mechanism_classes'],
        'posthoc_family':disc['posthoc']['xor_posthoc_family'],'neural_ladder':disc['ladders']['NEURAL_LIKE'],
        'novel_L7_claimed':any('L7_NOVEL' in xs for xs in disc['ladders'].values())
      },
      'strong_gate':gates,
      'claim_ceiling':r['claim_ceiling'],
      'forbidden_promotions':r['forbidden_promotions']
    }
    assert out['causal_forbidden_token_hits']==0
    assert out['d1']=={'supplied_family_members':729,'input_evaluations':2916,'tree_lowering_mismatches':0,'stack_lowering_mismatches':0,'g0_mismatches':0,'g0_max_program_instructions':23,'g0_max_runtime_steps':11,'g0_registers':4}
    assert out['d2']['tree_min_size']==out['d2']['stack_min_length']==11
    assert out['d2']['tree_semantics_seen']==420 and out['d2']['stack_states_seen']==44403 and out['d2']['identity_control_sizes']==[1,1] and out['d2']['affine_exact_matches']==0
    assert out['dev']['reverse_cases']==2 and out['d3']['heldout_horizons']==8 and len(out['d3']['pareto_front'])==3
    assert out['discovery']['generated']==4 and out['discovery']['verified']==4 and not out['discovery']['novel_L7_claimed']
    assert all(out['strong_gate'].values())
    return out

def main():
    p=HERE/'RESULT_V1.json'; r=json.loads(p.read_text()); out=project(r)
    (HERE/'RECEIPT_V1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__': main()
