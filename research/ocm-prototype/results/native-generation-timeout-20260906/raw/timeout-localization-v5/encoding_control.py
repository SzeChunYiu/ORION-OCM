"""Actual harmless native statistics and explicit nonfinite encoding controls."""
import importlib.util
import json
import math
from pathlib import Path
import sys
import diagnostic_worker as W

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('existing_capture',ROOT.parent/'capture.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def restore(value):
    if isinstance(value,dict):
        if set(value) == {'$cvc5_float'}:
            return {'NaN':float('nan'),'+Inf':float('inf'),'-Inf':float('-inf')}[value['$cvc5_float']]
        return {key:restore(item) for key,item in value.items()}
    if isinstance(value,list):
        return [restore(item) for item in value]
    return value


def identical(left,right,path=()):
    if isinstance(left,float) and math.isnan(left):
        assert isinstance(right,float) and math.isnan(right), path
    elif isinstance(left,dict):
        assert isinstance(right,dict) and left.keys() == right.keys(), path
        for key in left: identical(left[key],right[key],path+(key,))
    elif isinstance(left,(list,tuple)):
        assert len(left) == len(right), path
        for index,(a,b) in enumerate(zip(left,right)): identical(a,b,path+(index,))
    else:
        assert type(left) == type(right) and left == right, path
        if isinstance(left,float) and left == 0:
            assert math.copysign(1,left) == math.copysign(1,right),path


def nonfinite(value,path=()):
    if isinstance(value,float) and not math.isfinite(value):
        return [{'path':list(path),'tag':'NaN' if math.isnan(value) else ('+Inf' if value>0 else '-Inf')}]
    if isinstance(value,dict):
        return [row for key,item in value.items() for row in nonfinite(item,path+(key,))]
    if isinstance(value,(list,tuple)):
        return [row for i,item in enumerate(value) for row in nonfinite(item,path+(i,))]
    return []


def preserve(snapshot,root,index,encoder):
    # Native representation is written BEFORE either serializer.
    (root/f'snapshot-{index}.repr').write_text(repr(snapshot)+'\n')
    try:
        old = json.dumps(snapshot,sort_keys=True,allow_nan=False)
        prior = {'status':'SERIALIZED','text':old}
    except ValueError as exc:
        prior = {'status':'VALUE_ERROR','message':str(exc)}
    C.write(root/f'strict-{index}.json',prior)
    encoded = encoder(snapshot)
    text = json.dumps(encoded,sort_keys=True,allow_nan=False)
    (root/f'tagged-{index}.json').write_text(text+'\n')
    identical(snapshot,restore(json.loads(text)))
    return encoded,{'index':index,'strict_status':prior['status'],'nonfinite':nonfinite(snapshot),
                    'native_roundtrip':'EXACT_CLASS_AND_FINITE_VALUE_IDENTITY'}


def child(root):
    root=Path(root); rows=[]; encoder=W.encode_statistics
    def capture(snapshot):
        encoded,row=preserve(snapshot,root,len(rows),encoder); rows.append(row)
        return encoded
    W.encode_statistics=capture
    request=json.load(sys.stdin)
    commands=request['payload']['sygus'].splitlines()
    assert commands == ['(set-logic LIA)','(set-option :output sygus-sol-gterm)',
                        '(set-option :out "stderr")','(define-fun recorder_zero () Int 0)']
    recorder=W.Recorder(root/'boundaries.jsonl'); outputs=[]; error=None
    try:
        W.native(request,recorder,outputs)
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc)}
    finally:
        recorder.close()
    print(json.dumps({'role':'NATIVE_CONSTANT_DEFINITION_NO_SYNTHESIS_OR_CHECK',
                      'snapshot_rows':rows,'outputs':outputs,'error':error}))
    return 2 if error else 0


def run(root):
    root=Path(root);root.mkdir()
    synthetic=root/'synthetic';synthetic.mkdir()
    snapshot={'nan':float('nan'),'positive':float('inf'),'negative':float('-inf'),
              'finite':[0.0,-0.0,3.5,-9,True,'NaN',{'nested':17.0}]}
    _,row=preserve(snapshot,synthetic,0,W.encode_statistics)
    assert row['strict_status']=='VALUE_ERROR'
    assert [x['tag'] for x in row['nonfinite']]==['NaN','+Inf','-Inf']
    try:
        W.encode_statistics({'$cvc5_float':'native collision'})
    except ValueError as exc:
        collision=str(exc)
    else:
        raise AssertionError('reserved tag collision was accepted')
    C.write(synthetic/'CONTROL.json',{'result':'PASS','observation':row,'collision_refusal':collision})
    commands=['(set-logic LIA)','(set-option :output sygus-sol-gterm)',
              '(set-option :out "stderr")','(define-fun recorder_zero () Int 0)']
    request={'action':'synthesize','payload':{'sygus':'\n'.join(commands)+'\n'},'timeout_ms':5000}
    target=root/'native'
    argv=['/usr/bin/timeout','--kill-after=2s','20s','/usr/bin/taskset','-c','0',
          '/usr/bin/prlimit','--as=4294967296',sys.executable,'-B',str(Path(__file__).resolve()),
          '--child',str(target)]
    result=C.capture_one(argv,(json.dumps(request)+'\n').encode(),target,ROOT,24)
    raw=json.loads((target/'stdout').read_text())
    events=[json.loads(x) for x in (target/'boundaries.jsonl').read_text().splitlines()]
    C.write(root/'RAW.json',{'native':raw,'process':result,'commands':commands,
                           'worker_sha256':C.sha(ROOT/'diagnostic_worker.py'),'control_sha256':C.sha(__file__)})
    C.write(root/'seal.json',{str(p.relative_to(root)):{'sha256':C.sha(p),'bytes':p.stat().st_size}
                             for p in sorted(root.rglob('*')) if p.is_file()})
    assert result['exit_code']==0 and raw['error'] is None and raw['outputs']==[]
    invoked=[e['command'] for e in events if e['event']=='invoke_begin']
    assert invoked==['set-logic','set-option','set-option','define-fun']
    assert len([e for e in events if e['event']=='invoke_end'])==4
    assert events[-1]['event']=='command' and events[-1]['is_null']
    observed=[x for row in raw['snapshot_rows'] for x in row['nonfinite']]
    assert observed, 'constant-only native fixture exposed no nonfinite value'
    assert all(row['strict_status']=='VALUE_ERROR' for row in raw['snapshot_rows'] if row['nonfinite'])
    print(json.dumps({'status':'PASS','native_nonfinite':observed,'native_commands':invoked,
                      'synth_fun':0,'check_synth':0,'seal_sha256':C.sha(root/'seal.json')}))


if __name__ == '__main__':
    if sys.argv[1]=='--child':
        raise SystemExit(child(sys.argv[2]))
    run(sys.argv[1])
