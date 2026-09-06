"""Public, source-bound task contracts; explicit same grammar for every arm."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from sexpdata import Symbol as S
from clia_grammar import GRAMMAR, dump, forms

FIXTURES = Path(__file__).with_name('clia_fixtures')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def signatures(task):
    return {str(x[1]): {'parameters': x[2], 'sort': str(x[3])}
            for x in forms(task['original_sygus']) if str(x[0]) == 'synth-fun'}


def _explicit_grammar(parameters):
    i, b, k = S('OCM_I'), S('OCM_B'), S('OCM_K')
    expressions = [p[0] for p in parameters] + [k, [S('+'), i, i], [S('-'), i, i],
        [S('-'), i], [S('*'), k, i], [S('*'), i, k], [S('ite'), b, i, i]]
    bools = [S('true'), S('false'), [S('and'), b, b], [S('or'), b, b], [S('not'), b], [S('=>'), b, b]]
    bools += [[S(op), i, i] for op in ('=', '<', '<=', '>', '>=')]
    return [[[i, S('Int')], [b, S('Bool')], [k, S('Int')]],
            [[i, S('Int'), expressions], [b, S('Bool'), bools], [k, S('Int'), [[S('Constant'), S('Int')]]]]]


def load_task(task_id):
    manifest = json.loads((FIXTURES / 'manifest.json').read_text())
    if task_id == 'public_absdiff2_v1':
        manifest = json.loads((FIXTURES / 'later_consumption_v1.json').read_text())
    if not isinstance(task_id, str) or task_id not in manifest['fixtures']:
        raise ValueError('unknown public CLIA fixture')
    source = manifest['fixtures'][task_id]
    raw = (FIXTURES / source['file']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != source['sha256']:
        raise ValueError('public fixture source hash mismatch')
    original = raw.decode(); commands = forms(original)
    adapted = []
    for command in commands:
        if str(command[0]) == 'synth-fun':
            if len(command) != 4:
                raise ValueError('fixture must declare implicit CLIA grammar')
            command = command + _explicit_grammar(command[2])
        adapted.append(command)
    sygus = '\n'.join(dump(x) for x in adapted) + '\n'
    task = {'kind': 'clia', 'task_id': task_id, 'source': deepcopy(source),
            'original_sygus': original, 'sygus': sygus, 'grammar': deepcopy(GRAMMAR),
            'native_search_contract': 'Original implicit CLIA is a proposal-space overapproximation. Every returned usable proposal is independently filtered against the same explicit accepted grammar. No grammar reconstruction authority is trusted.',
            'adaptation': 'Accepted implicit CLIA replaced by explicit total grammar; integer constants, linear operations and conditionals only. Let/n-ary/closed-constant normalization preserves this grammar. Host operational bounds additionally apply equally to all arms.',
            'adapted_sha256': hashlib.sha256(sygus.encode()).hexdigest()}
    task['task_sha256'] = digest(task)
    return task


def validate_task(task):
    if not isinstance(task, dict) or task != load_task(task.get('task_id')):
        raise ValueError('full public task/grammar/source binding mismatch')
    return task
