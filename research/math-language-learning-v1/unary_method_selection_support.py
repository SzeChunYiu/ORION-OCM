"""Direct support-to-training validation; no mining or optimized query solving."""
from unary_contract import InputRefused,fields,task_digest,negate
from unary_rule_acquire import _fragment
from unary_rule_identity import canonical_rule,semantic_key
import unary_method_plain as D

def validate_supports(receipt,work):
    keys={}
    for item in receipt["acquisition"]["rules"]:
        seen=set()
        for support in item["supports"]:
            if type(support) is not dict:raise InputRefused("INVALID_FIELDS")
            fields(support,("semantic_key","task_sha256","episode","branch","cover",*(("dependency",) if "dependency" in support else ())))
            i=support["episode"]
            if type(i) is not int or not 0<=i<len(receipt["training"]):raise InputRefused("SELECTION_SUPPORT_EPISODE")
            row=receipt["training"][i];task=row["task"]
            if support["task_sha256"]!=task_digest(task):raise InputRefused("SELECTION_SUPPORT_TASK")
            if i not in keys:keys[i]=semantic_key(task,work)
            if support["semantic_key"]!=keys[i] or keys[i] in seen:raise InputRefused("SELECTION_SUPPORT_SEMANTICS")
            seen.add(keys[i]);branch=support["branch"]
            if branch not in ("query_true","query_false"):raise InputRefused("SELECTION_SUPPORT_BRANCH")
            cert=row["result"][branch];cover=support["cover"]
            if (cert is None or cert["kind"]!="unsat" or type(cert["obligation"]) is not int
                or cert["obligation"]!=len(task["premises"]) or type(cover) is not list
                or any(type(j) is not int or j not in cert["cover"] for j in cover)
                or cover!=sorted(set(cover)) or not 2<=len(cover)<len(task["premises"])):
                raise InputRefused("SELECTION_SUPPORT_COVER")
            if "dependency" in support:
                from unary_rule_dependency_check import verify_support
                verify_support(task,row["result"],support,item["rule"],work)
                continue
            conclusion=task["query"] if branch=="query_false" else negate(task["query"])
            if D.raw(canonical_rule(_fragment(task,cover,conclusion,work),work))!=D.raw(item["rule"]):
                raise InputRefused("SELECTION_SUPPORT_RULE")
        if len(seen)<2:raise InputRefused("SELECTION_SUPPORTS")
