"""Independent signed half-line intersection and whole-cell/codec certificates."""
from fractions import Fraction as F


def need(condition,message):
    if not condition:raise ValueError(message)


def intervals(rows,lo,hi):
    result={}
    for label,a,b,p,e in rows:
        if not (p and e):result[label]=None;continue
        lower,upper=lo,hi
        for other,c,d,q,f in rows:
            if not (q and f):continue
            slope=b-d;bound=c-a
            if slope==0:
                if bound<0:lower,upper=hi+1,lo
            elif slope>0:upper=min(upper,bound/slope)
            else:lower=max(lower,bound/slope)
        result[label]=None if lower>upper else (lower,upper)
    return result


def winners(rows,t):
    values=[(label,a+b*t) for label,a,b,p,e in rows if p and e]
    return tuple(sorted(label for label,value in values if all(value<=v for _,v in values)))


def verify_diagram(rows,lo,hi,diagram):
    need(type(diagram) is dict and set(diagram)=={'boundaries','cells','possible','universal','unique_everywhere'},'diagram schema')
    boundaries,cells=diagram['boundaries'],diagram['cells']
    need(type(boundaries) is tuple and type(cells) is tuple,'record tuples')
    need(all(type(record) is tuple and len(record)==2 and type(record[0]) is F for record in boundaries),'boundary records')
    points=tuple(record[0] for record in boundaries)
    need(bool(points) and points[0]==lo and points[-1]==hi,'endpoint coverage')
    need(all(a<b for a,b in zip(points,points[1:])),'boundary ordering')
    need(len(cells)==len(points)-1,'cell coverage')
    feasible=intervals(rows,lo,hi)
    active=[(a,b) for _,a,b,p,e in rows if p and e]
    pairs=[(a-c,b-d) for index,(a,b) in enumerate(active) for c,d in active[index+1:]]
    counts=dict(boundaries=0,cells=0,whole_cell_memberships=0,pair_cell_checks=0,boundary_memberships=0)
    for t,labels in boundaries:
        expected=tuple(sorted(label for label,i in feasible.items() if i is not None and i[0]<=t<=i[1]))
        need(type(labels) is tuple and labels==expected,'boundary labels')
        if lo<t<hi:need(any(b!=0 and a+b*t==0 for a,b in pairs),'spurious root')
        counts['boundaries']+=1;counts['boundary_memberships']+=len(rows)
    for index,record in enumerate(cells):
        need(type(record) is tuple and len(record)==4,'cell record')
        a,b,mid,labels=record
        need(all(type(x) is F for x in (a,b,mid)),'exact cell numbers')
        need((a,b)==points[index:index+2] and mid==(a+b)/2,'cell adjacency/sample')
        expected=[]
        for label,i in feasible.items():
            if i is not None:
                covers=i[0]<=a and b<=i[1]
                disjoint=i[1]<=a or b<=i[0]
                need(covers or disjoint,'partially covered open cell')
                if covers:expected.append(label)
            counts['whole_cell_memberships']+=1
        need(type(labels) is tuple and labels==tuple(sorted(expected)),'whole-cell labels')
        for intercept,slope in pairs:
            need((intercept+slope*a)*(intercept+slope*b)>=0,'concealed nonparallel pair root')
            counts['pair_cell_checks']+=1
        counts['cells']+=1
    possible=tuple(sorted(label for label,i in feasible.items() if i is not None))
    universal=tuple(sorted(label for label,i in feasible.items() if i==(lo,hi)))
    for key,expected in (('possible',possible),('universal',universal)):
        need(type(diagram[key]) is tuple and diagram[key]==expected,key+' summary')
    unique=possible[0] if len(possible)==1 else None
    need(diagram['unique_everywhere']==unique,'unique summary')
    need(universal==tuple(sorted(set(winners(rows,lo))&set(winners(rows,hi)))),'endpoint law')
    return counts


def verify_codec(rows,t,context,decoder):
    n=len(rows)
    need(type(context.n) is int and type(context.m) is int and (context.n,context.m)==(n,n),'codec dimensions')
    need(type(decoder) is tuple and len(decoder)==n,'decoder carrier')
    need(type(context.admitted) is tuple and type(context.defined) is tuple and
         all(type(x) is bool for x in context.admitted+context.defined),'flag types')
    need(type(context.values) is tuple and all(x is None or type(x) is int for x in context.values),'value code types')
    need(type(context.order) is tuple and all(type(row) is tuple and all(type(x) is bool for x in row) for row in context.order),'order types')
    expected=tuple((label,a+b*t) for label,a,b,_,_ in rows)
    need(all(type(x) is tuple and len(x)==2 and type(x[0]) is str and type(x[1]) is F for x in decoder),'decoder types')
    need(decoder==expected and len(set(decoder))==n,'decoder evaluation/injectivity')
    need(context.admitted==tuple(p for _,_,_,p,_ in rows),'fixed P')
    need(context.defined==tuple(e for _,_,_,_,e in rows),'fixed E')
    need(context.values==tuple(i if row[4] else None for i,row in enumerate(rows)),'coded evaluation')
    need(context.order==tuple(tuple(expected[j][1]<=expected[i][1] for j in range(n)) for i in range(n)),'comparison reflection')
    active=tuple(i for i,row in enumerate(rows) if row[3] and row[4])
    maximal=tuple(i for i in active if not any(context.order[i][j] and not context.order[j][i] for j in active))
    need(tuple(sorted(decoder[i][0] for i in maximal))==winners(rows,t),'all maximal IDs')
    return tuple(('ILLEGAL',None) if not row[3] else ('UNDEFINED',None) if not row[4] else ('VALUE',expected[i]) for i,row in enumerate(rows))
