from __future__ import annotations
from fractions import Fraction
import itertools, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALUES = (Fraction(0), Fraction(1,2), Fraction(1))
PREPS = ("p0","p1","p2")
EFFECTS = ("e0","e1","e2")

def sig(table, p, effects=EFFECTS):
    return tuple(table[(p,e)] for e in effects)

def operational_equiv(table, p, q, effects=EFFECTS):
    return sig(table,p,effects) == sig(table,q,effects)

def quotient_by_signature(table, preps=PREPS, effects=EFFECTS):
    groups = {}
    for p in preps:
        groups.setdefault(sig(table,p,effects), []).append(p)
    return tuple(sorted(tuple(v) for v in groups.values()))

def quotient_by_pairwise_graph(table, preps=PREPS, effects=EFFECTS):
    unseen=set(preps); comps=[]
    while unseen:
        root=min(unseen); stack=[root]; comp=set()
        while stack:
            p=stack.pop()
            if p in comp: continue
            comp.add(p); unseen.discard(p)
            for q in preps:
                if q not in comp and operational_equiv(table,p,q,effects):
                    stack.append(q)
        comps.append(tuple(sorted(comp)))
    return tuple(sorted(comps))

def separating_effect(table,p,q,effects=EFFECTS):
    for e in effects:
        if table[(p,e)] != table[(q,e)]:
            return e
    return None

def build_table(row):
    table={}; i=0
    for p in PREPS:
        for e in EFFECTS:
            table[(p,e)] = row[i]; i += 1
    return table

def main():
    table_count=0
    equivalent_pairs=0
    separated_pairs=0
    quotient_hist=Counter()
    relation_failures=0
    separator_failures=0
    oracle_disagreements=0
    reconstruction_failures=0

    for row in itertools.product(VALUES, repeat=len(PREPS)*len(EFFECTS)):
        table=build_table(row)
        table_count += 1
        for p in PREPS:
            relation_failures += int(not operational_equiv(table,p,p))
        for p,q in itertools.product(PREPS, repeat=2):
            relation_failures += int(operational_equiv(table,p,q) != operational_equiv(table,q,p))
        for p,q,r in itertools.product(PREPS, repeat=3):
            bad = operational_equiv(table,p,q) and operational_equiv(table,q,r) and not operational_equiv(table,p,r)
            relation_failures += int(bad)
        for p,q in itertools.combinations(PREPS,2):
            if operational_equiv(table,p,q):
                equivalent_pairs += 1
            else:
                separated_pairs += 1
                separator_failures += int(separating_effect(table,p,q) is None)
        q1=quotient_by_signature(table)
        q2=quotient_by_pairwise_graph(table)
        oracle_disagreements += int(q1 != q2)
        quotient_hist[len(q1)] += 1
        seen={}
        for cls in q1:
            s=sig(table,cls[0])
            if s in seen:
                reconstruction_failures += 1
            seen[s]=cls
            for p in cls:
                reconstruction_failures += int(sig(table,p) != s)

    alias_table={
        ("p","e0"):Fraction(0), ("p","e1"):Fraction(1),
        ("alias","e0"):Fraction(0), ("alias","e1"):Fraction(1),
        ("q","e0"):Fraction(1), ("q","e1"):Fraction(1),
    }
    alias_collapsed = sig(alias_table,"p",("e0","e1")) == sig(alias_table,"alias",("e0","e1"))
    sep = separating_effect(alias_table,"p","q",("e0","e1"))

    restricted = {("a","e0"):Fraction(0),("b","e0"):Fraction(0),
                  ("a","e1"):Fraction(0),("b","e1"):Fraction(1)}
    restricted_equiv = operational_equiv(restricted,"a","b",("e0",))
    expanded_equiv = operational_equiv(restricted,"a","b",("e0","e1"))

    assert table_count == 3**9
    assert relation_failures == 0
    assert separator_failures == 0
    assert oracle_disagreements == 0
    assert reconstruction_failures == 0
    assert alias_collapsed and sep is not None
    assert restricted_equiv and not expanded_equiv
    assert sum(quotient_hist.values()) == table_count

    result={
        "status":"GREEN",
        "registered_scope":"3 preparations x 3 binary-outcome effects; response probabilities in {0,1/2,1}",
        "response_tables_exhausted":table_count,
        "equivalent_unordered_pairs":equivalent_pairs,
        "separated_unordered_pairs":separated_pairs,
        "equivalence_relation_failures":relation_failures,
        "separator_failures":separator_failures,
        "independent_quotient_oracle_disagreements":oracle_disagreements,
        "state_reconstruction_failures":reconstruction_failures,
        "quotient_class_count_histogram":{str(k):quotient_hist[k] for k in sorted(quotient_hist)},
        "syntactic_alias_hostile":"COLLAPSED_AS_OPERATIONALLY_EQUIVALENT",
        "separating_context_hostile":sep,
        "incomplete_test_family_hostile":"RESTRICTED_EQUIVALENT__EXPANDED_SEPARATED",
        "state_role":"I->A",
        "effect_role":"A->I",
        "forbidden_promotions":[
            "UNIVERSAL_CONTEXTUAL_EQUIVALENCE_FROM_INCOMPLETE_TESTS",
            "QUOTIENT_REPRESENTED_INSIDE_MACHINE",
            "BISIMULATION_EQUALS_OPERATIONAL_EQUIVALENCE_UNCONDITIONALLY",
            "ABSOLUTE_STATE_ONTOLOGY_PROVEN"
        ],
        "claim_ceiling":"AJ2_OPERATIONAL_EQUIVALENCE_AND_STATE_RECONSTRUCTION_AT_FINITE_REGISTERED_TEST_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
