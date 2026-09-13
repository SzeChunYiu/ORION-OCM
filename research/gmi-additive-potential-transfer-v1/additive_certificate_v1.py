"""Finite rational sufficient certificates for explicit rowwise hulls."""
from fractions import Fraction as F
from finite_model_v1 import exact,validate

def potential(values,n):
    result=tuple(map(exact,values))
    if len(result)!=n+2 or any(v<0 for v in result) or any(result[n:]):
        raise ValueError("finite nonnegative potential, zero on both terminals required")
    return result

def row_values(values,shape,name):
    out=tuple(tuple(map(exact,row)) for row in values)
    if tuple(map(len,out))!=shape or any(v<0 for row in out for v in row):
        raise ValueError("invalid nonnegative "+name+" row register")
    return out

def certify(vertices,nominal,L,V,B,r,initial,A=None,epsilon=None):
    """The listed joint transition/charge rows AND nominal define the envelope.

    A claimed statistical/physical confidence-region inclusion is not inferred.
    """
    if not vertices:
        raise ValueError("no supplied envelope")
    models=tuple(vertices)+(nominal,)
    for item in models:
        validate(item)
    shape=tuple(map(len,nominal.rows))
    if any(tuple(map(len,item.rows))!=shape for item in models):
        raise ValueError("model interface mismatch")
    n=len(shape)
    L,V,B=(potential(v,n) for v in (L,V,B))
    r=row_values(r,shape,"error")
    mu=tuple(map(exact,initial))
    if len(mu)!=n+2 or any(p<0 for p in mu) or sum(mu)!=1:
        raise ValueError("invalid common initial law")
    if (A is None)!=(epsilon is None):
        raise ValueError("terminal potential and error register must be supplied together")
    if A is not None:
        A=potential(A,n)
        epsilon=row_values(epsilon,shape,"terminal error")
    slacks=[]
    for item in models:
        for x,acts in enumerate(item.rows):
            for a,row in enumerate(acts):
                dot=lambda f:sum(p*v for p,v in zip(row,f))
                duration=L[x]-1-dot(L)
                work=V[x]-item.charges[x][a]-dot(V)
                ref=nominal.rows[x][a]
                error=abs(item.charges[x][a]-nominal.charges[x][a])+sum(
                    V[y]*abs(row[y]-ref[y]) for y in range(n))
                transfer=r[x][a]-error
                reserve=B[x]-r[x][a]-dot(B)
                if min(duration,work,transfer,reserve)<0:
                    raise ValueError("duration/work/error potential inequality failed")
                record=dict(duration=duration,work=work,error=transfer,reserve=reserve)
                if A is not None:
                    tv=sum(abs(p-q) for p,q in zip(row,ref))/2
                    event_row=epsilon[x][a]-tv
                    event_reserve=A[x]-epsilon[x][a]-dot(A)
                    if min(event_row,event_reserve)<0:
                        raise ValueError("full-row terminal certificate failed")
                    record.update(event_row=event_row,event_reserve=event_reserve)
                slacks.append(record)
    integrate=lambda f:sum(p*v for p,v in zip(mu,f))
    return dict(expected_steps=integrate(L),expected_cost=integrate(V),
                cost_error=integrate(B),
                terminal_error=None if A is None else min(F(1),integrate(A)),
                terminal_status="NOT_CERTIFIED" if A is None else "CERTIFIED",
                minimum_slacks={key:min(row[key] for row in slacks)
                                for key in slacks[0]})

def survival_bound(certificate,horizon):
    if type(horizon) is not int or horizon<0:
        raise ValueError("nonnegative integer horizon required")
    return min(F(1),certificate["expected_steps"]/(horizon+1))
