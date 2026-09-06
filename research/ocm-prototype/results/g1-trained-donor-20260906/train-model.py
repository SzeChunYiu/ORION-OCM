from pathlib import Path
import hashlib,json,time,platform,resource,os
import ufal.udpipe as u
ROOT=Path(__file__).resolve().parent
config=json.loads((ROOT/'training-plan.json').read_text())
path=Path(config['train_path']);data=path.read_bytes()
assert hashlib.sha256(data).hexdigest()==config['train_sha256']
reader=u.InputFormat.newConlluInputFormat();reader.setText(data.decode())
error=u.ProcessingError();sentences=u.Sentences()
while True:
 sentence=u.Sentence()
 if not reader.nextSentence(sentence,error):break
 sentences.append(sentence)
assert not error.occurred(),error.message
record={'event':'TRAINING_STARTED','pid':os.getpid(),'sentences':len(sentences),'tokens':sum(len(s.words)-1 for s in sentences),'heldout_sentences':0,'python':platform.python_version(),'udpipe':[u.Version.current().major,u.Version.current().minor,u.Version.current().patch],'plan':config}
print(json.dumps(record),flush=True);start=time.perf_counter()
model=u.Trainer.train('morphodita_parsito',sentences,u.Sentences(),u.Trainer.NONE,u.Trainer.DEFAULT,u.Trainer.DEFAULT,error)
assert not error.occurred(),error.message
assert model is not None
body=bytes(model);assert body
out=ROOT/'ewt-train-default.udpipe';out.write_bytes(body)
assert u.Model.load(str(out)) is not None
record={'event':'TRAINING_COMPLETED','wall_seconds':time.perf_counter()-start,'model_bytes':len(body),'model_sha256':hashlib.sha256(body).hexdigest(),'maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(ROOT/'training-model.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
