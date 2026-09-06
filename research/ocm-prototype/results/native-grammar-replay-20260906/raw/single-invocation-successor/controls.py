"""Harmless structural controls; do not import or invoke cvc5/Z3."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import prepare_inputs as P

ROOT = Path(__file__).resolve().parent


def main():
    result = json.loads((ROOT/'native_grammar_si_all.json').read_text())
    assert P.validate(result) and result == P.build()
    rows = [{'case': 'actual_two_option_only_successor', 'status': 'PASS'}]
    assert P.sha(ROOT/'implicit_primitive.json') == P.IMPLICIT_SHA
    rows.append({'case': 'unchanged_strong_implicit_parent', 'status': 'PASS'})
    text = result['payload']['sygus']
    edits = [
        ('missing_si_option', text.replace('(set-option :sygus-si all)\n', '', 1)),
        ('non_strict_reconstruction', text.replace(':sygus-si-rcons all', ':sygus-si-rcons none', 1)),
        ('changed_constraint', text.replace('(>= (mux_3 x y z) x)', '(> (mux_3 x y z) x)', 1)),
        ('changed_native_grammar', text.replace('(+ A_Int_489 A_Int_489)', '(- A_Int_489 A_Int_489)', 1)),
        ('options_after_check', text.replace(P.OPTIONS, '', 1)+P.OPTIONS),
        ('duplicate_option', text.replace(P.OPTIONS, P.OPTIONS+P.OPTIONS, 1)),
    ]
    variants = []
    for name, changed in edits:
        assert changed != text
        item = deepcopy(result); item['payload']['sygus'] = changed
        variants.append((name, item))
    changed = deepcopy(result); changed['timeout_ms'] = 5001
    variants.append(('changed_native_deadline', changed))
    for name, item in variants:
        try:
            P.validate(item)
        except ValueError as exc:
            rows.append({'case': name, 'status': 'EXPECTED_REFUSAL', 'reason': str(exc)})
        else:
            raise AssertionError(name+' incorrectly accepted')
    assert not any(n.split('.')[0] in ('cvc5', 'z3') for n in sys.modules)
    record = {'scope': 'STRUCTURAL_INPUT_ONLY', 'rows': rows, 'passed': len(rows),
              'synthesis_calls': 0, 'native_checker_calls': 0,
              'native_parse': 'NOT_RUN', 'actual_task_outputs': 'NOT_RUN'}
    with (ROOT/'CONTROL.json').open('x') as out:
        json.dump(record, out, indent=2, sort_keys=True); out.write('\n')
    print(json.dumps({'passed': len(rows), 'synthesis_calls': 0, 'native_checker_calls': 0}))


if __name__ == '__main__':
    main()
