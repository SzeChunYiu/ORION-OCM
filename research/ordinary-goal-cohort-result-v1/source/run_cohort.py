"""One gated joined-cohort call; reuse native wrapper and GNU-time observation."""
from pathlib import Path
import json,os,resource,sys,time,traceback
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'vendor')]
import life_native as N
import trace_source as S
import cohort_suffix as T
from goal_library import raw_identity,identity,require
from cohort_input import adapt,transported_claims
from cohort_check import base_authority,bind_result

def load(path):return json.loads(Path(path).read_bytes())
def pin(path):return {'path':str(Path(path)),**raw_identity(Path(path).read_bytes())}
def exact(binding):require(pin(binding['path'])==binding,'file identity: '+binding['path'])
def write(path,value):N.store(path,N.encoded(value)+b'\n')
def main():
    start=time.perf_counter();before=resource.getrusage(resource.RUSAGE_SELF)
    request_path=Path(sys.argv[1]).resolve();request=load(request_path);gate_path=Path(request['gate']);gate=load(gate_path)
    require(gate['schema']=='ordinary.goal-cohort-native-gate.v1' and gate['authorized'] is True,'separate root authorization')
    require(gate['request']==pin(request_path) and gate['source_freeze']==request['source_freeze']
            and gate['scope']=='ONE_JOINED_4223_PLUS_22_NATIVE_PASS_NO_RETRY','exact root-bound request/scope')
    exact(request['source_freeze']);freeze=load(request['source_freeze']['path'])
    for item in freeze['files']:exact(item)
    require(pin(sys.executable)==request['python'] and sys.flags.isolated and sys.flags.no_site
            and sys.flags.dont_write_bytecode and not sys.flags.optimize,'pinned isolated runtime')
    require(os.getcwd()==request['cwd'],'registered cwd')
    opening={'request':pin(request_path),'gate':pin(gate_path),'freeze':pin(request['source_freeze']['path'])}
    outpath=Path(request['output']);outpath.mkdir(exist_ok=False)
    out={'terminal':'CANNOT_CHECK','stage':'inputs','native_calls':0,'wrapper_invocations':0,'work':{}}
    try:
        write(outpath/'INPUT-BINDINGS.json',opening)
        for k in ('cohort','original_suffix','base_authority','base_prefix'):exact(request[k])
        base_raw=Path(request['base_prefix']['path']).read_bytes();base_pin=raw_identity(base_raw)
        cohort=load(request['cohort']['path']);prior=load(request['base_authority']['path'])
        old_suffix=Path(request['original_suffix']['path']).read_bytes();base,_=S.index(base_raw)
        out['work'].update(caller_source_index_calls=1,caller_source_bytes_indexed=len(base_raw))
        authority=base_authority(base,prior,base_pin);out['stage']='members'
        require(cohort['prefix_identity_reported_by_admit']==base_pin,'historical/current base agreement')
        members=adapt(cohort,base,old_suffix,request['cohort']);write(outpath/'MEMBERS.json',members)
        out['stage']='transport';transport,suffix=T.construct(base_raw,base_pin,members,identity(members))
        write(outpath/'TRANSPORT.json',transport);N.store(outpath/'TRANSPORTED-SUFFIX.mm',suffix)
        claims=transported_claims(members,transport,suffix);write(outpath/'CLAIMS.json',claims)
        joined_raw=base_raw+b'\n'+suffix;N.store(outpath/'JOINED-PREFIX.mm',joined_raw);joined,_=S.index(joined_raw)
        out['work']['caller_source_index_calls']+=1;out['work']['caller_source_bytes_indexed']+=len(joined_raw)
        out['work'].update(constructor_source_index_calls=2,constructor_source_bytes_indexed=len(base_raw)+len(joined_raw))
        out['stage']='native';out['wrapper_invocations']=1;out['native_calls']=None
        native=N.verify(Path(request['base_prefix']['path']),claims,outpath/'native-01',request['native_sources'],authority,suffix)
        out.update(native_calls=native['native_calls'],native_result_file=pin(outpath/'native-01/result.json'),native_terminal=native['terminal'])
        out['stage']='result_binding'
        manifest,costs=bind_result(native,claims,base_raw,joined_raw,base,joined,authority,request['native_sources'],Path(request['base_prefix']['path']),outpath/'native-01')
        write(outpath/'LIBRARY-MANIFEST.json',manifest)
        write(outpath/'LIBRARY-ARTIFACT.json',{'manifest':identity(manifest),'manifest_file':pin(outpath/'LIBRARY-MANIFEST.json'),
            'base_prefix':request['base_prefix'],'joined_prefix':pin(outpath/'JOINED-PREFIX.mm'),'receipt':manifest['receipt'],
            'receipt_file':pin(outpath/'native-01/result.json'),'scope':'Current native result and exact source custody; no saved flag grants future proof authority.'})
        out.update(terminal='JOINED_COHORT_NATIVE_VERIFIED',stage='complete',library_costs=costs,
                   base_proofs=4223,cohort_proofs=22,joined_proofs=4245,trusted_axioms=100)
    except Exception as exc:
        out['error']={'type':type(exc).__name__,'message':str(exc)}
        N.store(outpath/'caller-error.txt',traceback.format_exc().encode())
    finally:
        try:
            require(pin(request_path)==opening['request'] and pin(gate_path)==opening['gate'],'request/gate unchanged')
            for item in freeze['files']:exact(item)
            for k in ('cohort','original_suffix','base_authority','base_prefix'):exact(request[k])
            require(pin(request['source_freeze']['path'])==opening['freeze'],'freeze unchanged')
            out['custody_unchanged']=True
        except Exception as exc:out.update(terminal='CANNOT_CHECK',custody_unchanged=False,custody_error=str(exc))
        after=resource.getrusage(resource.RUSAGE_SELF)
        out['process']={'pid':os.getpid(),'parent_pid':os.getppid(),'cwd':os.getcwd(),'python':sys.executable,
            'imported_modules':{k:str(Path(v.__file__).resolve()) for k,v in sys.modules.items() if getattr(v,'__file__',None)},
            'wall_s':time.perf_counter()-start,'user_cpu_s':after.ru_utime-before.ru_utime,'system_cpu_s':after.ru_stime-before.ru_stime,
            'process_highwater_rss_kib':after.ru_maxrss,'scope':'Main through post-custody; imports/final RESULT write excluded. Native and library windows nested.'}
        write(outpath/'RESULT.json',out)
    return 0 if out['terminal']=='JOINED_COHORT_NATIVE_VERIFIED' else 2
if __name__=='__main__':raise SystemExit(main())
