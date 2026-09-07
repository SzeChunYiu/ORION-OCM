"""Reproduce both independently authored finite checks and compare exact outputs."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'


def main():
    RESULTS.mkdir(exist_ok=True)
    for kind in ('primary', 'independent'):
        subprocess.run([sys.executable, str(ROOT / f'checker_{kind}.py'), '--output',
                        str(RESULTS / f'{kind}.json')], check=True)
    a = json.loads((RESULTS / 'primary.json').read_text())
    b = json.loads((RESULTS / 'independent.json').read_text())
    checks = []

    def equal(name, x, y):
        checks.append({'name': name, 'equal': x == y})
        if x != y:
            checks[-1].update(primary=x, independent=y)

    for which in ('full', 'restricted'):
        p, q = a['cycle'][which], b['w1'][which + '_pool']
        equal(which + ':rank', p['rank'], q['rank'])
        equal(which + ':inclusion-minimal', p['inclusion_minimal'], q['inclusion_minimal_bases'])
        for row in p['budget_rows']:
            k = str(row['budget'])
            equal(which + ':budget:' + k, row['minimum'], q['minimum_cardinality_by_budget'][k])
            equal(which + ':all-minimizers:' + k, row['minimizers'], q['minimum_bases_by_budget'][k])
        primary_subsets = {tuple(r['basis']): r for r in a['cycle']['all_subsets']}
        for row in q['subsets']:
            p_row = primary_subsets[tuple(row['basis'])]
            equal(which + ':all-target-lengths:' + str(row['basis']), p_row['lengths'], row['lengths'])
            equal(which + ':closure-size:' + str(row['basis']), p_row['closure_size'], row['closure_size'])
    equal('expanded-macro-costs', a['cycle']['expanded_macro_lengths'], b['w1']['weighted_macro_lengths'])
    for row in a['cycle']['z5_compilation']:
        key = ','.join(map(str, row['pair']))
        equal('z5:' + key, row['mutual_max'], b['w1']['z5_mutual_distances'][key])
        equal('z5-directed:' + key, [row['a_to_b'], row['b_to_a']],
              [b['w1']['z5_directed_lengths'][key]['a_compiled_over_b'],
               b['w1']['z5_directed_lengths'][key]['b_compiled_over_a']])
    equal('flip-closure', a['cycle']['flip_closure'], b['w1']['flip']['closure'])
    equal('flip-orbit', a['cycle']['zero_orbit'], b['w1']['flip']['initial_zero_orbit'])
    equal('support-current-classes', len(a['support']['answer_partition']), b['w2']['current_output_class_count'])
    equal('support-future-classes', len(a['support']['lifecycle_partition']), b['w2']['future_signature_class_count'])
    equal('support-monoid', a['support']['closure'], b['w2']['deletion_monoid'])
    equal('support-rank', a['support']['rank'], b['w2']['deletion_monoid_rank'])
    equal('support-all-16-errors', [r['errors'] for r in a['support']['answer_only_machines']],
          [r['errors'] for r in b['w2']['answer_only_machines']])
    equal('support-min-errors', a['support']['minimum_answer_only_errors'], b['w2']['answer_only_minimum_errors'])
    for row in a['diagnosis']:
        mode = 'informative' if row['informative_audit'] else 'constant'
        key = str(row['budget'])
        other = b['w3'][mode]['by_budget'][key]
        equal('diagnosis-forced:' + mode + ':' + key, float(Fraction(row['forced_accuracy'])), other['forced_accuracy'])
        equal('diagnosis-sound:' + mode + ':' + key, float(Fraction(row['sound_coverage'])), other['sound_committed_coverage'])
        vectors = sorted(set(tuple(-1 if o == 'abstain' else o for o in r['outputs']) for r in row['policies']))
        node = next(n for n in b['w3'][mode]['belief_nodes']
                    if n['belief'] == [0, 1] and n['remaining_budget'] == row['budget'])
        equal('diagnosis-all-outcomes:' + mode + ':' + key, [list(v) for v in vectors], node['attainable_outcome_vectors'])

    # Re-evaluate every emitted compilation witness directly from serialized maps.
    maps = a['cycle']['generator_maps']
    for row in a['cycle']['all_subsets']:
        for target, word in enumerate(row['words']):
            if word is None:
                continue
            endpoint = list(range(6))
            for name in word:
                endpoint = [maps[str(name)][s] for s in endpoint]
            equal('witness:' + str(row['basis']) + ':' + str(target), endpoint,
                  [(s + target) % 6 for s in range(6)])

    tracked = ['EXACT_MODELS_V1.md', 'checker_primary.py', 'checker_independent.py', 'reproduce.py',
               'results/primary.json', 'results/independent.json']
    manifest = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in tracked}
    report = {'evidence_class': 'E2', 'claim_ceiling': 'L0_EXACT_APPARATUS_PARENT_OWNED',
              'external_replication': False, 'protected_study_executed': False,
              'all_equal': all(c['equal'] for c in checks), 'comparison_count': len(checks),
              'checks': checks, 'sha256': manifest,
              'environment': {'python': sys.version, 'platform': platform.platform()},
              'specification_freeze_commit': 'b404904',
              'limitation': 'Internal authors, common specification and host; not E3/E5 or general cognition.'}
    (RESULTS / 'verification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: report[k] for k in ('all_equal', 'comparison_count', 'evidence_class')}))
    if not report['all_equal']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
