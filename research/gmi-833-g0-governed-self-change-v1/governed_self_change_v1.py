from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from typing import Tuple
import hmac, json

SOURCE_MAIN='88d8ac811f80dd3f5c0b1a20f53fdf7259e3ca9c'
FREEZE_COMMIT='b3afee5e0c8e70812653cf92ef9fd703d77b9d18'
CLAIM_CEILING='GMI_FINITE_GOVERNED_SELF_CHANGE_AND_VERIFIER_ADOPTION_AT_REGISTERED_SCOPE'
FORBIDDEN_PROMOTIONS=(
 'RECURSIVE_SELF_IMPROVEMENT_PROVED','AUTONOMOUS_SELF_AUTHORITY','VERIFIER_INFALLIBLE',
 'ARBITRARY_CODE_SAFE','SELF_MODIFICATION_OPTIMAL','UNBOUNDED_DEVELOPMENT',
 'CONSTITUTION_SELF_EDITABLE','COMPLETE_GMI')
Z3=(0,1,2)
AUTHORITY_ID='VERIFIER_V1'
ACCEPT='ACCEPT'; REJECT='REJECT'
PROPOSE_RESOURCES=(1,0,0,0,0,0)
VERIFY_RESOURCES=(0,1,1,0,0,0)
ADOPT_SUCCESS_RESOURCES=(0,0,0,1,1,1)
ADOPT_FAILURE_RESOURCES=(0,0,0,1,0,0)

@dataclass(frozen=True)
class ActiveMachine:
    behavior: Tuple[int,int,int]
    version: int

@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    candidate: Tuple[int,int,int]
    candidate_digest: str
    base_version: int
    sequence: int

@dataclass(frozen=True)
class VerificationReceipt:
    proposal_id: str
    candidate_digest: str
    base_version: int
    decision: str
    authority_id: str
    signature: str

@dataclass(frozen=True)
class GovernanceState:
    active: ActiveMachine
    pending: Tuple[Proposal,...]
    consumed: Tuple[str,...]
    next_sequence: int

@dataclass(frozen=True)
class TransitionResult:
    state: GovernanceState
    terminal: str
    resources: Tuple[int,int,int,int,int,int]

def validate_behavior(b):
    x=tuple(b)
    if len(x)!=3 or any(type(v) is not int or v not in Z3 for v in x):
        raise ValueError('MALFORMED_BEHAVIOR')
    return x

def validate_active(a):
    if not isinstance(a,ActiveMachine): raise ValueError('MALFORMED_ACTIVE')
    validate_behavior(a.behavior)
    if type(a.version) is not int or a.version<0: raise ValueError('INVALID_VERSION')
    return a

def validate_state(s):
    if not isinstance(s,GovernanceState): raise ValueError('MALFORMED_STATE')
    validate_active(s.active)
    if type(s.next_sequence) is not int or s.next_sequence<0: raise ValueError('INVALID_SEQUENCE')
    ids=[p.proposal_id for p in s.pending]
    if len(ids)!=len(set(ids)): raise ValueError('DUPLICATE_PENDING_ID')
    if set(ids) & set(s.consumed): raise ValueError('PENDING_CONSUMED_COLLISION')
    for p in s.pending:
        validate_behavior(p.candidate)
        if p.candidate_digest != candidate_digest(p.candidate): raise ValueError('PENDING_DIGEST_CORRUPTION')
        if type(p.base_version) is not int or p.base_version<0: raise ValueError('INVALID_PROPOSAL_VERSION')
    return s

def base_state():
    return GovernanceState(ActiveMachine((0,1,2),0),(),(),0)

def candidate_digest(candidate):
    c=validate_behavior(candidate)
    return sha256(json.dumps(c,separators=(',',':')).encode()).hexdigest()

def proposal_id(base_version,sequence,digest):
    return sha256(f'{base_version}:{sequence}:{digest}'.encode()).hexdigest()

def propose(state,candidate):
    validate_state(state); c=validate_behavior(candidate); d=candidate_digest(c)
    p=Proposal(proposal_id(state.active.version,state.next_sequence,d),c,d,state.active.version,state.next_sequence)
    ns=GovernanceState(state.active,state.pending+(p,),state.consumed,state.next_sequence+1)
    return ns,p,PROPOSE_RESOURCES

class ExternalVerifier:
    def __init__(self,secret:bytes,authority_id=AUTHORITY_ID):
        self.__secret=bytes(secret); self.authority_id=authority_id
    @staticmethod
    def policy(candidate):
        c=validate_behavior(candidate)
        return ACCEPT if c[0]==0 else REJECT
    def _payload(self,p,decision):
        return f'{self.authority_id}|{p.proposal_id}|{p.base_version}|{p.candidate_digest}|{decision}'.encode()
    def verify(self,p):
        if not isinstance(p,Proposal): raise ValueError('MALFORMED_PROPOSAL')
        decision=self.policy(p.candidate)
        sig=hmac.new(self.__secret,self._payload(p,decision),'sha256').hexdigest()
        return VerificationReceipt(p.proposal_id,p.candidate_digest,p.base_version,decision,self.authority_id,sig),VERIFY_RESOURCES
    def validate(self,p,r):
        if not isinstance(r,VerificationReceipt): return False,'MALFORMED_RECEIPT'
        if r.authority_id!=self.authority_id: return False,'AUTHORITY_MISMATCH'
        if (r.proposal_id,r.candidate_digest,r.base_version)!=(p.proposal_id,p.candidate_digest,p.base_version): return False,'RECEIPT_BINDING_MISMATCH'
        expected_decision=self.policy(p.candidate)
        if r.decision not in (ACCEPT,REJECT) or r.decision!=expected_decision: return False,'RECEIPT_DECISION_INVALID'
        sig=hmac.new(self.__secret,self._payload(p,r.decision),'sha256').hexdigest()
        if not hmac.compare_digest(sig,r.signature): return False,'SIGNATURE_INVALID'
        return True,'VALID'

def fixture_verifier():
    return ExternalVerifier(b'GMI833-E6-FIXTURE-VERIFIER-SECRET-V1')

def _pending_lookup(state,pid):
    return next((p for p in state.pending if p.proposal_id==pid),None)

def adopt(state,proposal,receipt,verifier):
    validate_state(state)
    if not isinstance(proposal,Proposal): return TransitionResult(state,'MALFORMED_PROPOSAL',ADOPT_FAILURE_RESOURCES)
    if proposal.proposal_id in state.consumed: return TransitionResult(state,'PROPOSAL_ALREADY_CONSUMED',ADOPT_FAILURE_RESOURCES)
    stored=_pending_lookup(state,proposal.proposal_id)
    if stored is None: return TransitionResult(state,'PROPOSAL_NOT_PENDING',ADOPT_FAILURE_RESOURCES)
    if stored!=proposal: return TransitionResult(state,'PROPOSAL_STATE_MISMATCH',ADOPT_FAILURE_RESOURCES)
    ok,reason=verifier.validate(proposal,receipt)
    if not ok: return TransitionResult(state,reason,ADOPT_FAILURE_RESOURCES)
    if proposal.base_version!=state.active.version: return TransitionResult(state,'STALE_BASE_VERSION',ADOPT_FAILURE_RESOURCES)
    if receipt.decision!=ACCEPT: return TransitionResult(state,'REJECTED_BY_VERIFIER',ADOPT_FAILURE_RESOURCES)
    active=ActiveMachine(proposal.candidate,state.active.version+1)
    pending=tuple(p for p in state.pending if p.proposal_id!=proposal.proposal_id)
    ns=GovernanceState(active,pending,state.consumed+(proposal.proposal_id,),state.next_sequence)
    return TransitionResult(ns,'ADOPTED',ADOPT_SUCCESS_RESOURCES)

def candidate_space():
    return tuple(product(Z3,repeat=3))

def exact_census():
    verifier=fixture_verifier()
    accepted=rejected=inert_fail=adopt_fail=reject_mutation_fail=replay_fail=0
    for c in candidate_space():
        s0=base_state(); sp,p,pres=propose(s0,c)
        if sp.active!=s0.active or pres!=PROPOSE_RESOURCES: inert_fail+=1
        r,vres=verifier.verify(p)
        if vres!=VERIFY_RESOURCES: adopt_fail+=1
        tr=adopt(sp,p,r,verifier)
        if r.decision==ACCEPT:
            accepted+=1
            if tr.terminal!='ADOPTED' or tr.state.active.behavior!=c or tr.state.active.version!=1 or tr.resources!=ADOPT_SUCCESS_RESOURCES: adopt_fail+=1
            rr=adopt(tr.state,p,r,verifier)
            if rr.terminal!='PROPOSAL_ALREADY_CONSUMED' or rr.state!=tr.state: replay_fail+=1
        else:
            rejected+=1
            if tr.terminal!='REJECTED_BY_VERIFIER' or tr.state.active!=s0.active or tr.resources!=ADOPT_FAILURE_RESOURCES: reject_mutation_fail+=1
    accepted_cs=[c for c in candidate_space() if c[0]==0]
    s=base_state(); s,p1,_=propose(s,accepted_cs[0]); s,p2,_=propose(s,accepted_cs[1]); r1,_=verifier.verify(p1); r2,_=verifier.verify(p2)
    a1=adopt(s,p1,r1,verifier); stale=adopt(a1.state,p2,r2,verifier)
    stale_ok=stale.terminal=='STALE_BASE_VERSION' and stale.state==a1.state
    s=base_state(); s,p1,_=propose(s,(0,2,1)); r1,_=verifier.verify(p1); a1=adopt(s,p1,r1,verifier)
    s2,p2,_=propose(a1.state,(0,2,2)); r2,_=verifier.verify(p2); a2=adopt(s2,p2,r2,verifier)
    path_ok=a1.terminal=='ADOPTED' and a1.state.active==ActiveMachine((0,2,1),1) and p2.base_version==1 and a2.terminal=='ADOPTED' and a2.state.active==ActiveMachine((0,2,2),2)
    return {'candidate_count':27,'accepted':accepted,'rejected':rejected,'proposal_inert_failures':inert_fail,'accepted_adoption_failures':adopt_fail,'rejected_mutation_failures':reject_mutation_fail,'replay_failures':replay_fail,'stale_receipt_control':stale_ok,'two_generation_control':path_ok}

def hostiles():
    verifier=fixture_verifier(); out={}
    s=base_state(); s,p,_=propose(s,(0,2,1)); r,_=verifier.verify(p)
    cases=[
      ('authority',VerificationReceipt(r.proposal_id,r.candidate_digest,r.base_version,r.decision,'OTHER',r.signature),'AUTHORITY_MISMATCH'),
      ('signature',VerificationReceipt(r.proposal_id,r.candidate_digest,r.base_version,r.decision,r.authority_id,'0'*64),'SIGNATURE_INVALID'),
      ('decision',VerificationReceipt(r.proposal_id,r.candidate_digest,r.base_version,REJECT,r.authority_id,r.signature),'RECEIPT_DECISION_INVALID'),
      ('digest',VerificationReceipt(r.proposal_id,'f'*64,r.base_version,r.decision,r.authority_id,r.signature),'RECEIPT_BINDING_MISMATCH'),
      ('version',VerificationReceipt(r.proposal_id,r.candidate_digest,9,r.decision,r.authority_id,r.signature),'RECEIPT_BINDING_MISMATCH')]
    for name,rr,expected in cases:
        tr=adopt(s,p,rr,verifier); out[name]=tr.terminal
        if tr.terminal!=expected or tr.state!=s: out[name]='FAIL'
    fakep=Proposal(p.proposal_id,(0,1,1),candidate_digest((0,1,1)),p.base_version,p.sequence)
    out['candidate_swap']=adopt(s,fakep,r,verifier).terminal
    sr=base_state(); sr,pr,_=propose(sr,(1,0,0)); real_reject,_=verifier.verify(pr)
    forged=VerificationReceipt(pr.proposal_id,pr.candidate_digest,pr.base_version,ACCEPT,AUTHORITY_ID,real_reject.signature)
    out['forged_accept']=adopt(sr,pr,forged,verifier).terminal
    try: validate_behavior((0,1,3)); out['malformed_candidate']='ACCEPTED'
    except ValueError as e: out['malformed_candidate']=str(e)
    try: validate_active(ActiveMachine((0,1,2),-1)); out['negative_version']='ACCEPTED'
    except ValueError as e: out['negative_version']=str(e)
    out['proposal_has_signature_field']=str('signature' in Proposal.__dataclass_fields__)
    out['verifier_secret_on_proposal']=str(any('secret' in x.lower() for x in Proposal.__dataclass_fields__))
    return out

def build_receipt():
    c=exact_census(); h=hostiles()
    green=(c=={'candidate_count':27,'accepted':9,'rejected':18,'proposal_inert_failures':0,'accepted_adoption_failures':0,'rejected_mutation_failures':0,'replay_failures':0,'stale_receipt_control':True,'two_generation_control':True}
           and h['authority']=='AUTHORITY_MISMATCH' and h['signature']=='SIGNATURE_INVALID' and h['decision']=='RECEIPT_DECISION_INVALID' and h['digest']=='RECEIPT_BINDING_MISMATCH' and h['version']=='RECEIPT_BINDING_MISMATCH' and h['candidate_swap']=='PROPOSAL_STATE_MISMATCH' and h['forged_accept']=='RECEIPT_DECISION_INVALID' and h['malformed_candidate']=='MALFORMED_BEHAVIOR' and h['negative_version']=='INVALID_VERSION' and h['proposal_has_signature_field']=='False' and h['verifier_secret_on_proposal']=='False')
    return {'schema':'GMI833GovernedSelfChangeReceiptV1','parent_issue':833,'issue':889,'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'verifier_authority':AUTHORITY_ID,'verifier_policy':'candidate[0] == 0','resource_vector':['proposals_written','verifier_calls','candidate_checks','adoption_attempts','active_writes','version_increments'],'resources':{'PROPOSE':list(PROPOSE_RESOURCES),'VERIFY':list(VERIFY_RESOURCES),'ADOPT_SUCCESS':list(ADOPT_SUCCESS_RESOURCES),'ADOPT_FAILURE':list(ADOPT_FAILURE_RESOURCES)},'census':c,'hostiles':h,'claim_ceiling':CLAIM_CEILING,'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),'terminal':'GMI_833_GOVERNED_SELF_CHANGE_V1_ALL_GREEN' if green else 'RED'}
def canonical_json(o): return json.dumps(o,indent=2,sort_keys=True,separators=(',',': '))+'\n'
def main(): print(canonical_json(build_receipt()),end='')
if __name__=='__main__': main()
