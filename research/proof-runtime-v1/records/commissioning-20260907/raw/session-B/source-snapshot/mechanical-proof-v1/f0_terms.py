"""Finite mechanical proof-term transport and a small dependent type checker.

Only beta conversion; constants are opaque. This host checker proposes/filters terms;
the independently pinned Lean target/kernel is the acceptance authority.
"""
from __future__ import annotations


class TermError(ValueError):
    pass


class TermLimit(TermError):
    pass


def from_data(value, *, max_nodes=4096, max_depth=128):
    remaining = [max_nodes]
    def visit(x, depth):
        remaining[0] -= 1
        if remaining[0] < 0 or depth > max_depth:
            raise TermLimit("transport syntax bound")
        if not isinstance(x, (list, tuple)) or not x or type(x[0]) is not str:
            raise TermError("term must be a tagged array")
        tag = x[0]
        if tag in ("sort", "var", "const"):
            if len(x) != 2 or type(x[1]) is not int or x[1] < 0:
                raise TermError("invalid numeric atom")
            if tag == "sort" and x[1] > 2:
                raise TermError("unregistered universe")
            return (tag, x[1])
        if tag not in ("app", "pi", "lam") or len(x) != 3:
            raise TermError("unregistered constructor or arity")
        return (tag, visit(x[1], depth + 1), visit(x[2], depth + 1))
    return visit(value, 0)


def to_data(term):
    return [term[0], term[1]] if len(term) == 2 else [term[0], to_data(term[1]), to_data(term[2])]


def constants_from_data(values):
    if not isinstance(values, dict):
        raise TermError("constant registry must be a mapping")
    result = {}
    for key, value in values.items():
        if type(key) is int and key >= 0:
            number = key
        elif type(key) is str and key.isascii() and key.isdecimal():
            try:
                number = int(key)
            except ValueError as exc:
                raise TermError("constant ID exceeds interpreter conversion bound") from exc
            if str(number) != key:
                raise TermError("noncanonical constant ID")
        else:
            raise TermError("noncanonical constant ID")
        if number in result:
            raise TermError("duplicate constant ID")
        result[number] = from_data(value)
    return result


def shift(term, amount, cutoff=0):
    tag = term[0]
    if tag == "var":
        n = term[1] + amount if term[1] >= cutoff else term[1]
        if n < 0:
            raise TermError("escaping variable")
        return (tag, n)
    if tag in ("sort", "const"):
        return term
    return (tag, shift(term[1], amount, cutoff),
            shift(term[2], amount, cutoff + (tag in ("pi", "lam"))))


def substitute(term, index, value, depth=0):
    tag = term[0]
    if tag == "var":
        return shift(value, depth) if term[1] == index + depth else term
    if tag in ("sort", "const"):
        return term
    return (tag, substitute(term[1], index, value, depth),
            substitute(term[2], index, value, depth + (tag in ("pi", "lam"))))


def instantiate(body, value):
    return shift(substitute(body, 0, shift(value, 1)), -1)


def _tick(fuel):
    fuel[0] -= 1
    if fuel[0] < 0:
        raise TermLimit("normalization/type-check fuel")


def _normal(term, fuel):
    _tick(fuel)
    tag = term[0]
    if tag in ("sort", "var", "const"):
        return term
    left, right = _normal(term[1], fuel), _normal(term[2], fuel)
    if tag == "app" and left[0] == "lam":
        return _normal(instantiate(left[2], right), fuel)
    return (tag, left, right)


def normalize(term, fuel=20000):
    return _normal(term, [fuel])


def _infer(term, constants, context, fuel):
    _tick(fuel)
    tag = term[0]
    if tag == "sort":
        return ("sort", term[1] + 1)
    if tag == "var":
        if term[1] >= len(context):
            raise TermError("unbound variable")
        return shift(context[term[1]], term[1] + 1)
    if tag == "const":
        if term[1] not in constants:
            raise TermError("undeclared constant")
        return constants[term[1]]
    if tag == "app":
        ftype = _normal(_infer(term[1], constants, context, fuel), fuel)
        if ftype[0] != "pi":
            raise TermError("application of nonfunction")
        actual = _normal(_infer(term[2], constants, context, fuel), fuel)
        if actual != _normal(ftype[1], fuel):
            raise TermError("argument type mismatch")
        return instantiate(ftype[2], term[2])
    domain = _normal(_infer(term[1], constants, context, fuel), fuel)
    if domain[0] != "sort":
        raise TermError("binder domain is not a type")
    body = _infer(term[2], constants, (term[1],) + context, fuel)
    if tag == "lam":
        return ("pi", term[1], body)
    if tag != "pi":
        raise TermError("unregistered constructor")
    codomain = _normal(body, fuel)
    if codomain[0] != "sort":
        raise TermError("Pi codomain is not a type")
    return ("sort", 0 if codomain[1] == 0 else max(domain[1], codomain[1]))


def infer(term, constants, context=(), *, fuel=20000):
    return _infer(term, constants, tuple(context), [fuel])


def check(term, expected, constants, context=(), *, fuel=20000):
    account = [fuel]
    actual = _normal(_infer(term, constants, tuple(context), account), account)
    if actual != _normal(expected, account):
        raise TermError("term does not inhabit requested type")


def node_count(term):
    return 1 if len(term) == 2 else 1 + node_count(term[1]) + node_count(term[2])


def const_dependencies(term):
    if term[0] == "const":
        return frozenset((term[1],))
    if len(term) == 2:
        return frozenset()
    return const_dependencies(term[1]) | const_dependencies(term[2])
