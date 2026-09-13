"""Full finite DCR payload; the historical record is checked first."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cost_contracts_v1 import ledger, refinement, additive_bounds, python_contract, separation
from historical_replay_v1 import replay_historical
from independent_oracle_v1 import trace_native
from typed_machine_v1 import execute
from typed_program_v1 import Program, Refusal, require
from witnesses_v1 import register, expression_census

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def run_checks():
    original = replay_historical()
    old, programs = register()
    rows, traces, comparisons = {}, {}, 0
    for name, program in list(programs.items()) + list(expression_census()):
        inputs, all_events = [], []
        for x in old.INPUTS:
            actual = execute(program, 'main', x)
            value, native = trace_native(program, 'main', x)
            python = tuple(e for e in actual.events if e.startswith('py:'))
            require(actual.value == value and python == native, 'independent native disagreement: '+name)
            if name in programs: require(value == sum(x) % 2, 'parity witness failed')
            inputs.append({'input': x, 'value': value, 'python_opcodes': len(python),
                           'events': actual.events, 'native_python_events': native})
            all_events.extend(actual.events)
            comparisons += 1
        traces[name] = tuple(all_events)
        rows[name] = {'inputs': inputs, 'event_ledger': ledger(all_events),
                      'events_sha256': digest(all_events),
                      'python_opcodes_per_sweep': sum(e.startswith('py:') for e in all_events)}
    parent_name = 'WRITTEN_SHARED_SUM_NET'
    parent, refines = traces[parent_name], {}
    for name in ('TRANSPARENT_PYTHON_PARENT', 'TRANSPARENT_PARTIAL_PARENT'):
        child = traces[name]
        delta = refinement(parent, child)
        all_contract = python_contract(parent + child)
        require(separation(parent, child, all_contract) == 'CERTIFIED_STRICTLY_LOWER', 'wrapper cost revival failed')
        refines[name] = {'preserves_ordered_parent_events': True, 'residual_events': delta,
                         'source_parent_sha256': hashlib.sha256(old.REGISTERED[parent_name].encode()).hexdigest(),
                         'python_cost': [int(x) for x in additive_bounds(child, all_contract)]}
    partial = traces['TRANSPARENT_PARTIAL_PARENT']
    py_only = {e: (1, 1) for e in parent + partial if e.startswith('py:')}
    native_int_count = {e: ((1, 1) if e.startswith('native:int:') else (0, 0)) for e in parent + partial}
    parent_int = additive_bounds(parent, native_int_count)
    partial_int = additive_bounds(partial, native_int_count)
    require(parent_int == partial_int == (32, 32), 'descendant int obligations were lost')
    unknown_lower, unknown_upper = additive_bounds(partial, py_only)
    require(unknown_upper is None, 'unknown native work got a finite upper bound')
    calls = []
    class Hidden:
        def __getitem__(self, x):
            calls.append(x)
            return old.written_shared_sum_net(x)
    try:
        Program({'main': 'def f(x):\n    return table[x]\n'}, data={'table': Hidden()})
    except Refusal as error:
        reason = str(error)
    else:
        raise Refusal('implicit Python object was admitted')
    require(not calls, 'refusal invoked an unknown method')
    return {'schema': 'GMI_TYPED_DELEGATION_COST_RECEIPT_V1', 'status': 'PASS',
            'scope': 'finite typed bytecode and explicit additive contracts; no physical frontier',
            'historical_full_replay': original, 'independent_execution_comparisons': comparisons,
            'source_cases': len(rows), 'rows': rows, 'wrapper_refinement': refines,
            'native_int_count_contract': {'parent': 32, 'transparent_partial': 32,
                                          'metric': 'defined int invocation count; not internal work'},
            'unknown_native_contract': {'python_lower_bound': int(unknown_lower), 'total_upper_bound': unknown_upper,
                                        'comparison': 'UNVERIFIABLE'},
            'implicit_object_refusal': {'reason': reason, 'method_invocations': len(calls)},
            'stronger_claims_not_established': ['arbitrary Python coverage', 'native internal work',
                'physical cost', 'larger-class minimum or Pareto frontier', 'unconditional refactoring monotonicity']}

if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
