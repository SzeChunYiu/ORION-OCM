"""Create-only serial induction capture, using the previously qualified process supervisor."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from supervision import capture_one, sha, write

ROOT = Path(__file__).resolve().parent
def verify(manifest):
    if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise ValueError('nonoptimized Python required')
    for path,b in manifest['bindings'].items():
        p=Path(path)
        if p.stat().st_size != b['bytes'] or sha(p) != b['sha256']:
            raise ValueError('BINDING_DRIFT: '+path)
    if str(Path(sys.executable).resolve()) != manifest['python_resolved']:
        raise ValueError('EXECUTABLE_DRIFT')

def run(manifest_path):
    start=time.perf_counter()
    manifest_path=Path(manifest_path); manifest=json.loads(manifest_path.read_text())
    output=Path(manifest['output']); output.mkdir()
    (output/'manifest.json').write_bytes(manifest_path.read_bytes())
    receipt={'status':'CANNOT_CHECK_EXECUTION', 'manifest_sha256':sha(manifest_path),
             'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'case':None, 'error':None, 'scientific_status':'NOT_ESTABLISHED'}
    try:
        verify(manifest)
        result=capture_one(manifest['argv'], Path(manifest['input']).read_bytes(),
                           output/'raw', ROOT, manifest['watchdog_seconds'])
        receipt['case']=result
        verify(manifest)
        side=output/'calls'/'caller-receipt.json'
        if result['exit_code']==0 and side.is_file():
            receipt['status']='RAW_CAPTURE_COMPLETE'
        else:
            receipt['status']='CANNOT_CHECK_EXECUTION'
    except (OSError, ValueError, KeyError) as exc:
        receipt['error']=type(exc).__name__+': '+str(exc)
    receipt['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt['supervisor_wall_including_pre_post_binding_s']=time.perf_counter()-start
    receipt['process_tree_cpu']='UNKNOWN'; receipt['process_tree_peak_rss']='UNKNOWN'
    calls=output/'calls'
    requests=list(calls.glob('verify-*-request.json'))
    responses=list(calls.glob('verify-*-result.json'))
    receipt['observed_boundaries']={
        'verify_boundary_requests':len(requests),
        'verify_completed_responses':len(responses),
        'native_verify_true_in_returned_responses':sum(json.loads(p.read_text()).get('native_invoked') is True for p in responses),
        'verify_without_response':len(requests)-len(responses),
        'compress_dispatch_request_present':(calls/'compress-request.json').is_file(),
        'compress_return_present':(calls/'compress-return.json').is_file(),
        'compress_exception_present':(calls/'compress-exception.json').is_file(),
        'note':'Boundary dispatch records are not proof of native entry if interrupted; unresolved execution stays UNKNOWN.'}
    write(output/'receipt.json', receipt)
    write(output/'seal.json', {str(p.relative_to(output)):{'sha256':sha(p),'bytes':p.stat().st_size}
                                for p in sorted(output.rglob('*')) if p.is_file()})
    print(json.dumps({'status':receipt['status'],'seal_sha256':sha(output/'seal.json')}))
    return 0 if receipt['status']=='RAW_CAPTURE_COMPLETE' else 2

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest', required=True)
    raise SystemExit(run(p.parse_args().manifest))
