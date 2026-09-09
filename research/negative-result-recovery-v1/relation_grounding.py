"""Exact bank-relative rule grounding by cached typed relations and indexed joins.

Research successor, not the frozen #203 implementation. The native matcher,
DV check, action schema and downstream proof checker are unchanged. A timeout
still propagates as UNKNOWN. Cache lifetime is exactly one compile invocation.
"""
from __future__ import annotations

from collections import Counter
import hashlib
from typing import Any
import finite_search as FS


def compile_parent(parent, bank, work, limit=200000, syntax_checker=None):
    if type(limit) is not int or limit < 1:
        raise ValueError("positive instance bound required")
    formulas = [["|-"] + row["tokens"] for row in bank["wff"]]
    if len({tuple(f) for f in formulas}) != len(formulas):
        raise ValueError("duplicate bank formula outside qualified scope")
    if any(not f or not all(type(t) is str for t in f) for f in formulas):
        raise ValueError("invalid bank formula")
    actions = []
    relation_cache = {}
    type_cache = {}
    counts = [Counter(f) for f in formulas]
    checker = syntax_checker or FS.M.T.syntax
    tick = getattr(work, "checkpoint", lambda: None)

    def count(key, n=1):
        work[key] = work.get(key, 0) + n

    def typed(kind, tokens):
        # The captured checker and context cannot change during this invocation.
        # Only the checker's explicit ValueError is finite non-membership.
        # SyntaxUnknown, MemoryError and other exceptions are never cached.
        tick()
        key = (kind, tuple(tokens))
        count("relation_type_requests")
        if key in type_cache:
            count("relation_type_hits")
            ok = type_cache[key]
        else:
            count("relation_type_misses")
            try:
                checker(kind, tokens)
                ok = True
            except ValueError:
                ok = False
            type_cache[key] = ok
        if not ok:
            raise ValueError("not a member of registered syntax grammar")
        return True

    def relation(pattern, floating):
        types = {h["statement"][1]: h["statement"][0] for h in floating}
        relevant = tuple(sorted((v, t) for v, t in types.items() if v in pattern))
        key = (tuple(pattern), relevant)
        if key in relation_cache:
            count("relation_cache_hits")
            return relation_cache[key]
        count("relation_cache_misses")
        literals = Counter(t for t in pattern if t not in types)
        rows = []
        # Every relation row records its *original* formula index. Join order
        # changes never permute the native proof's hypothesis slots.
        for index, formula in enumerate(formulas):
            tick()
            count("relation_formula_candidates")
            if any(n > counts[index].get(t, 0) for t, n in literals.items()):
                count("relation_literal_exclusions")
                continue
            for mapping in FS.M.match(pattern, formula, floating, {}, work, typed):
                rows.append((mapping, index))
                count("relation_rows")
                if len(rows) > limit:
                    raise ValueError("INSTANCE_BOUND: relation rows")
        entry = {"variables": frozenset(v for v, _ in relevant),
                 "rows": rows, "indexes": {}}
        relation_cache[key] = entry
        return entry

    def candidates(rel, bound):
        keys = tuple(sorted(rel["variables"] & bound.keys()))
        if not keys:
            return rel["rows"]
        if keys not in rel["indexes"]:
            index = {}
            for mapping, slot in rel["rows"]:
                tick()
                count("relation_index_rows")
                k = tuple(tuple(mapping[v]) for v in keys)
                index.setdefault(k, []).append((mapping, slot))
            rel["indexes"][keys] = index
        count("relation_index_lookups")
        return rel["indexes"][keys].get(tuple(tuple(bound[v]) for v in keys), ())

    for row in parent:
        tick()
        count("parent_contracts_scanned")
        if row["statement"][0] != "|-":
            continue
        floating = row["floating"]
        variables = {h["statement"][1] for h in floating}
        patterns = [row["statement"]] + [h["statement"] for h in row["essential"]]
        # Build the most literal-selective relations first; a truly empty
        # conjunct makes the join empty without constructing free products.
        preliminary = sorted(range(len(patterns)),
                             key=lambda i: (-sum(t not in variables for t in patterns[i]), i))
        relations = {}
        for slot in preliminary:
            rel = relation(patterns[slot], floating)
            if not rel["rows"]:
                count("empty_rule_relations")
                break
            relations[slot] = rel
        else:
            # Index lookup selectivity depends on the bindings already obtained.
            # Depth-first joins do not retain a potentially huge partial product.
            def join(remaining, mapping, slots):
                tick()
                count("relation_join_states")
                if not remaining:
                    if set(mapping) != variables:
                        raise ValueError("unbound mandatory variable")
                    count("dv_checks")
                    if not FS.M.dv_valid(row, mapping):
                        return
                    action = {"kind": "primitive", "label": row["label"],
                              "substitution": mapping, "query": slots[0],
                              "premises": [slots[i] for i in range(1, len(patterns))]}
                    action["id"] = hashlib.sha256(FS.C.canonical(action)).hexdigest()
                    actions.append(action)
                    count("primitive_instances")
                    if len(actions) > limit:
                        raise ValueError("INSTANCE_BOUND: complete instantiations")
                    return
                choices = [(len(selected := candidates(relations[i], mapping)), i, selected)
                           for i in remaining]
                _, slot, selected = min(choices, key=lambda item: (item[0], item[1]))
                rest = tuple(i for i in remaining if i != slot)
                for other, index in selected:
                    tick()
                    count("relation_join_candidates")
                    if any(mapping[k] != other[k] for k in mapping.keys() & other.keys()):
                        raise RuntimeError("join index returned incompatible binding")
                    join(rest, {**mapping, **other}, {**slots, slot: index})
            join(tuple(range(len(patterns))), {}, {})
    count("relation_distinct_type_entries", len(type_cache))
    count("relation_distinct_patterns", len(relation_cache))
    return actions
