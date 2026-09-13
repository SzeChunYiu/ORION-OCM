"""Closed source register; no arbitrary Python objects are admitted."""
import ast
import dis
from dataclasses import dataclass
from types import CodeType, MappingProxyType

class Refusal(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise Refusal(message)

def value_ok(value):
    return type(value) in (int, bool) or (type(value) is tuple and all(value_ok(x) for x in value))

@dataclass(frozen=True)
class Alias:
    target: str

@dataclass(frozen=True)
class Function:
    source: str
    code: CodeType
    parameter: str

ALLOWED = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign,
           ast.Return, ast.Name, ast.Load, ast.Store, ast.Tuple, ast.Constant,
           ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.BitXor, ast.BitAnd, ast.BitOr,
           ast.LShift, ast.RShift, ast.UnaryOp, ast.USub, ast.UAdd, ast.Invert,
           ast.Not, ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt,
           ast.GtE, ast.Subscript, ast.Call)

def parse_function(source):
    require(type(source) is str, "source must be text")
    tree = ast.parse(source)
    require(len(tree.body) == 1 and type(tree.body[0]) is ast.FunctionDef,
            "exactly one source function is required")
    fn = tree.body[0]
    require(fn.name == "f", "source function must be named f")
    args = fn.args
    require(len(args.args) == 1 and not args.posonlyargs and not args.kwonlyargs
            and args.vararg is None and args.kwarg is None and not args.defaults
            and not args.kw_defaults and args.args[0].annotation is None
            and fn.returns is None and not fn.decorator_list and not fn.type_params,
            "one unannotated positional argument, no decorators/defaults")
    require(bool(fn.body) and type(fn.body[-1]) is ast.Return
            and all(type(s) is ast.Assign for s in fn.body[:-1]), "straight-line assignments then return")
    for node in ast.walk(tree):
        require(type(node) in ALLOWED, "unsupported syntax: " + type(node).__name__)
        if type(node) is ast.Call:
            require(type(node.func) is ast.Name and len(node.args) == 1 and not node.keywords,
                    "only named one-argument calls")
        if type(node) is ast.Compare:
            require(len(node.ops) == 1, "chained comparison is outside the register")
        if type(node) is ast.Constant:
            require(type(node.value) in (int, bool), "only integer/Boolean constants")
        if type(node) is ast.Assign:
            require(len(node.targets) == 1, "one assignment target")
            target = node.targets[0]
            require(type(target) is ast.Name or (type(target) is ast.Tuple
                    and all(type(x) is ast.Name for x in target.elts)), "simple local assignment")
    code = next(c for c in compile(tree, "<typed-cost>", "exec").co_consts if type(c) is CodeType)
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    for i in dis.get_instructions(code)), "compiled control flow is forbidden")
    return Function(source, code, args.args[0].arg)

class Program:
    def __init__(self, sources, aliases=None, data=None):
        require(type(sources) is dict and bool(sources), "nonempty explicit source map required")
        aliases, data = dict(aliases or {}), dict(data or {})
        names = list(sources) + list(aliases) + list(data)
        require(all(type(n) is str and n.isidentifier() and not n.startswith('__') for n in names),
                "invalid binding name")
        require(len(names) == len(set(names)) and not {'int', 'sum'} & set(names), "binding collision")
        require(all(value_ok(v) for v in data.values()), "unresolved object/implicit dispatch")
        require(all(type(a) is Alias and type(a.target) is str and a.target in sources for a in aliases.values()),
                "only zero-prefix partial of a registered source function")
        self.functions = MappingProxyType({name: parse_function(src) for name, src in sources.items()})
        self.aliases = MappingProxyType(aliases)
        self.data = MappingProxyType(data)

    def binding(self, name):
        if name in self.functions: return ('function', name)
        if name in self.aliases: return ('partial', self.aliases[name].target)
        if name in ('int', 'sum'): return ('native', name)
        if name in self.data: return ('data', self.data[name])
        raise Refusal('unresolved binding: ' + str(name))
