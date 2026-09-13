"""Independent recursive execution of chosen events with actual retained strings."""
from hierarchy_v1 import price


def replay_events(reg, workload, allowed, events):
    cursor=0;store={};ledger=[];delivery=[]
    def emit(text):
        delivery.extend(('deliver',a,reg.delivery_price(a)) for a in text)
        return text
    def consume(kind,t,amount):
        nonlocal cursor
        expected=(kind,t,price(amount))
        if cursor>=len(events) or events[cursor]!=expected:
            raise ValueError('illegal event or incomplete charge')
        ledger.append(expected);cursor+=1
    def execute(t):
        if type(t) is str:
            consume('primitive',t,reg.costs[reg.primitives.index(t)]);return emit(t)
        if cursor<len(events) and events[cursor][0]=='invoke':
            if t not in store:raise ValueError('unacquired compiled artifact')
            consume('invoke',t,reg.invocation[t]);return emit(store[t])
        consume('expand',t,reg.dispatch[t])
        body=''.join(execute(child) for child in reg.bodies[t])
        if cursor<len(events) and events[cursor][:2]==('retain',t):
            if t in store or t not in allowed:raise ValueError('illegal admission')
            consume('retain',t,reg.admission[t])
            if body!=reg.expansion(t):raise ValueError('compiled trace failed verification')
            store[t]=body
        return body
    result=''.join(execute(t) for t in workload)
    if cursor!=len(events):raise ValueError('extra execution events')
    if result!=''.join(reg.expansion(t) for t in workload):raise ValueError('output mismatch')
    return dict(output=result,artifacts=store,total=sum(x[2] for x in ledger+delivery),
                reconstruction_charge=sum(x[2] for x in ledger),
                delivery_charge=sum(x[2] for x in delivery),delivery_events=delivery,
                actual_events=len(ledger)+len(delivery),retained_symbols=sum(map(len,store.values())))
