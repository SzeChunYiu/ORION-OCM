"""An explicit rule-data index, separate from the single OCM operator."""
from unary_contract import InputRefused
import unary_method_data as D

class MethodIndex:
    def __init__(self,store):
        self.store=store;self.work={"index_probes":0,"postings_examined":0}
        self.refusals=[];self.postings={"every":[],"no":[]}
        self.ks=store.rt.state.ks;self.state=self._state()
        for mid in store.method_ids:
            D.bump(self.work,"cold_entries_visited")
            item=store.read(mid)
            if not item["eligible"]:
                self.refusals.append({"method_id":mid,"correctness":item["correctness"],
                                      "selection":item["selection"]})
                continue
            kind=item["envelope"]["rule"]["conclusion"]["kind"]
            self.postings[kind].append(mid);D.bump(self.work,"postings_built")
        self.postings={k:tuple(v) for k,v in self.postings.items()}

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
