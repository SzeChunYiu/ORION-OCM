from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, FrozenSet, Optional, Tuple

F = Fraction


def _require_fraction(value, name):
    if not isinstance(value, Fraction):
        raise TypeError("%s must be Fraction" % name)
    return value


def _require_budget(value, name):
    _require_fraction(value, name)
    if value < 0 or value > 1:
        raise ValueError("%s must be in [0,1]" % name)
    return value


def _domain(values, name="domain"):
    values = tuple(values)
    if not values:
        raise ValueError("%s must be nonempty" % name)
    if not all(isinstance(v, Fraction) for v in values):
        raise TypeError("%s values must be Fraction" % name)
    if len(set(values)) != len(values):
        raise ValueError("%s contains duplicates" % name)
    if tuple(sorted(values)) != values:
        raise ValueError("%s must be sorted canonically" % name)
    return values


def _fstr(x):
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def _set_strings(values):
    return [_fstr(v) for v in sorted(values)]


@dataclass(frozen=True)
class NodeSpec:
    name: str
    domain: Tuple[Fraction, ...]
    parents: Tuple[str, ...]
    relation: Optional[Tuple[Tuple[Tuple[Fraction, ...], Fraction], ...]]
    beta: Fraction
    unknown_relation: bool


@dataclass(frozen=True)
class ActivatedContract:
    root_names: Tuple[str, ...]
    root_joint: FrozenSet[Tuple[Fraction, ...]]
    alpha: Fraction


class CompositionCampaign:
    def __init__(self):
        self._specs: Dict[str, NodeSpec] = {}
        self._outputs: Tuple[str, ...] = ()
        self._locked = False
        self._active: Optional[ActivatedContract] = None

    def register_node(self, name, domain, parents=(), relation=None,
                      beta=F(0), unknown_relation=False):
        if self._locked:
            raise RuntimeError("campaign locked after source activation")
        if not isinstance(name, str) or not name:
            raise ValueError("node name must be nonempty string")
        if name in self._specs:
            raise ValueError("duplicate node name")
        domain = _domain(domain, "domain[%s]" % name)
        parents = tuple(parents)
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate parent name")
        if name in parents:
            raise ValueError("self-cycle")
        _require_budget(beta, "beta")
        if not parents:
            if relation is not None or unknown_relation:
                raise ValueError("root cannot have a relation")
            if beta != 0:
                raise ValueError("root beta must be zero")
        else:
            if unknown_relation:
                if relation is not None:
                    raise ValueError("unknown relation cannot also be explicit")
                if beta != 0:
                    raise ValueError("universal unknown relation has beta zero")
            elif relation is None:
                raise ValueError("non-root requires relation or unknown marker")
            else:
                relation = tuple(relation)
                if not relation:
                    raise ValueError("explicit relation must be nonempty")
                seen = set()
                for entry in relation:
                    if not isinstance(entry, tuple) or len(entry) != 2:
                        raise ValueError("relation entry must be (parents, output)")
                    parent_values, out = entry
                    parent_values = tuple(parent_values)
                    if len(parent_values) != len(parents):
                        raise ValueError("relation parent arity mismatch")
                    if not all(isinstance(v, Fraction) for v in parent_values):
                        raise TypeError("relation parent values must be Fraction")
                    if not isinstance(out, Fraction):
                        raise TypeError("relation output must be Fraction")
                    key = (parent_values, out)
                    if key in seen:
                        raise ValueError("duplicate relation entry")
                    seen.add(key)
                relation = tuple((tuple(pv), out) for pv, out in relation)

        self._specs[name] = NodeSpec(
            name=name, domain=domain, parents=parents, relation=relation,
            beta=beta, unknown_relation=bool(unknown_relation),
        )
        return self._specs[name]

    def set_outputs(self, outputs):
        if self._locked:
            raise RuntimeError("campaign locked after source activation")
        outputs = tuple(outputs)
        if not outputs:
            raise ValueError("outputs must be nonempty")
        if len(set(outputs)) != len(outputs):
            raise ValueError("duplicate output")
        self._outputs = outputs

    @property
    def specs(self):
        return dict(self._specs)

    def _validate_graph(self):
        if not self._specs:
            raise ValueError("graph is empty")
        if not self._outputs:
            raise ValueError("outputs not set")
        for out in self._outputs:
            if out not in self._specs:
                raise ValueError("unknown output node")
        for spec in self._specs.values():
            for p in spec.parents:
                if p not in self._specs:
                    raise ValueError("unknown parent %s" % p)

        indeg = {n: 0 for n in self._specs}
        children = {n: [] for n in self._specs}
        for n, spec in self._specs.items():
            indeg[n] = len(spec.parents)
            for p in spec.parents:
                children[p].append(n)
        ready = sorted(n for n, d in indeg.items() if d == 0)
        order = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for child in sorted(children[n]):
                indeg[child] -= 1
                if indeg[child] == 0:
                    ready.append(child)
                    ready.sort()
        if len(order) != len(self._specs):
            raise ValueError("composition graph contains cycle")

        for n in order:
            spec = self._specs[n]
            if not spec.parents or spec.unknown_relation:
                continue
            parent_domains = [self._specs[p].domain for p in spec.parents]
            allowed_parent_tuples = set(itertools.product(*parent_domains))
            outputs_by_parent = {pv: set() for pv in allowed_parent_tuples}
            for pv, out in spec.relation:
                if pv not in allowed_parent_tuples:
                    raise ValueError("out-of-domain relation parent tuple")
                if out not in spec.domain:
                    raise ValueError("out-of-domain relation output")
                outputs_by_parent[pv].add(out)
            if any(not outs for outs in outputs_by_parent.values()):
                raise ValueError("relation must be total over registered parent domains")
        return tuple(order)

    def activate(self, root_joint, alpha):
        if self._locked:
            raise RuntimeError("source already activated")
        order = self._validate_graph()
        roots = tuple(sorted(n for n in order if not self._specs[n].parents))
        _require_budget(alpha, "alpha")
        root_joint = frozenset(tuple(row) for row in root_joint)
        if not root_joint:
            raise ValueError("root joint confidence set must be nonempty")
        for row in root_joint:
            if len(row) != len(roots):
                raise ValueError("root joint assignment arity mismatch")
            for name, value in zip(roots, row):
                if not isinstance(value, Fraction):
                    raise TypeError("root joint values must be Fraction")
                if value not in self._specs[name].domain:
                    raise ValueError("root joint value outside domain")
        self._locked = True
        self._active = ActivatedContract(roots, root_joint, alpha)
        return self._active

    def _relation_map(self, spec):
        if spec.unknown_relation:
            parent_domains = [self._specs[p].domain for p in spec.parents]
            return {pv: frozenset(spec.domain) for pv in itertools.product(*parent_domains)}
        out = {}
        for pv, y in spec.relation:
            out.setdefault(pv, set()).add(y)
        return {pv: frozenset(ys) for pv, ys in out.items()}

    def topological_order(self):
        return self._validate_graph()

    def global_assignments(self):
        if not self._locked or self._active is None:
            raise RuntimeError("activate source before propagation")
        order = self._validate_graph()
        roots = self._active.root_names
        partials = [dict(zip(roots, row)) for row in sorted(self._active.root_joint)]
        for n in order:
            spec = self._specs[n]
            if not spec.parents:
                continue
            rmap = self._relation_map(spec)
            next_partials = []
            for assignment in partials:
                key = tuple(assignment[p] for p in spec.parents)
                for out in sorted(rmap[key]):
                    new = dict(assignment)
                    new[n] = out
                    next_partials.append(new)
            partials = next_partials
        return tuple(partials)

    def global_set(self, node):
        if node not in self._specs:
            raise ValueError("unknown node")
        return frozenset(a[node] for a in self.global_assignments())

    def local_sets(self):
        if not self._locked or self._active is None:
            raise RuntimeError("activate source before propagation")
        order = self._validate_graph()
        result = {}
        for idx, root in enumerate(self._active.root_names):
            result[root] = frozenset(row[idx] for row in self._active.root_joint)
        for n in order:
            spec = self._specs[n]
            if not spec.parents:
                continue
            if spec.unknown_relation:
                result[n] = frozenset(spec.domain)
                continue
            rmap = self._relation_map(spec)
            values = set()
            for pv in itertools.product(*(sorted(result[p]) for p in spec.parents)):
                values.update(rmap[pv])
            result[n] = frozenset(values)
        return result

    def failure_budget(self):
        if not self._locked or self._active is None:
            raise RuntimeError("activate source first")
        raw = self._active.alpha + sum((s.beta for s in self._specs.values()), F(0))
        return raw, max(F(0), F(1) - raw)

    def output_terminal(self, node):
        values = self.global_set(node)
        if len(values) == 1:
            return "IDENTIFIED"
        seen = set()
        stack = [node]
        unknown = False
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            spec = self._specs[n]
            unknown = unknown or spec.unknown_relation
            stack.extend(spec.parents)
        if unknown:
            return "CANNOT_IDENTIFY_UNKNOWN_RELATION"
        return "SET_VALUED_UNCERTAINTY"


def joint_from_marginals(root_names, root_domains, marginal_sets, alpha_by_root):
    root_names = tuple(root_names)
    if len(set(root_names)) != len(root_names) or not root_names:
        raise ValueError("root_names must be unique and nonempty")
    sets = []
    total_alpha = F(0)
    for name in root_names:
        if name not in root_domains or name not in marginal_sets or name not in alpha_by_root:
            raise ValueError("missing marginal root contract")
        domain = _domain(root_domains[name], "root_domain[%s]" % name)
        values = tuple(marginal_sets[name])
        if not values:
            raise ValueError("marginal set must be nonempty")
        if not all(isinstance(v, Fraction) for v in values):
            raise TypeError("marginal values must be Fraction")
        if not set(values).issubset(set(domain)):
            raise ValueError("marginal set outside domain")
        _require_budget(alpha_by_root[name], "alpha[%s]" % name)
        total_alpha += alpha_by_root[name]
        sets.append(tuple(sorted(set(values))))
    joint = frozenset(itertools.product(*sets))
    return joint, total_alpha, max(F(0), F(1) - total_alpha)


def affine_interval_hull(x_lo, x_hi, a, b, e_lo=F(0), e_hi=F(0)):
    for value in (x_lo, x_hi, a, b, e_lo, e_hi):
        _require_fraction(value, "interval argument")
    if x_lo > x_hi or e_lo > e_hi:
        raise ValueError("invalid interval")
    corners = [a*x + b + e for x in (x_lo, x_hi) for e in (e_lo, e_hi)]
    return min(corners), max(corners), tuple(sorted(corners))


def _build_shared_ancestor():
    c = CompositionCampaign()
    c.register_node("x", (F(-1), F(1)))
    c.register_node("a", (F(-1), F(1)), ("x",),
                    (((F(-1),), F(-1)), ((F(1),), F(1))))
    c.register_node("b", (F(-1), F(1)), ("x",),
                    (((F(-1),), F(-1)), ((F(1),), F(1))))
    rel_y = tuple(((a,b), a-b) for a in (F(-1),F(1)) for b in (F(-1),F(1)))
    c.register_node("y", (F(-2), F(0), F(2)), ("a","b"), rel_y)
    c.set_outputs(("y",))
    c.activate(((F(-1),), (F(1),)), F(1,20))
    return c


def _build_nonlinear():
    c = CompositionCampaign()
    xdom=(F(-2),F(-1),F(1),F(2))
    zdom=(F(-1),F(1))
    c.register_node("x", xdom)
    c.register_node("z", zdom)
    c.register_node("sq", (F(1),F(4)), ("x",), tuple(((x,), x*x) for x in xdom))
    outdom=(F(0),F(2),F(3),F(5))
    c.register_node("out", outdom, ("sq","z"),
                    tuple(((sq,z), sq+z) for sq in (F(1),F(4)) for z in zdom))
    c.set_outputs(("out",))
    c.activate(tuple((x,z) for x in xdom for z in zdom), F(0))
    return c


def _build_setvalued():
    c=CompositionCampaign()
    c.register_node("u",(F(0),F(1)))
    rel=(((F(0),),F(0)),((F(0),),F(1)),((F(1),),F(1)),((F(1),),F(2)))
    c.register_node("s",(F(0),F(1),F(2)),("u",),rel)
    c.register_node("y",(F(0),F(2),F(4)),("s",),
                    tuple(((s,),F(2)*s) for s in (F(0),F(1),F(2))))
    c.set_outputs(("y",))
    c.activate(((F(0),),(F(1),)),F(0))
    return c


def _build_unknown():
    c=CompositionCampaign()
    c.register_node("x",(F(0),))
    c.register_node("q",(F(0),F(1),F(2)),("x",),unknown_relation=True)
    c.register_node("y",(F(1),F(2),F(3)),("q",),
                    tuple(((q,),q+1) for q in (F(0),F(1),F(2))))
    c.set_outputs(("y",))
    c.activate(((F(0),),),F(0))
    return c


def _marginal_dependence_control():
    atoms=set(range(20)); fail1={0}; fail2={1}
    good1=atoms-fail1; good2=atoms-fail2; joint=good1 & good2
    return {
        "marginal_1": _fstr(F(len(good1),20)),
        "marginal_2": _fstr(F(len(good2),20)),
        "actual_joint": _fstr(F(len(joint),20)),
        "union_bound_lower": _fstr(F(1)-F(1,20)-F(1,20)),
        "independence_product": _fstr(F(19,20)*F(19,20)),
        "independence_used": False,
        "bound_tight": F(len(joint),20)==F(9,10),
    }


def _operator_dependence_control():
    atoms=set(range(200)); source_fail=set(range(10)); beta1_fail={10,11}; beta2_fail={12}
    good=atoms-source_fail-beta1_fail-beta2_fail
    product=F(19,20)*F(99,100)*F(199,200)
    bound=F(1)-F(1,20)-F(1,100)-F(1,200)
    return {
        "actual_joint_good": _fstr(F(len(good),200)),
        "union_bound_lower": _fstr(bound),
        "failure_sum": _fstr(F(13,200)),
        "independence_product": _fstr(product),
        "independence_used": False,
        "bound_tight": F(len(good),200)==bound,
        "success_events_independent": F(len(good),200)==product,
    }


def build_receipt():
    shared=_build_shared_ancestor(); nonlinear=_build_nonlinear()
    setv=_build_setvalued(); unknown=_build_unknown()
    lo,hi,corners=affine_interval_hull(F(1,4),F(3,4),F(-2),F(3),F(-1,10),F(1,10))
    raw,cover=shared.failure_budget()
    return {
        "schema":"GMIUncertaintyCompositionResultV1",
        "issue":759,
        "claim_ceiling":"DEPENDENCY_AWARE_UNCERTAINTY_COMPOSITION_AT_REGISTERED_FINITE_DAG_SCOPE",
        "shared_ancestor":{"global_y":_set_strings(shared.global_set("y")),
                           "local_y":_set_strings(shared.local_sets()["y"]),
                           "strict_over_enclosure":shared.global_set("y") < shared.local_sets()["y"],
                           "source_failure":_fstr(raw),"coverage_lower_bound":_fstr(cover)},
        "nonlinear":{"global_out":_set_strings(nonlinear.global_set("out")),
                     "local_out":_set_strings(nonlinear.local_sets()["out"]),
                     "global_equals_local":nonlinear.global_set("out")==nonlinear.local_sets()["out"]},
        "set_valued":{"global_y":_set_strings(setv.global_set("y"))},
        "unknown_relation":{"global_q":_set_strings(unknown.global_set("q")),
                            "global_y":_set_strings(unknown.global_set("y")),
                            "terminal":unknown.output_terminal("y")},
        "marginal_root_dependence":_marginal_dependence_control(),
        "operator_failure_dependence":_operator_dependence_control(),
        "affine_parent_regression":{"hull":[_fstr(lo),_fstr(hi)],
                                    "corners":[_fstr(x) for x in corners]},
        "independence_assumption":False,
    }


if __name__=="__main__":
    print(json.dumps(build_receipt(),sort_keys=True,indent=2))
