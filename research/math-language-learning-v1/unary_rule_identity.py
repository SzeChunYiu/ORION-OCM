"""Training-only semantic grouping and alpha-normalized rule identity."""
from itertools import permutations
from unary_contract import InputRefused, validate_task
from unary_rule_contract import count, digest, encoded, seal_rule
from unary_rule_check import expression

def semantic_key(value,work):
    """All nonempty worlds, modulo predicate renaming; never a held-out oracle."""
    task=validate_task(value);names=task["predicates"];n=len(names)
    if n>3:raise InputRefused("TRAINING_SEMANTIC_BOUND")
    best=None
    for order in permutations(names):
        count(work,"semantic_renamings")
        assignments=[{name:bool(r&(1<<i)) for i,name in enumerate(order)} for r in range(1<<n)]
        tables=[]
        for s in [*task["premises"],task["query"]]:
            table=[]
            for a in assignments:
                left=expression(s["left"],a,work);right=expression(s["right"],a,work)
                table.append((not left or right) if s["kind"]=="every" else
                             not(left and right) if s["kind"]=="no" else
                             left and right if s["kind"]=="some" else left and not right)
            tables.append(table)
        base_bits=query_bits=0
        for world in range(1,1<<(1<<n)):
            count(work,"semantic_worlds")
            occupied=[r for r in range(1<<n) if world&(1<<r)]
            count(work,"semantic_region_membership_tests",1<<n)
            holds=[]
            for s,table in zip([*task["premises"],task["query"]],tables):
                values=[table[r] for r in occupied]
                count(work,"semantic_point_lookups",len(values))
                count(work,"semantic_statement_tests")
                holds.append(all(values) if s["kind"] in ("every","no") else any(values))
            if all(holds[:-1]):
                base_bits|=1<<(world-1)
                if holds[-1]:query_bits|=1<<(world-1)
        candidate=(base_bits,query_bits)
        count(work,"semantic_comparisons")
        if best is None or candidate<best:best=candidate
    return digest({"predicates":n,"models":best[0],"query_models":best[1]},work)

def canonical_rule(value,work):
    task=validate_task(value);names=task["predicates"]
    if len(names)>3:raise InputRefused("RULE_PARAMETERS")
    params=["P"+str(i) for i in range(len(names))]
    best=None;chosen=None
    for order in permutations(params):
        count(work,"canonicalization_candidates")
        rename=dict(zip(names,order))
        def walk(expr):
            count(work,"canonicalization_nodes")
            return ["pred",rename[expr[1]]] if expr[0]=="pred" else [expr[0],*(walk(x) for x in expr[1:])]
        def stmt(s):
            return {"kind":s["kind"],"left":walk(s["left"]),"right":walk(s["right"])}
        premises=sorted([stmt(s) for s in task["premises"]],key=lambda x:encoded(x,work))
        conclusion=stmt(task["query"])
        key=encoded({"premises":premises,"conclusion":conclusion},work)
        if best is None or key<best:best=key;chosen=(premises,conclusion)
    return seal_rule(params,*chosen,work)
