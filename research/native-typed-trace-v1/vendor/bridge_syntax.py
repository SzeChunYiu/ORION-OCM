"""Typed syntax transport only; no theorem-label dispatch or proof authority."""
OPS = {"<->": ("wff", "iff"), "->": ("wff", "implies"), "/\\": ("wff", "and"), "\\/": ("wff", "or"),
       "i^i": ("class", "intersection"), "u.": ("class", "union")}

class BridgeRefused(ValueError):
    pass

def declarations(floating):
    if type(floating) is not list or not 1 <= len(floating) <= 3:
        raise BridgeRefused("PREDICATE_BOUND")
    types = {}
    for hyp in floating:
        value = hyp["statement"]
        if type(value) is not list or len(value) != 2 or value[0] not in {"wff", "class"}:
            raise BridgeRefused("UNSUPPORTED_TYPE")
        if type(value[1]) is not str or not value[1] or value[1] in types:
            raise BridgeRefused("VARIABLE_DECLARATION")
        types[value[1]] = value[0]
    return types

def parse(tokens, types):
    if type(tokens) is not list or not 2 <= len(tokens) <= 512 or any(type(t) is not str for t in tokens):
        raise BridgeRefused("TOKEN_SHAPE")
    if tokens[0] != "|-": raise BridgeRefused("ASSERTION_TYPE")
    pos = 1
    def take():
        nonlocal pos
        if pos == len(tokens): raise BridgeRefused("UNEXPECTED_END")
        word = tokens[pos]; pos += 1
        return word
    def expr(depth=0):
        if depth > 16: raise BridgeRefused("DEPTH_BOUND")
        word = take()
        if word in types: return {"type": types[word], "op": "variable", "name": word}
        if word == "-.":
            argument = expr(depth+1)
            if argument["type"] != "wff": raise BridgeRefused("OPERATOR_TYPE")
            return {"type": "wff", "op": "not", "argument": argument}
        if word != "(": raise BridgeRefused("UNSUPPORTED_EXPRESSION")
        left = expr(depth+1); operator = take()
        if operator not in OPS: raise BridgeRefused("UNSUPPORTED_OPERATOR")
        expected, op = OPS[operator]
        right = expr(depth+1)
        if take() != ")": raise BridgeRefused("PARENTHESIS_SCOPE")
        if left["type"] != expected or right["type"] != expected:
            raise BridgeRefused("OPERATOR_TYPE")
        return {"type": expected, "op": op, "left": left, "right": right}
    body = expr()
    if pos < len(tokens):
        if take() != "C_": raise BridgeRefused("UNSUPPORTED_ASSERTION_OPERATOR")
        right = expr()
        if body["type"] != "class" or right["type"] != "class":
            raise BridgeRefused("SUBSET_TYPE")
        body = {"type": "wff", "op": "subset", "left": body, "right": right}
    if pos != len(tokens): raise BridgeRefused("TRAILING_TOKENS")
    if body["op"] not in {"implies", "subset"}:
        raise BridgeRefused("UNSUPPORTED_ASSERTION_ROOT")
    return {"turnstile": "|-", "body": body}

def translate(statement, hypotheses, floating, contract):
    types = declarations(floating)
    correspondence = {name: "P"+str(i) for i, name in enumerate(types)}
    native_hyps = [parse(h["statement"], types) for h in hypotheses]
    native_query = parse(statement, types)
    def expression(node):
        op = node["op"]
        if op == "variable": return ["pred", correspondence[node["name"]]]
        if op == "not": return ["not", expression(node["argument"])]
        left, right = expression(node["left"]), expression(node["right"])
        if op == "iff":
            return ["and", ["or", ["not", left], right], ["or", ["not", right], left]]
        if op == "implies": return ["or", ["not", left], right]
        if op in {"and", "intersection"}: return ["and", left, right]
        if op in {"or", "union"}: return ["or", left, right]
        raise BridgeRefused("UNSUPPORTED_EXPRESSION_TRANSPORT")
    def universal(assertion):
        node = assertion["body"]
        return {"kind": "every", "left": expression(node["left"]), "right": expression(node["right"])}
    task = contract.validate_task({"schema": contract.SCHEMA, "predicates": sorted(correspondence.values()),
        "premises": [universal(h) for h in native_hyps], "query": universal(native_query)})
    return {"native": {"types": types, "premises": native_hyps, "query": native_query},
        "correspondence": correspondence, "task": task, "task_sha256": contract.task_digest(task),
        "hypothesis_correspondence": [{"native_label": h["label"], "premise_index": i} for i, h in enumerate(hypotheses)]}
