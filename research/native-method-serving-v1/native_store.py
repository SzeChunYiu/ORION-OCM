"""External checked imports in actual KSO; durable import/use boundaries."""
from fractions import Fraction
from ocm.kso.space import Atom,Hyperedge
from ocm.store.ledger import LedgerStore
from native_contract import fields,require,InputRefused
import native_data as D
class NativeStore:
    def __init__(self,runtime,engine,*,create=False):
        self.rt=runtime;self.engine=engine;self.work={};self.source_map=engine.source_map;self.source_sha=engine.source_sha
        self.records={};self.intents={};self.attempts=[];self.uses=[];self.head=None;self.pending={}
        root=runtime.root/"native-method-journal"
        require(create or (root/"ledger.jsonl").is_file(),"MISSING_IMPORT_JOURNAL")
        self.journal=LedgerStore(root);entries=self.journal.entries();D.bump(self.work,"journal_rows_read",len(entries))
        if create:
            require(not entries,"IMPORT_ALREADY_EXISTS");engine.check_environment()
            self._append("IMPORT_PREPARE",{"sources_sha256":self.source_sha,"library":engine.inputs.identity,
                                         "qualification_sha256":D.hashed(engine.qualification)})
            self.environment={role:D.admit_evidence(runtime,role,self.environment_body(),self.work)
                              for role in ("source_environment","library_environment","checker_environment")}
            for mid in sorted(engine.qualification):
                qualified=engine.qualification[mid]
                proof=D.admit_evidence(runtime,"proof",qualified,self.work)
                applies=D.admit_evidence(runtime,"applicability",{"method_id":mid,"policy":"authored-import.v1"},self.work)
                plan={"id":mid,"payload_sha256":D.hashed(engine.inputs.methods[mid]),"proof":proof,"applicability":applies,
                      "qualification":qualified,"sources_sha256":self.source_sha}
                self.records[mid]=plan;anchor,atom,edge=self.items(plan)
                runtime.admit_batch(((anchor,(),"EXACT_CHECKER"),(atom,(edge,),"EXACT_CHECKER")))
            self._append("INIT",{"environment":self.environment,"records":self.records})
            entries=self.journal.entries()
        require(len(entries)>=2 and entries[0].kind=="IMPORT_PREPARE" and entries[1].kind=="INIT","INCOMPLETE_IMPORT")
        require(dict(entries[0].payload)=={"sources_sha256":self.source_sha,"library":engine.inputs.identity,
                "qualification_sha256":D.hashed(engine.qualification)},"IMPORT_SOURCE_OR_QUALIFICATION")
        init=D.parse(D.raw(entries[1].payload));fields(init,("environment","records"));self.environment=init["environment"];self.records=init["records"]
        fields(self.environment,("source_environment","library_environment","checker_environment"))
        require(set(self.records)==set(engine.qualification),"IMPORTED_METHOD_POPULATION")
        self.head=entries[-1].entry_hash;self.check_environment()
        for mid in self.records:self.read(mid)
        from native_journal import validate_receipt
        for row in entries[2:]:
            body=D.parse(D.raw(row.payload));qid=body.get("qid")
            if row.kind=="USE_PREPARE":
                require(qid not in self.intents,"DUPLICATE_USE");self.intents[qid]=body;self.pending[qid]=body
            elif row.kind in ("USE","USE_REFUSED"):
                require(qid in self.pending,"UNMATCHED_USE")
                validate_receipt(self,body,self.pending.pop(qid),successful=row.kind=="USE",replay=True)
                self.attempts.append(body)
                if row.kind=="USE":self.uses.append(body)
            else:raise InputRefused("JOURNAL_KIND")
        require(not self.pending,"INCOMPLETE_USE")
    def environment_body(self):return {"sources_sha256":self.source_sha,"library":self.engine.inputs.identity}
    def _append(self,kind,body):
        row=self.journal.append(kind,D.parse(D.raw(body)),expected_head=self.head);self.head=row.entry_hash
        D.bump(self.work,"journal_appends");D.bump(self.work,"journal_bytes_rewritten",self.journal.path.stat().st_size)
        return row
    def check_environment(self):
        self.engine.check_environment()
        for role,eid in self.environment.items():D.payload(self.rt,eid,role,expected=self.environment_body(),work=self.work)
    def warrant(self,eids=()):return self.rt.state.evidence.citation_warrant([*self.environment.values(),*eids])
    def items(self,plan):
        mid="native:method:"+plan["id"];w=self.warrant([plan["proof"]])
        anchor=Atom(mid+":proof","proof",w,scope=D.SCOPE,quarantined=True)
        atom=Atom(mid,"procedure",w,scope=D.SCOPE,content_ref=D.hashed(plan),meta=(("data",D.raw(plan).decode()),))
        edge=Hyperedge(mid+":support",(anchor.atom_id,),(mid,),"SUPPORT",warrant=w,scope=D.SCOPE,head_weights=(Fraction(1),))
        return anchor,atom,edge
    def read(self,mid):
        require(mid in self.records,"UNKNOWN_METHOD");plan=self.records[mid]
        fields(plan,("id","payload_sha256","proof","applicability","qualification","sources_sha256"))
        require(plan["id"]==mid and plan["payload_sha256"]==D.hashed(self.engine.inputs.methods[mid]) and
                plan["qualification"]==self.engine.qualification[mid] and plan["sources_sha256"]==self.source_sha,"METHOD_IDENTITY")
        D.payload(self.rt,plan["proof"],"proof",expected=plan["qualification"],work=self.work)
        D.payload(self.rt,plan["applicability"],"applicability",expected={"method_id":mid,"policy":"authored-import.v1"},work=self.work)
        anchor,atom,edge=self.items(plan)
        require(self.rt.state.ks.atom_view.get(atom.atom_id)==atom and self.rt.state.ks.atom_view.get(anchor.atom_id)==anchor
                and self.rt.state.ks.edge_view.get(edge.edge_id)==edge and self.rt.state.certificates.get(atom.atom_id)=="EXACT_CHECKER"
                and self.rt.state.certificates.get(anchor.atom_id)=="EXACT_CHECKER","METHOD_KSO_IDENTITY")
        return plan
    def eligible(self,requested,eid=None):
        self.check_environment();require(type(requested) is list and requested==sorted(set(requested)) and set(requested)<=set(self.records),"REQUESTED_METHODS")
        ids=[]
        for mid in requested:
            plan=self.read(mid);eids=[plan["proof"],plan["applicability"]]+([] if eid is None else [eid])
            if D.live(self.rt,self.warrant(eids))=="LIVE":ids.append(mid)
        return ids
    def require_selected_live(self,ids,eid):
        eids=[eid]
        for mid in ids:
            plan=self.read(mid);eids.extend([plan["proof"],plan["applicability"]])
        require(D.live(self.rt,self.warrant(eids))=="LIVE","SELECTED_COMBINED_WARRANT")
