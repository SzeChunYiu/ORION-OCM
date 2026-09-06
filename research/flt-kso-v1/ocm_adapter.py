"""A theorem subview of the existing OCMRuntime, not a second knowledge store.

Proposal execution goes through the canonical solve and exact input index.
Only this host adapter, after validating a fresh KernelSession-issued result,
may admit a checked proof/claim. Goal status is derived from live support routes;
planner metadata and failed attempts never confer theorem truth.
"""
from __future__ import annotations
import json
import time
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.operators.registry import OperatorSpec as RegisteredOperator, BackendKind
from ocm.kso.admission import CertificateKind
from ocm.kso.space import Atom,Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import WarrantProfile
from ocm.kso.resources import ResourceVector
from substrate import Refusal,digest_json,encoded,sha256
from kernel import KernelSession, ENVIRONMENT
from native import validate_formula,synthesize,emit_source

ENV_ID=digest_json(ENVIRONMENT)


def meta(**values): return tuple(sorted(values.items()))


class TheoremView:
    def __init__(self,runtime:OCMRuntime):
        self.runtime=runtime
        self.preparation={'name_collision_objects_examined':0}

    def open(self,name,formula):
        formula=validate_formula(formula)
        identity={'name':name,'formula':formula,'environment_id':ENV_ID}
        gid='flt:goal:'+digest_json(identity)
        for obj in self.runtime.state.ks.atoms:
            self.preparation['name_collision_objects_examined']+=1
            m=dict(obj.meta)
            if m.get('role')=='TaskRegistration' and m.get('name')==name and m.get('environment_id')==ENV_ID:
                if m.get('goal_id')!=gid: raise Refusal('DUPLICATE_THEOREM_NAME',name)
                return gid
        scope=Scope.of(ENV_ID)
        _,eid=self.runtime.admit_evidence(identity,'instruction','flt:registered-obligation:'+gid,scope=scope)
        w=WarrantProfile.of({eid})
        seed,proc=gid+':request',gid+':grammar'
        self.runtime.admit_object(Atom(seed,'query_seed',warrant=w,scope=scope,quarantined=True,
                                 meta=meta(role='TaskRegistration',environment_id=ENV_ID,goal_id=gid,name=name,
                                           formula_json=encoded(formula).decode(),grammar_id=proc)),(),CertificateKind.INSTRUCTION)
        self.runtime.admit_object(Atom(proc,'procedure',warrant=w,scope=scope,
                                 meta=meta(role='RegisteredPrimitiveGrammar',environment_id=ENV_ID)),
            (Hyperedge(gid+':registration',(seed,),(proc,),'SUPPORT',warrant=w,scope=scope),),CertificateKind.INSTRUCTION)
        # Admission requires exhibited warrant. Use the existing generative composition
        # path for UNKNOWN proposals; never assign instruction truth to the theorem.
        self.runtime.compose((proc,),gid,head_type='goal',
                             bridge_warrant=WarrantProfile.partial(()),
                             executable_ref='flt:proposed-obligation@1')
        return gid

    def goal(self,gid):
        obj=self.runtime.state.ks.atom(gid); data=dict(self.runtime.state.ks.atom(gid+':request').meta)
        if obj.atom_type!='goal' or data.get('role')!='TaskRegistration' or data.get('environment_id')!=ENV_ID:
            raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH')
        formula=validate_formula(json.loads(data['formula_json']))
        if data.get('goal_id')!=gid or gid!='flt:goal:'+digest_json({'name':data['name'],'formula':formula,'environment_id':ENV_ID}):
            raise Refusal('STATEMENT_IDENTITY_MISMATCH')
        return formula,data

    def status(self,gid):
        formula,_=self.goal(gid)
        # OR across checked routes, each route carries its own conjunctive warrant.
        for obj in self.runtime.state.ks.atoms:
            m=dict(obj.meta)
            if (obj.atom_type=='claim' and m.get('role')=='VerifiedClaim' and m.get('goal_id')==gid
                and m.get('environment_id')==ENV_ID and obj.content_ref==digest_json(formula)
                and self.runtime.state.certificates.get(obj.atom_id)==CertificateKind.EXACT_CHECKER.value
                and obj.is_live(self.runtime.state.revoked)):
                return 'PROVED'
        return 'OPEN'

    def admit_checked(self,gid,session,result,term):
        formula,data=self.goal(gid)
        if type(session) is not KernelSession or not session.authentic_for(result,formula,term):
            raise Refusal('CANNOT_CHECK_STALE_OR_UNISSUED_CHECKER_EVIDENCE')
        scope=Scope.of(ENV_ID)
        _,eid=self.runtime.admit_evidence(result,'proof','flt:kernel:'+result['run_id'],scope=scope)
        kernel_w=WarrantProfile.of({eid})
        proc=data['grammar_id']; w=kernel_w.meet(self.runtime.state.ks.atom(proc).warrant)
        pid=gid+':checked:'+result['run_id']; cid=gid+':claim:'+result['run_id']
        self.runtime.admit_object(Atom(pid,'proof',warrant=w,scope=scope,
            content_ref=result['source_sha256'],meta=meta(role='CheckedProof',goal_id=gid,environment_id=ENV_ID)),
            (Hyperedge(pid+':support',(proc,),(pid,),'COMPOSITION',warrant=kernel_w,scope=scope),),
            CertificateKind.EXACT_CHECKER)
        self.runtime.admit_object(Atom(cid,'claim',warrant=w,scope=scope,
            content_ref=digest_json(formula),meta=meta(role='VerifiedClaim',goal_id=gid,environment_id=ENV_ID)),
            (Hyperedge(cid+':support',(pid,),(cid,),'COMPOSITION',scope=scope),),CertificateKind.EXACT_CHECKER)
        return eid

    def attempt(self,gid,session,*,max_expansions=256,max_depth=24):
        formula,data=self.goal(gid); proc=data['grammar_id']; scope=Scope.of(ENV_ID)
        box={}; n=len(self.runtime.state.ks.atoms)
        def backend(ks,op_id,bindings):
            # Read the actual goal from this solve's KSO snapshot; no external proof donor.
            actual=dict(ks.atom(gid+':request').meta)
            current=validate_formula(json.loads(actual['formula_json']))
            if current!=formula or actual['environment_id']!=ENV_ID:
                raise Refusal('STATEMENT_IDENTITY_MISMATCH')
            proposal=synthesize(current,max_expansions=max_expansions,max_depth=max_depth)
            box['proposal']=proposal
            return proposal
        def checker(out):
            if out['formula']!=formula or out['term'] is None:
                box['checker']={'terminal':'FAILED_UNDER_BUDGET','kernel_verified':False}
                return SV.Status.FAIL
            result=session.check(formula,out['term']);box['checker']=result
            if result['kernel_verified']: return SV.Status.PASS
            return SV.Status.FAIL if result['terminal']=='CHECKER_REJECTED' else SV.Status.CANNOT_CHECK
        op=SV.OperatorSpec('flt.explicit-propositional-search','1',backend,(proc,),
                           output_type='proof',scope=scope,checker=checker)
        registered=RegisteredOperator(op.operator_id,op.version,BackendKind.PROOF,
            lambda ks,bindings:backend(ks,op.operator_id,bindings),(),output_type='proof',scope=scope)
        # The persistent manifest describes the generic grammar; task binding belongs
        # to the scoped runtime OperatorSpec above, not a conflicting grammar version.
        self.runtime.register_operator(registered)
        start=time.perf_counter(); index=SolveOperatorIndex((op,)); build_seconds=time.perf_counter()-start
        task=SV.Task(gid,(SV.QueryPart('Construct a proof under the registered grammar','goal',(proc,)),),context=ENV_ID)
        outcome=self.runtime.solve(task,index)
        proposal=box.get('proposal'); check=box.get('checker',{'terminal':'CANNOT_CHECK_NATIVE_PATH_NOT_EXECUTED','kernel_verified':False})
        if proposal is not None:
            record={'goal_id':gid,'proposal':proposal,'checker':check,
                    'epistemic_scope':'PROOF_SEARCH_EPISODE_NOT_THEOREM_TRUTH'}
            _,eid=self.runtime.admit_evidence(record,'observation','flt:attempt:'+str(len(self.runtime.events)),scope=scope)
            aid=gid+':attempt:'+str(len(self.runtime.events))
            self.runtime.admit_object(Atom(aid,'observation',warrant=WarrantProfile.of({eid}),scope=scope,
                quarantined=True,content_ref=digest_json(record),
                meta=meta(role='ProofAttempt',goal_id=gid,terminal=check['terminal'],environment_id=ENV_ID)),(),CertificateKind.OBSERVATION)
        kernel_evidence=None
        if outcome.decision is SV.Decision.ANSWER and check.get('kernel_verified'):
            kernel_evidence=self.admit_checked(gid,session,check,proposal['term'])
        return {'outcome':outcome.as_dict(),'proposal':proposal,'checker':check,'goal_status':self.status(gid),
                'kernel_evidence':kernel_evidence,'N_before_solve':n,'k_conservative':n,'k_over_N':1.0,
                'active_scope':'CANONICAL_NAVIGATION_TOUCHES_FULL_FIELD',
                'index_build':{'wall_seconds':build_seconds,**index.build_work},
                'preparation':dict(self.preparation),
                'native_resource_vector':ResourceVector(composition_work=0 if proposal is None else proposal['metrics']['proof_state_expansions']).as_dict(),
                'runtime_resource_vector':self.runtime.state.meter.as_dict(),
                'scientific_scaling':'NOT_ESTABLISHED'}
