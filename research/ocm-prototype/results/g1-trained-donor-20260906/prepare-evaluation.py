from pathlib import Path
import sys,json,hashlib,collections,datetime
ROOT=Path(__file__).resolve().parent
DATA=Path('/home/billy/orion-director-work/20260906/language-g1-audit/data')
sys.path.insert(0,'/home/billy/orion-director-work/20260906/ocm-vessel/research/ocm-n1')
from ud_induction import load_split
train=load_split(DATA/'en_ewt-ud-train.conllu','train');dev=load_split(DATA/'en_ewt-ud-dev.conllu','dev')
def nonpunct(s):return [w for w in s.tokens if w.upos!='PUNCT']
def band(s):
 n=len(nonpunct(s));return '0-5' if n<=5 else '6-10' if n<=10 else '11-20' if n<=20 else '21+'
def genre(s):return s.sent_id.split('-',1)[0]
pools=collections.defaultdict(list)
for i,s in enumerate(dev):pools[(genre(s),band(s))].append(i)
selected=[];cells=[]
for key in sorted(pools):
 ranked=sorted(pools[key],key=lambda i:hashlib.sha256(('UDPIPE-G1-20260906-V1|'+dev[i].sent_id).encode()).hexdigest())
 assert len(ranked)>=5,(key,len(ranked))
 selected.extend(ranked[:5]);cells.append({'genre':key[0],'band':key[1],'pool_count':len(ranked),'selected_indices':ranked[:5]})
assert len(cells)==20 and len(selected)==100
indices=sorted(set(range(50))|set(selected))
seen={tuple(w.form.lower() for w in nonpunct(s)) for s in train}
manifest={'role':'DEVELOPMENT_SELECTION_FROZEN_BEFORE_UDPIPE_OUTCOMES','registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seed_prefix':'UDPIPE-G1-20260906-V1|','main_contract':'ALL_INTEGER_TOKENS_CASE_PRESERVED','legacy_contract':'GOLD_PUNCT_STRIPPED_LOWERCASE','first50':list(range(50)),'genre_length100':sorted(selected),'union_count':len(indices),'cells':cells,'dev_sha256':hashlib.sha256((DATA/'en_ewt-ud-dev.conllu').read_bytes()).hexdigest(),'no_outcome_filters':True,'rows':[{'dev_index':i,'sent_id':dev[i].sent_id,'genre':genre(dev[i]),'band':band(dev[i]),'all_token_count':len(dev[i].tokens),'nonpunct_token_count':len(nonpunct(dev[i])),'normalized_train_surface_duplicate':tuple(w.form.lower() for w in nonpunct(dev[i])) in seen} for i in indices]}
(ROOT/'evaluation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
requests=[]
for contract in ['all_tokens','legacy_stripped']:
 for i in indices:
  words=dev[i].tokens if contract=='all_tokens' else nonpunct(dev[i])
  requests.append({'id':f'{contract}:{i:04d}','tokens':[w.form if contract=='all_tokens' else w.form.lower() for w in words]})
(ROOT/'requests.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in requests))
metric_plan={'role':'DEVELOPMENT_METRICS_PREDECLARED','registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'main_contract':'all_tokens','legacy_contract':'legacy_stripped','groups':['first50','genre_length100'],'metrics':['single_tree_exact_head_full_deprel','single_tree_exact_head_full_deprel_upos','micro_UAS','micro_LAS_base_relation','micro_LAS_full_relation','UPOS_accuracy','structurally_valid_coverage','refusals_errors','wall_and_CPU_RSS'],'base_relation_policy':'split deprel at first colon; retain full deprel metric separately','gold_nonprojective_policy':'retain in all denominators, diagnostic only','empty_legacy_input_policy':'ABSTAIN_EMPTY; exact false; zero token contribution; retained sentence denominator','legacy_gold_parent_removed_policy':'unmatchable arc scores incorrect; record count; no row exclusion','invalid_prediction_policy':'sentence exact false; all its token decisions incorrect; retained denominator','gold_location':'external grader only; worker receives requests.jsonl containing id and forms, no gold tags/trees','training_selection':'no dev selection or early stopping'}
(ROOT/'metric-plan.json').write_text(json.dumps(metric_plan,indent=2)+'\n')
print(json.dumps({'panel':len(selected),'union':len(indices),'requests':len(requests),'manifest_sha256':hashlib.sha256((ROOT/'evaluation-manifest.json').read_bytes()).hexdigest(),'metric_plan_sha256':hashlib.sha256((ROOT/'metric-plan.json').read_bytes()).hexdigest(),'outcomes_exist':(ROOT/'responses.jsonl').exists()}))
