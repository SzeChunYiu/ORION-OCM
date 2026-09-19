from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction

@dataclass
class Node:
    value: Fraction
    parents: tuple[tuple[int,Fraction], ...]

class Tape:
    def __init__(self): self.nodes=[]
    def leaf(self,v):
        self.nodes.append(Node(Fraction(v),())); return len(self.nodes)-1
    def add(self,a,b):
        self.nodes.append(Node(self.nodes[a].value+self.nodes[b].value,((a,Fraction(1)),(b,Fraction(1))))); return len(self.nodes)-1
    def mul(self,a,b):
        va,vb=self.nodes[a].value,self.nodes[b].value
        self.nodes.append(Node(va*vb,((a,vb),(b,va)))); return len(self.nodes)-1
    def pos(self,a):
        va=self.nodes[a].value; slope=Fraction(1) if va>0 else Fraction(0)
        self.nodes.append(Node(max(Fraction(0),va),((a,slope),))); return len(self.nodes)-1
    def reverse(self,out):
        adj=[Fraction(0) for _ in self.nodes]; adj[out]=Fraction(1)
        for i in range(out,-1,-1):
            for p,local in self.nodes[i].parents: adj[p]+=adj[i]*local
        return tuple(adj)

def graph_loss(theta,x,target):
    t=Tape(); x0=t.leaf(x[0]); x1=t.leaf(x[1]); ps=[t.leaf(v) for v in theta]
    w10,w11,w20,w21,v1,v2=ps
    a=t.mul(w10,x0); b=t.mul(w11,x1); z1=t.add(a,b); h1=t.pos(z1)
    c=t.mul(w20,x0); d=t.mul(w21,x1); z2=t.add(c,d); h2=t.pos(z2)
    e=t.mul(v1,h1); f=t.mul(v2,h2); y=t.add(e,f)
    tgt=t.leaf(target); neg=t.leaf(-1); nt=t.mul(neg,tgt); diff=t.add(y,nt)
    sq=t.mul(diff,diff); half=t.leaf(Fraction(1,2)); loss=t.mul(half,sq)
    return t,loss,ps,y

def reverse_gradient(theta,x,target):
    tape,loss,params,y=graph_loss(theta,x,target); adj=tape.reverse(loss)
    return tuple(adj[p] for p in params),tape.nodes[loss].value,tape.nodes[y].value,len(tape.nodes)

def loss_value(theta,x,target): return graph_loss(theta,x,target)[0].nodes[graph_loss(theta,x,target)[1]].value

def finite_difference(theta,x,target,h=Fraction(1,10)):
    out=[]
    for i in range(len(theta)):
        plus=list(theta); minus=list(theta); plus[i]+=h; minus[i]-=h
        out.append((loss_value(tuple(plus),x,target)-loss_value(tuple(minus),x,target))/(2*h))
    return tuple(out)

def update(theta,grad,eta=Fraction(1,10)):
    return tuple(Fraction(p)-eta*g for p,g in zip(theta,grad))

def cost_vectors(parameter_count=6,stored_nodes=24):
    return {
      'REVERSE_ACCUMULATION':{'forward_evals':1,'backward_sweeps':1,'stored_intermediates':stored_nodes,'parameter_trials':0,'randomness':0},
      'FINITE_DIFFERENCE':{'forward_evals':2*parameter_count,'backward_sweeps':0,'stored_intermediates':1,'parameter_trials':2*parameter_count,'randomness':0},
      'MUTATION_SEARCH':{'forward_evals':2*parameter_count,'backward_sweeps':0,'stored_intermediates':1,'parameter_trials':2*parameter_count,'randomness':1},
      'EXACT_GRID':{'forward_evals':3**parameter_count,'backward_sweeps':0,'stored_intermediates':1,'parameter_trials':3**parameter_count,'randomness':0}
    }

def certificate():
    theta=(Fraction(1),Fraction(-1),Fraction(-1),Fraction(1),Fraction(1),Fraction(1))
    cases=[]
    for x,target,expected in [((1,0),0,(1,0,0,0,1,0)),((0,1),0,(0,0,0,1,0,1))]:
        g,l,y,n=reverse_gradient(theta,x,target); fd=finite_difference(theta,x,target)
        assert g==tuple(Fraction(v) for v in expected)
        assert fd==g
        new=update(theta,g)
        assert loss_value(new,x,target)<l
        cases.append({'x':list(x),'target':target,'y':str(y),'loss':str(l),'gradient':[str(v) for v in g],'finite_difference':[str(v) for v in fd],'nodes':n})
    # Capability of the fixed computation does not depend on gradient availability.
    outputs=[]
    for x in ((0,0),(0,1),(1,0),(1,1)):
        _,_,y,_=reverse_gradient(theta,x,x[0]^x[1]); outputs.append(int(y))
    assert outputs==[0,1,1,0]
    return {'reverse_cases':cases,'fixed_outputs_with_or_without_gradient':outputs,'cost_vectors':cost_vectors(),'gradient_computation_separate_from_update':True,'chain_rule_parent_owned':True}
