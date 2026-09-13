"""Independent finite controls; analytic theorem quantifiers remain in the proofs."""
from fractions import Fraction as F
from itertools import product
import selection_v1 as S
import transport_v1 as T
import oracles_v1 as O

def need(ok,message):
    if not ok:raise ValueError(message)

def witnesses():
    p=(F(1,2),F(1,2))
    zero=S.posterior(p,(0,0))
    bayes=S.posterior(p,(1,2))
    mirror=S.entropy_update_from_factors(p,(1,2))
    need(zero["status"]=="UNDEFINED_ZERO_NORMALIZER","zero normalizer")
    need(bayes["posterior"]==mirror==(F(1,3),F(2,3)),"positive overlap")
    vals=(2,3,0);edges=((1,),(0,2),(1,))
    trap=S.certify_descent(vals,edges,{2})
    path=S.descend(vals,edges,0)
    revived=S.certify_descent(vals,((1,2),(0,2),(1,)),{2})
    need(trap["bad_minima"]==(0,) and path["terminal"]==0,"local trap")
    need(revived["status"]=="CERTIFIED","escape edge revival")
    exact=min(range(3),key=lambda i:vals[i])
    task={0:{2}};tables={"hill":{0:path["terminal"]},"exact":{0:exact}}
    selected=S.select_tables(task,tables,{"hill":F(1,2),"exact":F(2)},
                             setup=3,check_fee=F(1,2),visit_fee=1)
    need(selected["winners"]==("exact",) and selected["total"]==7,"adequacy before charge")
    rel,pairs=T.construct_relation({"s":2},{"cheap":1,"old":2},1)
    cover=T.certify({"s":2},{"cheap":1,"old":2},2,1,rel,{"M":("cheap",1)})
    need(cover["lower"]==cover["target_infimum"]==1,"epsilon transport")
    return dict(zero_likelihood=zero,positive_bayes=bayes,entropy_same_map=mirror,
                ordinal_trap=trap,trap_trajectory=path,escape_edge_revival=revived,
                exhaustive_minimum=exact,common_task_selection=selected,
                epsilon_cover=cover,pair_enumeration_comparisons=pairs,
                five_of_nine=T.threshold_completion(5,4,0),
                six_of_nine=T.threshold_completion(6,3,0))

def descent_census():
    pairs=tuple((i,j) for i in range(3) for j in range(3) if i!=j)
    cases=0;paths=0;certified=0
    for values in product(range(3),repeat=3):
        for flags in product((False,True),repeat=6):
            edges=tuple(tuple(j for (a,j),b in zip(pairs,flags) if a==i and b) for i in range(3))
            trajectories=[p for i in range(3) for p in O.terminal_paths(values,edges,i)]
            for mask in range(8):
                adequate={i for i in range(3) if mask&(1<<i)}
                actual=S.certify_descent(values,edges,adequate)
                oracle=all(p[-1] in adequate for p in trajectories)
                need((actual["status"]=="CERTIFIED")==oracle,"all-path adequacy")
                need(all(len(p)<=3 for p in trajectories),"finite strict path bound")
                cases+=1;paths+=len(trajectories);certified+=oracle
    return dict(graph_objective_adequacy_cases=cases,independent_maximal_paths=paths,
                adequate_certificates=certified)

def cover_census():
    cases=0;covered=0;assignments=0
    for vals in product(range(3),repeat=4):
        s=dict(zip(("a","b"),vals[:2]));t=dict(zip(("x","y"),vals[2:]))
        for e in (0,1):
            oracle=O.assignment_cover(s,t,e);assignments+=len(oracle)
            rel,_=T.construct_relation(s,t,e)
            try:
                result=T.certify(s,t,min(s.values()),e,rel,
                                 {j:(j,c) for j,c in t.items()})
            except ValueError:
                need(not oracle,"rejected real assignment")
            else:
                need(bool(oracle),"accepted uncovered target")
                need(result["lower"]<=min(t.values()),"actual target lower bound")
                covered+=1
            cases+=1
    return dict(account_error_cases=cases,covered_cases=covered,
                independently_enumerated_witness_functions=assignments)

def table_census():
    task={0:{0},1:{1}};cases=0
    all_tables=[dict(enumerate(x)) for x in product((0,1),repeat=2)]
    for rows in product(all_tables,repeat=2):
        tables=dict(zip(("a","b"),rows))
        for costs_tuple in product(range(3),repeat=2):
            costs=dict(zip(tables,costs_tuple))
            got=S.select_tables(task,tables,costs,setup=2,check_fee=1,visit_fee=1)
            need(tuple(sorted(got["winners"]))==O.table_winners(task,tables,costs),"table oracle")
            need(got["checks"]==4,"full inadequate-table validation")
            cases+=1
    return dict(complete_table_cost_cases=cases)

def gate_census():
    cases=0
    for total in range(1,10):
        for passes in range(total+1):
            for unknown in range(total-passes+1):
                failures=total-passes-unknown
                got=T.threshold_completion(passes,failures,unknown)
                need(got["status"]==O.threshold_worlds(passes,failures,unknown),"completion oracle")
                cases+=1
    return dict(registered_partial_cohorts=cases)
