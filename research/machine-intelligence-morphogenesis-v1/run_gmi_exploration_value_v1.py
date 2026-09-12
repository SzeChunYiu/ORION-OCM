from fractions import Fraction
import json

def cell(p,q,c):
    p,q,c=Fraction(p),Fraction(q),Fraction(c)
    th1_s0=p*(1-q); th0_s0=(1-p)*q
    th1_s1=p*q;     th0_s1=(1-p)*(1-q)
    post=max(th1_s0,th0_s0)+max(th1_s1,th0_s1)
    base=max(p,1-p)
    return post-base-c

pos=tie=neg=0
for pnum in range(1,10):
    p=Fraction(pnum,10)
    for qnum in range(5,11):
        q=Fraction(qnum,10)
        for cnum in range(0,6):
            c=Fraction(cnum,20)
            v=cell(p,q,c)
            if v>0: pos+=1
            elif v==0: tie+=1
            else: neg+=1

print(json.dumps({
 "artifact":"GMI_EXPLORATION_VALUE_RECEIPT_V1",
 "cells":pos+tie+neg,
 "explore":pos,
 "ties":tie,
 "exploit":neg,
 "terminal":"EXPLORATION_VALUE_EXACT_GRID_GREEN"
},indent=2,sort_keys=True))
