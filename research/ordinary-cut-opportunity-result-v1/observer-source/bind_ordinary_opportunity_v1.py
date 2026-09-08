"""Bind reviewed fixed inputs for one audit; this recorder does not run it."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/home/billy/orion-director-work/20260908')
ROOT = BASE / 'ordinary-cut-opportunity-v1/consumer-v3'
RUN = ROOT / 'prospective-run-01'
OBSERVER = RUN / 'observer-source'


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def descriptor(path):
    return {'path': str(path), **identity(path)}


def read_expected(path, digest):
    assert identity(path)['sha256'] == digest, str(path)
    return json.loads(path.read_bytes())


requirements = read_expected(OBSERVER / 'GATE-REQUIREMENTS.json',
    '36dbf86953b8bba2de5de6da528eb780e7bd177a18c6a85f27626eed944fec46')
reviews = {
    'native_outcome': (BASE / 'ordinary-training-trace-export-v1/ROOT-OUTCOME-QUALIFICATION-01.json',
        '59facbf5bb7a45fd375b2bf473fcedcf136e76196b5fc80b417d7a7041b607d9'),
    'consumer_source': (ROOT / 'independent-source-review-01/REVIEW.json',
        'd06181a462f0085c11dc59cec0bc128f9a3880f1eb92f247698b850beb33e5f0'),
    'observer_source': (RUN / 'independent-observer-review-01/REVIEW.json',
        '77d5b54e4851cf6e7f62b9fff2981b7547eb9d1d78e5d187568ced6199bd105a'),
}
accepted = {key: read_expected(path, digest) for key, (path, digest) in reviews.items()}
assert accepted['consumer_source']['remaining_blockers'] == []
assert accepted['consumer_source']['status'] == 'SOURCE_READY_FOR_SEPARATELY_GATED_REGISTERED_AUDIT'
assert accepted['observer_source']['remaining_blockers'] == []
assert accepted['observer_source']['status'] == 'SOURCE_READY_FOR_SEPARATE_ROOT_GATE'
contract = json.loads((OBSERVER / 'OBSERVER-CONTRACT.json').read_bytes())
assert identity(OBSERVER / 'OBSERVER-CONTRACT.json') == requirements['observer_contract']
assert identity(OBSERVER / 'observe_opportunity.py') == requirements['observer']
assert identity(OBSERVER / 'output_contract.py') == contract['output_contract']
request_path = RUN / 'REQUEST-PROSPECTIVE.json'
assert identity(request_path) == requirements['request']
request = json.loads(request_path.read_bytes())
assert request['sources'] == contract['sources'] and len(request['sources']) == 18
assert request['max_wall_s'] == 60 and request['max_token_states'] == 2000000
for name, expected in request['sources'].items():
    assert identity(ROOT / name) == expected, name
for group in (contract['inputs'], contract['implicit_registry_inputs']):
    for expected in group.values():
        assert identity(Path(expected['path'])) == {k: expected[k] for k in ('bytes', 'sha256')}
assert identity(Path(requirements['runtime']['path'])) == {k: requirements['runtime'][k] for k in ('bytes', 'sha256')}
gate_path = Path(requirements['actual_gate_path'])
for path in (gate_path, Path(requirements['output']), Path(requirements['observation']), RUN / 'caller-01'):
    assert path.name not in {p.name for p in path.parent.iterdir()}, str(path)
gate = {key: requirements[key] for key in (
    'request', 'observer', 'observer_contract', 'runtime', 'argv', 'cwd',
    'output', 'observation', 'max_runs', 'outer_wall_s', 'P1_inventory',
    'qualified_native_trace_authority', 'training_packet')}
gate.update(schema='ordinary.root-opportunity-gate.v1',
    authorization='ROOT_TRAINING_OPPORTUNITY_GATE',
    issued_utc=datetime.now(timezone.utc).isoformat(),
    accepted_reviews={key: descriptor(path) for key, (path, _) in reviews.items()},
    review_bindings={str(path): identity(path) for path in (
        Path(__file__).resolve(), OBSERVER / 'SOURCE-FREEZE.json',
        OBSERVER / 'SOURCE-REVIEW-REQUEST.json', OBSERVER / 'GATE-REQUIREMENTS.json',
        OBSERVER / 'qualification-01/QUALIFICATION.json',
        ROOT / 'SOURCE-REVIEW-REQUEST.json', ROOT / 'QUALIFICATION.json')},
    scope='One registered training-only two-node essential-port opportunity audit. '
          'All 4323 ordinary contracts retained; fixed 128 roots, original order, '
          '2M matcher states and 60-second soft deadline; 180-second outer containment. '
          'No native replay/admission, learner, evaluation, automatic retry or old gate reuse. '
          'Root accepts the exact bound reviews; outcome still requires qualification.')
with gate_path.open('x') as stream:
    json.dump(gate, stream, sort_keys=True, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps({'gate': descriptor(gate_path), 'execution_started': False}))
