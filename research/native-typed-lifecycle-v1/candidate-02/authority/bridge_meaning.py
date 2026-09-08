"""Independent source-token point semantics and complete finite-world transport check."""
import hashlib
import itertools
import json

def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()

class MeaningMismatch(ValueError):
    pass

def point(tokens, declarations, values):
    """Direct native token interpretation; does not consume translated/native exported AST."""
    words = iter(tokens)
    if next(words) != "|-": raise MeaningMismatch("TURNSTILE")
    def term(first=None):
        token = next(words) if first is None else first
        if token in declarations: return declarations[token], values[token]
        if token == "-.":
            sort, value = term()
            if sort != "wff": raise MeaningMismatch("NATIVE_TYPE")
            return "wff", not value
        if token != "(": raise MeaningMismatch("NATIVE_TOKEN")
        lt, left = term()
        operator = next(words)
        rt, right = term()
        if next(words) != ")": raise MeaningMismatch("NATIVE_SCOPE")
        if operator in ("->", "/\\", "\\/", "<->"):
            if (lt, rt) != ("wff", "wff"): raise MeaningMismatch("NATIVE_TYPE")
            if operator == "<->": return "wff", left == right
            value = ((not left) or right) if operator == "->" else (
                left and right if operator == "/\\" else left or right)
            return "wff", value
        if operator in ("i^i", "u."):
            if (lt, rt) != ("class", "class"): raise MeaningMismatch("NATIVE_TYPE")
            return "class", left and right if operator == "i^i" else left or right
        raise MeaningMismatch("NATIVE_OPERATOR")
    sort, value = term()
    end = next(words, None)
    if end == "C_":
        other_sort, other = term()
        if (sort, other_sort) != ("class", "class"): raise MeaningMismatch("NATIVE_SUBSET_TYPE")
        sort, value = "wff", (not value) or other
        end = next(words, None)
    if end is not None or sort != "wff": raise MeaningMismatch("NATIVE_ASSERTION")
    return value

def render_native(assertion, types):
    symbols = {"iff": "<->", "implies": "->", "and": "/\\", "or": "\\/", "intersection": "i^i", "union": "u."}
    def expression(node):
        op = node["op"]
        if op == "variable":
            if node["type"] != types[node["name"]]: raise MeaningMismatch("AST_VARIABLE_TYPE")
            return [node["name"]]
        expected = "class" if op in {"intersection", "union"} else "wff"
        if node["type"] != expected: raise MeaningMismatch("AST_OPERATOR_TYPE")
        if op == "not": return ["-."] + expression(node["argument"])
        left, right = expression(node["left"]), expression(node["right"])
        if op == "subset": return left + ["C_"] + right
        return ["("] + left + [symbols[op]] + right + [")"]
    if assertion["turnstile"] != "|-": raise MeaningMismatch("AST_TURNSTILE")
    return ["|-"] + expression(assertion["body"])

def check(source, bridge, contract, verifier):
    task = contract.validate_task(bridge["task"])
    names = task["predicates"]
    if not 1 <= len(names) <= 3: raise MeaningMismatch("FRAGMENT_BOUND")
    types = {h["statement"][1]: h["statement"][0] for h in source["floating"]}
    correspondence = bridge["correspondence"]
    if set(correspondence) != set(types) or sorted(correspondence.values()) != names:
        raise MeaningMismatch("CORRESPONDENCE")
    statements = [h["statement"] for h in source["essential"]] + [source["statement"]]
    translated = task["premises"] + [task["query"]]
    if bridge["native"]["types"] != types: raise MeaningMismatch("NATIVE_DECLARATIONS")
    native_asts = bridge["native"]["premises"] + [bridge["native"]["query"]]
    if [render_native(ast, types) for ast in native_asts] != statements:
        raise MeaningMismatch("NATIVE_AST_SOURCE")
    if len(statements) != len(translated): raise MeaningMismatch("OPEN_HYPOTHESES")
    regions = [{name: bool(region & (1 << i)) for i, name in enumerate(names)}
               for region in range(1 << len(names))]
    table = []
    for mask in range(1, 1 << len(regions)):
        world = [a for i, a in enumerate(regions) if mask & (1 << i)]
        native_world = [{var: a[pred] for var, pred in correspondence.items()} for a in world]
        native = [all(point(tokens, types, a) for a in native_world) for tokens in statements]
        unary = [verifier._holds(stmt, world) for stmt in translated]
        if native != unary:
            raise MeaningMismatch("TRUTH_MISMATCH_AT_WORLD_" + str(mask))
        table.append({"world_mask": mask, "truth": native})
    def first(predicate):
        found = next((row for row in table if predicate(row["truth"])), None)
        if found is None: return None
        mask = found["world_mask"]
        return {"world_mask": mask, "regions": [i for i in range(len(regions)) if mask & (1 << i)],
                "truth": found["truth"]}
    gates = {"premises_satisfiable": first(lambda t: all(t[:-1])),
             "query_not_tautological": first(lambda t: not t[-1]),
             "entailment_counterexample": first(lambda t: all(t[:-1]) and not t[-1]),
             "essentiality_counterexamples": [
                 first(lambda t, removed=i: all(v for j, v in enumerate(t[:-1]) if j != removed) and not t[-1])
                 for i in range(len(task["premises"]))]}
    return {"terminal": "INTERPRETATION_EQUIVALENT", "worlds": len(table),
            "region_count": len(regions), "table": table, "table_sha256": hashlib.sha256(raw(table)).hexdigest(),
            "gates": gates, "task_sha256": contract.task_digest(task),
            "scope": "Pointwise schema membership interpretation universally lifted over nonempty region sets; multiplicities are invisible in this unary fragment."}

def semantic_orbit(task, verifier):
    """Canonical full open-task truth signature under positive predicate bijections only."""
    names = task["predicates"]
    statements = task["premises"] + [task["query"]]
    choices = []
    for permutation in itertools.permutations(names):
        regions = [{original: bool(region & (1 << names.index(target)))
                    for original, target in zip(names, permutation)}
                   for region in range(1 << len(names))]
        table = [[verifier._holds(s, [a for i, a in enumerate(regions) if mask & (1 << i)])
                  for s in statements] for mask in range(1, 1 << len(regions))]
        choices.append((raw(table), dict(zip(names, permutation))))
    signature, correspondence = min(choices, key=lambda pair: pair[0])
    return {"signature_sha256": hashlib.sha256(signature).hexdigest(), "predicate_bijection": correspondence,
            "meaning": "Ordered external-premise truth values AND query truth, not the always-true implication alone.",
            "renaming_scope": "positive predicate permutations; no complement/converse rewrite"}
