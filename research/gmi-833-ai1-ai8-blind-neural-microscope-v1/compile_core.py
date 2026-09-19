from __future__ import annotations
from itertools import product

BITS=((0,0),(0,1),(1,0),(1,1))
COEFF=(-1,0,1)

def pos(z): return max(0,z)

def mul_repeat(k,x):
    sign=-1 if k<0 else 1
    total=0
    for _ in range(abs(k)): total += x
    return sign*total

def dot_repeat(weights,values):
    total=0
    for w,x in zip(weights,values): total += mul_repeat(w,x)
    return total

def direct_net(c,x):
    w10,w11,w20,w21,v1,v2=c; x0,x1=x
    h1=pos(w10*x0+w11*x1); h2=pos(w20*x0+w21*x1)
    return v1*h1+v2*h2

def lower_net(c,x):
    w10,w11,w20,w21,v1,v2=c; x0,x1=x
    h1=pos(dot_repeat((w10,w11),(x0,x1)))
    h2=pos(dot_repeat((w20,w21),(x0,x1)))
    return dot_repeat((v1,v2),(h1,h2))

def scale_expr(k,e):
    if k==0:return ('C',0)
    if k==1:return e
    if k==-1:return ('N',e)
    raise ValueError('registered family coefficient out of range')

def net_expr(c):
    w10,w11,w20,w21,v1,v2=c
    h1=('P',('A',scale_expr(w10,('X0',)),scale_expr(w11,('X1',))))
    h2=('P',('A',scale_expr(w20,('X0',)),scale_expr(w21,('X1',))))
    return ('A',scale_expr(v1,h1),scale_expr(v2,h2))

def eval_expr(e,x):
    t=e[0]
    if t=='X0':return x[0]
    if t=='X1':return x[1]
    if t=='C':return e[1]
    if t=='N':return -eval_expr(e[1],x)
    if t=='P':return pos(eval_expr(e[1],x))
    if t=='A':return eval_expr(e[1],x)+eval_expr(e[2],x)
    raise ValueError(t)

def to_stack(e):
    t=e[0]
    if t=='X0':return ('PX0',)
    if t=='X1':return ('PX1',)
    if t=='C':return (f'C{e[1]}',)
    if t=='N':return to_stack(e[1])+('NEG',)
    if t=='P':return to_stack(e[1])+('POS',)
    if t=='A':return to_stack(e[1])+to_stack(e[2])+('ADD',)
    raise ValueError(t)

def run_stack(p,x):
    st=[]
    for op in p:
        if op=='PX0':st.append(x[0])
        elif op=='PX1':st.append(x[1])
        elif op.startswith('C'):st.append(int(op[1:]))
        elif op=='NEG':st[-1]=-st[-1]
        elif op=='POS':st[-1]=pos(st[-1])
        elif op=='ADD':
            b=st.pop();a=st.pop();st.append(a+b)
        else:raise ValueError(op)
    assert len(st)==1
    return st[0]

def encode_signed(z): return (max(z,0),max(-z,0))
def decode_signed(pair): return pair[0]-pair[1]

def census():
    mul_cases=0
    for k in range(-2,3):
        for x in range(-3,4):
            assert mul_repeat(k,x)==k*x;mul_cases+=1
    signed_cases=0
    for z in range(-6,7):
        assert decode_signed(encode_signed(z))==z;signed_cases+=1
    nets=evals=lower_bad=stack_bad=0;max_stack_code=0
    for c in product(COEFF,repeat=6):
        nets+=1;e=net_expr(c);p=to_stack(e);max_stack_code=max(max_stack_code,len(p))
        for x in BITS:
            d=direct_net(c,x);l=lower_net(c,x);s=run_stack(p,x)
            evals+=1;lower_bad+=int(d!=l);stack_bad+=int(d!=s)
    xor=(1,-1,-1,1,1,1)
    xor_out=tuple(lower_net(xor,x) for x in BITS)
    return {
      'multiplication_repeated_addition_cases':mul_cases,
      'signed_pair_roundtrip_cases':signed_cases,
      'supplied_family_networks':nets,'supplied_family_input_evaluations':evals,
      'lower_arithmetic_mismatches':lower_bad,'stack_presentation_mismatches':stack_bad,
      'max_stack_code_length':max_stack_code,'xor_coefficients':xor,'xor_outputs':xor_out,
      'transcendentals_imported':False
    }
