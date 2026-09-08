"""Authorize the separately reviewed consumer only; never invoke acquisition."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys

root = Path('/home/billy/orion-director-work/20260908/native-typed-wff-consumer-revival-v1')
old = Path('/home/billy/orion-director-work/20260908/native-typed-wff-lifecycle-v1')
review = Path('/home/billy/orion-director-work/20260908/native-ocm-adoption-source-review-v1/typed-wff/lifecycle/consumer-revival/REVIEW.json')

def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def read(path):
    return json.loads(path.read_text())

assert identity(review) == {'bytes': 2192, 'sha256': '1a3da693254a8fcea2eb75ffb283ffa5e159331c7e0db36be36f4800258a179f'}
decision = read(review)
assert decision['verdict'] == 'SOURCE_AND_APPARATUS_QUALIFIED_FOR_SEPARATE_ROOT_GATE'
assert decision['remaining_source_blockers'] == []
assert identity(root / 'RUN-REQUEST.json') == decision['run_request']
assert identity(root / 'SOURCE-FREEZE.json') == decision['source_freeze']
assert identity(root / 'SOURCE-REVIEW-REQUEST-01.json') == decision['source_review_request']
request = read(root / 'RUN-REQUEST.json')
assert identity(Path(sys.executable)) == request['python_identity']
assert request['argv'] == [request['python'], '-I', '-S', '-B', str(root / 'run_b.py'), str(root / 'consumer-01')]
assert identity(root / 'B-INPUT.json') == request['prepared_input_envelope']
assert identity(root / 'B-GATE.json') == request['prepared_gate_envelope']
assert identity(root / 'PROJECTION.json') == request['projection']
assert identity(root / 'B-REQUEST.json') == request['issued_request']
assert identity(root / 'ORIGIN.json') == request['origin']
frozen = read(root / 'SOURCE-FREEZE.json')
checked = 0
for group in ('sources', 'inputs'):
    for relative, pin in frozen[group].items():
        assert identity(root / relative) == pin, relative
        checked += 1
origin = read(root / 'ORIGIN.json')
assert origin['original_root'] == str(old)
historical = {}
paths = {'failed_consumer': 'consumer-01/FAILURE.json', 'original_gate': 'EXECUTION-GATE.json',
         'original_outer_process': 'outer-01/PROCESS.json', 'original_source_freeze': 'SOURCE-FREEZE.json',
         'producer_process': 'lifecycle-01/A-PROCESS.json', 'producer_result': 'producer-01/RESULT.json',
         'producer_state': 'producer-01/STATE.json', 'projection': 'PROJECTION.json', 'requests': 'B-REQUEST.json'}
for key, relative in paths.items():
    assert identity(old / relative) == origin[key], key
    historical[str(old / relative)] = origin[key]
process = read(old / paths['producer_process'])
result = read(old / paths['producer_result'])
state = read(old / paths['producer_state'])
projection = read(root / 'PROJECTION.json')
assert process['exit_code'] == 0 and process['reaped'] is True
assert process['result'] == origin['producer_result']
assert result['pid'] == process['pid'] and result['terminal'] == 'ADMITTED_AND_PERSISTED'
assert result['state'] == origin['producer_state']
assert state['source_freeze'] == origin['original_source_freeze']
assert projection['origin']['source_freeze'] == state['source_freeze']
assert projection['origin']['state'] == origin['producer_state']
assert projection['origin']['process'] == origin['producer_process']
assert projection['origin']['producer_result'] == origin['producer_result']
assert projection['origin']['admission'] == state['admission']
assert projection['origin']['discovery'] == state['discovery']
assert projection['witnesses'] == state['witnesses']
assert result['eligible_method_ids'] == state['eligible_method_ids'] == projection['eligible_method_ids'] == []
envelope = read(root / 'B-INPUT.json')
assert envelope == {'projection': request['projection'], 'request': request['issued_request'],
                    'source_freeze': request['source_freeze']}
assert read(root / 'B-GATE.json') == {'input': request['prepared_input_envelope'],
                                    'exited_producer': origin['producer_process']}
assert list((root / 'outer-01').iterdir()) == [] and not (root / 'outer-01').is_symlink()
for name in ('EXECUTION-GATE.json', 'consumer-01'):
    assert not (root / name).exists() and not (root / name).is_symlink(), name
gate = {'schema': 'ocm.root-typed-consumer-revival-authorization.v1',
        'authorization': 'ROOT_GATE_OPEN', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'request': identity(root / 'RUN-REQUEST.json'), 'source_freeze': identity(root / 'SOURCE-FREEZE.json'),
        'review': {'path': str(review), **identity(review)}, 'argv': request['argv'],
        'prepared_input_envelope': request['prepared_input_envelope'],
        'prepared_gate_envelope': request['prepared_gate_envelope'],
        'historical_bindings': historical, 'frozen_bindings_checked': checked,
        'required_outer_checks': decision['required_outer_checks'],
        'scope': 'One fresh consumer only. No acquisition, bridge, discovery, reprojection or original supervisor. No retry.',
        'original_failure_remains_final': True, 'native_execution_by_authorizer': False}
path = root / 'EXECUTION-GATE.json'
data = (json.dumps(gate, indent=2, sort_keys=True) + '\n').encode()
with path.open('xb') as stream:
    stream.write(data); stream.flush(); os.fsync(stream.fileno())
fd = os.open(root, os.O_RDONLY)
try:
    os.fsync(fd)
finally:
    os.close(fd)
assert path.read_bytes() == data
print(json.dumps({'gate': str(path), 'identity': identity(path), 'frozen_bindings': checked,
                  'historical_bindings': len(historical), 'prepared_envelopes': 2, 'native_execution': False}))
