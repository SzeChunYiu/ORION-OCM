"""Authored syntax/ordinary axioms and demonstrated cut; never native-qualified."""
import json
from goal_library import Library,identity,raw_identity,proof_record
import trace_source as S
BASE=r"""
$c wff |- ( ) /\ -> $.
$v ph ps ch $.
wph $f wff ph $.
wps $f wff ps $.
wch $f wff ch $.
wa $a wff ( ph /\ ps ) $.
wi $a wff ( ph -> ps ) $.
OPEN
pair-h $e |- ph $.
ax-pair $a |- ( ph /\ ch ) $.
base-pair $p |- ( ph /\ ch ) $= wph wch pair-h ax-pair $.
CLOSE
OPEN
wrap-h $e |- ( ph /\ ch ) $.
ax-wrap $a |- ( ps -> ( ph /\ ch ) ) $.
CLOSE
"""
SUFFIX=r"""
OPEN
cut-h $e |- ph $.
learned-cut $p |- ( ps -> ( ph /\ ch ) ) $= wph wps wch wph wch cut-h ax-pair ax-wrap $.
CLOSE
"""
def native_text(text):return text.replace("OPEN",chr(36)+"{").replace("CLOSE",chr(36)+"}").encode()
def bundle(base=None,suffix=None):
    base=native_text(BASE) if base is None else base
    joined=base+b"\n"+(native_text(SUFFIX) if suffix is None else suffix)
    br,_=S.index(base);jr,_=S.index(joined)
    bp=[proof_record(r) for r in br.values() if r["kind"]=="$p"]
    jp=[proof_record(r) for r in jr.values() if r["kind"]=="$p"]
    receipt=b'{"scope":"AUTHORED_SYNTHETIC_ONLY","native_calls":0}\n'
    manifest={"schema":"ordinary.joined-library.v1","base_prefix":raw_identity(base),"joined_prefix":raw_identity(joined),
              "base_proofs":bp,"joined_proofs":jp,"cohort":jp[len(bp):],
              "axioms":[{"label":r["label"],"raw":r["raw"],"contract":identity(S.contract(r))}
                        for r in br.values() if r["kind"]=="$a"],"receipt":raw_identity(receipt)}
    return {"base":base,"joined":joined,"manifest":manifest,"manifest_pin":identity(manifest),
            "receipt":receipt,"receipt_pin":raw_identity(receipt)}
def restore(b):return Library(b["base"],b["joined"],b["manifest"],b["manifest_pin"],b["receipt"],b["receipt_pin"])
def task():
    return {"schema":"ordinary.goal-task.v1","query":["|-","(","ps","->","(","ph","/\\","ch",")",")"],
      "premises":[["|-","ph"]],"context":{"schema":"native.typed-context.v1","dv":[],
        "parameters":[{"id":"V"+str(i),"type":"wff","variable":v,"floating_label":"w"+v}
                      for i,v in enumerate(("ph","ps","ch"))]},
      "limits":{"max_decisions":2,"max_instances":50000,"max_token_states":2000000,"soft_wall_s":60}}
