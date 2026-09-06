#!/usr/bin/env python3
"""Verify the selected engineering receipt and all current/archival wrapper boundaries."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path(sys.argv[1]).resolve()
out=root/'research/ocm-prototype/results/pr90-current-engineering-20260906'
raw=out/'raw'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    with p.open('x') as f: json.dump(obj,f,indent=2,sort_keys=True); f.write('\n')
q=json.loads((raw/'qualification.json').read_text())
if q['exit_code'] or not q['source_unchanged'] or q['immutable_predecessor_mismatches']:
    raise SystemExit('qualification refused; no subsequent verification')
env=dict(os.environ); env['PYTHONPATH']=str(root/'src')
checks=[]
recipes=[('current_targets',['tools/m2_vendor_check.py','--targets-only','--manifest','docs/provenance/VENDORED_SOURCE_MANIFEST_CURRENT.json'])]
recipes += [('m'+str(n),['tools/m'+str(n)+'_receipt.py','--verify']) for n in range(1,13)]
recipes += [('v5_archival_custody',['tools/m12_paired_v5_receipt.py','--verify'])]
for name,args in recipes:
    argv=[sys.executable,*args]; start=time.perf_counter()
    proc=subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=raw/(name+'.log')
    with log.open('xb') as f: f.write(proc.stdout)
    checks.append({'name':name,'argv':argv,'exit_code':proc.returncode,
                   'wall_seconds':time.perf_counter()-start,'log_path':str(log.relative_to(out)),
                   'log_sha256':digest(log)})
sys.path.insert(0,str(root/'tools'))
import engineering_receipts as E
before=json.loads((raw/'before.json').read_text())
current=json.loads((root/'docs/provenance/engineering_revisions/CURRENT_ENGINEERING.json').read_text())
value=E.verify(root)
immutable=before['immutable_predecessor_sha256']
record={'checks':checks,'current':current,'current_verification':value,
        'source_id':E.source_id(E.V4.source_inventory(root)),
        'source_file_count':len(E.V4.source_inventory(root)),
        'source_unchanged':before['source_inventory']==E.V4.source_inventory(root),
        'immutable_predecessor_mismatches':[p for p,h in immutable.items() if not (root/p).is_file() or digest(root/p)!=h],
        'manifest_file_count':len(json.loads((root/'docs/provenance/VENDORED_SOURCE_MANIFEST_CURRENT.json').read_text())['files']),
        'space_vendor_targets':[x for x in json.loads((root/'docs/provenance/VENDORED_SOURCE_MANIFEST_CURRENT.json').read_text())['files'] if x['target_path']=='src/ocm/kso/space.py'],
        'scientific_promotion':'NOT_ESTABLISHED','protected_evaluation':'NOT_RUN'}
record['passed']=all(c['exit_code']==0 for c in checks) and record['source_unchanged'] and not record['immutable_predecessor_mismatches']
write(raw/'verification.json',record)
print(json.dumps({k:v for k,v in record.items() if k!='current_verification'},indent=2))
raise SystemExit(0 if record['passed'] else 1)
