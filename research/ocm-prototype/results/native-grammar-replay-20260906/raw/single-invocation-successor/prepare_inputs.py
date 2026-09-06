"""Two fixed public inputs; option-only construction, no native calls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import build_inputs as B

ROOT = Path(__file__).resolve().parent
OPTIONS = '(set-option :sygus-si all)\n(set-option :sygus-si-rcons all)\n'
BASE_SHA = '8f8b24d89d4a51c382ef9e9589364c6bb7c4f4a27409879ca2a577f380ff3fc2'
IMPLICIT_SHA = '3d521e6ced959b42b247fb1d44bff871278381e9687cc4bd61c841ae166e3c96'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def baseline():
    if sha(ROOT/'native_grammar_replay.json') != BASE_SHA:
        raise ValueError('frozen replay input drift')
    if sha(ROOT/'implicit_primitive.json') != IMPLICIT_SHA:
        raise ValueError('implicit parent input drift')
    task = json.loads(B.TASK.read_text())
    implicit = json.loads((ROOT/'implicit_primitive.json').read_text())
    rebuilt, _ = B.build(implicit, task, (ROOT/'native-implicit.stderr').read_text())
    old = json.loads((ROOT/'native_grammar_replay.json').read_text())
    if rebuilt != old:
        raise ValueError('exact printed grammar/full original spec drift')
    return old


def validate(successor):
    old = baseline()
    text = successor['payload']['sygus']
    if text.count(OPTIONS) != 1:
        raise ValueError('exact all/strict-all option pair required once')
    stripped = deepcopy(successor)
    stripped['payload']['sygus'] = text.replace(OPTIONS, '', 1)
    if stripped != old:
        raise ValueError('only the registered two-option addition is allowed')
    nodes = B.G.forms(text)
    expected = B.G.forms(OPTIONS)
    if nodes[3:5] != expected:
        raise ValueError('options must precede synth-fun and check-synth')
    if str(nodes[5][0]) != 'synth-fun' or str(nodes[-1][0]) != 'check-synth':
        raise ValueError('original command ordering required')
    return True


def build():
    successor = deepcopy(baseline())
    lines = successor['payload']['sygus'].splitlines(keepends=True)
    lines.insert(3, OPTIONS)
    successor['payload']['sygus'] = ''.join(lines)
    validate(successor)
    return successor


def main():
    result = build()
    with (ROOT/'native_grammar_si_all.json').open('x') as out:
        json.dump(result, out, indent=2, sort_keys=True); out.write('\n')
    with (ROOT/'native_grammar_si_all.sl').open('x') as out:
        out.write(result['payload']['sygus'])
    assert not any(n.split('.')[0] in ('cvc5', 'z3') for n in sys.modules)
    print(json.dumps({'status': 'STRUCTURAL_PREPARATION_ONLY',
                      'input_sha256': sha(ROOT/'native_grammar_si_all.json'),
                      'native_parse': 'NOT_RUN', 'synthesis_calls': 0,
                      'native_checker_calls': 0}))


if __name__ == '__main__':
    main()
