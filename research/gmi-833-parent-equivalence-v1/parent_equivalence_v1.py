#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from collections import defaultdict, deque

CLAIM_CEILING = "GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE"
FORBIDDEN_PROMOTIONS = [
    "ALL_GMI_EQUIVALENCE_IS_MYHILL_NERODE",
    "TRACE_EQUIVALENCE_EQUALS_BISIMULATION_UNIVERSALLY",
    "CLASSICAL_SUFFICIENCY_EQUALS_PREDICTIVE_SUFFICIENCY",
    "ALL_PSRS_ARE_MINIMAL",
    "UNIVERSAL_STOCHASTIC_MINIMALITY",
    "COMPLETE_GMI",
]


def canonical_partition(blocks):
    return tuple(sorted((tuple(sorted(block)) for block in blocks), key=lambda b: (b[0], len(b), b)))


def partition_from_class_map(class_map):
    blocks = defaultdict(list)
    for state, cls in class_map.items():
        blocks[cls].append(state)
    return canonical_partition(blocks.values())


def deterministic_behavior_partition(states, actions, output, transition):
    states = tuple(states)
    actions = tuple(actions)
    cls = {s: output[s] for s in states}
    while True:
        signatures = {s: (output[s], tuple(cls[transition[(s, a)]] for a in actions)) for s in states}
        sig_to_id = {sig: i for i, sig in enumerate(sorted(set(signatures.values()), key=repr))}
        nxt = {s: sig_to_id[signatures[s]] for s in states}
        if all((cls[x] == cls[y]) == (nxt[x] == nxt[y]) for x in states for y in states):
            return partition_from_class_map(nxt)
        cls = nxt


def deterministic_bisimulation_partition(states, actions, output, transition):
    states = tuple(states)
    relation = {(p, q) for p in states for q in states if output[p] == output[q]}
    while True:
        bad = {(p, q) for p, q in relation if any((transition[(p, a)], transition[(q, a)]) not in relation for a in actions)}
        if not bad:
            break
        relation -= bad
    seen, blocks = set(), []
    for p in states:
        if p not in seen:
            block = {q for q in states if (p, q) in relation and (q, p) in relation}
            seen |= block
            blocks.append(block)
    return canonical_partition(blocks)


def reachable_states(start, actions, transition):
    seen, q = {start}, deque([start])
    while q:
        s = q.popleft()
        for a in actions:
            t = transition[(s, a)]
            if t not in seen:
                seen.add(t)
                q.append(t)
    return seen


def dfa_witness():
    states, actions = (0, 1, 2, 3), ("a", "b")
    output = {0: 0, 1: 0, 2: 0, 3: 1}
    transition = {(0,"a"):1,(0,"b"):2,(1,"a"):3,(1,"b"):1,(2,"a"):3,(2,"b"):2,(3,"a"):3,(3,"b"):3}
    behavior = deterministic_behavior_partition(states, actions, output, transition)
    return {"states":states,"actions":actions,"output":output,"transition":transition,
            "reachable":tuple(sorted(reachable_states(0, actions, transition))),
            "behavior_partition":behavior,
            "bisimulation_partition":deterministic_bisimulation_partition(states, actions, output, transition)}


def exhaustive_deterministic_census():
    states, actions = (0,1,2), (0,1)
    total = 0
    for out_bits in product((0,1), repeat=3):
        output = dict(zip(states, out_bits))
        for targets in product(states, repeat=6):
            transition = {(s,a):targets[2*s+a] for s in states for a in actions}
            total += 1
            if deterministic_behavior_partition(states, actions, output, transition) != deterministic_bisimulation_partition(states, actions, output, transition):
                return {"machines":total,"expected_machines":5832,"mismatch_count":1}
    return {"machines":total,"expected_machines":5832,"mismatch_count":0}


def nfa_trace_set(start, transitions, max_depth):
    traces, frontier = {""}, {(start,"")}
    for _ in range(max_depth):
        nxt = set()
        for state, word in frontier:
            for label, target in transitions.get(state,()):
                nw = word + label
                traces.add(nw)
                nxt.add((target,nw))
        frontier = nxt
    return tuple(sorted(traces, key=lambda x:(len(x),x)))


def nfa_strong_bisimilar(left, right, transitions):
    states = sorted(set(transitions) | {t for edges in transitions.values() for _,t in edges})
    relation = {(p,q) for p in states for q in states}
    while True:
        bad = set()
        for p,q in relation:
            pe, qe = transitions.get(p,()), transitions.get(q,())
            if any(not any(l==l2 and (p2,q2) in relation for l2,q2 in qe) for l,p2 in pe) or any(not any(l==l2 and (p2,q2) in relation for l2,p2 in pe) for l,q2 in qe):
                bad.add((p,q))
        if not bad:
            break
        relation -= bad
    return (left,right) in relation


def nondeterministic_hostile():
    transitions = {"p":(("a","pb"),("a","pc")),"pb":(("b","t"),),"pc":(("c","t"),),"q":(("a","qbc"),),"qbc":(("b","t"),("c","t")),"t":()}
    p, q = nfa_trace_set("p",transitions,2), nfa_trace_set("q",transitions,2)
    return {"p_traces":p,"q_traces":q,"trace_equal":p==q,"strong_bisimilar":nfa_strong_bisimilar("p","q",transitions)}


def predictive_partition(laws):
    buckets = defaultdict(list)
    for h,law in laws.items():
        buckets[tuple(law)].append(h)
    return canonical_partition(buckets.values())


def is_predictive_sufficient(statistic, laws):
    hs = tuple(laws)
    return all(statistic[a] != statistic[b] or tuple(laws[a]) == tuple(laws[b]) for i,a in enumerate(hs) for b in hs[i+1:])


def predictive_sufficiency_witness():
    laws = {"hA":(Fraction(1,2),Fraction(1,2)),"hB":(Fraction(1,2),Fraction(1,4)),"hC":(Fraction(1,2),Fraction(1,2))}
    quotient, hs = predictive_partition(laws), tuple(laws)
    mins, min_count = set(), None
    assignments_checked = 0
    for labels in product(range(3), repeat=3):
        assignments_checked += 1
        stat = dict(zip(hs,labels))
        if not is_predictive_sufficient(stat,laws):
            continue
        n = len(set(labels))
        blocks = canonical_partition([[h for h in hs if stat[h]==v] for v in set(labels)])
        if min_count is None or n < min_count:
            min_count, mins = n, {blocks}
        elif n == min_count:
            mins.add(blocks)
    short = {h:(laws[h][0],) for h in hs}
    full = {h:tuple(laws[h]) for h in hs}
    return {"quotient":quotient,"quotient_classes":len(quotient),"minimum_value_count":min_count,"minimum_partitions":tuple(sorted(mins,key=repr)),"statistic_assignments_checked":assignments_checked,"short_tests_separate":predictive_partition(short)==quotient,"short_partition":predictive_partition(short),"full_tests_separate":predictive_partition(full)==quotient}


def finite_statistic_sufficient(sample_space, theta_distributions, statistic):
    for t in set(statistic[x] for x in sample_space):
        fiber = [x for x in sample_space if statistic[x]==t]
        conditionals=[]
        for dist in theta_distributions.values():
            mass = sum((dist.get(x,Fraction(0)) for x in fiber), Fraction(0))
            if mass:
                conditionals.append(tuple(dist.get(x,Fraction(0))/mass for x in fiber))
        if conditionals and any(c != conditionals[0] for c in conditionals[1:]):
            return False
    return True


def sufficiency_incomparability_witness():
    sample_a=(0,1)
    theta_a={0:{0:Fraction(1),1:Fraction(0)},1:{0:Fraction(0),1:Fraction(1)}}
    stat_a={0:0,1:0}
    future_a={0:(Fraction(1,2),Fraction(1,2)),1:(Fraction(1,2),Fraction(1,2))}
    sample_b=((0,0),(0,1),(1,0),(1,1))
    theta_b={0:{(0,0):Fraction(1,2),(0,1):Fraction(1,2)},1:{(1,0):Fraction(1,2),(1,1):Fraction(1,2)}}
    stat_b={h:h[0] for h in sample_b}
    future_b={h:((Fraction(1),Fraction(0)) if h[1]==0 else (Fraction(0),Fraction(1))) for h in sample_b}
    return {"A_predictive_sufficient":is_predictive_sufficient(stat_a,future_a),"A_parameter_sufficient":finite_statistic_sufficient(sample_a,theta_a,stat_a),"B_parameter_sufficient":finite_statistic_sufficient(sample_b,theta_b,stat_b),"B_predictive_sufficient":is_predictive_sufficient(stat_b,future_b)}


def jsonable(obj):
    if isinstance(obj,Fraction):
        return f"{obj.numerator}/{obj.denominator}"
    if isinstance(obj,dict):
        return {str(k):jsonable(v) for k,v in obj.items()}
    if isinstance(obj,(tuple,list,set)):
        return [jsonable(v) for v in obj]
    return obj


def build_receipt():
    dfa,census,nfa,ps,suf = dfa_witness(),exhaustive_deterministic_census(),nondeterministic_hostile(),predictive_sufficiency_witness(),sufficiency_incomparability_witness()
    checks={"mn_reachable_four_state_witness":dfa["reachable"]==(0,1,2,3),"mn_exact_three_class_quotient":dfa["behavior_partition"]==((0,),(1,2),(3,)),"deterministic_behavior_equals_bisim_fixture":dfa["behavior_partition"]==dfa["bisimulation_partition"],"deterministic_exhaustive_census_complete":census["machines"]==census["expected_machines"]==5832,"deterministic_exhaustive_census_no_mismatch":census["mismatch_count"]==0,"nondeterministic_trace_sets_equal":nfa["trace_equal"],"nondeterministic_strong_bisimulation_fails":not nfa["strong_bisimilar"],"predictive_quotient_two_classes":ps["quotient_classes"]==2,"predictive_quotient_minimum_cardinality":ps["minimum_value_count"]==ps["quotient_classes"],"predictive_minimum_partition_unique":ps["minimum_partitions"]==(ps["quotient"],),"incomplete_psr_tests_fail_to_separate":not ps["short_tests_separate"],"complete_registered_psr_tests_separate":ps["full_tests_separate"],"predictive_not_parameter_implication_hostile":suf["A_predictive_sufficient"] and not suf["A_parameter_sufficient"],"parameter_not_predictive_implication_hostile":suf["B_parameter_sufficient"] and not suf["B_predictive_sufficient"]}
    return jsonable({"schema":"GMI_833_PARENT_EQUIVALENCE_RESULT_V1","verdict":"GREEN" if all(checks.values()) else "RED","claim_ceiling":CLAIM_CEILING,"forbidden_promotions":FORBIDDEN_PROMOTIONS,"checks":checks,"mn_witness":{"behavior_partition":dfa["behavior_partition"],"reachable":dfa["reachable"],"quotient_state_count":len(dfa["behavior_partition"])},"deterministic_bisimulation_census":census,"nondeterministic_hostile":nfa,"predictive_sufficiency":{"quotient":ps["quotient"],"minimum_value_count":ps["minimum_value_count"],"sufficient_statistic_assignments_checked":ps["statistic_assignments_checked"],"short_partition":ps["short_partition"],"full_tests_separate":ps["full_tests_separate"]},"sufficiency_incomparability":suf,"parent_map":{"myhill_nerode":"EXACT_SPECIALIZATION_UNDER_DETERMINISTIC_LANGUAGE_ACCEPTANCE","deterministic_bisimulation":"EXACT_SPECIALIZATION_WITH_REGISTERED_OUTPUT_LABELS","nondeterministic_trace_vs_bisimulation":"STRICT_BOUNDARY_TRACE_EQUIVALENCE_IS_COARSER","classical_parameter_sufficiency":"INCOMPARABLE_WITH_PREDICTIVE_SUFFICIENCY_IN_GENERAL","predictive_state_representation":"COORDINATE_REALIZATION_IFF_TESTS_SEPARATE_PREDICTIVE_CLASSES"}})


def canonical_json(receipt):
    return json.dumps(receipt,indent=2,sort_keys=True)+"\n"


def main():
    r=build_receipt()
    print(canonical_json(r),end="")
    return 0 if r["verdict"]=="GREEN" else 1

if __name__=="__main__":
    raise SystemExit(main())
