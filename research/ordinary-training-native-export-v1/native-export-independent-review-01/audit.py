"""One independent retained-data audit. No target module is imported/executed."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json,os,time,traceback
from read_data import *
import check_custody,check_inventory,check_traces
start=time.perf_counter(); out={'schema':'ordinary.native-export.independent-data-audit.v1','pid':os.getpid(),
 'python':sys.executable,'cwd':os.getcwd(),'target_imports':False,'native_replays':0,'trace_replays':0,'learner_calls':0,'new_corpus_census':False}
try:
    q,g,s,p,result=check_custody.check()
    a,p1,packet,rel,records,extra=check_inventory.check(q,result)
    counts=check_traces.check(a,p1,packet,rel,records,result)
    # Reader controls: clean data above must succeed; malformed/different data must not pass equality/hash guards.
    catches=0
    for f in [lambda:parse(b'{"a":1,"a":2}'),lambda:equal('tampered-order',[1,2],[2,1]),
              lambda:canon_bound('tampered-trace',{'x':2},identity(canonical({'x':1}))),
              lambda:equal('tampered-file',identity(b'changed'),identity(b'original'))]:
        try:f()
        except (ValueError,AssertionError): catches+=1
    equal('reader-tamper-controls',catches,4)
    out.update(terminal='RETAINED_ARTIFACTS_CONSISTENT',counts=counts,additional_axioms=extra,
      native_passes={'fresh':4223,'observation':4223,'fallback':0},P0_contracts=4191,P1_contracts=4323,
      P1_base=4195,P1_released=128,source_files=9,start_pins=25,unchanged_inputs=26,
      historical_manifest_files=len(load(ROOT/'HASHES-02.json')['files']),
      observer_measured_outer_wall_s=p['measured_outer_wall_s'],observer_process_wall_s=p['process_wall_s'],
      observer_user_cpu_s=p['user_cpu_s'],observer_system_cpu_s=p['system_cpu_s'],rss_kib=p['rss_kib'],
      timing_scope=p['measurement_scope'],corpus_identity_scope='Inherited descriptor only; full corpus not read.',
      authority=identity(read(OUT/'NATIVE-AUTHORITY.json')),P1=identity(read(OUT/'P1-INVENTORY.json')),
      packet=identity(read(OUT/'TEACHING-PACKET-CANDIDATE.json')))
except Exception as e:
    out.update(terminal='INDEPENDENT_READER_INCOMPLETE',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc())
out.update(check_count=len(CHECKS),check_names=CHECKS,read_scope=READS,reader_wall_s=time.perf_counter()-start)
dest=Path(__file__).parent/'AUDIT-01.json'
with dest.open('xb') as f:f.write(canonical(out))
print(json.dumps({k:v for k,v in out.items() if k not in ['check_names','read_scope']},sort_keys=True))
raise SystemExit(0 if out['terminal']=='RETAINED_ARTIFACTS_CONSISTENT' else 2)
