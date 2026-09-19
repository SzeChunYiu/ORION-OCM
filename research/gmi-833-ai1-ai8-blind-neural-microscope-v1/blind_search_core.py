from __future__ import annotations
from collections import defaultdict, deque

DOMAIN=((0,0),(0,1),(1,0),(1,1))
TARGET_DIFF=tuple(a^b for a,b in DOMAIN)
TARGET_ID=tuple(a for a,b in DOMAIN)
LIMIT=8


def atom_semantics():
    return {
      ('X0',):tuple(a for a,b in DOMAIN),
      ('X1',):tuple(b for a,b in DOMAIN),
      ('C',-1):(-1,)*4,
      ('C',0):(0,)*4,
      ('C',1):(1,)*4,
    }

def expr_semantics(expr):
    tag=expr[0]
    if tag in ('X0','X1','C'): return atom_semantics()[expr]
    if tag=='N': return tuple(-v for v in expr_semantics(expr[1]))
    if tag=='P': return tuple(max(0,v) for v in expr_semantics(expr[1]))
    if tag=='A': return tuple(x+y for x,y in zip(expr_semantics(expr[1]),expr_semantics(expr[2])))
    raise ValueError(tag)

def expr_size(expr):
    if expr[0] in ('X0','X1','C'): return 1
    if expr[0] in ('N','P'): return 1+expr_size(expr[1])
    return 1+expr_size(expr[1])+expr_size(expr[2])

def bounded(sem): return all(-LIMIT<=v<=LIMIT for v in sem)

def semantic_dp(target,max_size=11):
    best={}; by=defaultdict(list)
    for expr,sem in atom_semantics().items():
        if sem not in best:
            best[sem]=(1,expr); by[1].append((sem,expr))
    if target in best: return {'expr':best[target][1],'size':1,'unique_semantics':len(best)}
    for size in range(2,max_size+1):
        for sem,expr in tuple(by[size-1]):
            for tag in ('N','P'):
                nsem=tuple(-v for v in sem) if tag=='N' else tuple(max(0,v) for v in sem)
                if bounded(nsem) and nsem not in best:
                    nexpr=(tag,expr); best[nsem]=(size,nexpr); by[size].append((nsem,nexpr))
        for left_size in range(1,size-1):
            right_size=size-1-left_size
            if left_size>right_size: continue
            for s1,e1 in tuple(by[left_size]):
                for s2,e2 in tuple(by[right_size]):
                    nsem=tuple(x+y for x,y in zip(s1,s2))
                    if bounded(nsem) and nsem not in best:
                        # ADD is commutative semantically; canonical text ordering is presentation only.
                        a,b=sorted((e1,e2),key=repr)
                        nexpr=('A',a,b); best[nsem]=(size,nexpr); by[size].append((nsem,nexpr))
        if target in best:
            return {'expr':best[target][1],'size':best[target][0],'unique_semantics':len(best)}
    return None

def execute_stack(program):
    st=[]; atoms=atom_semantics()
    for op in program:
        if op=='PX0': st.append(atoms[('X0',)])
        elif op=='PX1': st.append(atoms[('X1',)])
        elif op=='CM1': st.append(atoms[('C',-1)])
        elif op=='C0': st.append(atoms[('C',0)])
        elif op=='C1': st.append(atoms[('C',1)])
        elif op=='NEG': st[-1]=tuple(-v for v in st[-1])
        elif op=='POS': st[-1]=tuple(max(0,v) for v in st[-1])
        elif op=='ADD':
            b=st.pop(); a=st.pop(); st.append(tuple(x+y for x,y in zip(a,b)))
        else: raise ValueError(op)
        if len(st)>3 or not all(bounded(s) for s in st): raise ValueError('resource bound')
    return tuple(st)

def stack_bfs(target,max_len=11):
    pushes=(('PX0',atom_semantics()[('X0',)]),('PX1',atom_semantics()[('X1',)]),('CM1',(-1,)*4),('C0',(0,)*4),('C1',(1,)*4))
    q=deque([((),())]); seen={()}; expanded=0
    while q:
        stack,prog=q.popleft()
        if prog and len(stack)==1 and stack[0]==target:
            return {'program':prog,'length':len(prog),'states_seen':len(seen),'expanded':expanded}
        if len(prog)>=max_len: continue
        if len(stack)<3:
            for name,sem in pushes:
                ns=stack+(sem,)
                if ns not in seen:
                    seen.add(ns); q.append((ns,prog+(name,))); expanded+=1
        if stack:
            for name in ('NEG','POS'):
                s=stack[-1]; sem=tuple(-v for v in s) if name=='NEG' else tuple(max(0,v) for v in s)
                ns=stack[:-1]+(sem,)
                if bounded(sem) and ns not in seen:
                    seen.add(ns); q.append((ns,prog+(name,))); expanded+=1
        if len(stack)>=2:
            a,b=stack[-2],stack[-1]; sem=tuple(x+y for x,y in zip(a,b)); ns=stack[:-2]+(sem,)
            if bounded(sem) and ns not in seen:
                seen.add(ns); q.append((ns,prog+('ADD',))); expanded+=1
    return None

def direct_candidates():
    # Generic external competitors; names here describe mechanisms, not catalog families.
    return {
      'FINITE_MAP':TARGET_DIFF,
      'EQUALITY_CONDITIONAL':TARGET_DIFF,
      'DIRECT_X0':TARGET_ID,
    }

def score_semantics(sem,target):
    return {'errors':sum(int(a!=b) for a,b in zip(sem,target)),'verified':sem==target}

def discover(target):
    a=semantic_dp(target); b=stack_bfs(target)
    out=[]
    if a: out.append({'source':'SEMANTIC_TREE_DP','artifact':a['expr'],'primitive_size':a['size'],'semantics':expr_semantics(a['expr'])})
    if b: out.append({'source':'STACK_STATE_BFS','artifact':b['program'],'primitive_size':b['length'],'semantics':execute_stack(b['program'])[0]})
    return out
