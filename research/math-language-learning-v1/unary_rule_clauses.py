"""Exact universal disjunction views; expressions remain explicit Boolean data."""
from unary_contract import InputRefused
from unary_rule_contract import count,encoded

def normal(expr,work):
    count(work,"clause_expression_nodes")
    if expr[0]=="pred":return list(expr)
    children=[normal(x,work) for x in expr[1:]]
    if expr[0]=="not" and children[0][0]=="not":return children[0][1]
    return [expr[0],*children]

def neg(expr,work):return normal(["not",expr],work)

def ordered(terms,work):
    values={}
    for term in terms:
        value=normal(term,work);values[encoded(value,work)]=value
        count(work,"clause_literal_insertions")
    count(work,"clause_sort_entries",len(values))
    return [values[k] for k in sorted(values)]

def clause(statement,work):
    if statement["kind"] not in ("every","no"):raise InputRefused("CLAUSE_UNIVERSAL")
    return ordered([neg(statement["left"],work),statement["right"] if
                    statement["kind"]=="every" else neg(statement["right"],work)],work)

def statement(terms,work):
    if not 1<=len(terms)<=2:raise InputRefused("CLAUSE_WIDTH")
    return {"kind":"every","left":neg(terms[0],work),"right":terms[-1]}

def instantiate(expr,binding,work):
    count(work,"dependency_binding_nodes")
    if expr[0]=="pred":return binding[expr[1]]
    return normal([expr[0],*[instantiate(x,binding,work) for x in expr[1:]]],work)

def substituted(statement,binding,work):
    return {"kind":statement["kind"],"left":instantiate(statement["left"],binding,work),
            "right":instantiate(statement["right"],binding,work)}

def subset(left,right,work):
    lhs=[encoded(x,work) for x in left];rhs={encoded(x,work) for x in right}
    count(work,"clause_subset_tests",len(lhs))
    return all(x in rhs for x in lhs)
