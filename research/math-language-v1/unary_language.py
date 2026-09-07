"""Exact supplied controlled grammar; no morphology, world facts or learning."""
import re
from unary_contract import (InputRefused, MAX_DEPTH, MAX_PREMISES, MAX_TEXT_BYTES,
                            SCHEMA, predicate_name, validate_task)

TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[().?]")


def parse(text):
    if type(text) is not str or not text.isascii() or not text.strip():
        raise InputRefused("ASCII_TEXT_REQUIRED")
    if len(text.encode("ascii")) > MAX_TEXT_BYTES:
        raise InputRefused("TEXT_BOUND")
    tokens, end = [], 0
    for match in TOKEN.finditer(text):
        if text[end:match.start()].strip():
            raise InputRefused("UNSUPPORTED_TOKEN")
        tokens.append(match.group())
        end = match.end()
    if text[end:].strip():
        raise InputRefused("UNSUPPORTED_TOKEN")
    pos, names = 0, set()

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def take(expected=None):
        nonlocal pos
        found = peek()
        if found is None or (expected is not None and found != expected):
            raise InputRefused("EXPECTED_" + (expected or "TOKEN"))
        pos += 1
        return found

    def expression(depth=0):
        if depth > MAX_DEPTH:
            raise InputRefused("EXPRESSION_BOUND")
        if peek() != "(":
            name = predicate_name(take())
            names.add(name)
            return ["pred", name]
        take("(")
        if peek() == "not":
            take("not")
            node = ["not", expression(depth + 1)]
        else:
            left = expression(depth + 1)
            op = take()
            if op not in ("and", "or"):
                raise InputRefused("BOOLEAN_OPERATOR_REQUIRED")
            node = [op, left, expression(depth + 1)]
        take(")")
        return node

    def statement():
        kind = take()
        if kind not in ("every", "no", "some", "not"):
            raise InputRefused("QUANTIFIER_REQUIRED")
        if kind == "not":
            take("every")
            kind = "not_every"
        left = expression()
        take("is")
        return {"kind": kind, "left": left, "right": expression()}

    premises = []
    while peek() != "query":
        if len(premises) >= MAX_PREMISES:
            raise InputRefused("PREMISE_BOUND")
        premises.append(statement())
        take(".")
    take("query")
    query = statement()
    take("?")
    if peek() is not None:
        raise InputRefused("TRAILING_INPUT")
    return validate_task({"schema": SCHEMA, "predicates": sorted(names),
                          "premises": premises, "query": query})


def realize(value):
    """Canonical realization preserves the exact validated meaning and symbol names."""
    task = validate_task(value)
    def expression(expr):
        if expr[0] == "pred":
            return expr[1]
        if expr[0] == "not":
            return "(not " + expression(expr[1]) + ")"
        return "(" + expression(expr[1]) + " " + expr[0] + " " + expression(expr[2]) + ")"

    def statement(item):
        kind = "not every" if item["kind"] == "not_every" else item["kind"]
        return kind + " " + expression(item["left"]) + " is " + expression(item["right"])
    return "".join(statement(s) + ". " for s in task["premises"]) + "query " + statement(task["query"]) + "?"
