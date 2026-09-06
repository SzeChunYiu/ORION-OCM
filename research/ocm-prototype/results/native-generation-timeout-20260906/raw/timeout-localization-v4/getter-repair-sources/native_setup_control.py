"""Native API compatibility: exactly three setup commands, no synthesis declaration."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('existing_capture', ROOT.parent/'capture.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)


def run(output):
    setup = json.loads((ROOT.parent/'successor-v2/quoted-setup.json').read_text())
    commands = ['(set-logic LIA)', '(set-option :output sygus-sol-gterm)',
                '(set-option :out "stderr")']
    assert setup['commands'] == commands
    request = {'action':'synthesize', 'payload':{'sygus':'\n'.join(commands)+'\n'},
               'timeout_ms':5000}
    target = Path(output)
    argv = ['/usr/bin/timeout','--kill-after=2s','20s','/usr/bin/taskset','-c','0',
            '/usr/bin/prlimit','--as=4294967296',sys.executable,'-B',
            str(ROOT/'diagnostic_worker.py'),'--events',str(target/'boundaries.jsonl')]
    result = C.capture_one(argv, (json.dumps(request)+'\n').encode(), target, ROOT, 24)
    events = [json.loads(x) for x in (target/'boundaries.jsonl').read_text().splitlines()]
    invoked = [e['command'] for e in events if e['event'] == 'invoke_begin']
    completed = [e['command'] for e in events if e['event'] == 'invoke_end']
    raw = json.loads((target/'stdout').read_text())
    receipt = {'role':'NATIVE_SETUP_ONLY_NO_SYNTHESIS', 'commands':commands,
               'invoked':invoked, 'completed':completed, 'raw':raw,
               'worker_sha256':C.sha(ROOT/'diagnostic_worker.py'),
               'control_sha256':C.sha(__file__), 'process':result}
    C.write(target/'SETUP.json', receipt)
    C.write(target/'seal.json', {str(p.relative_to(target)):{'sha256':C.sha(p),'bytes':p.stat().st_size}
                               for p in sorted(target.rglob('*')) if p.is_file()})
    # Raw is sealed before any assertion, including an API/serialization failure.
    assert result['exit_code'] == 0
    assert invoked == completed == ['set-logic','set-option','set-option']
    assert not any(e['event'].endswith('_error') for e in events)
    assert events[-1]['event'] == 'command' and events[-1]['is_null'] is True
    assert raw['status'] == 'CANNOT_CHECK' and raw['returned_command_outputs'] == []
    assert raw['reason'] == 'native returned no candidate; not a no-program proof'
    snapshots = [e['snapshot'] for e in events if e['event'] == 'statistics_snapshot']
    assert len(snapshots) == 3 and all(s['statistics'] for s in snapshots)
    final = snapshots[-1]['effective_options']
    assert 'output' not in final and snapshots[-1]['output_tag_getter'].startswith('UNAVAILABLE:')
    tags = [e['value'] for e in events if e['event'] == 'option_end' and e['key'] == 'output']
    assert tags == ['options-auto','sygus-grammar','sygus-enumerator']
    assert final['out'] == 'stderr' and final['tlimit-per'] == '5000'
    print(json.dumps({'status':'SETUP_API_PASS','completed_setup_commands':3,
                      'synth_fun':0,'constraints':0,'check_synth':0,
                      'effective_options':final,'statistics_entries':[len(s['statistics']) for s in snapshots],
                      'receipt_sha256':C.sha(target/'SETUP.json')}))


if __name__ == '__main__':
    run(sys.argv[1])
