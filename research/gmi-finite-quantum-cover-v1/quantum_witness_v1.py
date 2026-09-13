"""Exact rational-ray/factor certificates for the declared unassisted interface."""
from rational_matrix_v1 import (add, dot, identity, matrix, multiply, mv, ray_state,
                               require, scale, trace, transpose, vector, zero)


def task_shape(task):
    require(type(task) is dict and set(task) == {"actions", "allowed"}, "task fields")
    k, allowed = task["actions"], task["allowed"]
    require(type(k) is int and k > 0, "nonempty finite action register required")
    require(type(allowed) in (list, tuple) and bool(allowed), "empty input register")
    require(all(type(row) in (list, tuple) and bool(row) for row in allowed), "empty contexts")
    ny = len(allowed[0])
    require(all(len(row) == ny for row in allowed), "unequal context register")
    promised = 0
    for row in allowed:
        for options in row:
            if options is None:
                continue
            require(type(options) in (set, frozenset) and bool(options),
                    "promised acceptable sets must be nonempty sets")
            require(all(type(a) is int and 0 <= a < k for a in options), "action label")
            promised += 1
    require(promised > 0, "empty promise is outside this witness register")
    return len(allowed), ny, k, promised


def validate_factors(task, factors, d):
    _, ny, k, _ = task_shape(task)
    require(type(factors) in (list, tuple) and len(factors) == ny, "measurement contexts")
    effects, isometries = [], []
    for row in factors:
        require(type(row) in (list, tuple) and len(row) == k, "measurement outcomes")
        blocks = tuple(matrix(b, d) for b in row)
        local = tuple(multiply(b, transpose(b)) for b in blocks)
        total = zero(d)
        for effect in local:
            total = add(total, effect)
        require(total == identity(d), "POVM completeness")
        isometry = tuple(line for b in blocks for line in transpose(b))
        require(multiply(transpose(isometry), isometry) == identity(d), "isometry illegal")
        effects.append(local)
        isometries.append(isometry)
    return tuple(effects), tuple(isometries)


def verify(task, rays, factors):
    nx, _, _, promised = task_shape(task)
    require(type(rays) in (list, tuple) and len(rays) == nx, "sender state register")
    vectors = tuple(vector(v) for v in rays)
    d = len(vectors[0])
    require(all(len(v) == d and dot(v, v) > 0 for v in vectors), "normalized nonzero states")
    effects, isometries = validate_factors(task, factors, d)
    probabilities = []
    for x, row in enumerate(task["allowed"]):
        rho = ray_state(vectors[x])
        for y, allowed in enumerate(row):
            if allowed is None:
                continue
            direct = tuple(trace(multiply(rho, e)) for e in effects[y])
            from_factor = tuple(dot(mv(transpose(matrix(b, d)), vectors[x]),
                                    mv(transpose(matrix(b, d)), vectors[x])) /
                                dot(vectors[x], vectors[x]) for b in factors[y])
            require(direct == from_factor, "Born/factor disagreement")
            require(sum(direct) == 1 and all(p >= 0 for p in direct), "probability contract")
            require(all(p == 0 for a, p in enumerate(direct) if a not in allowed),
                    "forbidden output")
            probabilities.append((x, y, direct))
    return {"dimension": d, "promised_pairs_checked": promised,
            "probabilities": probabilities, "isometries": isometries,
            "receiver_composite_dimension": d * task["actions"]}


def verify_mixed(task, mixtures, factors):
    nx, _, _, _ = task_shape(task)
    require(len(mixtures) == nx, "mixed sender state register")
    d = len(mixtures[0][0][1])
    effects, _ = validate_factors(task, factors, d)
    probabilities = []
    for x, mixture in enumerate(mixtures):
        require(bool(mixture), "empty mixture")
        weights = vector(tuple(w for w, _ in mixture))
        require(all(w >= 0 for w in weights) and sum(weights) == 1, "mixture weights")
        rho = zero(d)
        for weight, (_, v) in zip(weights, mixture):
            require(len(v) == d, "mixture dimensions")
            rho = add(rho, scale(weight, ray_state(v)))
        require(trace(rho) == 1, "mixed normalization")
        for y, allowed in enumerate(task["allowed"][x]):
            if allowed is None:
                continue
            values = tuple(trace(multiply(rho, e)) for e in effects[y])
            require(sum(values) == 1, "mixed measurement mass")
            require(all(p == 0 for a, p in enumerate(values) if a not in allowed),
                    "mixed forbidden output")
            probabilities.append((x, y, values))
    return probabilities


def task_fingerprint(task):
    import hashlib
    import json
    task_shape(task)
    value = {"actions": task["actions"], "allowed": [
        [None if cell is None else sorted(cell) for cell in row] for row in task["allowed"]]}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_registered(task, rays, factors, expected_task_sha256):
    require(task_fingerprint(task) == expected_task_sha256, "registered obligation/promise drift")
    return verify(task, rays, factors)
