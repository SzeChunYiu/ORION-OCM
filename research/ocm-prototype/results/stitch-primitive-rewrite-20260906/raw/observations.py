"""Retained incomplete native-response custody from prior qualified launcher."""
import json
from pathlib import Path

def observations(calls):
    """Read completed response evidence; retain incomplete files and unknown native entry."""
    requests={p.name.removesuffix('-request.json') for p in calls.glob('verify-*-request.json')}
    response_paths=sorted(calls.glob('verify-*-result.json'))
    valid={}; invalid=[]
    for path in response_paths:
        try:
            value=json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            invalid.append({'file':path.name,'reason':type(exc).__name__,'native_entry':'UNKNOWN'})
            continue
        if not isinstance(value,dict) or type(value.get('native_invoked')) is not bool:
            invalid.append({'file':path.name,'reason':'NON_OBJECT_OR_MISSING_BOOLEAN_NATIVE_FIELD',
                            'native_entry':'UNKNOWN'})
            continue
        valid[path.name.removesuffix('-result.json')]=value
    matched=requests & valid.keys()
    unresolved=requests-valid.keys()
    orphan=valid.keys()-requests
    count=sum(valid[key]['native_invoked'] is True for key in matched)
    return {
        'verify_boundary_requests':len(requests),
        'verify_response_files':len(response_paths),
        'verify_completed_responses':len(matched),
        'native_verify_true_in_returned_responses':count,
        'verify_without_response':len(unresolved),
        'invalid_or_incomplete_response_files':invalid,
        'orphan_response_keys':sorted(orphan),
        'native_invocations_overall':'UNKNOWN' if unresolved or invalid or orphan else count,
        'rewrite_dispatch_request_present':(calls/'rewrite-request.json').is_file(),
        'rewrite_return_present':(calls/'rewrite-return.json').is_file(),
        'rewrite_exception_present':(calls/'rewrite-exception.json').is_file(),
        'note':'Only completed matched responses establish native entry; malformed or missing evidence remains UNKNOWN. Raw files are unchanged.'}
