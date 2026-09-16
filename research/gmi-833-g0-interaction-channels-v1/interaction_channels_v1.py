from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations, product
from typing import Tuple, Iterable
import json

SOURCE_MAIN='88d8ac811f80dd3f5c0b1a20f53fdf7259e3ca9c'
FREEZE_COMMIT='d7d2c0dc99fefa3b175925d3c7884510086bee69'
CLAIM_CEILING='GMI_FINITE_EXPLICIT_COMMUNICATION_AND_EXTERNAL_CALL_OPERATORS_AT_REGISTERED_SCOPE'
FORBIDDEN_PROMOTIONS=('EMERGENT_COMMUNICATION','MULTI_AGENT_LEARNING_DERIVED','DISTRIBUTED_CONSENSUS_DERIVED','TOOL_USE_INTELLIGENCE_DERIVED','EXTERNAL_RESPONSE_IS_TRUTH','AUTHORITY_DELEGATED_TO_TOOL','AUTONOMOUS_AGENCY','COMPLETE_GMI')
AGENTS=(0,1,2); Z3=(0,1,2); MESSAGES=(0,1)
CHANNELS=tuple((a,b) for a in AGENTS for b in AGENTS if a!=b)
NO_MESSAGE='NO_MESSAGE'
RES_KEYS=('message_writes','message_reads','local_reads','local_writes','external_calls','external_input_units','external_output_units')

@dataclass(frozen=True)
class ExternalData:
    tool:str
    arg:int
    value:int
    status:str='EXTERNAL_DATA'

@dataclass(frozen=True)
class Machine:
    local:Tuple[int,int,int]
    queues:Tuple[Tuple[int,...],...]
    @staticmethod
    def empty(local=(0,0,0)):
        validate_local(local)
        return Machine(tuple(local),tuple(() for _ in CHANNELS))

def validate_local(local):
    x=tuple(local)
    if len(x)!=3 or any(type(v) is not int or v not in Z3 for v in x): raise ValueError('LOCAL_STATE')
    return x

def channel_index(src,dst):
    if type(src) is not int or type(dst) is not int or src not in AGENTS or dst not in AGENTS: raise ValueError('AGENT_OUTSIDE_CARRIER')
    if src==dst: raise ValueError('SELF_CHANNEL')
    return CHANNELS.index((src,dst))

def validate_message(m):
    if type(m) is not int or m not in MESSAGES: raise ValueError('MESSAGE_OUTSIDE_ALPHABET')
    return m

def validate_machine(machine):
    if not isinstance(machine,Machine): raise ValueError('MALFORMED_MACHINE')
    validate_local(machine.local)
    if len(machine.queues)!=6: raise ValueError('QUEUE_DOMAIN')
    for q in machine.queues:
        if not isinstance(q,tuple): raise ValueError('MALFORMED_QUEUE')
        for m in q: validate_message(m)
    return machine

def send(machine,src,dst,msg):
    validate_machine(machine); validate_message(msg); idx=channel_index(src,dst)
    qs=list(machine.queues); qs[idx]=qs[idx]+(msg,)
    return Machine(machine.local,tuple(qs)),(1,0,0,0,0,0,0)

def recv(machine,src,dst):
    validate_machine(machine); idx=channel_index(src,dst); qs=list(machine.queues); q=qs[idx]
    if q: val=q[0]; qs[idx]=q[1:]
    else: val=NO_MESSAGE
    return Machine(machine.local,tuple(qs)),val,(0,1,0,0,0,0,0)

def apply_received(machine,dst,msg):
    validate_machine(machine); validate_message(msg)
    if type(dst) is not int or dst not in AGENTS: raise ValueError('AGENT_OUTSIDE_CARRIER')
    loc=list(machine.local); loc[dst]=(loc[dst]+msg)%3
    return Machine(tuple(loc),machine.queues),(0,0,1,1,0,0,0)

TOOLS={'ROT':lambda x:(x+1)%3,'DOUBLE':lambda x:(2*x)%3}

def call(tool,arg):
    if tool not in TOOLS: raise ValueError('UNKNOWN_TOOL')
    if type(arg) is not int or arg not in Z3: raise ValueError('TOOL_ARGUMENT')
    return ExternalData(tool,arg,TOOLS[tool](arg)),(0,0,0,0,1,1,1)

def apply_external(machine,agent,data):
    validate_machine(machine)
    if type(agent) is not int or agent not in AGENTS: raise ValueError('AGENT_OUTSIDE_CARRIER')
    if not isinstance(data,ExternalData) or data.status!='EXTERNAL_DATA': raise ValueError('FORGED_EXTERNAL_DATA')
    if data.tool not in TOOLS or type(data.arg) is not int or data.arg not in Z3 or type(data.value) is not int or data.value!=TOOLS[data.tool](data.arg): raise ValueError('FORGED_EXTERNAL_DATA')
    loc=list(machine.local); loc[agent]=(loc[agent]+data.value)%3
    return Machine(tuple(loc),machine.queues),(0,0,1,1,0,0,0)

def validate_perm(pi):
    p=tuple(pi)
    if len(p)!=3 or set(p)!=set(AGENTS): raise ValueError('NON_BIJECTIVE_AGENT_REMINT')
    return p

def transport(machine,pi):
    validate_machine(machine); p=validate_perm(pi)
    loc=[0]*3
    for old,new in enumerate(p): loc[new]=machine.local[old]
    qs=[() for _ in CHANNELS]
    for idx,(src,dst) in enumerate(CHANNELS): qs[channel_index(p[src],p[dst])]=machine.queues[idx]
    return Machine(tuple(loc),tuple(qs))

def census():
    remint_checks=remint_fail=dest_fail=broadcast_fail=local_mut_fail=0
    for src,dst in CHANNELS:
        for msg in MESSAGES:
            base=Machine.empty((0,1,2)); sent,_=send(base,src,dst,msg)
            if [i for i,(a,b) in enumerate(zip(base.queues,sent.queues)) if a!=b]!=[channel_index(src,dst)]: dest_fail+=1
            if sent.local!=base.local: local_mut_fail+=1
            if sum(len(q) for q in sent.queues)!=1: broadcast_fail+=1
            for p in permutations(AGENTS):
                remint_checks+=1
                if transport(sent,p)!=send(transport(base,p),p[src],p[dst],msg)[0]: remint_fail+=1
    fifo_checks=fifo_fail=0
    for src,dst in CHANNELS:
      for m1,m2 in product(MESSAGES,repeat=2):
        x=Machine.empty(); x,_=send(x,src,dst,m1); x,_=send(x,src,dst,m2); x,a,_=recv(x,src,dst); x,b,_=recv(x,src,dst)
        fifo_checks+=1
        if (a,b)!=(m1,m2): fifo_fail+=1
    tool_checks=tool_fail=0; expected={'ROT':(1,2,0),'DOUBLE':(0,2,1)}
    for t in sorted(TOOLS):
      vals=[]
      for a in Z3:
        d,_=call(t,a); vals.append(d.value); tool_checks+=1
      if tuple(vals)!=expected[t]: tool_fail+=1
    comp={}
    for order in (('ROT','DOUBLE'),('DOUBLE','ROT')):
        comp['->'.join(order)]=[call(order[1],call(order[0],a)[0].value)[0].value for a in Z3]
    return {'remint_checks':remint_checks,'remint_failures':remint_fail,'destination_isolation_failures':dest_fail,'implicit_broadcast_failures':broadcast_fail,'send_local_mutation_failures':local_mut_fail,'fifo_checks':fifo_checks,'fifo_failures':fifo_fail,'tool_checks':tool_checks,'tool_failures':tool_fail,'tool_compositions':comp,'tool_composition_order_distinct':comp['ROT->DOUBLE']!=comp['DOUBLE->ROT']}

def separation():
    base=Machine.empty((1,0,2)); sent,_=send(base,0,1,1); recv_state,msg,_=recv(sent,0,1); applied,_=apply_received(recv_state,1,msg)
    empty_state,val,_=recv(Machine.empty(),0,1); data,_=call('ROT',0); untouched=Machine.empty((1,1,1)); applied_ext,_=apply_external(untouched,2,data)
    return {'send_does_not_change_local':sent.local==base.local,'recv_does_not_change_local':recv_state.local==base.local,'apply_received_changes_only_dst':applied.local==(1,1,2),'NO_MESSAGE_distinct_from_zero':val==NO_MESSAGE and val!=0 and empty_state==Machine.empty(),'call_result_unverified':data.status=='EXTERNAL_DATA','call_alone_no_machine_effect':untouched==Machine.empty((1,1,1)),'apply_external_changes_only_agent':applied_ext.local==(1,1,2)}

def hostiles():
    out={}; cases=[('self_send',lambda:send(Machine.empty(),0,0,1)),('agent_out',lambda:send(Machine.empty(),0,3,1)),('bad_message',lambda:send(Machine.empty(),0,1,2)),('bad_machine',lambda:validate_machine(object())),('bad_perm',lambda:validate_perm((0,0,2))),('unknown_tool',lambda:call('NOPE',0)),('bad_arg',lambda:call('ROT',3)),('forged_external',lambda:apply_external(Machine.empty(),0,ExternalData('ROT',0,2)))]
    for name,fn in cases:
        try: fn(); out[name]='ACCEPTED'
        except ValueError as e: out[name]=str(e)
    return out

def build_receipt():
    c=census(); s=separation(); h=hostiles()
    green=(c['remint_checks']==72 and c['remint_failures']==0 and c['destination_isolation_failures']==0 and c['implicit_broadcast_failures']==0 and c['send_local_mutation_failures']==0 and c['fifo_checks']==24 and c['fifo_failures']==0 and c['tool_checks']==6 and c['tool_failures']==0 and c['tool_composition_order_distinct'] and all(s.values()) and 'ACCEPTED' not in h.values())
    return {'schema':'GMI833InteractionChannelsReceiptV1','parent_issue':833,'issue':887,'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'agents':list(AGENTS),'message_alphabet':list(MESSAGES),'channels':[list(x) for x in CHANNELS],'tools':sorted(TOOLS),'resource_vector':list(RES_KEYS),'census':c,'separation':s,'hostiles':h,'claim_ceiling':CLAIM_CEILING,'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),'terminal':'GMI_833_INTERACTION_CHANNELS_V1_ALL_GREEN' if green else 'RED'}
def canonical_json(o): return json.dumps(o,indent=2,sort_keys=True,separators=(',',': '))+'\n'
def main(): print(canonical_json(build_receipt()),end='')
if __name__=='__main__': main()
