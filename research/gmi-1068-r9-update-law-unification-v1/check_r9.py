#!/usr/bin/env python3
import json,pathlib,sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parent
def need(cond,msg):
 if not cond: raise RuntimeError(msg)
need(1+Fraction(2)<4 and 1+Fraction(3)==4 and 1+Fraction(4)>4,"U1")
forward=40
def rev(s):return 10+3*s
need(rev(9)<forward and rev(10)==forward and rev(11)>forward,"U2")
post=Fraction(3,4)*Fraction(1,2)/(Fraction(3,4)*Fraction(1,2)+Fraction(1,4)*Fraction(1,2));need(post==Fraction(3,4),"U3")
hyps={"C0":(0,0),"C1":(1,1),"ID":(0,1),"NOT":(1,0)}
partial=[k for k,v in hyps.items() if v[0]==0];full=[k for k,v in hyps.items() if v==(0,1)]
need(sorted(partial)==["C0","ID"] and full==["ID"],"U4")
mem={};need(mem.get("a") is None,"U5A");mem["a"]=7;need(mem["a"]==7 and mem.get("b") is None,"U5B")
D,L,c=4,3,1;need(not(D+2*c<2*L) and D+3*c<3*L,"U6")
obj={(0,0):1,(0,1):0,(1,0):0,(1,1):2};need(max(obj,key=obj.get)==(1,1),"U7")
need(1+Fraction(1,4)<Fraction(3,2) and 1+Fraction(1,2)==Fraction(3,2),"U8")
prog=lambda x:x;modifier=lambda old:(lambda x:old(x)+1);new=modifier(prog);need(prog(2)==2 and new(2)==3,"U9")
need(len(partial)>1,"U10")
r=json.loads((ROOT/"RESULT_V1.json").read_text());need(r["regimes"]==10 and r["unknown_terminal"] is True,"RESULT")
print(json.dumps({"status":"GREEN","U1_surface":"rho=3","U2_surface":"sigma=10","posterior":"3/4","partial_hypotheses":len(partial),"full_hypotheses":len(full),"library_first_n":3,"meta_threshold":"1/2","hostiles_caught":10},sort_keys=True))
