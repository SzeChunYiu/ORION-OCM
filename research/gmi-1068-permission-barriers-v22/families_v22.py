"""Complete finite permission families with explicit history backpointers."""
from itertools import combinations
from core_v22 import need, records_checked, subset


def _sets(records, permission_count, *sets):
    records_checked(records, permission_count)
    for values in sets:
        subset(values, permission_count)
    return tuple(set(values) for values in sets)


def _powerset(values):
    ordered = sorted(values)
    return tuple(part for size in range(len(ordered) + 1)
                 for part in combinations(ordered, size))


def survivors(records, enabled, permission_count):
    allowed, = _sets(records, permission_count, enabled)
    return tuple(sorted(i for i, required in records if set(required) <= allowed))


def minimal_additions(records, baseline, available, permission_count):
    initial, universe = _sets(records, permission_count, baseline, available)
    need(initial <= universe, "baseline outside available universe")
    deficits = {frozenset(required) - initial for _, required in records
                if set(required) <= universe}
    return tuple(sorted(tuple(sorted(d)) for d in deficits
                        if not any(e < d for e in deficits)))


def blocks(records, available, blocker, permission_count):
    universe, removed = _sets(records, permission_count, available, blocker)
    need(removed <= universe, "deletion outside available universe")
    return not any(set(required) <= universe - removed for _, required in records)


def minimal_blockers(records, available, permission_count):
    universe, = _sets(records, permission_count, available)
    supports = [set(required) for _, required in records if set(required) <= universe]
    candidates = [frozenset(b) for b in _powerset(universe)
                  if all(set(b) & required for required in supports)]
    return tuple(sorted(tuple(sorted(b)) for b in candidates
                        if not any(c < b for c in candidates)))


def blocker_certificate(records, available, blocker, permission_count):
    universe, removed = _sets(records, permission_count, available, blocker)
    need(removed <= universe, "deletion outside available universe")
    live = [(i, set(required)) for i, required in records if set(required) <= universe]
    if any(not (required & removed) for _, required in live):
        return None
    certificate = []
    for permission in sorted(removed):
        witnesses = [i for i, required in live if required & removed == {permission}]
        if not witnesses:
            return None
        certificate.append((permission, min(witnesses)))
    return tuple(certificate)


def minimal_supports(records, permission_count):
    records_checked(records, permission_count)
    groups = {}
    for i, required in records:
        groups.setdefault(frozenset(required), []).append(i)
    return tuple(sorted((tuple(sorted(required)), tuple(sorted(ids)))
                        for required, ids in groups.items()
                        if not any(other < required for other in groups)))
