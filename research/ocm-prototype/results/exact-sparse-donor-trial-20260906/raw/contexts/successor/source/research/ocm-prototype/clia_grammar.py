"""Host-owned, total CLIA expression grammar; no solver/model authority here."""
from __future__ import annotations
import sexpdata as sx

GRAMMAR = {
    'id': 'ocm.clia-total-expressions.v1',
    'integer': 'parameter | integer literal | (+ I I...) | (- I) | (- I I...) | (* K I) | (* I K) | (ite B I I)',
    'boolean': 'true | false | (and B B...) | (or B B...) | (not B) | (=> B B) | (= I I) | (< I I) | (<= I I) | (> I I) | (>= I I)',
    'constant': 'K is a closed integer expression using literals, +, -, *; normalized to its exact integer value',
    'let': 'SMT-LIB simultaneous, unique, non-shadowing local bindings; only expression sharing, no recursion',
    'bounds': {'candidate_bytes': 65536, 'ast_nodes': 20000, 'ast_depth': 160, 'integer_bits': 4096},
    'normalization': 'n-ary +/-/and/or fold; let expands without capture; closed arithmetic constant-folds',
    'excluded': ['division', 'modulo', 'nonlinear variable multiplication', 'quantifiers', 'function calls', 'extra SMT commands'],
}


def forms(text):
    if not isinstance(text, str) or len(text.encode()) > GRAMMAR['bounds']['candidate_bytes']:
        raise ValueError('text outside declared byte bound')
    try:
        return sx.loads('(' + text + ')', true=None, false=None, nil=None)
    except (sx.ExpectClosingBracket, sx.ExpectNothing, sx.ExpectSExp) as exc:
        raise ValueError('invalid S-expression syntax') from exc


def dump(node):
    if isinstance(node, sx.Symbol):
        return str(node)
    if isinstance(node, list):
        return '(' + ' '.join(dump(x) for x in node) + ')'
    if type(node) is int:
        return str(node) if node >= 0 else f'(- {-node})'
    raise ValueError('only symbol/list/integer data are allowed')


def _identifier(node):
    if not isinstance(node, sx.Symbol):
        raise ValueError('identifier must be a symbol')
    name = str(node)
    if not name or not all(c.isascii() and (c.isalnum() or c in '_-') for c in name):
        raise ValueError('identifier outside declared spelling')
    return name


def validate(candidate, signatures):
    """Independent shape/type/scope/grammar pass, before native Z3 invocation."""
    definitions = forms(candidate)
    if len(definitions) == 1 and isinstance(definitions[0], list) and definitions[0] and isinstance(definitions[0][0], list):
        definitions = definitions[0]
    if len(definitions) != len(signatures):
        raise ValueError('exact function inventory required')
    seen = set(); count = 0

    def infer(node, env, depth=0):
        nonlocal count
        count += 1
        if count > GRAMMAR['bounds']['ast_nodes'] or depth > GRAMMAR['bounds']['ast_depth']:
            raise ValueError('expression exceeds operational bound')
        if type(node) is int:
            if node.bit_length() > GRAMMAR['bounds']['integer_bits']:
                raise ValueError('integer exceeds bit bound')
            return 'Int', node
        if isinstance(node, sx.Symbol):
            name = str(node)
            if name in ('true', 'false'):
                return 'Bool', None
            if name not in env:
                raise ValueError('unbound variable: ' + name)
            return env[name]
        if not isinstance(node, list) or not node or not isinstance(node[0], sx.Symbol):
            raise ValueError('invalid expression shape')
        op = str(node[0]); args = node[1:]
        if op == 'let':
            if len(args) != 2 or not isinstance(args[0], list) or not args[0]:
                raise ValueError('invalid let shape')
            additions = {}
            for binding in args[0]:
                if not isinstance(binding, list) or len(binding) != 2:
                    raise ValueError('invalid let binding')
                name = _identifier(binding[0])
                if name in env or name in additions or name in ('true', 'false'):
                    raise ValueError('duplicate or shadowing let binding')
                additions[name] = infer(binding[1], env, depth + 1)
            return infer(args[1], {**env, **additions}, depth + 1)
        allowed = {'+', '-', '*', 'ite', 'and', 'or', 'not', '=>', '=', '<', '<=', '>', '>='}
        if op not in allowed:
            raise ValueError('forbidden primitive: ' + op)
        values = [infer(x, env, depth + 1) for x in args]
        types = [x[0] for x in values]
        constants = [x[1] for x in values]
        if op in ('+', '-', '*'):
            if not values or any(t != 'Int' for t in types):
                raise ValueError('integer operands required')
            if (op == '+' and len(args) < 2) or (op == '*' and len(args) != 2):
                raise ValueError('wrong arithmetic arity')
            if op == '*' and all(c is None for c in constants):
                raise ValueError('nonlinear multiplication is forbidden')
            constant = None
            if all(c is not None for c in constants):
                if op == '+': constant = sum(constants)
                elif op == '-': constant = -constants[0] if len(constants) == 1 else constants[0] - sum(constants[1:])
                else: constant = constants[0] * constants[1]
                if constant.bit_length() > GRAMMAR['bounds']['integer_bits']:
                    raise ValueError('computed integer exceeds bit bound')
            return 'Int', constant
        if op == 'ite':
            if types != ['Bool', 'Int', 'Int']:
                raise ValueError('ite requires Bool/Int/Int')
            return 'Int', None
        if op in ('=', '<', '<=', '>', '>='):
            if types != ['Int', 'Int']:
                raise ValueError('comparison requires two Int operands')
        elif any(t != 'Bool' for t in types) or (op in ('and', 'or') and len(args) < 2) or (op == 'not' and len(args) != 1) or (op == '=>' and len(args) != 2):
            raise ValueError('invalid Boolean operands or arity')
        return 'Bool', None

    for definition in definitions:
        if not isinstance(definition, list) or len(definition) != 5 or not isinstance(definition[0], sx.Symbol) or str(definition[0]) != 'define-fun':
            raise ValueError('only complete define-fun expressions are allowed')
        name = _identifier(definition[1])
        if name not in signatures or name in seen:
            raise ValueError('unknown or duplicate function')
        expected = signatures[name]
        if definition[2] != expected['parameters'] or str(definition[3]) != 'Int':
            raise ValueError('parameter names/arity/sorts or output sort mismatch')
        env = {_identifier(p[0]): ('Int', None) for p in definition[2]}
        if len(env) != len(definition[2]):
            raise ValueError('duplicate formal parameter')
        if infer(definition[4], env)[0] != 'Int':
            raise ValueError('function must return Int')
        seen.add(name)
    return definitions
