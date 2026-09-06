"""Exposed typed task data only; no proof body, Lean text or search implementation."""


def _v(name): return ("local", name)
def _app(fn, *args):
    for arg in args: fn = ("app", fn, arg)
    return fn

def _pi(name, domain, body): return ("bind", name, domain, body)
def _arrow(domain, body): return _pi("_unused", domain, body)
def _close(bindings, body):
    for name, domain in reversed(bindings): body = _pi(name, domain, body)
    return body


def _lower(term, context=()):
    if term[0] == "local": return ["var", context.index(term[1])]
    if term[0] == "bind":
        return ["pi", _lower(term[2], context), _lower(term[3], (term[1],) + context)]
    if len(term) == 2: return list(term)
    return [term[0], _lower(term[1], context), _lower(term[2], context)]


def f0_fixture(*, rename="", reverse_premises=False, change=None):
    if change not in (None, "missing_member", "reversed_subset", "wrong_witness"):
        raise ValueError("unknown exposed fixture control")
    def name(s): return rename + s
    def v(s): return _v(name(s))
    def pi(n, d, b): return _pi(name(n), d, b)
    def close(bs, b): return _close([(name(n), d) for n, d in bs], b)
    ty, prop = ("sort", 1), ("sort", 0)
    H, A, V, W, q = map(v, ("H", "A", "V", "W", "q"))
    h, answer, actual = map(v, ("h", "answer", "actual"))
    eq = lambda x: _app(("const",0), A, _app(q,x), answer)
    predicate = _arrow(H, prop)
    common = [("H",ty),("A",ty),("V",predicate)]
    tail = [("q",_arrow(H,A)),("answer",A)]
    subset = pi("h",H,_arrow(_app(W,h),_app(V,h)))
    agreement = pi("h",H,_arrow(_app(V,h),eq(h)))
    sound = close(common + tail + [("actual",H),("member",_app(V,actual)),("agreement",agreement)],eq(actual))
    refinement = close(common + [("W",predicate)] + tail + [("subset",subset),("agreement",agreement)],
                       pi("h",H,_arrow(_app(W,h),eq(h))))
    eq_type = close([("A",ty),("x",A),("y",A)],prop)
    context = common + [("W",predicate)] + tail + [("actual",H)]
    witness = actual
    if change == "wrong_witness":
        context.append(("other",H)); witness = v("other")
    if change == "reversed_subset": subset = pi("h",H,_arrow(_app(V,h),_app(W,h)))
    premises = [("member",_app(W,witness)),("subset",subset),("agreement",agreement)]
    if change == "missing_member": premises = premises[1:]
    if reverse_premises: premises.reverse()
    return {"goal":_lower(close(context+premises,eq(actual))),
            "constants":{0:_lower(eq_type),1:_lower(sound),2:_lower(refinement)}}


def chain_fixture(length):
    if type(length) is not int or not 0 <= length <= 8:
        raise ValueError("registered chain fixture range")
    bindings = [("P"+str(i),("sort",0)) for i in range(length+1)]
    bindings += [("f"+str(i),_arrow(_v("P"+str(i)),_v("P"+str(i+1)))) for i in range(length)]
    bindings.append(("x",_v("P0")))
    return {"goal":_lower(_close(bindings,_v("P"+str(length)))),"constants":{}}
