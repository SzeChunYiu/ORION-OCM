"""Closed proof-term transport; names and commands never come from candidates.

This module validates syntax/scope only. Lean checks the independently fixed
target type and proof. No successful render is a proof acceptance decision.
"""
import re

CONSTANTS = ('Eq.{1}', 'MEFoundation.agreement_sound', 'MEFoundation.agreement_refinement')
ALLOWED_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})


def render_term(data, max_nodes=4096, max_depth=96):
    for value in (max_nodes, max_depth):
        if type(value) is not int or value < 1:
            raise ValueError('positive integer transport bounds required')
    count = 0

    def render(node, binders, depth):
        nonlocal count
        count += 1
        if count > max_nodes or depth > max_depth:
            raise ValueError('candidate exceeds registered transport bounds')
        if type(node) is not list or not node or type(node[0]) is not str:
            raise ValueError('candidate must use the closed array AST')
        tag = node[0]
        if tag in ('sort', 'var', 'const'):
            if len(node) != 2 or type(node[1]) is not int or node[1] < 0:
                raise ValueError('invalid numeric AST payload')
            value = node[1]
            if tag == 'sort' and value <= 2:
                return f'(Sort {value})'
            if tag == 'var' and value < len(binders):
                return binders[-1 - value]
            if tag == 'const' and value < len(CONSTANTS):
                return f'(@{CONSTANTS[value]})'
            raise ValueError('unregistered sort, free variable or constant')
        if tag not in ('app', 'pi', 'lam') or len(node) != 3:
            raise ValueError('unregistered AST constructor or arity')
        first = render(node[1], binders, depth + 1)
        if tag == 'app':
            second = render(node[2], binders, depth + 1)
            return f'({first} {second})'
        name = f'v{len(binders)}'
        body = render(node[2], binders + (name,), depth + 1)
        if tag == 'pi':
            return f'(forall ({name} : {first}), {body})'
        return f'(fun ({name} : {first}) => {body})'

    return render(data, (), 0)


def audit_axioms(output, expected):
    """Require exactly one unambiguous report from the trusted generated command."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1:
        raise ValueError('missing, duplicate, extra or noisy axiom report')
    line = lines[0]
    if line == f"'{expected}' does not depend on any axioms":
        return []
    match = re.fullmatch(re.escape(f"'{expected}' depends on axioms: ") + r'\[([^\]]*)\]', line)
    if match is None:
        raise ValueError('unexpected or malformed axiom report')
    fields = match[1].strip()
    axioms = [item.strip() for item in fields.split(',')] if fields else []
    if any(not item for item in axioms) or len(set(axioms)) != len(axioms) or not set(axioms) <= ALLOWED_AXIOMS:
        raise ValueError('unregistered or duplicated proof axiom')
    return sorted(axioms)
