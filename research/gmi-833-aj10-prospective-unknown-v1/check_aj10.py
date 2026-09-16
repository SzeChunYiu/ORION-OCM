from __future__ import annotations
import importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

D=load('aj10_discover',HERE/'discover_v1.py')
P=load('aj10_posthoc',HERE/'posthoc_taxonomy_v1.py')


def evaluated_live():
    a=D.table_route(); b=D.semantic_route(); assert a['truth']==b['truth']==list(D.TARGET)
    candidates=[a,b]; frontier=D.pareto(candidates)
    return {
      'schema':'AJ10_PRE_TAXONOMY_EVALUATION_V1',
      'heldout_task_id':D.ENV['task_id'],
      'taxonomy_visible_to_search':False,
      'capability_evaluated_before_taxonomy':True,
      'capability':{'protected_cases':8,'correct_cases_each':8,'exact':True},
      'candidates':candidates,
      'pareto_frontier':frontier,
      'unique_morphology_selected':False,
      'replication':'two materially different representations/search routes reproduce identical protected behavior'
    }


def main():
    live=evaluated_live(); committed=json.loads((HERE/'EVALUATED_CANDIDATES_V1.json').read_text())
    assert live==committed
    post=P.main_result(); post_c=json.loads((HERE/'POSTHOC_RESULT_V1.json').read_text()); assert post==post_c
    assert set(committed['pareto_frontier'])=={'T232','E4'}
    assert not committed['unique_morphology_selected']
    assert post['unknown_channel_exercised']
    assert post['candidates']['T232']['registered_taxonomy']=='UNKNOWN_MORPHOLOGY'
    assert post['candidates']['T232']['post_parent_terminal']=='PARENT_REDUCED_KNOWN'
    assert post['candidates']['E4']['registered_family']=='K10'
    assert not post['novel_form_claimed']
    assert post['novel_replication_gate']=='NOT_TRIGGERED_NO_NOVEL_CLAIM'

    src=(HERE/'discover_v1.py').read_text().lower()
    forbidden=['known_family_benchmark','k01','k02','k03','k04','k05','k06','k07','k08','k09','k10','k11','unknown_morphology','parent_reduced_known']
    hits=[x for x in forbidden if x in src]; assert not hits,hits

    env=json.loads((HERE/'HELDOUT_ENV_V1.json').read_text()); assert env['family_labels_present'] is False and env['taxonomy_visible_to_search'] is False
    result={
      'status':'GREEN',
      'heldout_task':'H1',
      'pre_taxonomy_exact_candidates':2,
      'pareto_frontier_size':2,
      'unique_morphology_selected':False,
      'unknown_channel_exercised':True,
      'unknown_candidate':'T232',
      'registered_family_candidate':'E4->K10',
      'strongest_parent_reduction':'T232->classical finite truth table; E4->finite program synthesis',
      'novel_form_claimed':False,
      'novel_replication_policy':'REQUIRED_IF_NOVEL; not triggered because no novel form is claimed',
      'independent_behavioral_replication':'PASS_TWO_MATERIALLY_DIFFERENT_ROUTES',
      'novelty_levels_recorded':['implementation','morphology_architecture','algorithmic_mechanism','computational_class','capability_profile'],
      'blind_source_forbidden_hits':hits,
      'terminal':'AJ10_UNKNOWN_CHANNEL_EXERCISED_WITH_PARENT_REDUCTION_AND_NO_FALSE_NOVELTY',
      'forbidden_promotions':['NOVEL_MI_DISCOVERED','GMI_DISCOVERS_ALL_MI','COMPLETE_GMI'],
      'claim_ceiling':'AJ10_PROSPECTIVE_UNKNOWN_CHANNEL_AND_POSTHOC_PARENT_REDUCTION_AT_REGISTERED_FINITE_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
