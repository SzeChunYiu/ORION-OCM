"""Checked KSO rules with a durable issuance journal; the two ledgers are not atomic."""
import time
from fractions import Fraction
from ocm.kso.space import Atom,Hyperedge
from ocm.kso.warrant import WarrantProfile
from ocm.store.ledger import LedgerStore
from unary_contract import InputRefused,fields
from unary_rule_acquire import acquire
from unary_rule_check import check_rule
from unary_rule_contract import validate_rule
import unary_method_data as D

class MethodStore:
    def __init__(self,runtime,*,create=False):
        self.rt=runtime;self.work={};self.records={};self.uses=[];self.attempts=[];self.intents={};self.head=None;self.selection=None
        start=time.monotonic();root=runtime.root/"unary-method-journal"
        if not create and not (root/"ledger.jsonl").is_file():raise InputRefused("MISSING_ISSUER_JOURNAL")
        self.journal=LedgerStore(root);self.source_map=D.sources(self.work)
        self.source_sha=D.hashed(self.source_map)
        entries=self.journal.entries();D.bump(self.work,"journal_rows_read",len(entries))
        D.bump(self.work,"journal_bytes_read",self.journal.path.stat().st_size)
        if create:
            if entries:raise InputRefused("ISSUER_ALREADY_EXISTS")
            env={role:D.admit_evidence(runtime,role,{"sources_sha256":self.source_sha},self.work)
                 for role in ("semantics","schema_environment","answer_environment")}
            self._append("INIT",{"schema":"ocm.unary-method.issuer.v1","sources":self.source_map,"environment":env})
            entries=self.journal.entries()
        if not entries or entries[0].kind!="INIT":raise InputRefused("ISSUER_INIT")
        init=D.parse(D.raw(entries[0].payload));fields(init,("schema","sources","environment"))
        if init["schema"]!="ocm.unary-method.issuer.v1" or init["sources"]!=self.source_map:
            raise InputRefused("METHOD_SOURCE_BINDING")
        self.environment=init["environment"];fields(self.environment,("semantics","schema_environment","answer_environment"))
        self._check_environment()
        pending={};pending_uses={};finished=[]
        for row in entries[1:]:
            D.bump(self.work,"issuer_records_decoded")
            body=D.parse(D.raw(row.payload))
            if row.kind=="SELECTION":
                if self.selection is not None or self.records or pending:raise InputRefused("SELECTED_DUPLICATE")
                self.selection=body
            elif row.kind=="PREPARE":
                mid=body.get("method_id")
                if type(mid) is not str or mid in pending or mid in self.records:raise InputRefused("ISSUER_DUPLICATE")
                pending[mid]=body
            elif row.kind=="ISSUE":
                fields(body,("method_id","plan_sha256"));mid=body["method_id"]
                if mid not in pending or D.hashed(pending[mid])!=body["plan_sha256"]:raise InputRefused("ISSUER_PLAN")
                self.records[mid]=pending.pop(mid)
            elif row.kind=="USE_PREPARE":
                qid=body.get("qid")
                if type(qid) is not str or qid in self.intents:raise InputRefused("DUPLICATE_USE")
                self.intents[qid]=body;pending_uses[qid]=body
            elif row.kind in ("USE","USE_REFUSED"):
                qid=body.get("qid")
                if qid not in pending_uses:raise InputRefused("UNMATCHED_USE")
                finished.append((body,pending_uses.pop(qid),row.kind=="USE"))
                self.attempts.append(body)
                if row.kind=="USE":self.uses.append(body)
            else:raise InputRefused("ISSUER_ROW_KIND")
        self.head=entries[-1].entry_hash
        if pending:raise InputRefused("INCOMPLETE_ISSUANCE")
        if pending_uses:raise InputRefused("INCOMPLETE_USE")
        from unary_method_selected import validate_selection
        validate_selection(self)
        for mid in self.records:self.read(mid)
        from unary_method_journal import validate_receipt
        for body,intent,successful in finished:
            validate_receipt(self,body,intent,successful=successful)
        D.bump(self.work,"restore_wall_s",time.monotonic()-start)

    @property
    def method_ids(self):return sorted(self.records)

    def _append(self,kind,body):
        row=self.journal.append(kind,D.parse(D.raw(body)),expected_head=self.head)
        self.head=row.entry_hash;D.bump(self.work,"journal_appends")
        D.bump(self.work,"journal_bytes_rewritten",self.journal.path.stat().st_size)
        return row

    def _check_environment(self):
        if D.sources(self.work)!=self.source_map:raise InputRefused("METHOD_SOURCE_BINDING")
        for role,eid in self.environment.items():
            D.payload(self.rt,eid,role,expected={"sources_sha256":self.source_sha},work=self.work)

    def _proof_warrant(self):
        return self.rt.state.evidence.citation_warrant([self.environment["semantics"],
                                                       self.environment["schema_environment"]])

    def _items(self,plan):
        envelope=plan["envelope"];w=self._proof_warrant()
        anchor=Atom(plan["anchor_id"],"proof",w,scope=D.SCOPE,quarantined=True,
                    content_ref=D.hashed(plan["proof_body"]),meta=(("data",D.raw(plan["proof_body"]).decode()),))
        method=Atom(plan["method_id"],"procedure",w,scope=D.SCOPE,content_ref=D.hashed(envelope),
                    meta=(("data",D.raw(envelope).decode()),))
        edge=Hyperedge(plan["edge_id"],(anchor.atom_id,),(method.atom_id,),"SUPPORT",warrant=w,scope=D.SCOPE,head_weights=(Fraction(1),))
        return anchor,method,edge

    def acquire_selected(self,training,development,contract,*,observation=None,dependency_donor=False):
        from unary_method_selected import acquire_selected
        return acquire_selected(self,training,development,contract,observation=observation,dependency_donor=dependency_donor)

    def acquire(self,episodes):
        start=time.monotonic();self._check_environment()
        if self.selection is not None:raise InputRefused("SELECTED_ALREADY_ACQUIRED")
        if D.live(self.rt,self._proof_warrant())!="LIVE":raise InputRefused("RULE_CHECKER_UNAVAILABLE")
        episodes=D.parse(D.raw(episodes));result=acquire(episodes)
        D.bump(self.work,"acquisition_calls")
        discovery=D.admit_evidence(self.rt,"discovery",{"training":episodes,"acquisition":result},self.work)
        if len(result["rules"])>8:raise InputRefused("AUTHORED_SELECTION_BOUND")
        issued=[]
        for item in result["rules"]:
            rule=validate_rule(item["rule"]);mid="unary:method:"+rule["rule_id"]
            if mid in self.records:raise InputRefused("METHOD_ALREADY_ISSUED")
            checked=check_rule(rule);D.bump(self.work,"schema_checks")
            if not checked["accepted"]:raise InputRefused("RULE_CHECK_FAILED")
            utility=D.admit_evidence(self.rt,"utility",{"policy":"authored-selected.v1","rule_id":rule["rule_id"]},self.work)
            proof_body={"rule":rule,"certificate":checked,"sources_sha256":self.source_sha}
            proof=D.admit_evidence(self.rt,"proof",proof_body,self.work,self._proof_warrant())
            envelope={"schema":"ocm.unary-method.data.v1","rule":rule,"schema_certificate":checked,
                      "proof":proof,"discovery":discovery,"utility":utility,
                      **self.environment,"sources_sha256":self.source_sha}
            if len(D.raw(envelope))>65536:raise InputRefused("METHOD_ENVELOPE_BOUND")
            plan={"method_id":mid,"anchor_id":mid+":proof","edge_id":mid+":support",
                  "envelope":envelope,"proof_body":proof_body}
            self._append("PREPARE",plan)
            anchor,method,edge=self._items(plan)
            self.rt.admit_batch(((anchor,(),"EXACT_CHECKER"),(method,(edge,),"EXACT_CHECKER")))
            D.bump(self.work,"atomic_kso_batches")
            self._append("ISSUE",{"method_id":mid,"plan_sha256":D.hashed(plan)})
            self.records[mid]=plan;self.read(mid);issued.append(mid)
        D.bump(self.work,"acquisition_wall_s",time.monotonic()-start)
        return {"terminal":result["terminal"],"method_ids":issued,"acquisition":result,"work":dict(self.work)}

    def read(self,mid):
        self._check_environment()
        if type(mid) is not str or mid not in self.records:raise InputRefused("UNISSUED_METHOD")
        plan=self.records[mid];fields(plan,("method_id","anchor_id","edge_id","envelope","proof_body"))
        if plan["method_id"]!=mid:raise InputRefused("METHOD_PLAN_ID")
        atom=self.rt.state.ks.atom_view.get(mid)
        if atom is None:raise InputRefused("MISSING_METHOD_ATOM")
        if D.live(self.rt,atom.warrant)=="UNKNOWN":raise InputRefused("UNKNOWN_METHOD_WARRANT")
        envelope=D.atom_data(atom,self.work)
        fields(envelope,("schema","rule","schema_certificate","proof","discovery","utility",
                         "semantics","schema_environment","answer_environment","sources_sha256"))
        if D.raw(envelope)!=D.raw(plan["envelope"]):raise InputRefused("METHOD_PLAN_BINDING")
        if envelope["schema"]!="ocm.unary-method.data.v1" or envelope["sources_sha256"]!=self.source_sha:
            raise InputRefused("METHOD_SOURCE_BINDING")
        if any(envelope[k]!=v for k,v in self.environment.items()):raise InputRefused("METHOD_ENVIRONMENT")
        rule=validate_rule(envelope["rule"])
        if mid!="unary:method:"+rule["rule_id"]:raise InputRefused("METHOD_ID")
        checked=check_rule(rule);D.bump(self.work,"schema_checks")
        if not checked["accepted"] or D.raw(checked)!=D.raw(envelope["schema_certificate"]):
            raise InputRefused("RULE_CHECK_FAILED")
        body={"rule":rule,"certificate":checked,"sources_sha256":self.source_sha}
        if D.raw(body)!=D.raw(plan["proof_body"]):raise InputRefused("PROOF_BODY")
        D.payload(self.rt,envelope["proof"],"proof",expected=body,derived=self._proof_warrant(),work=self.work)
        D.payload(self.rt,envelope["discovery"],"discovery",work=self.work)
        utility={"policy":"authored-selected.v1","rule_id":rule["rule_id"]}
        if self.selection is not None:
            from unary_method_selected import utility_body
            utility=utility_body(self,rule["rule_id"])
        D.payload(self.rt,envelope["utility"],"utility",expected=utility,work=self.work)
        anchor,expected,edge=self._items(plan)
        if (atom!=expected or self.rt.state.ks.atom_view.get(anchor.atom_id)!=anchor or
            self.rt.state.ks.edge_view.get(edge.edge_id)!=edge or
            any(self.rt.state.certificates.get(a.atom_id)!="EXACT_CHECKER" for a in (anchor,expected))):
            raise InputRefused("METHOD_KSO_BINDING")
        proof_w=self.rt.state.evidence.records[envelope["proof"]].warrant
        correctness=D.live(self.rt,proof_w)
        selected=D.live(self.rt,self.rt.state.evidence.citation_warrant([envelope["utility"]]))
        return {"method_id":mid,"rule_id":rule["rule_id"],"envelope":envelope,
                "correctness":correctness,"selection":selected,
                "eligible":correctness=="LIVE" and selected=="LIVE"}
