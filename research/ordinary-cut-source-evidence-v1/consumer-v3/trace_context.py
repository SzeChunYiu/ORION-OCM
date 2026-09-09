"""Exact qualified trace transport bindings; no native proof checking or discovery."""
def span(value):
    if type(value) is not list or len(value)!=2 or any(type(x) is not int for x in value) or not 0<=value[0]<value[1]:
        raise ValueError("native-index span schema")
    return value
def validate(row,whole,p1,authority,project,identity):
    label=row["label"];trace=row["trace"];contracts=row["contracts"]
    binding=authority["trace_bindings"][label]
    if set(binding)!={"trace","contracts"} or binding["trace"]!=identity(trace) or binding["contracts"]!=identity(contracts):
        raise ValueError("exact qualified trace/contract bytes")
    source=trace["source"];start=span(source["span"])[0]
    if source["label"]!=label or trace["label"]!=label or project(source)!=whole:
        raise ValueError("trace whole contract")
    selected=authority["selected_scope_bindings"][label]
    if selected["contract"]!=identity(whole) or any(
       selected[k]!=source[k] for k in ("active_variables","active_dv")):
        raise ValueError("current native source context")
    if selected["source_raw"]!=source["raw"] or selected["proof_raw"]!=source["proof_raw"]:
        raise ValueError("current native source/proof identity")
    nodes=trace["nodes"]
    if type(nodes) is not list or not 1<=len(nodes)<=256 or source["dv"]!=[] or source["active_dv"]!=[]:
        raise ValueError("trace-ready transport prerequisites")
    if type(contracts) is not dict or set(contracts)!={n["label"] for n in nodes if "label" in n}:
        raise ValueError("used contract population")
    for key,used in contracts.items():
        if used["label"]!=key or span(used["span"])[1]>start:
            raise ValueError("used native-index order")
        if used["kind"] in ("$f","$e"):
            if set(used)!={"label","kind","statement","span"}:raise ValueError("hypothesis contract schema")
            context=source["floating"] if used["kind"]=="$f" else source["essential"]
            if {"label":key,"statement":used["statement"]} not in context:
                raise ValueError("current mandatory hypothesis context")
        elif used["kind"] in ("$a","$p"):
            if set(used)!=set(whole)|{"span"} or project(used)!=p1.get(key) or used["dv"]!=[]:
                raise ValueError("trace ordinary contract authority")
        else:raise ValueError("used contract kind")
