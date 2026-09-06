"""Command-boundary localization only; no internal-phase or comparative timing claim."""
import argparse
import importlib.metadata as metadata
import json
import math
import os
from pathlib import Path
import resource
import sys
import time

TAGS = ('options-auto', 'sygus-grammar', 'sygus-enumerator')
OPTION_NAMES = ('sygus', 'incremental', 'tlimit-per', 'check-synth-sol',
                'out', 'sygus-si', 'sygus-grammar-norm')


class Recorder:
    def __init__(self, path):
        self.stream = Path(path).open('x')
        self.sequence = 0

    def emit(self, event, **fields):
        row = {'seq': self.sequence, 'event': event,
               'monotonic_ns': time.monotonic_ns(), 'pid': os.getpid(), **fields}
        text = json.dumps(row, sort_keys=True, allow_nan=False)
        self.stream.write(text+'\n')
        self.stream.flush()
        self.sequence += 1

    def close(self):
        self.stream.close()


def boundary(recorder, stage, operation, **fields):
    recorder.emit(stage+'_begin', **fields)
    try:
        value = operation()
    except Exception as exc:
        recorder.emit(stage+'_error', **fields, error_type=type(exc).__name__,
                      error_message=str(exc))
        raise
    recorder.emit(stage+'_end', **fields)
    return value


def encode_statistics(snapshot):
    """Lossless JSON tags for nonfinite native values; finite values stay unchanged."""
    def visit(value):
        if isinstance(value, float) and not math.isfinite(value):
            return {'$cvc5_float': 'NaN' if math.isnan(value) else ('+Inf' if value > 0 else '-Inf')}
        if isinstance(value, dict):
            if '$cvc5_float' in value:
                raise ValueError('reserved nonfinite tag already present in native statistics')
            return {key: visit(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [visit(item) for item in value]
        return value
    return visit(snapshot)


def statistics(solver, recorder, location, index, command):
    fields = {'location': location, 'index': index, 'command': command}
    snapshot = boundary(recorder, 'statistics_collect', lambda: {
        'statistics': solver.getStatistics().get(internal=True, defaulted=True),
        'effective_options': {key: solver.getOption(key) for key in OPTION_NAMES},
        'output_tag_getter': 'UNAVAILABLE: pinned getOption(output) is ungettable; requested tags and successful setters are recorded separately.'},
        **fields)
    # Serialization has its own flushed begin/error/end: it is not solver work.
    encoded = boundary(recorder, 'statistics_serialize',
                       lambda: json.dumps(encode_statistics(snapshot), sort_keys=True, allow_nan=False),
                       **fields)
    recorder.emit('statistics_snapshot', **fields, snapshot=json.loads(encoded))


def command_loop(parser, solver, recorder, output):
    index = 0
    while True:
        command = boundary(recorder, 'parse', parser.nextCommand, index=index)
        is_null, name = boundary(recorder, 'command_metadata',
                                lambda: (True, '') if command.isNull() else (False, command.getCommandName()),
                                index=index)
        recorder.emit('command', index=index, command=name, is_null=is_null)
        if is_null:
            break
        if name == 'check-synth':
            statistics(solver, recorder, 'before_invoke', index, name)
        text = boundary(recorder, 'invoke',
                        lambda: command.invoke(solver, parser.getSymbolManager()),
                        index=index, command=name)
        # Preserve a completed returned candidate before statistics can fail.
        recorder.emit('invoke_output', index=index, command=name, text=text)
        if text.strip():
            output.append(text)
        statistics(solver, recorder, 'after_invoke', index, name)
        index += 1


def native(request, recorder, output):
    import cvc5
    if metadata.version('cvc5') != '1.3.4':
        raise ValueError('cvc5 version mismatch')
    if request['action'] != 'synthesize':
        raise ValueError('only the frozen synthesize request shape is supported')
    solver = boundary(recorder, 'solver_create', cvc5.Solver)
    options = [('sygus', 'true'), ('incremental', 'false'),
               ('tlimit-per', str(request['timeout_ms'])), ('check-synth-sol', 'true'),
               ('out', 'stderr')] + [('output', tag) for tag in TAGS]
    recorder.emit('requested_options', api_options=options,
                  input_options='Preserved verbatim; each command is independently marked.')
    for key, value in options:
        boundary(recorder, 'option', lambda: solver.setOption(key, value),
                 key=key, value=value)
    parser = boundary(recorder, 'parser_create', lambda: cvc5.InputParser(solver))
    boundary(recorder, 'input_setup', lambda: parser.setStringInput(
        cvc5.InputLanguage.SYGUS_2_1, request['payload']['sygus'], 'bound-public-clia'))
    command_loop(parser, solver, recorder, output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--events', required=True)
    args = parser.parse_args()
    start = time.perf_counter(); cpu = time.process_time(); output = []
    recorder = Recorder(args.events)
    try:
        request = json.load(sys.stdin)
        native(request, recorder, output)
        candidate = '\n'.join(output)
        solution = candidate.lstrip().startswith('(') and 'define-fun' in candidate
        result = {'status': 'SOLUTION' if solution else 'CANNOT_CHECK',
                  'candidate': candidate if solution else '',
                  'solver_result': 'solution' if solution else candidate.strip(),
                  'reason': '' if solution else 'native returned no candidate; not a no-program proof'}
    except Exception as exc:
        result = {'status': 'CANNOT_CHECK', 'reason': f'{type(exc).__name__}: {exc}'}
    finally:
        recorder.close()
    result.update({'returned_command_outputs': output, 'solver': 'cvc5 1.3.4',
                   'scope': 'Public API boundary diagnostic; semantic output NOT_GRADED.',
                   'metrics': {'worker_wall_s': time.perf_counter()-start,
                               'worker_cpu_s': time.process_time()-cpu,
                               'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               'worker_pid': os.getpid()}})
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
