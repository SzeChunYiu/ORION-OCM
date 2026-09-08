"""Independent pointwise checks of intermediate evidence; never calls the miner."""
from itertools import permutations
from unary_contract import InputRefused,fields,negate,validate_task,task_digest
from unary_verify import verify_result
from unary_rule_contract import count,validate_rule,encoded
from unary_rule_check import check_rule,expression,point
from unary_rule_clauses import clause,neg,ordered,substituted,subset
import unary_method_plain as D

def _require(condition,reason):
    if not condition:raise InputRefused(reason)

def _binding(task,rule,binding,work):
    fields(binding,tuple(rule["parameters"]))
    witnesses=[{"kind":"every","left":e,"right":e} for e in binding.values()]
    witnesses += [{"kind":"every","left":["pred",n],"right":["pred",n]} for n in task["predicates"]]
    probe=dict(task,premises=witnesses)
    validate_task(probe);count(work,"dependency_binding_validations")

def _truth(terms,assignment,work):
    values=[expression(x,assignment,work) for x in terms]
    count(work,"dependency_literal_checks",len(values))
    return any(values)

def verify_link(rule,task,cover,binding,link,work):
    D.raw(link);D.raw(binding);task=validate_task(task);rule=validate_rule(rule,work)
    fields(link,("schema","premises","conclusion","target"))
    _require(link["schema"]=="ocm.unary-clause-link.v1","DEPENDENCY_LINK_VERSION")
    _require(type(cover) is list and all(type(i) is int and 0<=i<len(task["premises"]) for i in cover)
             and cover==sorted(set(cover)) and len(cover)==len(rule["premises"]),"DEPENDENCY_COVER")
    _binding(task,rule,binding,work)
    actual=[task["premises"][i] for i in cover]
    universal=task["query"]["kind"] in ("every","no")
    target=task["query"] if universal else negate(task["query"])
    instantiated=[substituted(p,binding,work) for p in rule["premises"]]
    conclusion=substituted(rule["conclusion"],binding,work)
    _require(link["premises"]==[clause(p,work) for p in actual]
             and link["conclusion"]==clause(conclusion,work) and link["target"]==clause(target,work),
             "DEPENDENCY_LINK_CONTENT")
    left=sorted((encoded(clause(p,work),work) for p in instantiated))
    right=sorted((encoded(c,work) for c in link["premises"]))
    _require(left==right and subset(link["conclusion"],link["target"],work),"DEPENDENCY_SUBSTITUTION")
    # Check actual AST semantics independently of the normalization/matching algorithm.
    for region in range(1<<len(task["predicates"])):
        a={n:bool(region&(1<<i)) for i,n in enumerate(task["predicates"])}
        count(work,"dependency_point_checks")
        for p,c in zip(actual,link["premises"]):
            _require(point(p,a,work)==_truth(c,a,work),"DEPENDENCY_NORMALIZATION")
        _require(point(conclusion,a,work)==_truth(link["conclusion"],a,work)
                 and point(target,a,work)==_truth(link["target"],a,work),"DEPENDENCY_NORMALIZATION")
        _require(not all(point(p,a,work) for p in actual) or point(conclusion,a,work),"DEPENDENCY_INTERMEDIATE")
        _require(not point(conclusion,a,work) or point(target,a,work),"DEPENDENCY_WEAKENING")

def _roles(rule,binding,pivot,residuals,work):
    clauses=[clause(p,work) for p in rule["premises"]];goal=clause(rule["conclusion"],work)
    for left,middle,right in permutations(rule["parameters"]):
        count(work,"dependency_role_checks")
        a,b,c=(["pred",n] for n in (left,middle,right))
        expected=[ordered([a,b],work),ordered([neg(b,work),c],work)]
        if (sorted(map(lambda x:encoded(x,work),clauses))==sorted(map(lambda x:encoded(x,work),expected))
            and goal==ordered([a,c],work)
            and binding[left]==residuals[0] and binding[middle]==pivot and binding[right]==residuals[1]):
            return
    raise InputRefused("DEPENDENCY_ROLE_BINDING")

def verify_support(task,result,support,rule,work):
    D.raw(support);task=validate_task(task);rule=validate_rule(rule,work)
    fields(support,("semantic_key","task_sha256","episode","branch","cover","dependency"))
    count(work,"dependency_training_verifications")
    _require(verify_result(task,result) and result["premises"]["kind"]=="model","DEPENDENCY_TRAINING")
    _require(support["task_sha256"]==task_digest(task),"DEPENDENCY_TASK")
    branch=support["branch"];_require(branch in ("query_true","query_false"),"DEPENDENCY_BRANCH")
    cert=result[branch];cover=support["cover"]
    _require(type(cover) is list and len(cover)==2 and all(type(i) is int for i in cover)
             and cover==sorted(set(cover)) and len(cover)<len(task["premises"])
             and cert["kind"]=="unsat" and type(cert["obligation"]) is int
             and cert["obligation"]==len(task["premises"]) and all(i in cert["cover"] for i in cover),"DEPENDENCY_COVER")
    step=support["dependency"]
    fields(step,("schema","order","pivot","residuals","resolvent","target","binding"))
    _require(step["schema"]=="ocm.unary-pivot-step.v1" and type(step["order"]) is list
             and all(type(i) is int for i in step["order"]) and sorted(step["order"])==cover,"DEPENDENCY_STEP")
    clauses=[clause(task["premises"][i],work) for i in step["order"]]
    pivot=step["pivot"];residuals=step["residuals"]
    _require(type(pivot) is list and len(pivot)==2 and pivot[0]=="pred" and pivot[1] in task["predicates"]
             and type(residuals) is list and len(residuals)==2 and all(len(c)==2 for c in clauses),"DEPENDENCY_PIVOT")
    _require(pivot in clauses[0] and neg(pivot,work) in clauses[1]
             and residuals==[[x for x in c if x!=p][0] for c,p in zip(clauses,[pivot,neg(pivot,work)])],
             "DEPENDENCY_RESIDUALS")
    resolvent=ordered(residuals,work)
    _require(step["resolvent"]==resolvent,"DEPENDENCY_RESOLVENT")
    _require(len(rule["parameters"])==3 and len(rule["premises"])==2,"DEPENDENCY_SCHEMA_SHAPE")
    fields(step["binding"],tuple(rule["parameters"]))
    _roles(rule,step["binding"],pivot,residuals,work)
    query=task["query"] if branch=="query_false" else negate(task["query"])
    linked=dict(task,query=query)
    link={"schema":"ocm.unary-clause-link.v1","premises":[clause(task["premises"][i],work) for i in cover],
          "conclusion":resolvent,"target":step["target"]}
    verify_link(rule,linked,cover,step["binding"],link,work)
    # Original instantiated dependencies, as well as the lifted schema, must be essential.
    essential=[False,False]
    for region in range(1<<len(task["predicates"])):
        a={n:bool(region&(1<<i)) for i,n in enumerate(task["predicates"])}
        count(work,"dependency_essentiality_assignments")
        ps=[point(task["premises"][i],a,work) for i in cover]
        for removed in range(2):
            count(work,"dependency_essentiality_checks")
            if ps[1-removed] and not _truth(resolvent,a,work):essential[removed]=True
    _require(all(essential),"DEPENDENCY_NONESSENTIAL")
    checked=check_rule(rule,work)
    _require(checked["accepted"],"DEPENDENCY_SCHEMA")
    return checked
