"""Measured coordinate report; never infer physical work from interpreter steps."""
from __future__ import annotations
import argparse
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import continue_lineage as C


def analyze(root, predecessor):
    result = E.read(root / 'RESULT.json')
    old = E.read(predecessor / 'RESULT.json')
    reports = {m: E.read(root / (m + '.json')) for m in C.MODES}
    launches = {m: E.read(root / ('LAUNCH-' + m + '.json')) for m in C.MODES}
    raw = {}
    for mode, report in reports.items():
        launch = launches[mode]
        raw[mode] = {'interpreter_steps': result['totals'][mode].get('interpreter_steps', 0),
                     'dictionary_lookups': result['totals'][mode].get('lookups', 0),
                     'trie_edge_lookups': result['totals'][mode].get('edge_lookups', 0),
                     'trie_terminal_lookups': result['totals'][mode].get('terminal_lookups', 0),
                     'whole_process_wall_seconds': launch['wall_seconds'],
                     'whole_process_user_cpu_seconds': launch['user_cpu_seconds'],
                     'whole_process_system_cpu_seconds': launch['system_cpu_seconds'],
                     'solve_wall_seconds_nested_in_whole_process': sum(r['wall_seconds'] for r in report['rows']),
                     'index_build_wall_seconds_nested_in_whole_process': report['build_wall_seconds'],
                     'load_wall_seconds_nested_in_whole_process': report['load_wall_seconds'],
                     'linux_process_peak_rss_kib_not_additive': report['peak_rss_kib']}
    p, t = raw['ordinary-point'], raw['ordinary-prefix']
    saved = p['interpreter_steps'] - t['interpreter_steps']
    extra = t['trie_edge_lookups'] + t['trie_terminal_lookups'] - p['dictionary_lookups']
    return {'terminal': 'PHYSICAL_PAYBACK_NOT_ESTABLISHED', 'raw': raw,
            'exact_coordinate_boundary': {
                'saved_interpreter_steps': saved, 'additional_equal_unit_lookups': extra,
                'inequality': 'saved_steps*w_instruction > extra_lookup_work + extra_build_selection_lifecycle_cost',
                'separate_price_inequality': '130377*w_instruction + 63924*w_dictionary > 236713*w_edge + 241253*w_terminal + C_extra',
                'equal_lookup_price_threshold_excluding_extra_cost': str(Fraction(extra, saved)),
                'scope': 'conditional symbolic prices; not CPU instructions, wall time, energy or a measured physical conversion'},
            'measured_fixed_costs_separate_from_use': {
                'predecessor_acquisition_wall_seconds': old['acquisition_wall_seconds'],
                'predecessor_memory_admission_wall_seconds': old['admission_wall_seconds'],
                'new_selection_wall_seconds': result['selection_wall_seconds'],
                'new_representation_admission_wall_seconds': result['representation_admission_wall_seconds'],
                'observer_refutation_wall_seconds': E.read(root / 'REPRESENTATION-WITNESS.json')['construction_wall_seconds'],
                'revisions': result['revisions']},
            'no_double_counting': 'Nested solve/load/build timers must not be added to whole-process times. Controller time also contains comparison work. RSS is a maximum, not a sum.',
            'exact_policy_disposition': 'P2 weakly dominates P1 and P0 in interpreter-step count for every legal point call; strict choice at this coordinate requires no learned router. Full-cost choice remains price/environment/lifetime dependent.',
            'all_acquisition_and_research_costs_measured': False,
            'strongest_library_learning_parents_executed_in_this_continuation': False,
            'architecture_specific_physical_advantage': False,
            'energy': 'NOT_MEASURED', 'active_k_over_N': 'NOT_MEASURED',
            'physical_order_design': 'single fixed-order observations; descriptive, not randomized performance inference'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--predecessor', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    a = parser.parse_args()
    result = analyze(a.root.resolve(), a.predecessor.resolve())
    E.write(a.report, result)
    print(E.encoded(result).decode())
