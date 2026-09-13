"""Derive typed ports from the bound native definitions; inspect AST, never execute it."""
import ast
from contract_v1 import require


def native_contract(files):
    tree = ast.parse(files["native/morph.py"])
    names = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                for key, value in zip(target.elts, node.value.elts):
                    if isinstance(key, ast.Name) and isinstance(value, ast.Constant):
                        names[key.id] = value.value
    def literal(node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name): return names[node.id]
        if isinstance(node, ast.Tuple): return tuple(literal(x) for x in node.elts)
        raise ValueError("outside native literal kind declaration")
    declarations = [n.value for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "KINDS" for t in n.targets)]
    require(len(declarations) == 1, "native kind declaration ambiguous")
    kinds = {literal(k): literal(v) for k, v in
             zip(declarations[0].keys, declarations[0].values)}
    vm = ast.parse(files["native/vm.py"])
    def branch(kind):
        rows = [n for n in ast.walk(vm) if isinstance(n, ast.If)
                and ast.unparse(n.test) == "k == " + repr(kind)]
        require(len(rows) == 1, "native evaluation branch ambiguous: " + kind)
        return rows[0].body
    def port(call):
        require(isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr == "_in", "native input role no longer explicit")
        value = ast.literal_eval(call.args[1])
        require(type(value) is int and value >= 0, "invalid native role port")
        return value
    linear = branch("LINEAR")[0].value
    require(isinstance(linear, ast.Call) and linear.func.attr == "_dot",
            "LINEAR no longer uses native parameter dot reader")
    affine, grad = branch("AFFINE"), branch("GRAD")
    roles = {"LINEAR": {"parameter": port(linear.args[0]), "data": port(linear.args[1])},
             "AFFINE": {"parameter": port(affine[0].value), "data": port(affine[1].value)},
             "GRAD": {"parameter": port(grad[0].value), "prediction": port(grad[1].value),
                      "target": port(grad[2].value)}}
    require(set(roles) <= set(kinds) and "DOT" not in kinds, "native alphabet changed")
    require(all(roles[k]["parameter"] == 0 for k in roles), "native coefficient ports changed")
    require(all(kinds[k][1][0] == "vec" for k in roles), "parameter port type changed")
    require(kinds["EDGE"][1:3] == (("vec",), "vec"), "identity-route type changed")
    return kinds, roles
