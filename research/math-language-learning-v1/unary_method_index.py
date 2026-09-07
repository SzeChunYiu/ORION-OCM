"""An explicit rule-data index, separate from the single OCM operator."""
from unary_contract import InputRefused
import unary_method_data as D

class MethodIndex:
    def __init__(self,store):
        self.store=store;self.work={"index_probes":0,"postings_examined":0}
        self.refusals=[];self.postings={"every":[],"no":[]}
        self.ks=store.rt.state.ks;self.state=self._state()
        from unary_method_postings import contents
        self.postings,self.refusals=contents(store,self._content_state(),self.work)

    def _content_state(self):
        s=self.store.rt.state;items=[]
        for mid in self.store.method_ids:
            D.bump(self.work,"cache_binding_entries")
            plan=self.store.records[mid];env=plan["envelope"]
            items.append((mid,s.ks.atom_view.get(mid),s.ks.atom_view.get(plan["anchor_id"]),
                          s.ks.edge_view.get(plan["edge_id"]),s.certificates.get(mid),
                          s.certificates.get(plan["anchor_id"]),
                          tuple(s.evidence.records.get(env[k]) for k in
                          ("proof","discovery","utility","semantics","schema_environment","answer_environment"))))
        return (tuple(items),s.revoked,s.evidence.revoked,s.nogoods,s.evidence.nogoods,self.store.source_sha)

    def _state(self):
        s=self.store.rt.state
        return (s.revoked,s.evidence.revoked,s.nogoods,s.evidence.nogoods,
                len(s.evidence.records),self.store.head)

    def validate(self):
        if self.store.rt.state.ks is not self.ks or self._state()!=self.state:
            raise InputRefused("STALE_INDEX")

    def select(self,kind):
        self.validate()
        if type(kind) is not str or kind not in self.postings:raise InputRefused("INDEX_KIND")
        D.bump(self.work,"index_probes")
        ids=self.postings[kind];D.bump(self.work,"postings_examined",len(ids))
        return list(ids)
