"""Trusted native adapters. Requests are created by host code, never direct proposals."""
import importlib.metadata as metadata
import json
import os
import resource
import sys
import time


def synthesize(payload, timeout_ms):
    import cvc5
    if metadata.version('cvc5') != '1.3.4':
        return {'status': 'CANNOT_CHECK', 'reason': 'cvc5 version mismatch'}
    solver = cvc5.Solver()
    for key, value in [('sygus', 'true'), ('incremental', 'false'),
                       ('tlimit-per', str(timeout_ms)), ('check-synth-sol', 'true')]:
        solver.setOption(key, value)
    parser = cvc5.InputParser(solver)
    parser.setStringInput(cvc5.InputLanguage.SYGUS_2_1, payload['sygus'], 'bound-public-clia')
    output = []
    while True:
        command = parser.nextCommand()
        if command.isNull():
            break
        text = command.invoke(solver, parser.getSymbolManager())
        if text.strip():
            output.append(text)
    candidate = '\n'.join(output)
    counters = {str(k): v for k, v in solver.getStatistics() if str(k) in
                ('resource::resourceUnitsUsed', 'global::totalTime')}
    status = 'SOLUTION' if candidate.lstrip().startswith('(') and 'define-fun' in candidate else 'CANNOT_CHECK'
    return {'status': status, 'candidate': candidate if status == 'SOLUTION' else '',
            'solver_result': 'solution' if status == 'SOLUTION' else candidate.strip(),
            'reason': '' if status == 'SOLUTION' else 'native solver returned no candidate; not a no-program proof',
            'solver': 'cvc5 1.3.4', 'logical_counters_not_physical_cost': counters}


def verify(payload, timeout_ms):
    import z3
    if metadata.version('z3-solver') != '5.1.0.0':
        return {'status': 'CANNOT_CHECK', 'reason': 'Z3 version mismatch'}
    solver = z3.Solver(); solver.set(timeout=timeout_ms)
    solver.add(z3.parse_smt2_string(payload['smt2']))
    answer = solver.check()
    result = {'status': 'PASS' if answer == z3.unsat else 'FAIL' if answer == z3.sat else 'CANNOT_CHECK',
              'solver_result': str(answer), 'solver': 'Z3 5.1.0.0'}
    if answer == z3.sat:
        result['counterexample'] = str(solver.model())
    elif answer == z3.unknown:
        result['reason'] = solver.reason_unknown()
    return result


def main():
    start = time.perf_counter(); cpu = time.process_time()
    try:
        request = json.load(sys.stdin)
        actions = {'synthesize': synthesize, 'verify': verify}
        result = actions[request['action']](request['payload'], request['timeout_ms'])
    except Exception as exc:
        result = {'status': 'CANNOT_CHECK', 'reason': f'{type(exc).__name__}: {exc}'}
    result['metrics'] = {'worker_wall_s': time.perf_counter() - start,
                         'worker_cpu_s': time.process_time() - cpu,
                         'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         'worker_pid': os.getpid()}
    print(json.dumps(result))

if __name__ == '__main__':
    main()
