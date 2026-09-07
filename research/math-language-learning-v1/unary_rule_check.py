"""Pointwise Boolean proof of universal substitution; independent of region solver."""
from unary_rule_contract import count, validate_rule

def expression(expr,assignment,work):
    count(work,"expression_nodes")
    if expr[0]=="pred":return assignment[expr[1]]
    if expr[0]=="not":return not expression(expr[1],assignment,work)
    left=expression(expr[1],assignment,work);right=expression(expr[2],assignment,work)
    return left and right if expr[0]=="and" else left or right

def point(statement,assignment,work):
    count(work,"statement_tests")
    a=expression(statement["left"],assignment,work)
    b=expression(statement["right"],assignment,work)
    return (not a or b) if statement["kind"]=="every" else not(a and b)

def check_rule(value,work=None):
    work={} if work is None else work
    before=dict(work)
    rule=validate_rule(value,work);names=rule["parameters"]
    table=[];counterexample=None;essential=[None]*len(rule["premises"])
    for region in range(1<<len(names)):
        count(work,"schema_assignments")
        a={name:bool(region&(1<<i)) for i,name in enumerate(names)}
        ps=[point(p,a,work) for p in rule["premises"]]
        q=point(rule["conclusion"],a,work)
        valid=not all(ps) or q;table.append(valid)
        if not valid and counterexample is None:counterexample=dict(a)
        for removed in range(len(ps)):
            count(work,"essentiality_checks")
            # A countermodel after deleting this premise proves it is indispensable.
            count(work,"essentiality_index_tests",len(ps))
            count(work,"essentiality_premise_reads",len(ps)-1)
            others=[p for i,p in enumerate(ps) if i!=removed]
            if not q and all(others) and essential[removed] is None:essential[removed]=dict(a)
    valid=all(table);composite=all(x is not None for x in essential)
    return {"accepted":valid and composite,"rule_id":rule["rule_id"],"truth_table":table,
            "counterexample":counterexample,"essentiality_counterexamples":essential,
            "reason":"VALID_ESSENTIAL_COMPOSITE" if valid and composite else
                     "NON_ESSENTIAL_PREMISE" if valid else "COUNTEREXAMPLE",
            "counters":{k:v-before.get(k,0) for k,v in work.items()}}
