"""Static opcode contract for the declared flat threshold rendering."""
import dis
from itertools import product

INPUTS = tuple(product((0, 1), repeat=3))
PARITY = tuple(sum(x) % 2 for x in INPUTS)
SHARED_WITNESS = ("def f(x):\n    a,b,c=x\n    s=a+b+c\n"
    "    h0=int(s>=1)\n    h1=int(s>=2)\n    h2=int(s>=3)\n"
    "    return int(h0-h1+h2>=1)\n")
XOR_WITNESS = "def f(x):\n    a,b,c=x\n    return (a^b)^c\n"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compiled(source, environment=None):
    namespace = {} if environment is None else dict(environment)
    exec(compile(source, "<registered-flat-threshold>", "exec"), namespace)
    fn = namespace["f"]
    instructions = tuple(dis.get_instructions(fn, adaptive=False, show_caches=False))
    require(not any(i.opcode in dis.hasjabs or i.opcode in dis.hasjrel
                    or i.opname in ("YIELD_VALUE", "RETURN_GENERATOR") for i in instructions),
            "outside straight-line coordinate")
    return len([i for i in instructions if i.opname not in ("RESUME", "CACHE")]), fn, instructions


def linear(weights, names):
    terms = [(w, n) for w, n in zip(weights, names) if w]
    require(terms, "nonempty flat form")
    def term(w, n):
        return n if w == 1 else "-" + n if w == -1 else str(w) + "*" + n
    text = term(*terms[0])
    for w, n in terms[1:]:
        text += ("+" + term(w, n)) if w > 0 else ("-" + term(-w, n))
    return text


def native_cost_contract():
    head = "def f(x):\n    a,b,c=x\n"
    base = compiled(head + "    return 0\n")[0]
    require(base == 6, "UNVERIFIABLE: opcode layout differs from registered BASE6")
    own, shared, output = {}, {}, {}
    for degree in range(1, 4):
        expression = "+".join(("a", "b", "c")[:degree])
        own[degree] = compiled(head + "    h=int(" + expression + ">=1)\n    return 0\n")[0] - base
        shared[degree] = compiled(head + "    s=" + expression + "\n    return 0\n")[0] - base
        require(own[degree] == 4 + 2 * degree and shared[degree] == 2 * degree,
                "UNVERIFIABLE: hidden/form opcode layout differs")
    with_s = head + "    s=a\n"
    shared_unit = (compiled(with_s + "    h=int(s>=1)\n    return 0\n")[0]
                   - compiled(with_s + "    return 0\n")[0])
    require(shared_unit == 6, "UNVERIFIABLE: shared threshold opcode layout differs")
    for degree in range(1, 7):
        names = ["h" + str(i) for i in range(degree)]
        start = head + "".join("    " + name + "=0\n" for name in names)
        output[degree] = (compiled(start + "    return int(" + "+".join(names) + ">=1)\n")[0]
                          - compiled(start + "    return 0\n")[0])
        require(output[degree] == 3 + 2 * degree, "UNVERIFIABLE: output opcode layout differs")
    return {"base": base, "own_hidden": {str(d): c for d, c in own.items()},
            "shared_form": {str(d): c for d, c in shared.items()}, "shared_unit": shared_unit,
            "output_increment": {str(d): c for d, c in output.items()},
            "contract": "flat syntax: BASE6, own>=4+2d, shared>=2d, unit>=6, output>=3+2r",
            "native_representatives_match": True}


def syntax_stress_controls():
    head = "def f(x):\n    a,b,c=x\n"; base = compiled(head + "    return 0\n")[0]
    checked = 0
    for weights in product((-3, -1, 0, 1, 3), repeat=3):
        degree = sum(w != 0 for w in weights)
        if not degree:
            continue
        expression = linear(weights, ("a", "b", "c"))
        own = compiled(head + "    h=int(" + expression + ">=1)\n    return 0\n")[0] - base
        shared = compiled(head + "    s=" + expression + "\n    return 0\n")[0] - base
        require(own >= 4 + 2 * degree and shared >= 2 * degree, "flat syntax undercuts lower law")
        checked += 1
    large = linear((10**100, -10**101, 1), ("a", "b", "c"))
    require(compiled(head + "    h=int(" + large + ">=1)\n    return 0\n")[0] - base >= 10,
            "large coefficient undercuts support floor")
    start = head + "".join("    p" + str(i) + "=0\n" for i in range(270))
    lower, _, instructions = compiled(start + "    h=int(p260+p261+p262>=1)\n    return 0\n")
    overhead = compiled(start + "    return 0\n")[0]
    require(lower - overhead >= 10, "extended operands undercut support floor")
    require(any(i.opname == "EXTENDED_ARG" for i in instructions), "extended-argument control vacuous")
    return {"signed_zero_large_support_patterns": checked, "large_integer_control": True,
            "extended_argument_control": True, "general_compiler_verified_by_sampling": False}


def certified_lower(shape, active_gates, total_support=6):
    require(type(active_gates) is int and active_gates >= 3, "need proved active-gate lower bound")
    if shape == "A":
        require(type(total_support) is int and max(6, active_gates) <= total_support <= 3 * active_gates,
                "need proved support-incidence bound")
        return 9 + 6 * active_gates + 2 * total_support
    require(shape == "B", "unknown registered shape")
    return 15 + 8 * active_gates
