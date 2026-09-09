"""Bind one screening attempt after root acceptance of the exact supplied reviews."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

BASE = Path('/home/billy/orion-director-work/20260908')
ROOT = BASE / 'ordinary-cut-screening-successor-v1'
OBS = ROOT / 'observer-source'
SOURCE_REVIEW = ROOT / 'independent-source-review-01/REVIEW.json'
SOURCE_REVIEW_SHA = '350365177de3dbce0f1f6816abca42df3e250341a7609ed41d16fb73f8320936'
REQUEST_SHA = 'fd9af79a0e66fec0aac44e167c94bb23df87b6e3c64df6177df1e8d186e6fd83'
CALLER_SHA = '7a3ab0a81785ab99e9ed073f1c233a0b8a57e9a4b87e73459811789b6d3222ed'


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def descriptor(path):
    return {'path': str(path), **identity(path)}


def read_expected(path, sha):
    assert identity(path)['sha256'] == sha, str(path)
    return json.loads(path.read_bytes())


def main():
    review_path, review_sha, observer_sha, contract_sha = sys.argv[1:]
    review_path = Path(review_path).resolve(strict=True)
    read_expected(review_path, review_sha)  # Root accepts this exact document before invocation.
    source_review = read_expected(SOURCE_REVIEW, SOURCE_REVIEW_SHA)
    assert source_review['remaining_source_blockers'] == []
    assert source_review['status'] == 'SOURCE_READY_FOR_SEPARATE_OBSERVER_REVIEW_AND_ROOT_GATE'
    contract = read_expected(OBS / 'OBSERVER-CONTRACT.json', contract_sha)
    request_path = OBS / 'EXECUTION-REQUEST-DRAFT.json'
    request = read_expected(request_path, REQUEST_SHA)
    observer = OBS / 'observe_screening.py'
    assert identity(observer)['sha256'] == observer_sha
    caller = BASE / 'capture_screening_caller.py'
    assert identity(caller)['sha256'] == CALLER_SHA
    assert request['schema'] == 'ordinary.retained-screening-request.v1'
    assert contract['request'] == descriptor(request_path)
    assert request['source_review'] == descriptor(SOURCE_REVIEW)
    assert request['inputs'] == contract['inputs']
    assert request['runtime'] == contract['lark_runtime']
    assert request['sources'] == contract['sources'] and len(request['sources']) == 10
    assert (request['P1_count'], request['proposal_occurrences'], request['max_token_states'],
            request['max_wall_s'], request['syntax_token_limit'], request['syntax_proof_limit'],
            request['outer_containment_s']) == (4323, 76, 2000000, 60, 512, 4096, 180)
    assert identity(OBS / 'output_contract.py') == contract['output_contract']
    for name, pin in request['sources'].items():
        assert identity(ROOT / name) == pin, name
    for pin in request['inputs'].values():
        assert identity(Path(pin['path'])) == {k: pin[k] for k in ('bytes', 'sha256')}
    for name, pin in request['runtime']['files'].items():
        assert identity(Path(request['runtime']['path']) / name) == pin, name
    for pin in (request['runtime']['manifest'], request['runtime']['wheel'], contract['python'], contract['source_freeze']):
        assert identity(Path(pin['path'])) == {k: pin[k] for k in ('bytes', 'sha256')}
    gate_path = OBS / 'ROOT-SCREENING-GATE.json'
    output, observation = OBS / 'screening-01', OBS / 'observation-01'
    assert request['gate_path'] == str(gate_path)
    assert contract['paths'] == dict(gate=str(gate_path), output=str(output), observation=str(observation), root=str(ROOT))
    for path in (gate_path, output, observation, OBS / 'caller-01'):
        assert not path.exists() and path.name not in {p.name for p in path.parent.iterdir()}, str(path)
    argv = [contract['python']['path'], '-I', '-S', '-B', str(ROOT / 'run_screening.py'), str(request_path), str(output)]
    assert request['entry_argv'] == argv
    bindings = [Path(__file__).resolve(), caller, ROOT / 'SOURCE-FREEZE.json',
                ROOT / 'SOURCE-REVIEW-REQUEST.json', ROOT / 'QUALIFICATION.json',
                OBS / 'SOURCE-FREEZE.json', OBS / 'SOURCE-REVIEW-REQUEST.json']
    gate = dict(schema='ordinary.root-retained-screening-gate.v1', authorization='ROOT_RETAINED_SCREENING_GATE',
                issued_utc=datetime.now(timezone.utc).isoformat(), request=identity(request_path),
                observer=identity(observer), observer_contract=identity(OBS / 'OBSERVER-CONTRACT.json'),
                runtime=contract['python'], argv=argv, cwd=str(ROOT), output=str(output),
                observation=str(observation), max_runs=1, outer_wall_s=180, inputs=request['inputs'],
                accepted_reviews=dict(screening_source=descriptor(SOURCE_REVIEW), observer_source=descriptor(review_path)),
                review_bindings={str(p): identity(p) for p in bindings},
                scope='One screening-only attempt over all76 saved ordered occurrences and full4323 P1. '
                      'Original2M matcher states/60-second soft window, explicit512-token/4096-label syntax domain, '
                      '180-second outer containment. Prior costs/refusals retained. No native/export/extraction '
                      'replay, learner, evaluation, automatic retry or prior gate reuse. Outcome remains unqualified.')
    with gate_path.open('x') as stream:
        json.dump(gate, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'gate': descriptor(gate_path), 'execution_started': False}))


if __name__ == '__main__':
    main()
