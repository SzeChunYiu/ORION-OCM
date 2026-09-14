"""Exact prefix Bellman choice with all primitive deliveries charged."""
from fractions import Fraction as F


def exact(value):
    if type(value) not in (int,F) or value<0:
        raise ValueError('finite nonnegative rational price required')
    return F(value)


def solve(target,skills,primitive=1,delivery=0):
    if not isinstance(target,str):raise ValueError('string target required')
    c,d=exact(primitive),exact(delivery)
    if any(not isinstance(s,str) or not s for s in skills):
        raise ValueError('nonempty skill strings required')
    prices={s:exact(v) for s,v in skills.items()}
    n=len(target);v=[F(0)]*(n+1);w=[(n-i)*(c+d) for i in range(n+1)]
    selected=[None]*n;entries=[];local=[];tests=0;primitive_values=[]
    for i in range(n-1,-1,-1):
        p=c+d+v[i+1];best=(p,1,None);match=False
        for s,u in prices.items():
            tests+=1
            if target.startswith(s,i):
                match=True;candidate=u+len(s)*d+v[i+len(s)]
                if candidate<best[0]:best=(candidate,len(s),s)
        v[i]=best[0];selected[i]=best[1:]
        if match:entries.append(i)
        if v[i]<p:local.append(i)
        primitive_values.append(p)
    delta=[a-b for a,b in zip(w,v)]
    for i in range(n):
        if delta[i]-delta[i+1] != c+d+v[i+1]-v[i]:
            raise ValueError('local advantage identity')
    i=0;trace=[];cost=F(0);events=[]
    while i<n:
        width,s=selected[i];text=target[i] if s is None else s
        charge=c if s is None else prices[s]
        events.append(dict(position=i,kind='primitive' if s is None else 'skill',
                           emitted=text,reconstruction=charge,delivery=len(text)*d))
        trace.append(text);cost+=charge+len(text)*d;i+=width
    if ''.join(trace)!=target or cost!=v[0]:raise ValueError('executable selector')
    return dict(values=v,bare=w,delta=delta,entries=sorted(entries),local=sorted(local),
                emitted=''.join(trace),events=events,cost=cost,
                dp_primitive_choices=n,dp_match_tests=tests)


def complete_parses(target,skills,primitive=1,delivery=0,start=0):
    """Independent forward stack execution: no Bellman/reused solver values."""
    stack=[(start,F(0),'')];out=[];n=len(target)
    while stack:
        i,cost,emitted=stack.pop()
        if i==n:
            if emitted!=target[start:]:raise ValueError('oracle output mismatch')
            out.append(cost);continue
        stack.append((i+1,cost+primitive+delivery,emitted+target[i]))
        for s,u in skills.items():
            if target[i:i+len(s)]==s:
                stack.append((i+len(s),cost+u+len(s)*delivery,emitted+s))
    return out
