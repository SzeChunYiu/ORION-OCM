"""Harmless recorder controls: no cvc5 import and no public task inputs."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import diagnostic_worker as W


class Command:
    def __init__(self, mode, null=False):
        self.mode, self.null = mode, null

    def isNull(self):
        return self.null

    def getCommandName(self):
        return '' if self.null else 'harmless-stub'

    def invoke(self, solver, symbols):
        if self.mode == 'invoke_error':
            raise ValueError('STUB_INVOKE_ERROR')
        if self.mode == 'invoke_timeout':
            time.sleep(10)
        return 'preserved harmless output\n'


class Parser:
    def __init__(self, mode):
        self.mode, self.count = mode, 0

    def nextCommand(self):
        if self.mode == 'parse_error':
            raise ValueError('STUB_PARSE_ERROR')
        self.count += 1
        return Command(self.mode, self.count > 1)

    def getSymbolManager(self):
        return None


class Solver:
    def __init__(self, mode):
        self.mode = mode

    def getStatistics(self):
        return self

    def get(self, *, internal, defaulted):
        assert internal is True and defaulted is True
        if self.mode == 'stats_error':
            raise ValueError('STUB_STATS_ERROR')
        if self.mode == 'stats_timeout':
            time.sleep(10)
        return {'harmless': object() if self.mode == 'serialize_error' else 7}

    def getOption(self, key):
        assert key != 'output', 'pinned native output option is ungettable'
        return 'stub-'+key


def child(mode, events):
    recorder = W.Recorder(events); output = []; error = None
    try:
        W.command_loop(Parser(mode), Solver(mode), recorder, output)
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        recorder.close()
    print(json.dumps({'mode':mode, 'output':output, 'error':error,
                      'cvc5_imported':any(x == 'cvc5' or x.startswith('cvc5.') for x in sys.modules)}))
    return 2 if error else 0


def run(root):
    root = Path(root); root.mkdir()
    source = Path(__file__).resolve()
    capture_path = source.parent.parent/'capture.py'
    spec = importlib.util.spec_from_file_location('existing_capture', capture_path)
    capture = importlib.util.module_from_spec(spec); spec.loader.exec_module(capture)
    cases = ('success','parse_error','invoke_error','invoke_timeout',
             'stats_error','serialize_error','stats_timeout')
    rows = []
    for mode in cases:
        argv = [sys.executable, '-B', str(source), '--child', mode,
                '--events', str(root/mode/'boundaries.jsonl')]
        if mode.endswith('timeout'):
            argv = ['/usr/bin/timeout', '--kill-after=1s', '0.2s']+argv
        result = capture.capture_one(argv, b'{}\n', root/mode, source.parent, 2)
        events = [json.loads(x) for x in (root/mode/'boundaries.jsonl').read_text().splitlines()]
        names = [x['event'] for x in events]
        assert [x['seq'] for x in events] == list(range(len(events)))
        assert len({x['pid'] for x in events}) == 1
        if mode.endswith('timeout'):
            assert result['exit_code'] == 124
            expected = 'invoke_begin' if mode == 'invoke_timeout' else 'statistics_collect_begin'
            assert names[-1] == expected
            assert (root/mode/'stdout').read_bytes() == b''
        else:
            raw = json.loads((root/mode/'stdout').read_text())
            assert raw['cvc5_imported'] is False
            assert result['exit_code'] == (0 if mode == 'success' else 2)
            if mode == 'success':
                assert raw['output'] == ['preserved harmless output\n']
                assert names == ['parse_begin','parse_end','command_metadata_begin',
                    'command_metadata_end','command','invoke_begin','invoke_end',
                    'invoke_output','statistics_collect_begin','statistics_collect_end',
                    'statistics_serialize_begin','statistics_serialize_end','statistics_snapshot',
                    'parse_begin','parse_end','command_metadata_begin','command_metadata_end','command']
            elif mode == 'parse_error':
                assert names == ['parse_begin','parse_error']
            elif mode == 'invoke_error':
                assert names[-2:] == ['invoke_begin','invoke_error']
                assert 'invoke_end' not in names
            else:
                stage = 'statistics_collect' if mode == 'stats_error' else 'statistics_serialize'
                assert names[-2:] == [stage+'_begin', stage+'_error']
                assert 'invoke_end' in names and raw['output'] == ['preserved harmless output\n']
        rows.append({'mode':mode, 'result':result, 'events':len(events), 'last_event':names[-1]})
    receipt = {'scope':'HARmless_STUB_ONLY_NO_NATIVE_OR_PUBLIC_TASK'.upper(),
               'source_sha256':capture.sha(source), 'worker_sha256':capture.sha(source.parent/'diagnostic_worker.py'),
               'cases':rows, 'passed':len(rows), 'native_calls':0}
    capture.write(root/'CONTROL.json', receipt)
    capture.write(root/'seal.json', {str(p.relative_to(root)):{'sha256':capture.sha(p),'bytes':p.stat().st_size}
                                    for p in sorted(root.rglob('*')) if p.is_file()})
    print(json.dumps({'passed':len(rows), 'receipt_sha256':capture.sha(root/'CONTROL.json')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--child'); parser.add_argument('--events'); parser.add_argument('--output')
    args = parser.parse_args()
    if args.child:
        raise SystemExit(child(args.child, args.events))
    run(args.output)
