from __future__ import annotations
from fractions import Fraction
from blind_search_core import TARGET_DIFF,TARGET_ID,discover,direct_candidates,score_semantics
from selection_outcome import resources,pareto_front,winners

def discover_gmi(target,horizon):
    raw=[]
    for item in discover(target):
        raw.append({
          'candidate_id':f"CAND_{item['source']}",
          'source':item['source'],'artifact':item['artifact'],'semantics':tuple(item['semantics']),
          'verified':score_semantics(tuple(item['semantics']),target)['verified'],
          'mechanism_class':'COMPOSITION','resource_vector':resources()['COMPOSITION'],
          'taxonomy':None
        })
    direct=direct_candidates()
    if target==TARGET_DIFF:
        raw += [
          {'candidate_id':'CAND_RULE','source':'GENERIC_CONDITIONAL','artifact':'equality-test+conditional','semantics':direct['EQUALITY_CONDITIONAL'],'verified':True,'mechanism_class':'RULE','resource_vector':resources()['RULE'],'taxonomy':None},
          {'candidate_id':'CAND_TABLE','source':'FINITE_EXTENTIONAL_MAP','artifact':'four-entry-map','semantics':direct['FINITE_MAP'],'verified':True,'mechanism_class':'TABLE','resource_vector':resources()['TABLE'],'taxonomy':None}
        ]
    elif target==TARGET_ID:
        raw += [{'candidate_id':'CAND_DIRECT','source':'DIRECT_INPUT_PROCESS','artifact':'x0','semantics':direct['DIRECT_X0'],'verified':True,'mechanism_class':'RULE','resource_vector':resources()['RULE'],'taxonomy':None}]
    verified=[c for c in raw if c['verified']]
    class_vectors={c['mechanism_class']:c['resource_vector'] for c in verified}
    front=pareto_front(class_vectors)
    preferred,_=winners(horizon,class_vectors) if target==TARGET_DIFF else (tuple(sorted(class_vectors)),{})
    for c in verified:
        c['disposition']='SELECTED_UNKNOWN' if c['mechanism_class'] in preferred else 'REACHED_NOT_SELECTED'
    return {
      'generated_count':len(raw),'verified_count':len(verified),'unclassified_candidates':verified,
      'pareto_mechanism_classes':list(front),'preferred_mechanism_classes':list(preferred),
      'architecture_names_in_output':False,'unknown_channel_preserved':True
    }

def status_ladder(candidate,posthoc_match=None,predicted=False,replicated=False):
    levels=['L0_EXPRESSIBLE','L1_REACHABLE']
    if candidate.get('verified'): levels.append('L2_FUNCTIONAL')
    if candidate.get('disposition') in ('SELECTED_UNKNOWN','REACHED_NOT_SELECTED'): levels.append('L3_RESOURCE_EVALUATED')
    if posthoc_match: levels.append('L4_BLIND_RECOVERED')
    if predicted: levels.append('L5_PREDICTED')
    if replicated: levels.append('L6_REPLICATED')
    return levels
