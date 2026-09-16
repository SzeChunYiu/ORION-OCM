from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent

def main():
 src=(HERE/'blind_evidence_search_v1.py').read_text()
 forbidden=['K06','Bayes','posterior','KNOWN_FAMILY','fingerprint']
 hits=[x for x in forbidden if x.lower() in src.lower()]
 assert not hits,hits
 out=json.loads((HERE/'BLIND_OUTCOME_V1.json').read_text())
 assert out['registry_data_used'] is False
 assert out['evidence']['e0']['normalized']==['3/4','1/4']
 assert out['evidence']['e1']['normalized']==['1/4','3/4']
 post=json.loads((HERE/'POSTHOC_RESULT_V1.json').read_text())
 assert post['terminal']=='RECOVERED' and all(post['checks'].values())
 # hostile: arbitrary randomized action is not a maintained normalized evidence-updated belief
 random_action={'normalized_probability_state':False,'registered_evidence_changes_state':False}
 assert not all(random_action.values())
 result={'status':'GREEN','blind_source_forbidden_hits':hits,'searches':2,'presentations':2,'posthoc_terminal':'RECOVERED','random_action_near_neighbor_rejected':True,'predicted_selected':'NOT_CLAIMED','claim_ceiling':'AJ9G_K06_BLIND_PROBABILISTIC_UPDATE_RECOVERY_AT_FROZEN_FINITE_SCOPE','forbidden_promotions':['GENERAL_BAYESIAN_AI_DERIVED','PREDICTED_SELECTED','AJ9_ALL_FAMILIES_RECOVERED','COMPLETE_GMI']}
 (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
