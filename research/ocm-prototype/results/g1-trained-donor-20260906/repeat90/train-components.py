from pathlib import Path
import json,hashlib,time,resource,os
import ufal.udpipe as u
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'training-plan.json').read_text())
data=Path(plan['train_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==plan['train_sha256']
reader=u.InputFormat.newConlluInputFormat();reader.setText(data.decode());error=u.ProcessingError();sentences=u.Sentences()
while True:
 sentence=u.Sentence()
 if not reader.nextSentence(sentence,error):break
 sentences.append(sentence)
assert not error.occurred(),error.message
print(json.dumps({'event':'TRAINING_STARTED','pid':os.getpid(),'sentences':len(sentences),'tokens':sum(len(s.words)-1 for s in sentences),'heldout_sentences':0,'orchestration':'ADAPT checkpointed official component reuse'}),flush=True)
for stage in ['tagger','parser']:
 start=time.perf_counter();usage0=resource.getrusage(resource.RUSAGE_SELF)
 tagger=u.Trainer.DEFAULT if stage=='tagger' else 'from_model=file:'+str(ROOT/'tagger-default.udpipe')
 parser=u.Trainer.NONE if stage=='tagger' else u.Trainer.DEFAULT
 print(json.dumps({'event':'STAGE_STARTED','stage':stage,'tokenizer':u.Trainer.NONE,'tagger':tagger,'parser':parser}),flush=True)
 model=u.Trainer.train('morphodita_parsito',sentences,u.Sentences(),u.Trainer.NONE,tagger,parser,error)
 assert not error.occurred(),error.message
 assert model is not None
 body=bytes(model);assert body
 output=ROOT/('tagger-default.udpipe' if stage=='tagger' else 'ewt-train-default.udpipe')
 temporary=output.with_suffix('.temporary');temporary.write_bytes(body);temporary.replace(output)
 assert u.Model.load(str(output)) is not None
 usage=resource.getrusage(resource.RUSAGE_SELF)
 receipt={'event':'STAGE_COMPLETED','stage':stage,'wall_seconds':time.perf_counter()-start,'cpu_user_seconds':usage.ru_utime-usage0.ru_utime,'cpu_system_seconds':usage.ru_stime-usage0.ru_stime,'process_cpu_user_seconds':usage.ru_utime,'process_cpu_system_seconds':usage.ru_stime,'process_maxrss_kib':usage.ru_maxrss,'artifact':output.name,'artifact_bytes':len(body),'artifact_sha256':hashlib.sha256(body).hexdigest(),'teacher_train_sha256':plan['train_sha256'],'no_development_selection':True}
 (ROOT/(stage+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
