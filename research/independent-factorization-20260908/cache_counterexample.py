#!/usr/bin/env python3
"""Run the retained RED against an explicitly supplied PR150 source file.

Usage: python cache_counterexample.py --source /path/to/synthetic_evolvability.py
Expected source head: bb70e79050dea04bd0bff8f228fda1dc72dcd09f.
This is an authored finite counterexample, not a rerun of the published NK sweep.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


class Land:
    n = 2
    def __init__(self):
        self.calls = 0
    def comp(self, x, i):
        self.calls += 1
        a, b = x & 1, (x >> 1) & 1
        return .30*a + .35*b if i == 0 else 1.0-a*b
    def components(self, x):
        return [self.comp(x, i) for i in range(self.n)]


class FixedStart:
    def randrange(self, n):
        return 0


def run(module, land, edges):
    state = {}
    def trace(frame, event, arg):
        if frame.f_code is module.local_search.__code__ and event == 'return':
            state['x'] = frame.f_locals['x']
        return trace
    prior, before = sys.gettrace(), land.calls
    try:
        sys.settrace(trace)
        reported, charged = module.local_search(land, FixedStart(), edges)
    finally:
        sys.settrace(prior)
    calls = land.calls-before
    if 'x' not in state:
        raise RuntimeError('Source local_search return-state could not be observed')
    actual = sum(land.components(state['x']))/land.n
    return {'x': state['x'], 'reported': reported, 'actual': actual,
            'search_component_calls': calls, 'extra_check_component_calls': land.n,
            'source_full_equivalent_cost': charged}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    if not source.is_file():
        parser.error('Supply the actual PR150 Python source file; no download is performed')
    spec = importlib.util.spec_from_file_location('pr150_under_test', source)
    if spec is None or spec.loader is None:
        raise RuntimeError('Could not load supplied source')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ('discover_factorization', 'local_search'):
        if not callable(getattr(module, name, None)):
            raise RuntimeError('Supplied source lacks '+name)
    land = Land()
    edges, discovery_cost = module.discover_factorization(land, FixedStart())
    result = {'evidence': 'E2_AUTHORED_SOURCE_COUNTEREXAMPLE',
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'inferred_edges': edges, 'discovery_component_calls': land.calls,
              'source_discovery_full_equivalents': discovery_cost,
              'incomplete': run(module, land, edges),
              'complete': run(module, land, [[0, 1], [0, 1]]),
              'true_optimum': max(sum(land.components(x))/2 for x in range(4)),
              'claim_ceiling': 'General cache soundness only; original random NK numbers not audited'}
    result['counterexample_reproduced'] = abs(result['incomplete']['reported']-result['incomplete']['actual']) > 1e-10
    result['complete_edge_ablation_sound'] = abs(result['complete']['reported']-result['complete']['actual']) <= 1e-10
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
