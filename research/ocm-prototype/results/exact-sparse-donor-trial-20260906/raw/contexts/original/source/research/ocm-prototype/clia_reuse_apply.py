"""ADAPT Z3 parsing/substitution/simplification; fixed evaluator, never synthesis."""
import time
import z3
from clia_grammar import GRAMMAR, forms
import clia_reuse_descriptor as D


def validate_request(desc, request):
    if not isinstance(request, dict) or set(request) != {'kind', 'program_id', 'arguments'} or request['kind'] != 'clia_apply':
        raise ValueError('typed application request required')
    if request['program_id'] != desc['id']: raise ValueError('application descriptor mismatch')
    parameters = forms(desc['candidate'])[0][2]
    args = request['arguments']
    if not isinstance(args, list) or len(args) != len(parameters) or any(type(x) is not int or x.bit_length() > GRAMMAR['bounds']['integer_bits'] for x in args):
        raise ValueError('wrong argument arity, exact integer type or operational bound')
    return args


class CompiledProgram:
    def __init__(self, descriptor):
        start = time.perf_counter()
        self.descriptor = D.validate(descriptor)
        definition = forms(descriptor['candidate'])[0]
        names = [str(p[0]) for p in definition[2]]
        self.variables = tuple(z3.Int(n) for n in names)
        marker = z3.Int('OCM_REUSE_RESULT')
        parsed = z3.parse_smt2_string(descriptor['candidate'] + '\n(assert (= OCM_REUSE_RESULT (' + str(definition[1]) + ' ' + ' '.join(names) + ')))',
                                    decls={**dict(zip(names, self.variables)), 'OCM_REUSE_RESULT': marker})
        if len(parsed) != 1 or not z3.is_eq(parsed[0]): raise ValueError('invalid compiled expression')
        self.expression = parsed[0].arg(1)
        self.compile_wall_s = time.perf_counter() - start

    def evaluate(self, arguments):
        result = z3.simplify(z3.substitute(self.expression, *[(v, z3.IntVal(x)) for v, x in zip(self.variables, arguments)]))
        if not z3.is_int_value(result): raise ValueError('ground application did not simplify to an integer')
        return result.as_long()

    def apply(self, request):
        args = validate_request(self.descriptor, request)
        start = time.perf_counter()
        value = self.evaluate(args)
        return {'status': 'APPLIED', 'program_id': self.descriptor['id'], 'program_sha256': self.descriptor['program_sha256'],
                'arguments': list(args), 'value': value, 'backend': 'Z3_PARSE_SUBSTITUTE_SIMPLIFY',
                'application_wall_s': time.perf_counter() - start}


def check_value(desc, request, output):
    """Bind the returned value to P(tuple); a universal certificate alone cannot pass it."""
    start = time.perf_counter()
    try:
        D.validate(desc); args = validate_request(desc, request)
        if not isinstance(output, dict) or output.get('status') != 'APPLIED' or type(output.get('value')) is not int:
            raise ValueError('no exact returned integer')
        if not isinstance(output.get('arguments'), list) or any(type(x) is not int for x in output['arguments']):
            raise ValueError('returned tuple requires exact integer types')
        if output.get('program_id') != desc['id'] or output.get('program_sha256') != desc['program_sha256'] or output.get('arguments') != args:
            raise ValueError('returned tuple/program identity mismatch')
        # Fixed Check independently reparses canonical data, never trusts backend cache/witness.
        expected = CompiledProgram(desc).evaluate(args)
        status = 'PASS' if output['value'] == expected else 'FAIL'
        return {'status': status, 'reason': 'POINTWISE_VALUE_MATCH' if status == 'PASS' else 'WRONG_APPLICATION_VALUE',
                'program_id': desc['id'], 'arguments': list(args), 'value': output['value'],
                'scope': 'EXACT_PROGRAM_APPLICATION; universal spec authority comes from descriptor support',
                'shared_engine': 'Z3', 'check_wall_s': time.perf_counter() - start}
    except (ValueError, TypeError, KeyError, z3.Z3Exception) as exc:
        return {'status': 'FAIL', 'reason': str(exc), 'check_wall_s': time.perf_counter() - start}
