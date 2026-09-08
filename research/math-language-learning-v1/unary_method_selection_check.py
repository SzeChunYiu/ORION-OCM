"""Selection receipt arithmetic/semantic verification, without mining or query solving."""
from unary_contract import InputRefused,fields,validate_task
from unary_rule_check import check_rule
from unary_method_verify_use import verify_use,verify_answer
import unary_method_plain as D

MATCH_KEYS=("matching_nodes","mapping_attempts","premise_index_reads","index_probes")
def natural(x):
    if type(x) is not int or x<0:raise InputRefused("SELECTION_COUNTER")
    return x

def query_count(row):
    o=row["observation"]
    q=natural(o["query_constraints"])
    if q!=natural(o["parent_semantic_total"]["constraints_checked"])-natural(o["preparation"]["constraints_checked"]):
        raise InputRefused("SELECTION_QUERY_DELTA")
    return q

def decisions(r):
    pool=[x["rule"] for x in r["acquisition"]["rules"]];ranking=[];n=len(r["baseline"])
    if pool!=sorted(pool,key=lambda x:x["rule_id"]) or len({x["rule_id"] for x in pool})!=len(pool):
        raise InputRefused("SELECTION_POOL_ORDER")
    if len(r["trials"])!=n*len(pool):raise InputRefused("SELECTION_TRIAL_COUNT")
    for ri,rule in enumerate(pool):
        benefit=match=0
        for i,base in enumerate(r["baseline"]):
            row=r["trials"][ri*n+i]
            if row["rule_id"]!=rule["rule_id"] or type(row["row"]) is not int or row["row"]!=i:
                raise InputRefused("SELECTION_TRIAL_ORDER")
            if D.raw(row["task"])!=D.raw(base["task"]):raise InputRefused("SELECTION_TRIAL_TASK")
            benefit+=query_count(base)-query_count(row)
            match+=sum(natural(row["application"]["counters"].get(k,0)) for k in MATCH_KEYS)
        ranking.append({"rule_id":rule["rule_id"],"benefit":benefit,"matching_work":match,"inner_bytes":len(D.raw(rule))})
    ranking.sort(key=lambda x:(-x["benefit"],x["matching_work"],x["inner_bytes"],x["rule_id"]))
    ids={x["rule_id"] for x in [x for x in ranking if x["benefit"]>0][:8]}
    selected=[x for x in pool if x["rule_id"] in ids]
    terminal="SELECTED" if selected else "NO_DEVELOPMENT_BENEFIT" if pool else "NO_METHOD_ACQUIRED"
    return {"ranking":ranking,"selected":selected,"terminal":terminal,"pool_sha256":D.hashed(pool),
            "ranking_sha256":D.hashed(ranking),"library_sha256":D.hashed(selected)}

def validate_receipt(value,*,work,sources_sha256=None):
    if type(work) is not dict:raise TypeError("work must be a dict")
    D.bump(work,"selection_receipt_validations")
    from unary_method_selection import validate_contract,SCHEMA
    r=D.parse(D.raw(value))
    fields(r,("schema","stage","contract","sources_sha256","training","acquisition","baseline","trials",
              "ranking","selected","terminal","pool_sha256","ranking_sha256","library_sha256","work","receipt_sha256"))
    sealed=r.pop("receipt_sha256")
    if sealed!=D.hashed(r):raise InputRefused("SELECTION_RECEIPT_HASH")
    if r["schema"]!=SCHEMA or r["stage"]!="COMPLETE" or r["sources_sha256"]!=(D.hashed(D.sources(work)) if sources_sha256 is None else sources_sha256):
        raise InputRefused("SELECTION_SOURCE")
    policy=validate_contract(r["contract"])
    if len(r["training"])!=policy["training_rows"] or len(r["baseline"])!=policy["development_rows"]:
        raise InputRefused("SELECTION_COUNTS")
    for row in [*r["training"],*r["baseline"],*r["trials"]]:
        validate_task(row["task"])
        if row["terminal"]!="COMPLETE" or not verify_answer(row["task"],row["result"],work=work,counter="selection_answer_revalidations"):
            raise InputRefused("SELECTION_ANSWER_CERTIFICATE")
        query_count(row)
    lookup={}
    for item in r["acquisition"]["rules"]:
        rule=item["rule"];checked=check_rule(rule)
        D.bump(work,"selection_schema_revalidations")
        for name,count in checked["counters"].items():D.bump(work,"selection_schema_"+name,count)
        if not checked["accepted"] or D.raw({k:v for k,v in checked.items() if k!="counters"})!=D.raw(
                {k:v for k,v in item["schema_certificate"].items() if k!="counters"}):
            raise InputRefused("SELECTION_RULE_CERTIFICATE")
        for count in item["schema_certificate"]["counters"].values():natural(count)
        if len({s["semantic_key"] for s in item["supports"]})<2:raise InputRefused("SELECTION_SUPPORTS")
        lookup[rule["rule_id"]]={"eligible":True,"envelope":{"rule":rule}}
    from unary_method_selection_support import validate_supports
    validate_supports(r,work)
    for row in r["trials"]:
        app=row["application"]
        if app["terminal"]=="PROPOSED":
            if D.raw(app["result"])!=D.raw(row["result"]):raise InputRefused("SELECTION_APPLICATION_RESULT")
            universal=row["task"]["query"]["kind"] in ("every","no")
            use={"method_id":row["rule_id"],"rule_id":row["rule_id"],"binding":app["binding"],
                 "cover":app["cover"],"recipes_applied":1,"replaced_branch":"no" if universal else "yes"}
            if "dependency" in app:use["dependency"]=app["dependency"]
            verify_use(row["task"],use,lookup.__getitem__,work=work)
        elif app["terminal"] not in ("NO_MATCH","INCONSISTENT_BASE"):raise InputRefused("SELECTION_APPLICATION")
    for key,expected in decisions(r).items():
        if D.raw(r[key])!=D.raw(expected):raise InputRefused("SELECTION_DECISION")
    r["receipt_sha256"]=sealed
    return r
