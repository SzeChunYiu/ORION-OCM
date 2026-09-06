from pathlib import Path
import hashlib,json,time,resource,platform,sys
import ufal.udpipe as u
ROOT=Path(__file__).resolve().parent
start=time.perf_counter();model_path=ROOT/'ewt-train-default.udpipe';model=u.Model.load(str(model_path));assert model is not None
load_seconds=time.perf_counter()-start
requests_path=ROOT/'requests.jsonl';assert not (ROOT/'responses.jsonl').exists()
requests=[json.loads(s) for s in requests_path.read_text().splitlines()]
results=[]
with (ROOT/'responses.jsonl').open('w') as stream:
 for request in requests:
  assert set(request)=={'id','tokens'}
  assert isinstance(request['id'],str) and all(isinstance(s,str) for s in request['tokens'])
  start=time.perf_counter();row={'id':request['id'],'status':'PREDICTED','words':[]}
  if not request['tokens']:row['status']='ABSTAIN_EMPTY'
  else:
   sentence=u.Sentence()
   for form in request['tokens']:sentence.addWord(form)
   # No supplied tags, lemmas, features, heads or relations exist at this boundary.
   assert all(not w.upostag and not w.lemma and w.head<0 for w in list(sentence.words)[1:])
   error=u.ProcessingError()
   if not model.tag(sentence,u.Model.DEFAULT,error):row.update(status='TAGGER_ERROR',error=error.message)
   elif not model.parse(sentence,u.Model.DEFAULT,error):row.update(status='PARSER_ERROR',error=error.message)
   else:row['words']=[{'id':w.id,'form':w.form,'head':w.head,'deprel':w.deprel,'upos':w.upostag} for w in list(sentence.words)[1:]]
  row['wall_seconds']=time.perf_counter()-start;results.append(row)
  stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
usage=resource.getrusage(resource.RUSAGE_SELF)
record={'role':'DEVELOPMENT_DONOR_PREDICTIONS_NOT_GOLD_CERTIFICATES','python':platform.python_version(),'requests':len(requests),'model_load_seconds':load_seconds,'inference_wall_seconds':sum(x['wall_seconds'] for x in results),'cpu_user_seconds':usage.ru_utime,'cpu_system_seconds':usage.ru_stime,'maxrss_kib':usage.ru_maxrss,'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'request_sha256':hashlib.sha256(requests_path.read_bytes()).hexdigest(),'response_sha256':hashlib.sha256((ROOT/'responses.jsonl').read_bytes()).hexdigest(),'no_gold_input':True,'worker_read_contract':['model bytes','id and token forms only']}
(ROOT/'inference-resources.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
