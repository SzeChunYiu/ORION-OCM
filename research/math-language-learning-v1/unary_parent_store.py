"""Conventional one-log WAL checked library; no KSO or OCM runtime instance."""
import time
from pathlib import Path
from unary_parent_sources import LedgerStore
from unary_contract import InputRefused,fields
from unary_rule_check import check_rule
import unary_method_plain as D
import unary_parent_sources as S
import unary_parent_payloads as P

ROLES=("semantics","schema_environment","answer_environment")
class ParentStore:
    def __init__(self,root,*,create=False):
        self.root=Path(root);self.work={};self.head=None;self.refs={};self.records={}
        self.roles={};self.revision=0;self.uses=[];self.attempts=[];self._raw={};self.selection=None;self._decoded={};self._validated=None
        start=time.monotonic()
        if self.root.is_symlink():raise InputRefused("PARENT_ROOT")
        if create:self.root.mkdir(parents=True,exist_ok=False)
        elif not (self.root/"journal/ledger.jsonl").is_file():raise InputRefused("MISSING_PARENT_JOURNAL")
        self.source_map=S.sources(self.work);self.source_sha=D.hashed(self.source_map)
        self.journal=LedgerStore(self.root/"journal");self.payloads=self.root/"payloads"
        if create:
            self.payloads.mkdir();P.fsync_dir(self.root)
            self._append("INIT",{"schema":"ocm.unary-parent.v1","sources":self.source_map})
        from unary_parent_journal import restore
        restore(self);self._enter(source_checked=True);self._validate_library()
        D.bump(self.work,"restore_wall_s",time.monotonic()-start)

    @property
    def method_ids(self):return sorted(self.records)

    def _append(self,kind,body):
        row=self.journal.append(kind,D.parse(D.raw(body)),expected_head=self.head)
        self.head=row.entry_hash;D.bump(self.work,"journal_appends")
        D.bump(self.work,"journal_bytes_rewritten",self.journal.path.stat().st_size)
        return row

    def _enter(self,*,source_checked=False):
        if not source_checked and S.sources(self.work)!=self.source_map:raise InputRefused("PARENT_SOURCE")
        entries=self.journal.entries();D.bump(self.work,"journal_rows_read",len(entries))
        D.bump(self.work,"journal_bytes_read",self.journal.path.stat().st_size)
        if not entries or entries[-1].entry_hash!=self.head:raise InputRefused("PARENT_HEAD_CHANGED")
        raw=P.validate(self.payloads,self.refs,self.work)
        if self._raw and raw!=self._raw:raise InputRefused("PARENT_PAYLOAD_CHANGED")
        self._raw=raw

    def _validate_library(self,*,force=False):
        from unary_method_selection_check import validate_receipt
        if self.selection is None:
            if self.records:raise InputRefused("PARENT_NO_SELECTION")
            return
        key=(tuple(sorted(self.refs.items())),self.source_sha,tuple(sorted((k,v["role"]) for k,v in self.roles.items())))
        if not force and self._validated==key:return
        selected=validate_receipt(D.parse(self._raw[self.selection]),sources_sha256=self.source_sha,work=self.work)
        rules={x["rule_id"]:x for x in selected["selected"]}
        if set(self.records)!={"unary:method:"+x for x in rules}:raise InputRefused("PARENT_MEMBERSHIP")
        for mid,digest in self.records.items():
            env=D.parse(self._raw[digest])
            fields(env,("schema","rule","schema_certificate","selection","sources_sha256",
                        "semantics","schema_environment","answer_environment","discovery","utility"))
            if (env["schema"]!="ocm.unary-parent.method.v1" or env["selection"]!=self.selection
                or env["sources_sha256"]!=self.source_sha or mid!="unary:method:"+env["rule"]["rule_id"]
                or D.raw(env["rule"])!=D.raw(rules[env["rule"]["rule_id"]])):raise InputRefused("PARENT_METHOD")
            proof=check_rule(env["rule"]);D.bump(self.work,"schema_checks")
            if not proof["accepted"] or D.raw(proof)!=D.raw(env["schema_certificate"]):raise InputRefused("PARENT_SCHEMA")
            for role in (*ROLES,"discovery","utility"):
                if self.roles.get(env[role],{}).get("role")!=role:raise InputRefused("PARENT_ROLE")
            if any(env[k]!="role:"+k for k in ROLES):raise InputRefused("PARENT_ENVIRONMENT")
            self._decoded[mid]=P.freeze(env,self.work)
        self._validated=key

    def read(self,mid):
        if type(mid) is not str or mid not in self.records:raise InputRefused("UNISSUED_METHOD")
        D.bump(self.work,"cached_method_reads");env=P.thaw(self._decoded[mid],self.work)
        states=[self.roles[env[k]]["state"] for k in ("semantics","schema_environment")]
        correctness="LIVE" if all(s=="LIVE" for s in states) else "UNKNOWN" if "UNKNOWN" in states else "REVOKED"
        selection=self.roles[env["utility"]]["state"]
        return {"method_id":mid,"rule_id":env["rule"]["rule_id"],"envelope":env,
                "correctness":correctness,"selection":selection,"eligible":correctness==selection=="LIVE"}

    def answers_live(self):return all(self.roles["role:"+r]["state"]=="LIVE" for r in ("semantics","answer_environment"))

    def acquire_selected(self,training,development,selection_contract,*,observation=None,dependency_donor=False):
        from unary_method_selection import acquire_selected
        from unary_method_selection_check import validate_receipt
        self._enter()
        if self.selection is not None:raise InputRefused("PARENT_ALREADY_ACQUIRED")
        if not all(self.roles["role:"+r]["state"]=="LIVE" for r in ("semantics","schema_environment")):
            raise InputRefused("RULE_CHECKER_UNAVAILABLE")
        result=acquire_selected(training,development,selection_contract,work=self.work,observation=observation,sources_sha256=self.source_sha,dependency_donor=dependency_donor)
        validate_receipt(result,sources_sha256=self.source_sha,work=self.work)
        receipt=D.raw(result);selection=D.hashed(result);objects={selection:receipt};records={}
        for rule in result["selected"]:
            D.bump(self.work,"schema_checks")
            env={"schema":"ocm.unary-parent.method.v1","rule":rule,"schema_certificate":check_rule(rule),
                 "selection":selection,"sources_sha256":self.source_sha,
                 **{r:"role:"+r for r in ROLES},"discovery":"discovery:"+selection,"utility":"utility:"+rule["rule_id"]}
            raw=D.raw(env);digest=D.hashed(env);objects[digest]=raw;records["unary:method:"+rule["rule_id"]]=digest
        intent={"schema":"ocm.unary-parent.admission.v1","selection":selection,"records":records,
                "refs":{k:len(v) for k,v in objects.items()},"sources_sha256":self.source_sha}
        self._append("ADMIT_PREPARE",intent)
        for raw in objects.values():P.put(self.payloads,raw,self.work)
        self._append("ADMIT",{"intent_sha256":D.hashed(intent)})
        from unary_parent_journal import restore
        restore(self);self._enter(source_checked=True);self._validate_library()
        return result

    def revise(self,role,state,*,mid=None):
        self._enter()
        data=D.parse(D.raw({"role":role,"state":state,"mid":mid}));role,state,mid=data["role"],data["state"],data["mid"]
        if role not in (*ROLES,"discovery","utility") or state not in ("LIVE","REVOKED","UNKNOWN"):
            raise InputRefused("PARENT_REVISION")
        rid="role:"+role if role in ROLES else self.read(mid)["envelope"][role]
        body={"record":rid,"role":role,"state":state,"revision":self.revision+1}
        self._append("REVISE",body);self.roles[rid]={"role":role,"state":state};self.revision+=1
        self._validate_library(force=state=="LIVE")
        return body

    def persist(self):
        self._enter();self._validate_library();P.fsync_dir(self.root)
        return {"head":self.head,"revision":self.revision,"work":dict(self.work)}
