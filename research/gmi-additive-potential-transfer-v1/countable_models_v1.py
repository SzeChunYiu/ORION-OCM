"""Analytic countable witnesses; finite calls do not verify all-state premises."""
from fractions import Fraction as F
from finite_model_v1 import exact

def positive_state(n):
    if type(n) is not int or n<1:
        raise ValueError("positive integer state required")

def polynomial_row(n,theta):
    positive_state(n)
    theta=exact(theta)
    if not 0<=theta<=1:
        raise ValueError("theta outside registered continuum")
    p=(n*n-theta)/((n+1)**2)
    return {0:1-p,n+1:p}

def polynomial_slacks(n,theta,envelope):
    positive_state(n)
    theta,e=exact(theta),exact(envelope)
    if not 0<=theta<=e<=1:
        raise ValueError("parameter outside supplied confidence interval")
    p=polynomial_row(n,theta)[n+1]
    nominal=polynomial_row(n,0)[n+1]
    duration=2*n-p*2*(n+1)-1
    r=2*e/(n+1)
    row_error=abs(p-nominal)*2*(n+1)
    epsilon=e/((n+1)**2)
    return dict(duration=duration,work=duration,error=r-row_error,
                reserve=2*e*(1-p)-r,
                event_row=epsilon-abs(p-nominal),
                event_reserve=e*(1-p)-epsilon)

def doubling_row(n):
    positive_state(n)
    return {0:F(1,2),2*n:F(1,2)}

def walk(row,start,horizon,potential=None):
    """Independent path distribution execution from each supplied next-state row."""
    positive_state(start)
    if type(horizon) is not int or horizon<0:
        raise ValueError("nonnegative integer horizon required")
    active={start:F(1)}
    cost=F(0)
    for _ in range(horizon):
        next_active={}
        cost+=sum(active.values())
        for x,mass in active.items():
            outcomes=row(x)
            if sum(outcomes.values())!=1 or any(p<0 for p in outcomes.values()):
                raise ValueError("invalid executed row")
            for y,p in outcomes.items():
                if y and p:
                    next_active[y]=next_active.get(y,F(0))+mass*p
        active=next_active
    value=None if potential is None else sum(p*potential(x) for x,p in active.items())
    return dict(prefix_cost=cost,survival=sum(active.values()),envelope=value)

def polynomial_controls():
    minimum=None
    rows=0
    for n in (1,2,7,32):
        for e in (F(0),F(1,4),F(1)):
            for theta in sorted({F(0),e/2,e}):
                slacks=polynomial_slacks(n,theta,e)
                current=min(slacks.values())
                if current<0:
                    raise AssertionError("polynomial certificate arithmetic failed")
                minimum=current if minimum is None else min(minimum,current)
                rows+=1
    intervals=[]
    for theta in (F(0),F(1,4),F(1)):
        out=walk(lambda n:polynomial_row(n,theta),1,16,lambda n:2*n)
        if theta==0 and out["survival"]!=F(1,17**2):
            raise AssertionError("polynomial telescoping oracle mismatch")
        intervals.append(dict(theta=theta,lower=out["prefix_cost"],
                              upper=out["prefix_cost"]+out["envelope"],
                              survival=out["survival"]))
    return dict(rational_rows=rows,minimum_slack=minimum,prefix_horizon=16,
                exact_cost_intervals=intervals,
                all_state_warrant="analytic identities C1-C2, not finite enumeration")

def envelope_controls():
    records=[]
    for h in (0,1,4,12):
        out=walk(doubling_row,3,h,lambda n:n+2)
        if out["envelope"]!=3+F(2,2**h) or out["prefix_cost"]!=2-F(2,2**h):
            raise AssertionError("nonvanishing envelope control failed")
        records.append(dict(horizon=h,**out,actual_cost_tail=F(2,2**h)))
    signed=walk(doubling_row,2,4,lambda n:2-n)
    if signed["prefix_cost"]<=0 or signed["envelope"]!=-signed["prefix_cost"]:
        raise AssertionError("signed-potential countermodel failed")
    return dict(nonvanishing_envelope_limit=3,actual_expected_cost=2,
                finite_prefixes=records,signed_potential_countermodel=signed)
