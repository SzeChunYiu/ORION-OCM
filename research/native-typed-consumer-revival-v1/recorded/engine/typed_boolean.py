"""Donor expression parser with its original depth/token accounting.

Only the final assertion-root restriction is omitted: ordinary substitutions may be
any existing typed expression. Source-goal meaning translation remains unchanged.
"""
from vendor.bridge_syntax import OPS, BridgeRefused

def parse_expression(tokens, types):
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
    return {"turnstile": "|-", "body": body}
