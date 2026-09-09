"""Additive research binding to the existing OCM runtime; not a second truth store."""
from __future__ import annotations
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
import json
import math
import sys
import time
from typing import Callable
from mechanisms import (REPO,SCHEMA,M,MethodScope,encoded,digest,require,wire,coefficients,
                        recover_method,prefix_search,learn_guard,validate_guard,
                        select_representation,validate_representation_certificate)
from diagnosis import diagnose
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.runtime import solve as SV
from ocm.operators.registry import OperatorSpec, BackendKind
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
sys.path.insert(0,str(REPO/'research/g2-cognitive-objects-v1'))
from g2_cognitive_objects.types import (FailureAttemptV1,RepresentationChangeV1,ScopeState,
    FailureKind,ResourceVector,AcquisitionLineage,OriginCategory,CheckStatus,CorrectnessEvidence,
    Verdict,UsefulnessEvidence,CurrentAuthorizationState,Liveness,PrimitiveAlias)

SCOPE=Scope.of('g3-scoped-development.v1')
METHOD='g3:imported-macro'; GUARD='g3:failure-guard'; FAILURE='g3:failed-attempt'


def lease(rt):
    return {'head':rt.events[-1].event_hash if rt.events else None,'state':rt.state.kso_state_hash,
            'evidence':rt.state.evidence_epoch,'registry':rt.state.registry_revision}


def live(rt,w):
    return rt.state.evidence.nogoods.filter_interval(rt.state.nogoods.filter_interval(w)).liveness(
        rt.state.revoked|rt.state.evidence.revoked).value


def add_atom(rt,name,kind,body,w):
    anchor=Atom(name+':input','observation',w,scope=SCOPE,quarantined=True)
    atom=Atom(name,kind,w,scope=SCOPE,content_ref=digest(body),meta=(('data',encoded(body).decode()),))
    edge=Hyperedge(name+':support',(anchor.atom_id,),(name,),'SUPPORT',warrant=w,scope=SCOPE,
                   head_weights=(Fraction(1),))
    rt.admit_batch(((anchor,(),'OBSERVATION'),(atom,(edge,),'OBSERVATION')))


def payload(rt,name):
    atom=rt.state.ks.atom_view.get(name)
    require(atom is not None and atom.scope==SCOPE and len(atom.meta)==1 and atom.meta[0][0]=='data',
            'MISSING_OR_MALFORMED_FIELD_OBJECT')
    body=json.loads(atom.meta[0][1]); require(digest(body)==atom.content_ref,'FIELD_PAYLOAD_IDENTITY')
    return body


def check_bindings(rt,binding,source):
    require(binding['source']==source,'SOURCE_DRIFT')
    require(payload(rt,METHOD)==binding['method_body'],'METHOD_BINDING')
    require(live(rt,rt.state.evidence.citation_warrant([binding['environment']]))=='LIVE','ENVIRONMENT_NOT_LIVE')


def load(root,binding,source,expected):
    rt=OCMRuntime(root); require(lease(rt)==expected,'STALE_LINEAGE_LEASE')
    check_bindings(rt,binding,source);return rt


def install(root,source):
    rt=OCMRuntime(root);require(not rt.events,'NONEMPTY_LINEAGE')
    _,env=rt.admit_evidence({'source':source,'contract':SCHEMA},'instruction','g3:environment',scope=SCOPE)
    method=recover_method()
    _,permission=rt.admit_evidence(method,'instruction','g3:historical-method-import-permission',scope=SCOPE)
    w=rt.state.evidence.citation_warrant([env,permission]);add_atom(rt,METHOD,'procedure',method,w)
    rt.persist()
    return {'source':source,'environment':env,'method_permission':permission,'method_body':method,
            'guard_permission':None,'failure_evidence':None,'representation':None,
            'representation_permission':None,'observer':'coefficients'},rt


def acquire_failure(rt,binding):
    s=MethodScope(source=binding['source']);start=time.perf_counter();cpu=time.process_time()
    attempt=prefix_search(M.normal_form(('inc',)),s,'training:inc')
    guard=learn_guard(attempt);require(guard is not None,'NO_GENERALIZABLE_FAILURE')
    validate_guard(guard,attempt)
    _,episode=rt.admit_evidence(attempt,'observation','g3:executed-failure',scope=SCOPE)
    _,validation=rt.admit_evidence({'attempt':digest(attempt),'guard':digest(guard),
                    'checker':'independent-complete-enumeration+degree-bounded-polynomial-identity'},
                    'proof','g3:checked-failure-generalization',scope=SCOPE)
    support=[binding['environment'],binding['method_permission'],episode,validation]
    authorization=CurrentAuthorizationState(admitted=True,proof_liveness=Liveness.LIVE,
        applicability_liveness=Liveness.LIVE,serving_liveness=Liveness.LIVE,warrant_ids=tuple(support),
        scope=ScopeState(contexts=('g3-scoped-development.v1',)),status=CheckStatus.MEASURED)
    transport=FailureAttemptV1(attempt_id=digest(attempt),method_id=METHOD,
        task_id=digest(attempt['target']),scope=ScopeState(contexts=('g3-scoped-development.v1',)),
        budget=digest(s.data()),environment_version=s.environment,outcome=attempt['terminal'],
        feedback='Complete bounded prefix failure; primitive fallback remains admissible.',
        failure_kind=FailureKind.METHOD_FAILURE,
        resources=ResourceVector(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
            work_units=attempt['checked_programs'],verifier_calls=2,
            notes=('Timing includes acquisition/validation; historical macro acquisition is unpaid.',
                   'Zero default coordinates without a stated meter are not physical measurements.')),
        acquisition_lineage=AcquisitionLineage(origin_category=OriginCategory.LEARNED_APPLICABILITY,
            episode_ids=(episode,),donor_ids=(METHOD,),prior_information_ids=('fixed-feature-menu-v1',),
            source_sha256=binding['source'],training_task_ids=(digest(attempt['target']),),
            discovery_evidence_id=episode,status=CheckStatus.MEASURED),
        correctness=CorrectnessEvidence(checker_id='complete-enumeration-independent-point-check',
            proof_evidence_id=validation,certificate_sha256=digest(guard),verdict=Verdict.PASS,
            status=CheckStatus.MEASURED),
        usefulness=UsefulnessEvidence(status=CheckStatus.CANNOT_CHECK,
            cannot_check_reason='Fresh-task intervention has not run at admission.'),authorization=authorization)
    w=rt.state.evidence.citation_warrant(support)
    add_atom(rt,FAILURE,'observation',{'transport':asdict(transport),'attempt':attempt},w)
    add_atom(rt,GUARD,'constraint',guard,w)
    binding=dict(binding,guard_permission=validation,failure_evidence=episode)
    rt.persist();return binding,{'attempt':attempt,'guard':guard,'transport':asdict(transport),
        'acquisition_wall_seconds':time.perf_counter()-start,'acquisition_cpu_seconds':time.process_time()-cpu}


def active_guard(rt,binding):
    if binding['guard_permission'] is None:return None,0
    atom=rt.state.ks.atom_view.get(GUARD)
    require(atom is not None,'MISSING_GUARD')
    if live(rt,atom.warrant)!='LIVE':return None,0
    guard=payload(rt,GUARD);attempt=payload(rt,FAILURE)['attempt']
    count=validate_guard(guard,attempt)
    return guard,count


def change_guard_permission(rt,binding,restore):
    require(binding['guard_permission'] is not None,'NO_GUARD_PERMISSION')
    if restore:rt.reinstate([binding['guard_permission']])
    else:rt.revoke([binding['guard_permission']])
    rt.persist()
    return {'guard_liveness':live(rt,rt.state.ks.atom_view[GUARD].warrant),
            'method_liveness':live(rt,rt.state.ks.atom_view[METHOD].warrant),
            'logical_nogoods':rt.state.nogoods.as_dict()}


def inspect_last_backend(_ks,inputs):
    p=tuple(inputs['program']);require(all(t in M.PRIMITIVES for t in p),'OBSERVER_INPUT')
    return {'program':list(p),'last':p[-1] if p else None}


def inspect_last_checker(packet):
    return SV.Status.PASS if packet.get('last')==(packet['program'][-1] if packet['program'] else None) else SV.Status.FAIL


def acquire_representation(rt,binding,observer):
    start=time.perf_counter();cpu=time.process_time();old=binding['representation']
    before=payload(rt,old) if old else None
    invalidation=None
    if binding['observer']!=observer:
        require(observer=='coefficients-last','UNREGISTERED_OBSERVER_CHANGE')
        require(before is not None,'NO_REPRESENTATION_TO_REFINE')
        try:
            validate_representation_certificate(before,observer,5)
        except ValueError:
            invalidation={'old':old,'old_observer':binding['observer'],'new_observer':observer,
                          'terminal':diagnose({'kind':'representation','left':['inc','dec'],'right':['dec','inc'],
                              'representation':before['name'],'observer':observer,'bound':5})['terminal'],
                          'left':['inc','dec'],'right':['dec','inc'],
                          'equal_coefficients':wire(M.normal_form(('inc','dec'))),
                          'new_observations':['dec','inc']}
        require(invalidation is not None,'EXPECTED_REPRESENTATION_BREAK_NOT_ESTABLISHED')
        rt.revoke([binding['representation_permission']])
        w=rt.state.evidence.citation_warrant([binding['environment']])
        rt.register_operator(OperatorSpec('g3:inspect-last',binding['source'],BackendKind.PROGRAMMATIC,
            inspect_last_backend,(),output_type='observation',warrant=w,scope=SCOPE,checker=inspect_last_checker))
    cert=select_representation(observer,5);validate_representation_certificate(cert,observer,5)
    _,permission=rt.admit_evidence({'certificate':digest(cert),'observer':observer,'source':binding['source']},
                    'proof','g3:checked-representation-contract',scope=SCOPE)
    name='g3:representation:'+observer
    w=rt.state.evidence.citation_warrant([binding['environment'],permission])
    add_atom(rt,name,'representation',cert,w)
    transport=RepresentationChangeV1(change_id=digest(cert),before_representation_id=old or 'RAW_PROGRAM_STATES',
        after_representation_id=name,trigger='OBSERVATION_ALIAS' if before else 'CHECKED_FINITE_REPRESENTATION_SELECTION',
        primitive_alias=PrimitiveAlias.NOT_ASSESSED,
        lifecycle_equivalence=CheckStatus.CANNOT_CHECK if invalidation else CheckStatus.MEASURED,
        acquisition_lineage=AcquisitionLineage(origin_category=OriginCategory.LEARNED_APPLICABILITY,
             episode_ids=(permission,),prior_information_ids=('fixed-representation-language-v1',),
             source_sha256=binding['source'],discovery_evidence_id=permission,status=CheckStatus.MEASURED),
        correctness=CorrectnessEvidence(checker_id='finite-observation-depth-successor-congruence',
             proof_evidence_id=permission,certificate_sha256=digest(cert),verdict=Verdict.PASS,status=CheckStatus.MEASURED),
        usefulness=UsefulnessEvidence(status=CheckStatus.CANNOT_CHECK,
             cannot_check_reason='Only contract preservation established before fresh serving.'),
        authorization=CurrentAuthorizationState(admitted=True,proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.LIVE,serving_liveness=Liveness.LIVE,
            warrant_ids=(binding['environment'],permission),scope=ScopeState(contexts=('g3-scoped-development.v1',)),
            status=CheckStatus.MEASURED),
        notes=('Equivalence protects registered observations, budget depth and actions, not identical work traces.',
               'A new distinguishing operator invalidates the old scope before reuse.'))
    add_atom(rt,name+':change','observation',asdict(transport),w)
    binding=dict(binding,representation=name,representation_permission=permission,observer=observer)
    rt.persist()
    return binding,{'certificate':cert,'transport':asdict(transport),'invalidation':invalidation,
        'old_liveness':live(rt,rt.state.ks.atom_view[old].warrant) if old else None,
        'acquisition_wall_seconds':time.perf_counter()-start,'acquisition_cpu_seconds':time.process_time()-cpu}


def active_representation(rt,binding):
    name=binding['representation'];require(name is not None,'NO_REPRESENTATION')
    atom=rt.state.ks.atom_view.get(name);require(atom is not None and live(rt,atom.warrant)=='LIVE', 'REPRESENTATION_NOT_LIVE')
    cert=payload(rt,name);validate_representation_certificate(cert,binding['observer'],5);return cert


def diagnostic(x):
    if isinstance(x,float) and not math.isfinite(x):return {'extended_real':str(x)}
    if isinstance(x,Fraction):return str(x)
    if isinstance(x,dict):return {str(k):diagnostic(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [diagnostic(v) for v in x]
    return x


def commit_batch(rt,binding,occurrence,targets,generate:Callable,extra_support=()):
    """One vector-valued proof claim; every issued goal is independently checked.

    Batch boundaries avoid inventing per-goal OCM overhead from a full-history
    ledger; actual batch/replay costs are measured and never called sparse scaling.
    """
    require(len(targets)>0 and len({t['identity'] for t in targets})==len(targets),'COMPLETE_UNIQUE_POPULATION')
    require(all(t['identity']==digest(wire(t['coefficients'])) for t in targets),'GOAL_IDENTITY')
    taskbody={'occurrence':occurrence,'targets':targets,'source':binding['source']}
    _,issued_id=rt.admit_evidence(taskbody,'instruction','g3:issued-goal-batch',scope=SCOPE)
    qid='g3:query:'+occurrence
    support=[binding['environment'],issued_id,*extra_support]
    support=list(dict.fromkeys(support))
    query_w=rt.state.evidence.citation_warrant([binding['environment'],issued_id])
    answer_w=rt.state.evidence.citation_warrant(support)
    add_atom(rt,qid,'query_seed',taskbody,query_w)
    issued=None;op=None;key=None;stats={'dispatches':0,'checks':0,'verified_goals':0}
    def current():
        require(rt.state.operators.operators.get(key) is op,'DISPATCHER_CHANGED')
        require(live(rt,answer_w)=='LIVE','SUPPORT_CHANGED')
    def backend(ks,inputs):
        nonlocal issued
        current();require(inputs=={'qid':qid},'ISSUED_QUERY_BINDING')
        stats['dispatches']+=1;packet=generate();issued=encoded(packet);return json.loads(issued)
    def checker(packet):
        stats['checks']+=1
        try:
            current();require(issued is not None and encoded(packet)==issued,'UNISSUED_PACKET')
            require(type(packet) is dict and set(packet)=={'rows'} and len(packet['rows'])==len(targets),'PACKET_POPULATION')
            for goal,row in zip(targets,packet['rows']):
                require(row['target']==goal['identity'],'ISSUED_TARGET_ORDER')
                result=row['result']
                require(result['terminal']=='VERIFIED_POLYNOMIAL_IDENTITY','UNVERIFIED_GOAL')
                p=tuple(result['program']);require(len(p)<=5,'OUTSIDE_ISSUED_LENGTH')
                require(M.normal_form(p)==coefficients(goal['coefficients']),'EXACT_POLYNOMIAL_REFUSAL')
                stats['verified_goals']+=1
            return SV.Status.PASS
        except Exception as exc:
            stats['error']=str(exc);return SV.Status.CANNOT_CHECK
    env_w=rt.state.evidence.citation_warrant([binding['environment']])
    op=OperatorSpec('g3:goal-dispatch',binding['source'],BackendKind.PROGRAMMATIC,backend,(),
                   output_type='proof',warrant=env_w,scope=SCOPE,checker=checker)
    key=rt.register_operator(op)
    wrapper=SV.OperatorSpec(op.operator_id,op.version,lambda ks,name,ctx:op.backend(ks,{'qid':qid}),
        (qid,),output_type='proof',warrant=answer_w,scope=SCOPE,checker=checker)
    outcome=rt.solve(SV.Task(qid,(SV.QueryPart(qid,'query_seed',(qid,)),),context='g3-scoped-development.v1'),(wrapper,))
    rt.persist()
    return {**stats,'committed':SV.committed(outcome),'trace':diagnostic(outcome.trace.as_dict()),
            'packet':json.loads(issued) if issued is not None else None,'answer_support':support,
            'event_count':len(rt.events),'runtime_meter':rt.state.meter.as_dict(),'lease':lease(rt)}
