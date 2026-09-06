"""Capture public native donor development receipts; no protected or hosted run."""
import hashlib,json,os,subprocess,time,resource,sys
from pathlib import Path
root=Path('/home/billy/orion-director-work/20260906/ocm-g1')
base=root/'research/ocm-prototype';sys.path.insert(0,str(base))
from clia_tasks import load_task
from clia_solver import propose
from clia_checker import check
files=sorted(base.glob('clia_*.py'))+sorted(base.glob('test_clia_*.py'))+sorted((base/'clia_fixtures').glob('*'))
source={str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'lines':len(p.read_bytes().splitlines())} for p in files}
start=time.perf_counter();cpu=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN);rows=[]
for name in ['jmbl_fg_max3','jmbl_fg_max10','jmbl_fg_array_search_4','jmbl_fg_array_search_10','jmbl_fg_mpg_guard2']:
 task=load_task(name);proposal=propose(task);checked=check(task,proposal)
 rows.append({'task':task,'proposal':proposal,'check':checked})
# A budget diagnostic: preserve the actual outcome, never force unknown.
diagnostic=check(rows[1]['task'],rows[1]['proposal'],timeout_ms=1)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
r={'classification':'PUBLIC_DEVELOPMENT_ONLY','source_head':subprocess.check_output(['/usr/bin/git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'source_files':source,'capture_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':rows,'checker_1ms_diagnostic':diagnostic,'wall_s':time.perf_counter()-start,'host_cpu_s':time.process_time()-cpu,'terminated_child_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'measurement_scope':'Serial process envelope including host task loading/checking and terminated child CPU; no other children were launched by this process. Package installation/development and energy excluded.','pid':os.getpid()}
p=Path('/home/billy/orion-director-work/20260906/clia-direct-development.json');p.write_text(json.dumps(r,indent=2)+'\n')
assert all(x['proposal']['status']=='SOLUTION' and x['check']['grammar']=='PASS' and x['check']['semantic']=='PASS' and not x['check'].get('reason') for x in rows)
print(json.dumps({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'passed':len(rows),'diagnostic':diagnostic.get('solver_result'),'wall_s':r['wall_s'],'host_cpu_s':r['host_cpu_s'],'child_cpu_s':r['terminated_child_cpu_s']}))
