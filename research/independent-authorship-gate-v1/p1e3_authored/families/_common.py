"""Shared assembly helpers for the implication-system studio package.

Pure stdlib, no filesystem, no network. Every family module builds a raw core
(dict with elements/implications/base/excluded/weights/goals) and hands it to
`make_instance`, which computes audit-only expected answers by exact fixpoint
and brute-force subset enumeration, then enforces the hard bounds.
"""

HARD_BOUNDS = {
    "elements": 24, "implications": 64, "base": 24,
    "excluded": 12, "goals": 8, "addable": 16, "weight_min": 1, "weight_max": 99,
}


def closure(implications, start):
    """Smallest superset of `start` closed under the rules (fixpoint)."""
    held = set(start)
    changed = True
    while changed:
        changed = False
        for rule in implications:
            if all(a in held for a in rule["if"]):
                for b in rule["then"]:
                    if b not in held:
                        held.add(b)
                        changed = True
    return held


def addable_atoms(core):
    return set(core["elements"]) - closure(core["implications"], core["base"])


def _cost(atom, weights):
    return weights.get(atom, 1)


def min_seed(core):
    """Brute-force minimum-cost seed. Returns dict or IMPOSSIBLE marker."""
    addable = sorted(addable_atoms(core))
    excl = set(core["excluded"])
    candidates = [a for a in addable if a not in excl]
    weights = core["weights"]
    subsets = []
    n = len(candidates)
    for mask in range(1 << n):
        s = [candidates[i] for i in range(n) if mask >> i & 1]
        subsets.append(s)
    subsets.sort(key=lambda s: (sum(_cost(a, weights) for a in s), len(s), s))
    for s in subsets:
        grown = closure(core["implications"], core["base"] + s)
        if grown & excl:
            continue
        if set(core["goals"]) <= grown:
            return {"cost": sum(_cost(a, weights) for a in s),
                    "seed": sorted(s)}
    return {"status": "IMPOSSIBLE"}


def check_bounds(core):
    els = set(core["elements"])
    assert len(els) <= HARD_BOUNDS["elements"], "too many elements"
    assert len(core["implications"]) <= HARD_BOUNDS["implications"], "too many rules"
    assert len(core["base"]) <= HARD_BOUNDS["base"], "base too large"
    assert len(core["excluded"]) <= HARD_BOUNDS["excluded"], "excluded too large"
    assert len(core["goals"]) <= HARD_BOUNDS["goals"], "goals too large"
    for w in core["weights"].values():
        assert HARD_BOUNDS["weight_min"] <= w <= HARD_BOUNDS["weight_max"], "weight out of range"
    refs = set(core["base"]) | set(core["excluded"]) | set(core["goals"])
    refs |= set(core["weights"])
    for r in core["implications"]:
        refs |= set(r["if"]) | set(r["then"])
    assert refs <= els, "dangling atom reference: %s" % (refs - els)
    assert len(addable_atoms(core)) <= HARD_BOUNDS["addable"], "too many addable atoms"


def make_instance(family, instance_id, core, surface):
    check_bounds(core)
    grown = closure(core["implications"], core["base"])
    goals_held = sorted(set(core["goals"]) & grown)
    ms = min_seed(core)
    intent = {
        "intent_role": "audit_only",
        "expected_closure_size": len(grown),
        "expected_goals_reachable": goals_held,
        "expected_min_seed": ms,
        "note": surface.pop("intent_note", ""),
    }
    inst = {"family": family, "instance_id": instance_id,
            "core": core, "surface": surface, "intent": intent}
    return inst
