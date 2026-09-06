"""Deterministic typed application closure after leading-Pi introduction.

No fixture/Lean names, target selector, arbitrary internal lambdas or induction.
Exhaustion concerns only this finite application fragment; FOUND is not acceptance.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import f0_terms as T


@dataclass(frozen=True)
class SearchLimits:
    max_application_depth: int = 5
    max_terms: int = 5000
    max_steps: int = 20000
    max_intro: int = 32
    max_nodes: int = 4096
    max_normalize: int = 20000


@dataclass(frozen=True)
class SearchResult:
    status: str
    candidate: list | None
    reason: str
    counters: dict[str, int]
    limits: dict[str, int]
    used_constants: tuple[int, ...] = ()


def search(goal, constants, limits=None):
    limits = SearchLimits() if limits is None else limits
    counters = {key:0 for key in ("introductions", "generated_terms", "applications", "index_probes", "type_checks")}
    settings = asdict(limits) if isinstance(limits, SearchLimits) else {}
    def result(status, reason, candidate=None):
        return SearchResult(status, None if candidate is None else T.to_data(candidate), reason,
                            dict(counters), settings,
                            () if candidate is None else tuple(sorted(T.const_dependencies(candidate))))
    try:
        if not settings or any(type(v) is not int or v < (0 if k=="max_application_depth" else 1)
                               for k,v in settings.items()):
            raise T.TermError("invalid registered limits")
        original = T.from_data(goal, max_nodes=limits.max_nodes)
        registry = T.constants_from_data(constants)
        def normal(t): return T.normalize(t, limits.max_normalize)
        def infer(t, ctx=()):
            counters["type_checks"] += 1
            return normal(T.infer(t, registry, ctx, fuel=limits.max_normalize))
        for declared in registry.values():
            if infer(declared)[0] != "sort":
                raise T.TermError("constant signature is not a closed type")
        if infer(original)[0] != "sort":
            raise T.TermError("goal is not a closed type")
        target, context, introductions = normal(original), (), []
        while target[0] == "pi":
            if len(introductions) >= limits.max_intro:
                raise T.TermLimit("max_intro reached")
            domain, target = target[1], target[2]
            introductions.append(domain)
            context = (domain,) + context
            counters["introductions"] += 1
        target = normal(target)
        prefix_nodes = sum(1 + T.node_count(t) for t in introductions)
        body_bound = limits.max_nodes - prefix_nodes
        if body_bound < 1:
            raise T.TermLimit("max_nodes cannot hold introduced telescope")
        entries, seen, by_type = [], set(), {}
        def finish(term):
            for domain in reversed(introductions): term = ("lam", domain, term)
            counters["type_checks"] += 1
            T.check(term, original, registry, fuel=limits.max_normalize)
            if T.node_count(term) > limits.max_nodes:
                raise T.TermLimit("max_nodes exceeded by complete term")
            return result("FOUND", "Typed proposal; independent kernel acceptance required", term)
        def add(term, ty, depth, size):
            if term in seen: return False
            if counters["generated_terms"] >= limits.max_terms:
                raise T.TermLimit("max_terms reached")
            seen.add(term)
            entry = (term, normal(ty), depth, size)
            entries.append(entry)
            by_type.setdefault(entry[1], []).append(entry)
            counters["generated_terms"] += 1
            return True
        seeds = [("var", i) for i in range(len(context))]
        seeds += [("const", i) for i in sorted(registry)]
        for term in seeds:
            ty = infer(term, context)
            add(term, ty, 0, 1)
            if ty == target: return finish(term)
        for depth in range(1, limits.max_application_depth + 1):
            # Freeze the preceding layers: an argument at this depth belongs to
            # a later application layer and must not enter the current frontier.
            prior = tuple(entries)
            prior_index = {ty:tuple(values) for ty,values in by_type.items()}
            added = 0
            for fn, ftype, fd, fnodes in prior:
                if ftype[0] != "pi": continue
                counters["index_probes"] += 1
                for arg, _, ad, anodes in prior_index.get(normal(ftype[1]), ()):
                    if max(fd, ad) != depth - 1: continue
                    size = 1 + fnodes + anodes
                    if size > body_bound: continue
                    term = ("app", fn, arg)
                    if term in seen: continue
                    if counters["applications"] >= limits.max_steps:
                        raise T.TermLimit("max_steps reached")
                    counters["applications"] += 1
                    # Independent inference rechecks the typed-index proposal.
                    ty = infer(term, context)
                    added += add(term, ty, depth, size)
                    if ty == target: return finish(term)
            if not added: break
        return result("EXHAUSTED_REGISTERED_BOUND", "No inhabitant in registered depth/node-bounded application closure; not theorem falsity")
    except T.TermLimit as exc:
        return result("CANNOT_CHECK", "Operational bound: " + str(exc))
    except (T.TermError, RecursionError) as exc:
        return result("CANNOT_CHECK", "Unsupported or invalid task: " + str(exc))
