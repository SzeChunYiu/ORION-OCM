"""Future release/prefix correspondence checks; uses unchanged donor parsers."""
def bind_population(raw,release,S,T):
    end=release["source_end_exclusive"];closures=release["synthetic_scope_closures"]
    if type(end) is not int or type(closures) is not int or end<0 or closures<0:raise ValueError("prefix cut")
    if raw[end:]!=b"\n"+b"$}\n"*closures:raise ValueError("exact source cut/scope closures")
    rows,index_end=S.index(raw)
    proofs=[r for r in rows.values() if r["kind"]=="$p"]
    if index_end!=len(raw) or len(proofs)!=4223 or proofs[-1]["span"][1]!=end:raise ValueError("exact prefix population")
    expected_axioms=[{"label":r["label"],"raw":r["raw"]} for r in rows.values() if r["kind"]=="$a"]
    if expected_axioms!=release["axiom_identities"]:raise ValueError("axiom difference requires a new authority contract")
    excluded=set()
    for position,declared in zip(range(4096,4224),release["roots"]):
        row=proofs[position-1]
        if row["label"]!=declared["label"]:raise ValueError("released label/ordinal")
        for key,source_key in (("statement","statement"),("proof_raw","proof_raw"),("source_raw","raw")):
            if row[source_key]!=declared[key]:raise ValueError("released source identity")
        direct=sorted({op["label"] for op in T.operations(row) if "label" in op and op["label"] in rows
                       and rows[op["label"]]["kind"]=="$p"})
        forbidden=sorted(set(direct)&excluded)
        expected=("EXCLUDED_PRIOR_PROTECTED" if declared["source_disposition"]=="EXCLUDED_PRIOR_PROTECTED"
                  else "EXCLUDED_DEPENDS_PRIOR_PROTECTED" if forbidden else "RELEASED")
        if direct!=declared["direct_theorem_dependencies"] or forbidden!=declared["forbidden_dependencies"]:
            raise ValueError("released dependency identity")
        if declared["source_disposition"]!=expected:raise ValueError("protected dependency closure")
        if expected!="RELEASED":excluded.add(row["label"])
    return rows,proofs

def context(row):
    return {"active_variables":row["active_variables"],"active_dv":row["active_dv"]}

def allowed_inventory(rows,proofs,release,S):
    base={r["label"] for r in proofs[:4095]}|{r["label"] for r in rows.values() if r["kind"]=="$a"}
    released={r["label"] for r in release["roots"] if r["source_disposition"]=="RELEASED"}
    contracts=[S.contract(r) for r in rows.values() if r["label"] in base|released]
    return contracts,[r["label"] for r in contracts if r["label"] in base],[
        r["label"] for r in release["roots"] if r["label"] in released]

def validate_base(base,rows,proofs,S):
    if len(base)!=4191 or sum(r["kind"]=="$a" for r in base)!=96:raise ValueError("unchanged 4191-contract P0 required")
    labels=[r["label"] for r in base]
    if len(labels)!=len(set(labels)):raise ValueError("P0 duplicate")
    if [r["label"] for r in base if r["kind"]=="$p"]!=[r["label"] for r in proofs[:4095]]:raise ValueError("unchanged P0 theorem population")
    if any(r["kind"] not in {"$a","$p"} or r!=S.contract(rows[r["label"]]) for r in base):raise ValueError("P0 contract change requires new authority")
    if [S.contract(r) for r in rows.values() if r["label"] in set(labels)]!=base:raise ValueError("P0 source order")
