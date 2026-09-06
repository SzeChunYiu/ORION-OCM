from pathlib import Path
import sys,json,io,collections,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source'))
import conll18_ud_eval as official
sys.path.insert(0,'/home/billy/orion-director-work/20260906/ocm-vessel/research/ocm-n1')
from ud_induction import load_split
from ud_grammar import is_projective
DATA=Path('/home/billy/orion-director-work/20260906/language-g1-audit/data')
def conllu(words):
 return ''.join('\t'.join([str(w['id']),w['form'],'_',w['upos'] or '_','_','_',str(w['head']),w['deprel'] or '_','_','_'])+'\n' for w in words)+'\n'
def validate(words,forms):
 if len(words)!=len(forms):return 'WORD_COUNT_MISMATCH'
 if not forms:return 'EMPTY_INPUT'
 for i,(w,form) in enumerate(zip(words,forms),1):
  if set(w)!={'id','form','head','deprel','upos'}:return 'WORD_SCHEMA'
  if type(w['id']) is not int or w['id']!=i or w['form']!=form:return 'TOKEN_BINDING'
  if type(w['head']) is not int or not 0<=w['head']<=len(forms):return 'HEAD_RANGE'
  if not isinstance(w['upos'],str) or not isinstance(w['deprel'],str):return 'LABEL_TYPE'
 try:official.load_conllu(io.StringIO(conllu(words)))
 except official.UDError as error:return 'INVALID_TREE:'+str(error)
 return None
def project_gold(sentence,contract):
 tokens=list(sentence.tokens) if contract=='all_tokens' else [t for t in sentence.tokens if t.upos!='PUNCT']
 mapping={t.token_id:i for i,t in enumerate(tokens,1)};mapping[0]=0
 return [{'id':i,'form':t.form if contract=='all_tokens' else t.form.lower(),'head':mapping.get(t.head),'deprel':t.deprel,'upos':t.upos} for i,t in enumerate(tokens,1)]
def score(words,gold,valid):
 n=len(gold);uas=las=full=upos=0
 if valid:
  for p,g in zip(words,gold):
   h=p['head']==g['head'];uas+=h;las+=h and p['deprel'].split(':',1)[0]==g['deprel'].split(':',1)[0];full+=h and p['deprel']==g['deprel'];upos+=p['upos']==g['upos']
 return {'tokens':n,'uas_correct':uas,'las_base_correct':las,'las_full_correct':full,'upos_correct':upos,'exact_tree':bool(valid and n and full==n),'exact_typed_tree':bool(valid and n and full==n and upos==n)}
def summarize(rows):
 n=sum(r['tokens'] for r in rows)
 x={'sentences':len(rows),'tokens':n,'valid_sentences':sum(r['valid'] for r in rows),'status_counts':dict(collections.Counter(r['status'] for r in rows)),'exact_tree_count':sum(r['exact_tree'] for r in rows),'exact_typed_tree_count':sum(r['exact_typed_tree'] for r in rows),'inference_wall_seconds':sum(r['wall_seconds'] for r in rows)}
 for metric,key in [('UAS','uas_correct'),('LAS_base','las_base_correct'),('LAS_full','las_full_correct'),('UPOS','upos_correct')]:x[metric]={'correct':sum(r[key] for r in rows),'denominator':n,'rate':sum(r[key] for r in rows)/n if n else None}
 x.update(valid_coverage=x['valid_sentences']/len(rows),exact_tree_rate=x['exact_tree_count']/len(rows),exact_typed_tree_rate=x['exact_typed_tree_count']/len(rows))
 return x
def main():
 dev=load_split(DATA/'en_ewt-ud-dev.conllu','dev')
 manifest=json.loads((ROOT/'evaluation-manifest.json').read_text());metadata={r['dev_index']:r for r in manifest['rows']}
 requests={r['id']:r for r in map(json.loads,(ROOT/'requests.jsonl').read_text().splitlines())}
 responses=list(map(json.loads,(ROOT/'responses.jsonl').read_text().splitlines()));assert len(responses)==len(requests) and len({r['id'] for r in responses})==len(requests)
 rows=[];crosschecks=0
 for prediction in responses:
  rid=prediction['id'];request=requests[rid];contract,ix=rid.split(':');index=int(ix);gold=project_gold(dev[index],contract)
  reason=validate(prediction['words'],request['tokens']) if prediction['status']=='PREDICTED' else prediction['status']
  valid=reason is None;result=score(prediction['words'],gold,valid)
  if valid and all(w['head'] is not None for w in gold):
   metrics=official.evaluate(official.load_conllu(io.StringIO(conllu(gold))),official.load_conllu(io.StringIO(conllu(prediction['words']))))
   assert metrics['UAS'].correct==result['uas_correct'] and metrics['LAS'].correct==result['las_base_correct'] and metrics['UPOS'].correct==result['upos_correct'];crosschecks+=1
  rows.append({'id':rid,'dev_index':index,'contract':contract,'genre':metadata[index]['genre'],'band':metadata[index]['band'],'train_surface_duplicate':metadata[index]['normalized_train_surface_duplicate'],'gold_projective_diagnostic':is_projective(dev[index]),'gold_parent_removed_count':sum(w['head'] is None for w in gold),'status':prediction['status'],'valid':valid,'invalid_reason':reason,'wall_seconds':prediction['wall_seconds'],**result})
 (ROOT/'scores.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
 groups={}
 for contract in ['all_tokens','legacy_stripped']:
  for name in ['first50','genre_length100']:
   wanted=set(manifest[name]);subset=[r for r in rows if r['contract']==contract and r['dev_index'] in wanted]
   group=summarize(subset)
   for key in ['genre','band','train_surface_duplicate','gold_projective_diagnostic']:group['by_'+key]={str(value):summarize([r for r in subset if r[key]==value]) for value in sorted({r[key] for r in subset})}
   groups[contract+'/'+name]=group
 record={'role':'DEVELOPMENT_DONOR_ONLY_NOT_SHARED_VESSEL_OR_LLM_COMPARISON','groups':groups,'official_metric_crosschecks':crosschecks,'total_rows':len(rows),'response_sha256':hashlib.sha256((ROOT/'responses.jsonl').read_bytes()).hexdigest(),'gold_dev_sha256':hashlib.sha256((DATA/'en_ewt-ud-dev.conllu').read_bytes()).hexdigest(),'metric_plan_sha256':hashlib.sha256((ROOT/'metric-plan.json').read_bytes()).hexdigest(),'protected_claim_authority':False}
 (ROOT/'evaluation-summary.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:{m:v[m] for m in ['sentences','tokens','valid_sentences','exact_tree_count','exact_typed_tree_count','UAS','LAS_base','LAS_full','UPOS']} for k,v in groups.items()}))
if __name__=='__main__':main()
