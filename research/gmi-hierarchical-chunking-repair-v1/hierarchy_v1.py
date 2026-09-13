"""Exact scalar policy synthesis for a supplied acyclic compiled-artifact register."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache


def price(x):
    if type(x) not in (int, F) or x < 0:
        raise ValueError("exact finite nonnegative price required")
    return F(x)


@dataclass(frozen=True)
class Register:
    primitives: tuple
    costs: tuple
    bodies: tuple
    admission: tuple
    invocation: tuple
    dispatch: tuple
    delivery: tuple = ()  # explicit empty tuple declares zero delivery prices

    def __post_init__(self):
        if any(type(x) is not tuple for x in (self.primitives, self.costs, self.bodies,
                                             self.admission, self.invocation, self.dispatch, self.delivery)):
            raise ValueError("immutable explicit tables required")
        if not self.primitives or len(set(self.primitives)) != len(self.primitives):
            raise ValueError("nonempty distinct primitive register")
        if any(type(a) is not str or len(a) != 1 for a in self.primitives):
            raise ValueError("single-symbol primitives required")
        if self.delivery and len(self.delivery)!=len(self.primitives):
            raise ValueError('complete delivery prices required')
        if len(self.costs) != len(self.primitives):
            raise ValueError("complete primitive prices required")
        n = len(self.bodies)
        if any(len(x) != n for x in (self.admission, self.invocation, self.dispatch)):
            raise ValueError("complete rule prices required")
        for x in self.costs + self.admission + self.invocation + self.dispatch + self.delivery:
            price(x)
        for j, body in enumerate(self.bodies):
            if type(body) is not tuple or not body:
                raise ValueError("nonempty immutable body required")
            for t in body:
                if not ((type(t) is str and t in self.primitives) or
                        (type(t) is int and 0 <= t < j)):
                    raise ValueError("forward/cyclic/unknown body reference")

    def valid_token(self, t):
        return ((type(t) is str and t in self.primitives) or
                (type(t) is int and 0 <= t < len(self.bodies)))

    def delivery_price(self, a):
        return price(self.delivery[self.primitives.index(a)]) if self.delivery else F(0)

    def expansion(self, t):
        if not self.valid_token(t):
            raise ValueError("unknown token")
        if type(t) is str:
            return t
        return ''.join(self.expansion(c) for c in self.bodies[t])


def solve(reg, workload, allowed):
    if type(workload) is not tuple or any(not reg.valid_token(t) for t in workload):
        raise ValueError("complete immutable workload required")
    allowed = frozenset(allowed)
    if any(type(j) is not int or not 0 <= j < len(reg.bodies) for j in allowed):
        raise ValueError("unknown admission option")
    counts = dict(token_states=0, candidate_transitions=0)

    def offer(table, mask, cost, trace):
        counts['candidate_transitions'] += 1
        if mask not in table or cost < table[mask][0]:
            table[mask] = (cost, trace)

    def sequence(tokens, mask):
        table = {mask: (F(0), ())}
        for t in tokens:
            nxt = {}
            for old, (cost, trace) in table.items():
                for new, extra, events in token(t, old):
                    offer(nxt, new, cost+extra, trace+events)
            table = nxt
        return table

    @lru_cache(None)
    def token(t, mask):
        counts['token_states'] += 1
        if type(t) is str:
            c = price(reg.costs[reg.primitives.index(t)])
            return ((mask, c, (('primitive', t, c),)),)
        table = {}
        if mask & (1 << t):
            c = price(reg.invocation[t])
            offer(table, mask, c, (('invoke', t, c),))
        d = price(reg.dispatch[t])
        for new, (cost, events) in sequence(reg.bodies[t], mask).items():
            trace = (('expand', t, d),)+events
            offer(table, new, cost+d, trace)
            if t in allowed and not mask & (1 << t):
                s = price(reg.admission[t])
                offer(table, new | (1 << t), cost+d+s, trace+(('retain', t, s),))
        return tuple((m, c, e) for m, (c, e) in sorted(table.items()))

    results = sequence(workload, 0)
    final, (cost, events) = min(results.items(), key=lambda item: (item[1][0], item[0]))
    emitted = ''.join(t if kind == 'primitive' else reg.expansion(t)
                      for kind, t, _ in events if kind in ('primitive', 'invoke'))
    expected = ''.join(reg.expansion(t) for t in workload)
    if emitted != expected or sum(e[2] for e in events) != cost:
        raise ValueError("execution trace/ledger disagreement")
    delivery_events=tuple(('deliver',a,reg.delivery_price(a)) for a in emitted)
    delivered=sum(e[2] for e in delivery_events)
    return dict(cost=cost+delivered, reconstruction_cost=cost, delivery_cost=delivered,
                final_mask=final, events=events, delivery_events=delivery_events, output=emitted,
                final_costs={m:c+delivered for m,(c,_) in results.items()}, analysis=counts,
                representation=dict(rules=len(reg.bodies),
                    body_tokens=sum(map(len,reg.bodies)),workload_tokens=len(workload),
                    expanded_rule_symbols=sum(len(reg.expansion(j)) for j in range(len(reg.bodies))),
                    retained_expanded_symbols=sum(len(reg.expansion(j)) for j in range(len(reg.bodies))
                                                  if final & (1 << j))))
