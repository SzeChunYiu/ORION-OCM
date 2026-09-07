"""E2 exact calibration. Standard library only; no OCM runtime imports."""
from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
from heapq import heappop, heappush
from itertools import combinations, product
import json
from pathlib import Path


def compose(first, second):
    return tuple(second[first[x]] for x in range(len(first)))


def shortest_maps(n, generators, weights=None):
    identity = tuple(range(n))
    distance, witness = {identity: 0}, {identity: []}
    pending = [(0, identity)]
    weights = weights or {name: 1 for name in generators}
    while pending:
        cost, current = heappop(pending)
        if distance[current] != cost:
            continue
        for name, op in sorted(generators.items()):
            nxt = compose(current, op)
            candidate = cost + weights[name]
            if candidate < distance.get(nxt, float('inf')):
                distance[nxt] = candidate
                witness[nxt] = witness[current] + [name]
                heappush(pending, (candidate, nxt))
    return distance, witness


def subsets(pool):
    return [s for k in range(len(pool) + 1) for s in combinations(pool, k)]


def rotations(n):
    return {a: tuple((x + a) % n for x in range(n)) for a in range(n)}


def cycle():
    maps = rotations(6)
    rows = []
    for basis in subsets(tuple(range(1, 6))):
        distances, words = shortest_maps(6, {a: maps[a] for a in basis})
        rows.append({'basis': list(basis), 'lengths': [distances.get(maps[a]) for a in range(6)],
                     'words': [words.get(maps[a]) for a in range(6)], 'closure_size': len(distances)})

    def pool_summary(pool):
        eligible = [r for r in rows if set(r['basis']) <= set(pool)]
        generating = [r for r in eligible if r['closure_size'] == 6]
        minimal = [r['basis'] for r in generating if not any(
            set(q['basis']) < set(r['basis']) for q in generating)]
        budget_rows = []
        for budget in range(6):
            covers = [r['basis'] for r in generating if max(r['lengths']) <= budget]
            size = min(map(len, covers), default=None)
            budget_rows.append({'budget': budget, 'minimum': size,
                                'minimizers': [b for b in covers if len(b) == size]})
        return {'rank': min(len(r['basis']) for r in generating),
                'inclusion_minimal': minimal, 'budget_rows': budget_rows}

    distances, _ = shortest_maps(6, {a: maps[a] for a in (1, 2, 3)}, {1: 1, 2: 2, 3: 3})
    five = rotations(5)
    compilation = []
    for a, b in ((1, 2), (2, 4), (1, 4)):
        da, _ = shortest_maps(5, {a: five[a]})
        db, _ = shortest_maps(5, {b: five[b]})
        compilation.append({'pair': [a, b], 'a_to_b': db[five[a]],
                            'b_to_a': da[five[b]], 'mutual_max': max(db[five[a]], da[five[b]])})
    flip, _ = shortest_maps(2, {'flip': (1, 0)})
    return {'state_set': list(range(6)), 'generator_maps': maps, 'all_subsets': rows,
            'full': pool_summary((1, 2, 3, 4, 5)), 'restricted': pool_summary((1, 2, 3)),
            'expanded_macro_lengths': [distances[maps[a]] for a in range(6)],
            'z5_compilation': compilation, 'flip_closure': [list(t) for t in sorted(flip)],
            'constant_zero_in_flip_closure': (0, 0) in flip,
            'zero_orbit': sorted({t[0] for t in flip})}


def refine_partition(states, labels, actions):
    part = {s: int(labels[s]) for s in states}
    while True:
        ids, nxt = {}, {}
        for s in states:
            signature = (labels[s], tuple(part[op[s]] for op in actions.values()))
            if signature not in ids:
                ids[signature] = len(ids)
            nxt[s] = ids[signature]
        if all((part[a] == part[b]) == (nxt[a] == nxt[b]) for a in states for b in states):
            return [[s for s in states if nxt[s] == k] for k in sorted(set(nxt.values()))]
        part = nxt


def support():
    states = list(range(4))
    labels = {s: bool(s) for s in states}
    actions = {'ra': tuple(s & ~1 for s in states), 'rb': tuple(s & ~2 for s in states)}
    closure, _ = shortest_maps(4, actions)
    nonidentity = {str(i): t for i, t in enumerate(sorted(closure)) if t != tuple(states)}
    generators = [list(b) for b in subsets(tuple(nonidentity))
                  if set(shortest_maps(4, {k: nonidentity[k] for k in b})[0]) == set(closure)]
    errors = []
    for table in product((0, 1), repeat=4):
        wrong = sum(table[2 * int(labels[s]) + a] != int(labels[op[s]])
                    for s in states for a, op in enumerate(actions.values()))
        errors.append({'table': list(table), 'errors': wrong})
    return {'states': states, 'actions': actions,
            'transitions': [{'state': s, 'action': name, 'next': op[s], 'next_label': labels[op[s]]}
                            for s in states for name, op in actions.items()],
            'answer_partition': [[0], [1, 2, 3]],
            'lifecycle_partition': refine_partition(states, labels, actions),
            'query_only_partition': refine_partition(states, labels, {}),
            'closure': [list(t) for t in sorted(closure)],
            'rank': min(map(len, generators)),
            'answer_only_machines': errors,
            'minimum_answer_only_errors': min(r['errors'] for r in errors),
            'all_transition_count': 8,
            'alternate_support_after_ra_ab': bool(actions['ra'][3])}


def policies(budget, informative):
    result = [('stop', 0), ('stop', 1), ('stop', 'abstain')]
    if budget >= 1:
        result += [('retry', {'FAIL': p}) for p in policies(budget - 1, informative)]
    if budget >= 2:
        observations = ('0', '1') if informative else ('SAME',)
        children = policies(budget - 2, informative)
        result += [('audit', dict(zip(observations, ps))) for ps in product(children, repeat=len(observations))]
    return result


def execute_policy(policy, hidden, informative):
    action, value = policy
    if action == 'stop':
        return value
    obs = 'FAIL' if action == 'retry' else str(hidden) if informative else 'SAME'
    return execute_policy(value[obs], hidden, informative)


def information_graph(budget, informative):
    start = ((0, 1), budget)
    seen, queue, edges = {start}, deque([start]), []
    while queue:
        belief, remaining = queue.popleft()
        for action, cost in (('retry', 1), ('audit', 2)):
            if cost > remaining:
                continue
            outcomes = {}
            for h in belief:
                obs = 'FAIL' if action == 'retry' else str(h) if informative else 'SAME'
                outcomes.setdefault(obs, []).append(h)
            for obs, hs in sorted(outcomes.items()):
                nxt = (tuple(hs), remaining - cost)
                edges.append({'from': [list(belief), remaining], 'action': action,
                              'observation': obs, 'to': [list(nxt[0]), nxt[1]]})
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return {'nodes': [[list(b), r] for b, r in sorted(seen)], 'edges': edges}


def diagnosis():
    rows = []
    for informative in (False, True):
        for budget in range(3):
            evaluated = []
            for p in policies(budget, informative):
                outputs = [execute_policy(p, h, informative) for h in (0, 1)]
                evaluated.append({'policy': p, 'outputs': outputs,
                                  'correct': sum(o == h for h, o in enumerate(outputs)),
                                  'wrong': sum(o != h and o != 'abstain' for h, o in enumerate(outputs)),
                                  'committed': sum(o != 'abstain' for o in outputs)})
            forced = [r for r in evaluated if r['committed'] == 2]
            sound = [r for r in evaluated if r['wrong'] == 0]
            accuracy = max(r['correct'] for r in forced)
            coverage = max(r['committed'] for r in sound)
            rows.append({'informative_audit': informative, 'budget': budget,
                         'policy_count': len(evaluated), 'forced_accuracy': str(Fraction(accuracy, 2)),
                         'sound_coverage': str(Fraction(coverage, 2)),
                         'best_forced_policy': next(r['policy'] for r in forced if r['correct'] == accuracy),
                         'best_sound_policy': next(r['policy'] for r in sound if r['committed'] == coverage),
                         'information_graph': information_graph(budget, informative), 'policies': evaluated})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'checker': 'primary_v1', 'evidence_class': 'E2', 'cycle': cycle(),
              'support': support(), 'diagnosis': diagnosis()}
    serialized = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    else:
        print(serialized, end='')


if __name__ == '__main__':
    main()
