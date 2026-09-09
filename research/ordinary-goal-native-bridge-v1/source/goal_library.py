"""Exact ordered source/receipt custody; no saved flag supplies native authority."""
import hashlib,json,time
import trace_source as S
def encoded(value):return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def identity(value):return raw_identity(encoded(value))
def raw_identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def require(ok,reason):
    if not ok:raise ValueError(reason)
def proof_record(row):
    return {"label":row["label"],"contract":identity(S.contract(row)),
            "proof":identity(row["proof"]),"proof_raw":row["proof_raw"],"raw":row["raw"]}
class Library:
    def __init__(self,base_raw,joined_raw,manifest,manifest_pin,receipt_raw,receipt_pin):
        started=time.perf_counter()
        self._costs={"snapshot_decodes":0,"snapshot_bytes_materialized":0,"snapshot_decode_wall_s":0.0}
        require(identity(manifest)==manifest_pin,"library manifest pin")
        require(raw_identity(receipt_raw)==receipt_pin==manifest["receipt"],"cohort receipt pin")
        require(set(manifest)=={"schema","base_prefix","joined_prefix","base_proofs","joined_proofs","axioms","cohort","receipt"},
                "library manifest schema")
        require(manifest["schema"]=="ordinary.joined-library.v1","library schema")
        require(type(base_raw) is bytes and type(joined_raw) is bytes,"source bytes")
        require(raw_identity(base_raw)==manifest["base_prefix"] and
                raw_identity(joined_raw)==manifest["joined_prefix"],"prefix source pin")
        require(joined_raw.startswith(base_raw+b"\n"),"exact base followed by cohort")
        base,_=S.index(base_raw);joined,_=S.index(joined_raw)
        require(not any(k.startswith("search-hyp-") or k in {"cut-f0","cut-f1","cut-f2"} for k in joined),
                "private proof-label namespace collision")
        require(all(joined.get(k)==v for k,v in base.items()),"base source changed")
        bp=[proof_record(r) for r in base.values() if r["kind"]=="$p"]
        jp=[proof_record(r) for r in joined.values() if r["kind"]=="$p"]
        require(bp==manifest["base_proofs"] and jp==manifest["joined_proofs"],"ordered complete proof inventory")
        axioms=[{"label":r["label"],"raw":r["raw"],"contract":identity(S.contract(r))}
                for r in base.values() if r["kind"]=="$a"]
        require(axioms==manifest["axioms"] and
                axioms==[{"label":r["label"],"raw":r["raw"],"contract":identity(S.contract(r))}
                         for r in joined.values() if r["kind"]=="$a"],"unchanged exact axiom authority")
        require(jp==bp+manifest["cohort"],"exact ordered cohort, no union or replacement")
        require(all(r["kind"]!="$f" for k,r in joined.items() if k not in base),"cohort adds floating declaration")
        self._snapshot=encoded({"manifest":manifest,"rows":list(joined.values())}).decode()
        self._base_raw=base_raw;self._joined_raw=joined_raw
        self._costs.update(source_index_calls=2,source_bytes_indexed=len(base_raw)+len(joined_raw),
                           construction_wall_s=time.perf_counter()-started)
    def _decode(self):
        started=time.perf_counter();value=json.loads(self._snapshot)
        self._costs["snapshot_decodes"]+=1;self._costs["snapshot_bytes_materialized"]+=len(self._snapshot.encode())
        self._costs["snapshot_decode_wall_s"]+=time.perf_counter()-started
        return value
    @property
    def costs(self):return dict(self._costs)
    @property
    def rows(self):return {r["label"]:r for r in self._decode()["rows"]}
    @property
    def manifest(self):return self._decode()["manifest"]
    @property
    def pin(self):return identity(self.manifest)
    @property
    def base_raw(self):return self._base_raw
    @property
    def joined_raw(self):return self._joined_raw
    @property
    def contracts(self):return [S.contract(r) for r in self.rows.values() if r["kind"] in {"$a","$p"}]
    @property
    def cohort_labels(self):return [r["label"] for r in self.manifest["cohort"]]
    def authority(self):
        m=self.manifest;labels=[a["label"] for a in m["axioms"]]
        return {"prefix":m["joined_prefix"],"prefix_proof_count":len(m["joined_proofs"]),
                "trusted_assertion_count":len(labels),"trusted_assertions_sha256":identity(labels)["sha256"]}
