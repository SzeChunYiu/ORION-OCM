"""Synthetic native-shaped control records. No synthetic status supplies authority."""
from pathlib import Path
import copy,json
import life_native as N
import trace_source as S
from structural_fixture import trace_from_proof
from caller_bindings import raw_identity
from hole_match import identity
ROOT=Path(__file__).resolve().parent

def fixture():
    definition=json.loads((ROOT/"inputs/DEFINITION.json").read_text())
    ordinary=json.loads((ROOT/"inputs/ordinary-contracts.json").read_text())
    lines=["$c wff |- ( ) -> /\\ \\/ $.","$v ph ps ch $."]
    for p in definition["source_claim"]["parameters"]:
        lines.append(f"{p['floating_label']} $f {p['type']} {p['variable']} $.")
    for row in ordinary:
        lines.append(chr(36)+"{")
        for h in row["essential"]:lines.append(f"{h['label']} $e {' '.join(h['statement'])} $.")
        # Deliberately unverified dummy bodies: indexing/structural transport controls only.
        proof=" $= wph" if row["kind"]=="$p" else ""
        lines.extend([f"{row['label']} {row['kind']} {' '.join(row['statement'])}{proof} $.","$}"])
    prefix_raw=("\n".join(lines)+"\n").encode()+(ROOT/"inputs/admission-suffix.mm").read_bytes()
    prefix,_=S.index(prefix_raw)
    definition["pattern_contracts"]={k:{**S.contract(prefix[k]),"span":prefix[k]["span"]}
                                      for k in definition["pattern_contracts"]}
    claim=definition["source_claim"];suffix=N.serialize([claim]);database_raw=prefix_raw+b"\n"+suffix
    rows,_=S.index(database_raw);source=rows[claim["label"]]
    trace=trace_from_proof(source,rows,claim["proof"])
    used={n["label"] for n in trace["nodes"]}
    contracts={k:{**S.contract(rows[k]),"span":rows[k]["span"]} for k in used}
    trusted=[k for k,v in prefix.items() if v["kind"]=="$a"]
    labels=[k for k,v in prefix.items() if v["kind"]=="$p"]
    authority={"prefix":raw_identity(prefix_raw),"prefix_proof_count":len(labels),
      "trusted_assertion_count":len(trusted),"trusted_assertions_sha256":identity(trusted)["sha256"]}
    sources={"index":{"path":"synthetic-index","bytes":1,"sha256":"1"*64},
      "adapter":{"path":"synthetic-adapter","bytes":1,"sha256":"2"*64},
      "verifier":{"path":"synthetic-verifier-never-executed","bytes":1,"sha256":"3"*64}}
    prefix_path=Path("/synthetic-only/prefix.mm");archive=Path("/synthetic-only/native")
    result={"terminal":"NATIVE_VERIFIED","native_calls":1,"error":None,"claims_sha256":identity([claim])["sha256"],
      "sources":sources,"closed_prefix":{"path":str(prefix_path),**raw_identity(prefix_raw)},
      "suffix":raw_identity(suffix),"database":{"path":str(archive/"database.mm"),**raw_identity(database_raw)},
      "trusted_assertions":trusted,"verified_labels":labels+[claim["label"]],"selected":[claim["label"]],
      "traces":{claim["label"]:trace},"contracts":contracts}
    return dict(definition=definition,result=result,claim=claim,prefix_raw=prefix_raw,database_raw=database_raw,
                authority=authority,sources=sources,prefix_path=prefix_path,archive=archive)

def serializable(f):
    return {k:({"ascii":v.decode(),"identity":raw_identity(v)} if isinstance(v,bytes)
                 else str(v) if isinstance(v,Path) else copy.deepcopy(v)) for k,v in f.items()}
