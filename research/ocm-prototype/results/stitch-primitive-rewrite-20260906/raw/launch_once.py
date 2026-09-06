"""Create-only two-group rewrite qualification; original supervisor is reused."""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import time
from supervision import capture_one,sha,write
from observations import observations

ROOT=Path(__file__).resolve().parent

def verify(manifest):
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise ValueError('nonoptimized Python required')
    if str(Path(sys.executable).resolve())!=manifest['python_resolved']:
        raise ValueError('EXECUTABLE_DRIFT')
    for path,b in manifest['bindings'].items():
        p=Path(path)
        if p.stat().st_size!=b['bytes'] or sha(p)!=b['sha256']:
            raise ValueError('BINDING_DRIFT: '+path)
    if [g['group'] for g in manifest['groups']]!=['manual','train']:
        raise ValueError('fixed serial group assignment mismatch')

def side_receipt(path):
    try:
        value=json.loads(path.read_text())
        if not isinstance(value,dict):
            raise ValueError('caller receipt not an object')
        return value,None
    except (OSError,ValueError,UnicodeError) as exc:
        return None,type(exc).__name__+': '+str(exc)

def run(manifest_path):
    start=time.perf_counter(); manifest_path=Path(manifest_path)
    manifest=json.loads(manifest_path.read_text())
    output=Path(manifest['output']);output.mkdir()
    (output/'manifest.json').write_bytes(manifest_path.read_bytes())
    receipt={'status':'CANNOT_CHECK_EXECUTION','manifest_sha256':sha(manifest_path),
             'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'assigned_groups':['manual','train'],'groups':[],'error':None}
    try:
        verify(manifest)
        for group in manifest['groups']:
            verify(manifest)
            directory=output/group['group'];directory.mkdir()
            result=capture_one(group['argv'],Path(group['input']).read_bytes(),
                               directory/'raw',ROOT,manifest['watchdog_seconds'])
            observed=observations(directory/'calls')
            side,error=side_receipt(directory/'calls/caller-receipt.json')
            complete=(result['exit_code']==0 and side is not None
                      and side.get('status')=='CALLER_RETURNED'
                      and observed['native_invocations_overall']!='UNKNOWN'
                      and observed['rewrite_dispatch_request_present']
                      and observed['rewrite_return_present'])
            receipt['groups'].append({'group':group['group'],'process':result,
                'observations':observed,'caller':side,'side_error':error,
                'raw_complete':complete})
            verify(manifest)
        if all(x['raw_complete'] for x in receipt['groups']):
            receipt['status']='RAW_CAPTURE_COMPLETE'
    except (OSError,ValueError,KeyError) as exc:
        receipt['error']=type(exc).__name__+': '+str(exc)
    done={g['group'] for g in receipt['groups']}
    receipt['not_run']=[g for g in receipt['assigned_groups'] if g not in done]
    statuses={g['group']:(g['caller'] or {}).get('qualification_status') for g in receipt['groups']}
    receipt['normalization_status']='CANNOT_CHECK_NORMALIZATION'
    if receipt['status']=='RAW_CAPTURE_COMPLETE' and statuses.get('manual')=='MANUAL_BOUNDARY_QUALIFIED':
        if statuses.get('train')=='TRAIN_NORMALIZATION_QUALIFIED':
            receipt['normalization_status']='SUPPLIED_PRIMITIVE_NORMALIZATION_QUALIFIED'
        elif statuses.get('train')=='TRAIN_EQUIVALENT_NO_EFFECTIVE_NORMALIZATION':
            receipt['normalization_status']='SUPPORTED_REWRITE_NO_TRAIN_EFFECT'
    receipt.update(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        supervisor_wall_including_all_pre_post_binding_s=time.perf_counter()-start,
        process_tree_cpu='UNKNOWN',process_tree_peak_rss='UNKNOWN',compression='NOT_RUN',
        new_useful_operator='NOT_ESTABLISHED')
    write(output/'receipt.json',receipt)
    write(output/'seal.json',{str(p.relative_to(output)):{'sha256':sha(p),'bytes':p.stat().st_size}
                             for p in sorted(output.rglob('*')) if p.is_file()})
    print(json.dumps({'status':receipt['status'],'normalization_status':receipt['normalization_status'],
                      'seal_sha256':sha(output/'seal.json')}))
    return 0 if receipt['status']=='RAW_CAPTURE_COMPLETE' else 2

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True)
    raise SystemExit(run(p.parse_args().manifest))
