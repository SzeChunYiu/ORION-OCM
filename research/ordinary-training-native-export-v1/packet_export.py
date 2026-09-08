"""Candidate artifacts only; separate root qualification is required before learning."""
POLICY="ALL_PREFIX_AXIOMS_PLUS_P0_THEOREMS_PLUS_RELEASED_TRAINING_THEOREMS"

def assemble(req,release,rows,proofs,base,verified,observed,trace_error,S,P,B,U):
    contracts,base_labels,released_labels=P.allowed_inventory(rows,proofs,release,S)
    by_label={r["label"]:r for r in contracts};packet_rows=[];trace_bindings={};dispositions={};retained={}
    for root in release["roots"]:
        label=root["label"];released=root["source_disposition"]=="RELEASED"
        trace=observed.traces.get(label) if observed is not None and released else None
        observed_trace=trace
        trace,trace_contracts,reason=U.prepare(trace,rows,S) if released else (None,{},None)
        if released:
            if trace is None and observed is not None and label in observed.unusable:reason=observed.unusable[label]
            elif trace is None and observed_trace is None and trace_error is not None:reason={"stage_error":trace_error}
            dispositions[label]={"status":"TRACE_READY" if trace else "TRACE_UNUSABLE","reason":reason}
            if observed_trace is not None and trace is None:retained[label]={"reason":reason,"trace":observed_trace}
        row={k:root[k] for k in ("ordinal","label","source_disposition")}
        row.update(whole_contract=B.identity(B.canonical(by_label[label])) if released else None,
            trace_disposition="TRACE_READY" if trace else "TRACE_UNUSABLE" if released else "EXCLUDED",
            trace=trace,contracts=trace_contracts)
        packet_rows.append(row)
        if trace:trace_bindings[label]={"trace":B.identity(B.canonical(trace)),
                                        "contracts":B.identity(B.canonical(trace_contracts))}
    base_axioms={r["label"] for r in base if r["kind"]=="$a"}
    axiom_rows=[r for r in rows.values() if r["kind"]=="$a"]
    authority={"schema":"ordinary.native-prefix-authority.v2","terminal":"FRESH_PREFIX_NATIVE_VERIFIED",
        "proof_ordinal_count":4223,"verified_labels":verified.verified,
        "release":req["release"],"prefix":req["prefix"],"registry_scope":req["registry_scope"],
        "authority_contract":req["authority_contract"],"P0_contracts":req["P0_contracts"],
        "corpus":req["corpus"],"python":req["python"],"verifier":req["verifier"],"sources":req["sources"],
        "axioms":[{"contract":S.contract(r),"raw":r["raw"]} for r in axiom_rows],
        "additional_axiom_labels":[r["label"] for r in axiom_rows if r["label"] not in base_axioms],
        "selected_scope_bindings":{label:{"contract":B.identity(B.canonical(S.contract(rows[label]))),
            "source_raw":rows[label]["raw"],"proof_raw":rows[label]["proof_raw"],
            **verified.scope_bindings[label]} for label in released_labels},
        "trace_bindings":trace_bindings,"trace_dispositions":dispositions,
        "trace_stage":"COMPLETE" if trace_error is None and all(x["status"]=="TRACE_READY" for x in dispositions.values()) else "PARTIAL_OR_UNUSABLE",
        "admission":"SEPARATE_ROOT_QUALIFICATION_REQUIRED","old_native_receipt_inherited":False}
    inventory={"schema":"ordinary.native-P1-inventory.v2","release":req["release"],
        "inventory_policy":POLICY,"base_labels":base_labels,"released_labels":released_labels,"contracts":contracts}
    packet={"schema":"ordinary.training-trace-packet.v2","release":req["release"],
            "ordinals":list(range(4096,4224)),"roots":packet_rows}
    return authority,inventory,packet,retained

def emit(output,authority,inventory,packet,retained,base,B):
    B.write(output/"CUSTODIAN-UNUSABLE-TRACES.json",retained)
    authority_pin=B.write(output/"NATIVE-AUTHORITY.json",authority)
    inventory["native_trace_authority"]=authority_pin
    p1_pin=B.write(output/"P1-INVENTORY.json",inventory)
    packet.update(native_trace_authority=authority_pin,P1_inventory=p1_pin)
    return {"native_authority":authority_pin,"P1_inventory":p1_pin,
            "training_packet":B.write(output/"TEACHING-PACKET-CANDIDATE.json",packet),
            "P0_contracts":B.write(output/"P0-CONTRACTS.json",base)}
