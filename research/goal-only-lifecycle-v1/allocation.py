"""Prospective set-algebra development allocation, never imported by the solver.

Membership truth tables are an independent finite semantics oracle for this
intersection/union/difference grammar. They are NOT supplied proof routes.
This is development data, not protected independent replication.
"""
from __future__ import annotations
from collections import defaultdict
from functools import lru_cache
import hashlib
from itertools import permutations, product
import json
import sys
from pathlib import Path
import argparse
from lifecycle import encoded, identity, read_json, require, write_new, checked_file, raw_id

VARIABLES = ("A", "B", "C")
OPS = ("i^i", "u.", "\\")
SALT = "ocm-goal-only-cold-development-v1-20260909"
MAX_OPERATORS = 3
LIMITS = {"max_decisions": 3, "max_instances": 100000,
          "max_token_states": 2000000, "soft_wall_s": 8.0}
# Selection is fixed before any solve result; readiness counts are emitted too.
# At most one pair per left/right term-shape family, then hash-ranked, no refill
# after unsupported or failed results. The small quota is an engineering budget.
POSITIVE_CAP = 8
NEGATIVE_CAP = 2

@lru_cache(None)
def trees(n):
    if n == 0:
        return VARIABLES
    return tuple((op, a, b) for left in range(n) for op in OPS
                 for a in trees(left) for b in trees(n - 1 - left))

def tokens(t):
    return [t] if isinstance(t, str) else ["(", *tokens(t[1]), t[0], *tokens(t[2]), ")"]

def evaluate(t, assignment):
    if isinstance(t, str):
        return assignment[t]
    a, b = evaluate(t[1], assignment), evaluate(t[2], assignment)
    return (a and b) if t[0] == "i^i" else ((a or b) if t[0] == "u." else (a and not b))

def mask(t):
    return sum(int(evaluate(t, dict(zip(VARIABLES, bits)))) << i
               for i, bits in enumerate(product((False, True), repeat=3)))

def shape(t):
    return "_" if isinstance(t, str) else (t[0], shape(t[1]), shape(t[2]))

def canonical(statement):
    # Simultaneous global renaming, never matching official proof-label sequences.
    variants = []
    for order in permutations(VARIABLES):
        renaming = dict(zip(VARIABLES, order))
        variants.append(tuple(renaming.get(x, x) for x in statement))
    return min(variants)

def rank(value):
    return hashlib.sha256(SALT.encode() + b"\0" + encoded(value)).hexdigest()

def population(manifest, source_rows):
    # All three variables occur in each term, to preserve the mandatory frame.
    ts = sorted((t for t in trees(MAX_OPERATORS) if set(tokens(t)) & set(VARIABLES) == set(VARIABLES)), key=lambda t: tuple(tokens(t)))
    groups = defaultdict(list)
    for t in ts:
        groups[mask(t)].append(t)
    supplied = set()
    for row in source_rows.values():
        if row["kind"] not in {"$a", "$p"} or row.get("essential") or row.get("dv"):
            continue
        floating = row.get("floating", [])
        if len(floating) != 3 or any(h["statement"][0] != "class" for h in floating):
            continue
        renaming = dict(zip((h["statement"][1] for h in floating), VARIABLES))
        statement = [renaming.get(t, t) for t in row["statement"]]
        supplied.add(canonical(statement))
    candidates = {}
    counts = {"term_count": len(ts), "semantic_classes": len(groups), "exact_or_alpha_supplied_exclusions": 0,
              "positive_pairs_before_canonicalization": 0}
    for same in groups.values():
        for j, a in enumerate(same):
            for b in same[j + 1:]:
                statement = ["|-", *tokens(a), "=", *tokens(b)]
                key = canonical(statement)
                reverse = canonical(["|-", *tokens(b), "=", *tokens(a)])
                key = min(key, reverse)
                counts["positive_pairs_before_canonicalization"] += 1
                if key in supplied:
                    counts["exact_or_alpha_supplied_exclusions"] += 1
                    continue
                family = encoded(sorted([shape(a), shape(b)], key=encoded)).decode()
                value = {"query": list(key), "truth": True, "family": family}
                if key not in candidates:
                    candidates[key] = value
    positives = sorted(candidates.values(), key=rank)
    selected = []
    families = set()
    for p in positives:
        if p["family"] not in families:
            families.add(p["family"])
            selected.append(p)
            if len(selected) == POSITIVE_CAP:
                break
    # Negative controls are adjacent hash-ranked terms with different truth tables.
    ordered = sorted(ts, key=lambda t: rank(tokens(t)))
    negatives = []
    for a, b in zip(ordered, ordered[1:]):
        if mask(a) != mask(b):
            q = list(canonical(["|-", *tokens(a), "=", *tokens(b)]))
            negatives.append({"query": q, "truth": False, "family": "negative-control"})
    selected += sorted(negatives, key=rank)[:NEGATIVE_CAP]
    selected.sort(key=rank)
    context = {"schema": "native.typed-context.v1", "dv": [], "parameters": [
        {"id": "V" + str(i), "type": "class", "variable": v, "floating_label": "c" + v}
        for i, v in enumerate(VARIABLES)]}
    tasks = [{"schema": "ordinary.goal-task.v1", "query": s["query"], "premises": [],
              "context": context, "limits": dict(LIMITS)} for s in selected]
    counts.update(canonical_positive_pairs=len(positives), positive_families=len({s["family"] for s in positives}),
                  selected_positive=sum(s["truth"] for s in selected), selected_negative=sum(not s["truth"] for s in selected))
    return tasks, {"schema": "ordinary.goal-development-allocation.v1", "salt": SALT,
                   "grammar": {"variables": VARIABLES, "operators": OPS, "operators_per_term": MAX_OPERATORS},
                   "limits": LIMITS, "counts": counts, "manifest": identity(manifest),
                   "population": identity(tasks), "scorer_only": [dict(s, task=identity(t)) for s, t in zip(selected, tasks)],
                   "scope": "Prospective authored development allocation; semantic families are not independent experimental lifetimes."}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--prefix", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    require(not args.out.exists(), "fresh allocation directory")
    manifest = read_json(args.manifest)
    raw = checked_file(args.prefix, manifest["joined_prefix"])
    pins = read_json(Path(__file__).with_name("DEPENDENCIES.json"))
    source = pins["files"]["engine/vendor/trace_source.py"]
    path = args.repo / source["path"]
    checked_file(path, source["identity"])
    # Indexing a frozen training prefix only; no verifier or goal search executes.
    import importlib.util
    spec = importlib.util.spec_from_file_location("allocation_training_index", path)
    index = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(index)
    source_rows, _ = index.index(raw)
    tasks, audit = population(manifest, source_rows)
    audit["training_index_source"] = source
    audit["joined_prefix"] = raw_id(raw)
    write_new(args.out / "TASKS.json", encoded(tasks) + b"\n")
    write_new(args.out / "ALLOCATION.json", encoded(audit) + b"\n")
    print(json.dumps(audit["counts"], sort_keys=True))
