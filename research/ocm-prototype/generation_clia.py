"""Narrow CLIA/Stitch translation; the existing grammar remains admission authority."""
from dataclasses import dataclass
import re
import sexpdata as sx
from clia_grammar import dump, forms, validate
from clia_tasks import signatures, validate_task
import clia_process

S = sx.Symbol


def one(text):
    nodes = forms(text)
    if len(nodes) != 1:
        raise ValueError('one expression required')
    return nodes[0]


def substitute(node, env):
    if isinstance(node, S):
        return env.get(str(node), node)
    if isinstance(node, list):
        return [substitute(x, env) for x in node]
    return node


def unlet(node, env=None):
    env = {} if env is None else env
    if isinstance(node, S):
        return env.get(str(node), node)
    if not isinstance(node, list):
        return node
    if str(node[0]) == 'let':
        additions = {str(k): unlet(v, env) for k, v in node[1]}
        return unlet(node[2], {**env, **additions})
    return [node[0], *(unlet(x, env) for x in node[1:])]


def encode(candidate, sigs):
    """Validate first; eliminate non-shadowing simultaneous lets, then bind formals."""
    result = []
    for d in validate(candidate, sigs):
        names = [str(p[0]) for p in d[2]]
        body = substitute(unlet(d[4]), {n: S('$' + str(len(names)-i-1)) for i, n in enumerate(names)})
        for _ in names:
            body = [S('lam'), body]
        result.append({'name': str(d[1]), 'program': dump(body)})
    return result


@dataclass(frozen=True)
class Macro:
    name: str
    body: str  # expanded primitive expression with #i holes; no binder
    sorts: tuple[str, ...]
    result: str


def expand(node, library, used=None, depth=0):
    if depth > 160:
        raise ValueError('expansion exceeds depth bound')
    if not isinstance(node, list):
        return node
    if not node or not isinstance(node[0], S):
        raise ValueError('first-order application required')
    op = str(node[0]); args = [expand(x, library, used, depth+1) for x in node[1:]]
    if op not in library:
        return [node[0], *args]
    m = library[op]
    if len(args) != len(m.sorts):
        raise ValueError('macro arity mismatch')
    if used is not None:
        used.append(op)
    return substitute(one(m.body), {'#'+str(i): x for i, x in enumerate(args)})


def admit_macros(records):
    """Infer CLIA sorts; host validation refuses unsafe coefficient holes/grammar."""
    library = {}
    for record in records:
        name, arity = record['name'], record['arity']
        if not re.fullmatch(r'fn_[0-9]+', name) or name in library or type(arity) is not int or not 1 <= arity <= 2:
            raise ValueError('invalid/duplicate macro name or parameterized arity')
        body = expand(one(record['body']), library)
        holes = {}; visited = 0

        def infer(n, want=None, depth=0):
            nonlocal visited
            visited += 1
            if depth > 160 or visited > 20000:
                raise ValueError('macro outside host AST bounds')
            if type(n) is int:
                result = 'Int'
            elif isinstance(n, S):
                token = str(n)
                if re.fullmatch(r'#[0-9]+', token):
                    i = int(token[1:])
                    if i >= arity or want is None or (i in holes and holes[i] != want):
                        raise ValueError('unconstrained/out-of-range/mixed-sort hole')
                    holes[i] = want; result = want
                elif token in ('true', 'false'):
                    result = 'Bool'
                else:
                    raise ValueError('free variable, recursive macro or unsupported symbol')
            elif isinstance(n, list) and n and isinstance(n[0], S):
                op = str(n[0]); count = len(n)-1
                if op in ('+', '-', '*'):
                    sorts, result = ['Int']*count, 'Int'
                elif op == 'ite':
                    sorts, result = ['Bool', 'Int', 'Int'], 'Int'
                elif op in ('=', '<', '<=', '>', '>='):
                    sorts, result = ['Int', 'Int'], 'Bool'
                elif op in ('and', 'or', 'not', '=>'):
                    sorts, result = ['Bool']*count, 'Bool'
                else:
                    raise ValueError('unsupported primitive/binder/forward macro')
                if len(sorts) != count:
                    raise ValueError('macro primitive arity')
                for x, sort in zip(n[1:], sorts):
                    infer(x, sort, depth+1)
            else:
                raise ValueError('invalid macro expression')
            if want is not None and result != want:
                raise ValueError('macro sort mismatch')
            return result

        result = infer(body)
        if set(holes) != set(range(arity)):
            raise ValueError('all declared holes must occur')
        # Bool representatives remain nonconstant; Int holes are arbitrary variables.
        representatives = {'#'+str(i): S('h'+str(i)) if holes[i] == 'Int' else [S('='), S('h'+str(i)), 0] for i in holes}
        probe = substitute(body, representatives)
        if result == 'Bool':
            probe = [S('ite'), probe, 1, 0]
        params = [[S('h'+str(i)), S('Int')] for i in range(arity)]
        validate(dump([S('define-fun'), S('probe'), params, S('Int'), probe]), {'probe': {'parameters': params}})
        library[name] = Macro(name, dump(body), tuple(holes[i] for i in range(arity)), result)
    return library


def decode(program, name, sigs, library=None):
    body = one(program); params = sigs[name]['parameters']; names = [str(x[0]) for x in params]
    for _ in names:
        if not isinstance(body, list) or len(body) != 2 or not isinstance(body[0], S) or str(body[0]) != 'lam':
            raise ValueError('exact original outer binders required')
        body = body[1]
    used = []; body = expand(body, library or {}, used)
    body = substitute(body, {'$'+str(i): S(n) for i, n in enumerate(reversed(names))})
    candidate = dump([S('define-fun'), S(name), params, S('Int'), body])
    validate(candidate, {name: sigs[name]})
    return {'candidate': candidate, 'macro_calls_in_input': used}


def equivalent(left, right, sigs, *, timeout_ms=5000):
    a, b = validate(left, sigs), validate(right, sigs)
    if len(a) != 1:
        raise ValueError('one function per equivalence obligation')
    da, db = a[0], b[0]; da[1], db[1] = S('left'), S('right')
    params = da[2]; args = ' '.join(dump(p[0]) for p in params)
    smt = '\n'.join([dump(da), dump(db)] + [f'(declare-const {dump(p[0])} Int)' for p in params])
    smt += f'\n(assert (not (= (left {args}) (right {args}))))\n'
    return clia_process.invoke('verify', {'smt2': smt}, timeout_ms=timeout_ms, deadline_s=10)


def request(task, library):
    """Explicit primitive parent plus typed calls; constraints and checker unchanged."""
    validate_task(task)
    commands = forms(task['sygus']); additions = []
    for m in library.values():
        params = [[S('h'+str(i)), S(t)] for i, t in enumerate(m.sorts)]
        body = substitute(one(m.body), {'#'+str(i): p[0] for i, p in enumerate(params)})
        additions.append([S('define-fun'), S(m.name), params, S(m.result), body])
    for c in commands:
        if str(c[0]) == 'synth-fun':
            for m in library.values():
                production = [S(m.name), *(S('OCM_I' if t == 'Int' else 'OCM_B') for t in m.sorts)]
                nt = S('GEN_'+m.name)  # native :gterm identifies nonterminals, not production IDs
                c[4].append([nt, S(m.result)])
                c[5][0 if m.result == 'Int' else 1][2].append(nt)
                c[5].append([nt, S(m.result), [production]])
    return '\n'.join(dump(c) for c in commands[:1]+additions+commands[1:])+'\n'
