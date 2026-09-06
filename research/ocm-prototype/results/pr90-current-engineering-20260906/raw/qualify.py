#!/usr/bin/env python3
"""Execute current engineering qualification once; retain immutable prior bindings."""
from pathlib import Path
import hashlib,json,os,resource,subprocess,sys,time
from datetime import datetime,timezone
root=Path(sys.argv[1]).resolve()
out=root/'research/ocm-prototype/results/pr90-current-engineering-20260906'
raw=out/'raw'
raw.mkdir(parents=True,exist_ok=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    with p.open('x') as f: json.dump(obj,f,indent=2,sort_keys=True); f.write('\n')
git=lambda *args: subprocess.check_output(['/usr/bin/git',*args],cwd=root)
sys.path.insert(0,str(root/'tools'))
import engineering_receipts as E
inventory=E.V4.source_inventory(root)
paths=git('ls-files','-z','docs/provenance','research/ocm-prototype/results/surprise-channel-repair-20260906','research/ocm-prototype/results/surprise-channel-integration-20260906','research/ocm-prototype/results/pr90-cache-accounting-port-20260906','research/ocm-prototype/results/pr90-digest-compatibility-repair-20260906','research/ocm-prototype/results/pr90-registry-compatibility-repair-20260906').decode().split('\0')
pointer='docs/provenance/engineering_revisions/CURRENT_ENGINEERING.json'
immutable={p:digest(root/p) for p in paths if p and p!=pointer}
pre={'head':git('rev-parse','HEAD').decode().strip(),'source_inventory':inventory,
     'source_id':E.source_id(inventory),'immutable_predecessor_sha256':immutable,
     'current_before':json.loads((root/pointer).read_text()),'python':sys.version,
     'executable':sys.executable,'started_at':datetime.now(timezone.utc).isoformat(),
     'status_before':git('status','--porcelain=v1').decode()}
write(raw/'before.json',pre)
env=dict(os.environ); env['PYTHONPATH']=str(root/'src')
argv=[sys.executable,'tools/record_engineering_revision.py']
before=resource.getrusage(resource.RUSAGE_CHILDREN); start=time.perf_counter()
with (raw/'recorder.log').open('xb') as log:
    proc=subprocess.run(argv,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
record={'argv':argv,'exit_code':proc.returncode,'wall_seconds':time.perf_counter()-start,
        'direct_child_cpu_user_seconds':after.ru_utime-before.ru_utime,
        'direct_child_cpu_system_seconds':after.ru_stime-before.ru_stime,
        'resource_scope':'supervisor RUSAGE_CHILDREN observations; no independent process-tree completeness claim',
        'log_sha256':digest(raw/'recorder.log'),'completed_at':datetime.now(timezone.utc).isoformat(),
        'source_unchanged':inventory==E.V4.source_inventory(root),
        'immutable_predecessor_mismatches':[p for p,h in immutable.items() if not (root/p).is_file() or digest(root/p)!=h],
        'current_after':json.loads((root/pointer).read_text()),
        'scientific_promotion':'NOT_ESTABLISHED','protected_evaluation':'NOT_RUN'}
write(raw/'qualification.json',record)
print(json.dumps(record,indent=2),flush=True)
raise SystemExit(proc.returncode or (0 if record['source_unchanged'] and not record['immutable_predecessor_mismatches'] else 2))
