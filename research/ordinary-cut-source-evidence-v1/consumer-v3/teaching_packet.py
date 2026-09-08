"""Bindings for externally native-qualified training data; never a native checker."""
import hashlib,json
import trace_context
POLICY="ALL_PREFIX_AXIOMS_PLUS_P0_THEOREMS_PLUS_RELEASED_TRAINING_THEOREMS"
FIELDS={"label","kind","statement","floating","essential","dv"}
ROW={"ordinal","label","source_disposition","whole_contract","trace_disposition","trace","contracts"}
def contract(source):return {k:source[k] for k in sorted(FIELDS)}
def contract_identity(value):
    raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode()
    return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def index(rows):
    found={}
    for row in rows:
        if set(row)!=FIELDS or type(row["label"]) is not str or not row["label"] or row["kind"] not in ("$a","$p"):
            raise ValueError("ordinary contract schema")
        if row["label"] in found:raise ValueError("duplicate ordinary contract")
        found[row["label"]]=row
    return found
def validate(base,packet,inventory,release,request,authority):
    if release["schema"]!="ordinary.training-release.v2" or release["corpus"]!=request["corpus"] or release["registry_scope"]!=request["registry_scope"]:
        raise ValueError("release source/registry authority")
    if set(packet)!={"schema","release","ordinals","roots","native_trace_authority","P1_inventory"} or packet["schema"]!="ordinary.training-trace-packet.v2":
        raise ValueError("training packet schema")
    if set(inventory)!={"schema","release","native_trace_authority","inventory_policy","base_labels","released_labels","contracts"} or inventory["schema"]!="ordinary.native-P1-inventory.v2":
        raise ValueError("P1 inventory schema")
    if packet["release"]!=request["release_receipt"] or inventory["release"]!=request["release_receipt"]:
        raise ValueError("released packet identity")
    if packet["native_trace_authority"]!=request["qualified_native_trace_authority"] or inventory["native_trace_authority"]!=request["qualified_native_trace_authority"]:
        raise ValueError("external qualified native authority")
    if packet["P1_inventory"]!=request["P1_inventory"] or inventory["inventory_policy"]!=POLICY:
        raise ValueError("complete P1 authority")
    if authority["schema"]!="ordinary.native-prefix-authority.v2" or authority["terminal"]!="FRESH_PREFIX_NATIVE_VERIFIED" or authority["proof_ordinal_count"]!=4223:
        raise ValueError("fresh native authority contract")
    if authority["release"]!=request["release_receipt"] or authority["registry_scope"]!=request["registry_scope"] or authority["corpus"]!=request["corpus"] or authority["P0_contracts"]!=request["P0_contracts"]:
        raise ValueError("fresh native authority bindings")
    if {k:authority["prefix"][k] for k in ("bytes","sha256")}!=release["closed_source"]:
        raise ValueError("fresh native prefix identity")
    ordinals=list(range(4096,4224))
    if packet["ordinals"]!=ordinals or release["ordinals"]!=ordinals or len(packet["roots"])!=128 or len(release["roots"])!=128:
        raise ValueError("fixed chronological population")
    roots=packet["roots"]
    if any(set(row)!=ROW for row in roots):raise ValueError("training row schema")
    if [row["ordinal"] for row in roots]!=ordinals or len({row["label"] for row in roots})!=128:
        raise ValueError("root ordinal/label population")
    if [(x["ordinal"],x["label"],x["source_disposition"]) for x in roots]!=[
       (x["ordinal"],x["label"],x["source_disposition"]) for x in release["roots"]]:
        raise ValueError("release root/disposition identity")
    base_index=index(base);p1=index(inventory["contracts"])
    base_p=[r["label"] for r in base if r["kind"]=="$p"]
    if len(base)!=4191 or len(base_p)!=4095:raise ValueError("unchanged complete P0")
    if any(p1.get(label)!=row for label,row in base_index.items()):raise ValueError("P0 weakened or changed")
    if [r for r in inventory["contracts"] if r["label"] in base_index]!=base:raise ValueError("P0 order")
    if authority["verified_labels"]!=base_p+[r["label"] for r in roots]:
        raise ValueError("fresh native verified population")
    released=[r["label"] for r in roots if r["source_disposition"]=="RELEASED"]
    axioms=[r["label"] for r in release["axiom_identities"]]
    if len(axioms)!=len(set(axioms)):raise ValueError("axiom identity population")
    if [r["label"] for r in inventory["contracts"] if r["kind"]=="$a"]!=axioms:
        raise ValueError("explicit new prefix axiom inventory")
    if [r["label"] for r in inventory["contracts"] if r["kind"]=="$p"]!=base_p+released:
        raise ValueError("whole P1 theorem population")
    if inventory["released_labels"]!=released or inventory["base_labels"]!=[
       r["label"] for r in inventory["contracts"] if r["kind"]=="$a" or r["label"] in base_p]:
        raise ValueError("P1 manifest labels")
    if set(authority["selected_scope_bindings"])!=set(released) or set(authority["trace_dispositions"])!=set(released):
        raise ValueError("native released scope population")
    ready={r["label"] for r in roots if r["trace_disposition"]=="TRACE_READY"}
    if set(authority["trace_bindings"])!=ready:raise ValueError("native ready trace population")
    native_axioms=authority["axioms"]
    if [a["contract"] for a in native_axioms]!=[r for r in inventory["contracts"] if r["kind"]=="$a"] or [
       {"label":a["contract"]["label"],"raw":a["raw"]} for a in native_axioms]!=release["axiom_identities"]:
        raise ValueError("native complete axiom identity")
    if authority["additional_axiom_labels"]!=[x for x in axioms if x not in base_index]:
        raise ValueError("native additional axiom disclosure")
    released_by={r["label"]:r for r in release["roots"]}
    for row in roots:
        if row["source_disposition"]!="RELEASED":
            if row["source_disposition"] not in ("EXCLUDED_PRIOR_PROTECTED","EXCLUDED_DEPENDS_PRIOR_PROTECTED"):
                raise ValueError("unknown release disposition")
            if row["whole_contract"] is not None or row["trace"] is not None or row["contracts"]!={} or row["trace_disposition"]!="EXCLUDED":
                raise ValueError("excluded root exposure")
            continue
        selected=authority["selected_scope_bindings"][row["label"]]
        issued=released_by[row["label"]]
        if selected["contract"]!=row["whole_contract"] or selected["source_raw"]!=issued["source_raw"] or selected["proof_raw"]!=issued["proof_raw"]:
            raise ValueError("native released whole-contract/source binding")
        disposition=authority["trace_dispositions"][row["label"]]
        if set(disposition)!={"status","reason"} or disposition["status"]!=row["trace_disposition"]:
            raise ValueError("native trace disposition")
        if p1[row["label"]]["statement"]!=released_by[row["label"]]["statement"]:raise ValueError("released whole theorem statement")
        if row["whole_contract"]!=contract_identity(p1[row["label"]]):raise ValueError("whole theorem contract binding")
        if row["trace_disposition"]=="TRACE_UNUSABLE":
            if row["trace"] is not None or row["contracts"]!={}:raise ValueError("unusable trace schema")
        elif row["trace_disposition"]=="TRACE_READY":
            if disposition["reason"] is not None:raise ValueError("ready trace reason")
            trace_context.validate(row,p1[row["label"]],p1,authority,contract,contract_identity)
        else:raise ValueError("trace disposition")
    return inventory["contracts"]
