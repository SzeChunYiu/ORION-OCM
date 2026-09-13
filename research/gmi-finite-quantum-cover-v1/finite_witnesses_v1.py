"""Independent finite witnesses and protocol-class boundary controls."""
from fractions import Fraction as F
from itertools import combinations, product
from classical_parent_v1 import classical_optimum
from quantum_witness_v1 import verify, verify_mixed
from rational_matrix_v1 import (add, dot, identity, multiply, ray_state, require,
                                scale, trace, transpose)


def relation_census():
    options = tuple(frozenset(a for a in range(3) if mask & (1 << a)) for mask in range(1, 8))
    counts, encoders, pairs = {1: 0, 2: 0, 3: 0}, 0, 0
    for row in product(options, repeat=3):
        task = {"actions": 3, "allowed": tuple((allowed,) for allowed in row)}
        common = set.intersection(*(set(s) for s in row))
        distinct_singletons = all(len(s) == 1 for s in row) and len(set(row)) == 3
        # Independent analytic lower certificate, only for this 3-input/1-context register.
        lower = 1 if common else 3 if distinct_singletons else 2
        parent = classical_optimum(task)
        require(parent["dimension"] == lower, "classical upper/quantum lower mismatch")
        result = verify(task, parent["rays"], parent["factors"])
        require(result["dimension"] == lower, "constructed upper dimension differs")
        counts[lower] += 1
        encoders += parent["encoders_examined"]
        pairs += result["promised_pairs_checked"]
    require(counts == {1: 169, 2: 168, 3: 6}, "incomplete relational census")
    return {"tasks": 343, "dimension_histogram": counts, "promised_pairs_checked": pairs,
            "classical_encoders_examined": encoders,
            "quantum_lower_basis": "common-action obstruction and three orthogonal forced outputs"}


def mixed_support_controls():
    basis = identity(3)
    factors = ((ray_state(basis[0]), ray_state(basis[1]), ray_state(basis[2])),)
    task = {"actions": 3, "allowed": ((frozenset((0, 1)),), (frozenset((2,)),))}
    selected = (basis[0], basis[1], (F(3, 5), F(4, 5), F(0)))
    checked, changed = 0, 0
    for denominator in range(2, 10):
        weight = F(1, denominator)
        mixtures = (((weight, basis[0]), (1 - weight, basis[1])), ((F(1), basis[2]),))
        mixed = verify_mixed(task, mixtures, factors)
        for v in selected:
            require(v[2] == 0 and dot(v, v) == 1, "pure vector left positive support")
            pure = verify(task, (v, basis[2]), factors)
            checked += 1
            changed += int(pure["probabilities"] != mixed)
    require(checked == changed == 24, "response-vs-adequacy control collapsed")
    return {"positive_mixtures": 8, "supported_pure_choices": checked,
            "response_distributions_changed": changed, "adequacy_preserved": True}


def random_access_controls():
    inputs = tuple(product((0, 1), repeat=2))
    task = {"actions": 2, "allowed": tuple(tuple(frozenset((x[y],))
            for y in range(2)) for x in inputs)}
    # Every pair differs at an available receiver index, forcing K4 orthogonality.
    conflicting = sum(any(x[y] != z[y] for y in range(2))
                      for x, z in combinations(inputs, 2))
    require(conflicting == 6, "random-access lower clique incomplete")
    parent = classical_optimum(task)
    require(parent["dimension"] == 4, "bare random-access parent")
    checked = verify(task, parent["rays"], parent["factors"])
    informed = {"actions": 2, "allowed": tuple(tuple(
        frozenset((x[y],)) if y == known else None for y in range(2))
        for x in inputs for known in range(2))}
    informed_parent = classical_optimum(informed)
    require(informed_parent["dimension"] == 2, "sender-query-informed positive control")
    verify(informed, informed_parent["rays"], informed_parent["factors"])
    return {"original_quantum_lower_dimension": 4, "original_constructed_dimension": 4,
            "original_promised_pairs": checked["promised_pairs_checked"],
            "sender_also_knows_index_dimension": 2, "same_interface": False}


def factor_orientation_control():
    task = {"actions": 2, "allowed": ((frozenset((0,)),), (frozenset((1,)),))}
    factors = ((((0, 1), (0, 0)), ((0, 0), (1, 0))),)
    result = verify(task, identity(2), factors)
    # Non-symmetric factors make Bv differ from the required transpose(B)v.
    require(factors[0][0] != transpose(factors[0][0]), "orientation control is vacuous")
    return {"dimension": 2, "promised_pairs_checked": result["promised_pairs_checked"],
            "non_symmetric_factor_control": True}


def assistance_control():
    initial = (1, 0, 0, 1)
    local = (((1, 0), (0, 1)), ((0, 1), (1, 0)),
             ((1, 0), (0, -1)), ((0, 1), (-1, 0)))
    def tensor(a, b):
        return tuple(tuple(a[i][j] * b[k][l] for j in range(2) for l in range(2))
                     for i in range(2) for k in range(2))
    require(all(multiply(transpose(u), u) == identity(2) for u in local), "sender operation illegal")
    rays = tuple(tuple(dot(row, initial) for row in tensor(u, identity(2))) for u in local)
    require(all(dot(u, v) == 0 for u, v in combinations(rays, 2)), "Bell decoding conflict")
    factors = (tuple(ray_state(v) for v in rays),)
    task = {"actions": 4, "allowed": tuple((frozenset((x,)),) for x in range(4))}
    verify(task, rays, factors)
    return {"sent_subsystem_dimension": 2, "preshared_receiver_dimension": 2,
            "joint_receiver_dimension": 4, "exact_messages": 4,
            "bare_identity_task_minimum_dimension": 4,
            "unassisted_protocol_class": False}


def nonprojective_control():
    task = {"actions": 3, "allowed": ((frozenset((0, 1)),), (frozenset((2,)),))}
    factors = ((((F(3, 5), 0), (0, 0)), ((F(4, 5), 0), (0, 0)),
                ((0, 0), (0, 1))),)
    result = verify(task, identity(2), factors)
    effect = multiply(factors[0][0], transpose(factors[0][0]))
    require(multiply(effect, effect) != effect, "POVM control is accidentally projective")
    require(result["probabilities"][0][2] == (F(9, 25), F(16, 25), F(0)),
            "nonprojective exact probabilities differ")
    return {"dimension": 2, "outcomes": 3, "nonprojective": True,
            "first_input_probabilities": result["probabilities"][0][2],
            "isometry": result["isometries"][0]}


def shared_seed_control():
    task = {"actions": 2, "allowed": ((frozenset((0,)),), (frozenset((1,)),))}
    basis = identity(2)
    rays = (basis, tuple(reversed(basis)))
    effects = tuple(tuple(ray_state(v) for v in encoding) for encoding in rays)
    # Both matched seed branches encode x xor seed and undo that same seed.
    branches = tuple(verify(task, encoding, (measurement,))
                     for encoding, measurement in zip(rays, effects))
    correlated = tuple(sum((F(1, 2) * b["probabilities"][x][2][x] for b in branches), F(0))
                       for x in range(2))
    independent = []
    for x in range(2):
        rho = scale(F(1, 2), add(ray_state(rays[0][x]), ray_state(rays[1][x])))
        effect = scale(F(1, 2), add(effects[0][x], effects[1][x]))
        independent.append(trace(multiply(rho, effect)))
    require(correlated == (F(1), F(1)), "correlated seed protocol failed")
    require(independent == [F(1, 2), F(1, 2)], "correlation-loss control collapsed")
    return {"fixed_seed_dimensions": [b["dimension"] for b in branches],
            "correlated_success_each_input": correlated,
            "independently_averaged_success_each_input": independent,
            "feasibility_preserved_by_fixing_seed": True,
            "independent_averaging_preserves_protocol": False}
