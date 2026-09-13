"""Constructive triangle and C5 messages; exact certificates, no measurements."""
from itertools import combinations, product
from joint_relation_model_v1 import (Relation, cover_protocol, fixed_bits, from_preimages,
                                     incidence_bound, joint_relation, minimum_cover, preimages)
from joint_relation_oracle_v1 import (joint_selector_optimum, product_selector_minimum,
                                      selector_optimum, verify_pair_protocol)


def check(value, reason):
    if not value:
        raise AssertionError(reason)


def triangle():
    relation = Relation(tuple(tuple(a for a in range(3) if a != x) for x in range(3)), 3)
    local = selector_optimum(relation.rows)
    decoder = ((0, 0), (1, 1), (2, 2))
    joint = joint_relation(relation, relation)
    protocol = cover_protocol(joint, tuple(a*3+b for a, b in decoder))
    oracle = joint_selector_optimum(relation.rows, relation.rows)
    check(local["width"] == 2 and oracle["width"] == 3, "triangle widths")
    records = verify_pair_protocol(relation.rows, relation.rows, protocol["encoder"], decoder)
    check(all(set(a) & set(b) for a, b in combinations(relation.rows, 2)), "pairwise compatibility")
    check(not set.intersection(*(set(row) for row in relation.rows)), "triple incompatibility")
    area = (len(joint.rows)+4-1)//4
    check(area == 3, "triangle area lower certificate")
    return dict(rows=relation.rows, local_width=2, product_width=4, shared_width=3,
                product_bits=fixed_bits(4), shared_bits=fixed_bits(3), area_lower=area,
                independent_selectors=oracle["selectors"], pairgraph_incorrect_width=1,
                decoder=decoder, encoder=protocol["encoder"], executions=records)


def c5_relation():
    return from_preimages(((0, 2), (1, 3), (2, 4), (0, 3), (1, 4)), 5)


def c5_construction():
    relation = c5_relation()
    sets = preimages(relation)
    pairs = tuple(product(range(5), repeat=2))
    masks = tuple(sum(1 << (x*5+y) for x in sets[a] for y in sets[b]) for a, b in pairs)
    full = (1 << 25)-1
    examined = 0
    for ids in combinations(range(25), 8):
        examined += 1
        union = 0
        for i in ids:
            union |= masks[i]
        if union == full:
            break
    else:
        raise AssertionError("eight-message construction absent")
    decoder = tuple(pairs[i] for i in ids)
    encoder = tuple(next(k for k, i in enumerate(ids) if masks[i] & (1 << p)) for p in range(25))
    return relation, encoder, decoder, examined


def c5():
    relation, encoder, decoder, examined = c5_construction()
    expected = ((0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (2, 3), (3, 2), (4, 4))
    check(decoder == expected and examined == 64566, "pinned constructive search")
    local = selector_optimum(relation.rows)
    separate = product_selector_minimum(relation.rows, relation.rows)
    check(local["width"] == 3 and separate["width"] == 9, "optimized local/product parent")
    bounds = incidence_bound(relation, relation, local["width"], local["width"])
    check(bounds["row"] == bounds["column"] == 8 and bounds["area"] == 7, "incidence stronger than area")
    executions = verify_pair_protocol(relation.rows, relation.rows, encoder, decoder)
    rows = tuple(sum(x in preimages(relation)[a] for a, b in decoder) for x in range(5))
    check(min(rows) >= 3 and sum(rows) == 16, "actual row/message incidences")
    check(len(set(encoder)) == 8, "all eight messages used")
    return dict(preimages=tuple(tuple(sorted(s)) for s in preimages(relation)), rows=relation.rows,
                local_width=3, product_width=9, shared_width=8, product_bits=4, shared_bits=3,
                bounds=bounds, local_selectors=local["selectors"], product_parent=separate,
                eight_subsets_examined=examined, decoder=decoder, encoder=encoder,
                actual_row_incidences=rows, executions=executions)
